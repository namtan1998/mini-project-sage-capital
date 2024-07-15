from django.contrib import admin
from django.urls import path
from app.views import UserRegister, UserLogin, FavoriteManagement, TagManagement, CategoryManagement

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/register', UserRegister.as_view(), name='register'),
    path('user/login', UserLogin.as_view(), name='login'),
    path('favorite', FavoriteManagement.as_view(), name='get-favorite'),
    path('favorite/add', FavoriteManagement.as_view(), name='add-favorite'),
    path('favorite/<int:pk>/delete', FavoriteManagement.as_view(), name='delete-favorite'),
    path('favorite/<int:pk>/update', FavoriteManagement.as_view(), name='update-favorite'),
    path('tag', TagManagement.as_view(), name='get-tag'),
    path('tag/add', TagManagement.as_view(), name='add-tag'),
    path('tag/<int:pk>/delete', TagManagement.as_view(), name='delete-tag'),
    path('tag/<int:pk>/update', TagManagement.as_view(), name='update-tag'),
    path('category', CategoryManagement.as_view(), name='get-category'),
    path('category/add', CategoryManagement.as_view(), name='add-category'),
    path('category/<int:pk>/delete', CategoryManagement.as_view(), name='delete-category'),
    path('category/<int:pk>/update', CategoryManagement.as_view(), name='update-category'),
    
]