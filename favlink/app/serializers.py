from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from .models import Favorite, Category, Tag

User = get_user_model()
class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    repassword = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e)
        return value
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'repassword')


    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('repassword')
        if password != password2:
            raise serializers.ValidationError('Passwords does not match.')
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            validated_data['username'], validated_data['email'], validated_data['password']
        )
        return user


User = get_user_model()
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, style={'input_type': 'password'})

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        user = User.objects.filter(username=username).first()
        if not user or not user.check_password(password):
            raise serializers.ValidationError('Invalid username or password.')
        return attrs

class CategorySerializer(serializers.ModelSerializer):
    def __init__(self, *args, user=None, **kwargs):
        self.user = user 
        super().__init__(*args, **kwargs) 

    def create(self, validated_data):
        if self.user is not None: 
            validated_data['user'] = self.user
        return super().create(validated_data)

    class Meta:
        model = Category
        fields = ('id', 'name', 'user_id')

class TagSerializer(serializers.ModelSerializer):
    def __init__(self, *args, user=None, **kwargs):
        self.user = user 
        super().__init__(*args, **kwargs) 

    def create(self, validated_data):
        if self.user is not None: 
            validated_data['user'] = self.user
        return super().create(validated_data)

    class Meta:
        model = Tag
        fields = ('id', 'name', 'user_id')

class FavoriteSerializer(serializers.ModelSerializer):

    def __init__(self, *args, user=None, **kwargs):
        self.user = user 
        super().__init__(*args, **kwargs) 
    

    def __init__(self, *args, user=None, **kwargs):
        self.user = user 
        super().__init__(*args, **kwargs) 
    
    class Meta:
        model = Favorite
        fields = ['id', 'user_id','url', 'title', 'category', 'tags', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def validate_url(self, value):
        if not isinstance(value, str) or not value.startswith('http'):
            raise serializers.ValidationError('Invalid URL format.')
        
        return value
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        tag_names = [tag.name for tag in instance['tags'] if tag.user_id == self.user]
        data['tags'] = tag_names
        data['category'] = instance['category'].name
        return data
    

class FavoriteWithTagNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        tag_names = [tag.name for tag in instance.tags.all()]
        data['tags'] = tag_names
        data['category'] = instance.category.name
        return data