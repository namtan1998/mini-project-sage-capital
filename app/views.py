from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .serializers import FavoriteWithTagNameSerializer, RegisterSerializer, LoginSerializer, FavoriteSerializer, TagSerializer, CategorySerializer
from django.contrib.auth import get_user_model
from app.models import Favorite, Category, Tag
import requests
from django_filters import rest_framework as filters
from django.db.models import Q
from app.module import handle_category, handle_tags_id

User = get_user_model()

class UserRegister(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLogin(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        user = User.objects.get(username=username)

        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_200_OK)
    

class FavoriteManagement(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        try:
            category_id = handle_category(request.data, user)
        except (ValueError, Category.DoesNotExist)  as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            tags_id = handle_tags_id(request.data, user)
        except (ValueError, Tag.DoesNotExist) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        new_data = {
            'url': request.data['url'],
            'title': request.data['title'],
            'category': category_id,
            'tags': tags_id,
        }
        serializer = FavoriteSerializer(data=new_data, user=user.id)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        if serializer.is_valid():
            url = serializer.validated_data['url']
            category = serializer.validated_data.get('category', None)
            tags = serializer.validated_data.get('tags', [])

            try:
                response = requests.get(url)
                response.raise_for_status() 
                title = response.text[:100] 
            except requests.exceptions.RequestException as e:
                return Response({'error': f"Failed to fetch title: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
            
            user_favorites = Favorite.objects.filter(user=user)
            url_exists = user_favorites.filter(url=url).exists()

            if url_exists:
                return Response({'error': 'This URL is already favorited'}, status=status.HTTP_208_ALREADY_REPORTED)
            favorite = Favorite.objects.create(user=user, url=url, title=title, category=category)
            favorite.tags.set(tags)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request):
        user = request.user
        search_query = request.query_params
        if search_query:
            get_title = request.query_params.get('title', None)
            get_url = request.query_params.get('url', None)
            get_category = request.query_params.get('category', None)

            filters = Q()

            if get_title:
                filters |= Q(title__icontains=get_title)
            if get_url:
                filters |= Q(url__icontains=get_url)

            if get_category:
                try:
                    category = Category.objects.get(user=user, name=get_category)
                    filters &= Q(category=category)
                except Category.DoesNotExist:
                    return Response({'error': 'Invalid category name'}, status=status.HTTP_400_BAD_REQUEST)

            favorites = Favorite.objects.filter(user=user).filter(filters)
        else:
            favorites = Favorite.objects.filter(user=user)
        serializer = FavoriteWithTagNameSerializer(favorites, many=True)
        response_data = {
            'count': favorites.count(),
            'data': serializer.data
        }

        return Response(response_data)

    def delete(self, request, pk):
        user = request.user
        try:
            favorite = Favorite.objects.get(pk=pk, user=user)
        except Favorite.DoesNotExist:
            return Response({"msg": "Data Not Found"},status=status.HTTP_404_NOT_FOUND)
        favorite.delete()
        return Response({"msg": "success"}, status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, pk):
        user = request.user
        try:
            favorite = Favorite.objects.get(pk=pk, user=user)
        except Favorite.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = FavoriteSerializer(favorite, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data)
    
class TagManagement(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        serializer = TagSerializer(data=request.data, user=user)
        if serializer.is_valid():
            try:
                Tag.objects.get(user=user, name=request.data['name'])
                return Response({'error': 'Tag already exists'}, status=status.HTTP_400_BAD_REQUEST)
            except Tag.DoesNotExist:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    def get(self, request):
        user = request.user
        tag = Tag.objects.filter(user_id=user.id)
        serializer = TagSerializer(tag, many=True)
        response_data = {
            'count': tag.count(),
            'data': serializer.data
        }
        return Response(response_data)

    def delete(self, request, pk):
        user = request.user
        try:
            tag = Tag.objects.get(pk=pk, user=user)
        except Tag.DoesNotExist:
            return Response({"msg": "Data Not Found"},status=status.HTTP_404_NOT_FOUND)
        tag.delete()
        return Response({"msg": "success"}, status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, pk):
        user = request.user
        try:
            tag = Tag.objects.get(pk=pk, user=user)
        except Tag.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = TagSerializer(tag, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data)
        
    
class CategoryManagement(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        
        user = request.user
        serializer = CategorySerializer(data=request.data, user=user)
        if serializer.is_valid():
            try:
                Category.objects.get(user=user, name=request.data['name'])
                return Response({'error': 'Category already exists'}, status=status.HTTP_400_BAD_REQUEST)
            except Category.DoesNotExist:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    def get(self, request):
        user = request.user
        category = Category.objects.filter(user_id=user.id)
        
        serializer = CategorySerializer(category, many=True)
        response_data = {
            'count': category.count(),
            'data': serializer.data
        }

        return Response(response_data)

    def delete(self, request, pk):
        user = request.user
        try:
            category = Category.objects.get(pk=pk, user=user)
        except Category.DoesNotExist:
            return Response({"msg": "Data Not Found"},status=status.HTTP_404_NOT_FOUND)
        category.delete()
        return Response({"msg": "success"}, status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, pk):
        user = request.user
        try:
            category = Category.objects.get(pk=pk, user=user)
        except Category.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = CategorySerializer(category, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data)
