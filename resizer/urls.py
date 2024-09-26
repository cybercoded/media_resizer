from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('upload/', views.upload, name='upload'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('preview/<int:id>/', views.preview, name='preview'),
    path('update-settings/', views.update_settings, name='update_settings'),
    path('delete-images/<int:original_image_id>/', views.delete_images, name='delete_images'),
    path('download_all_resized_images/<int:id>/', views.download_all_resized_images, name='download_all_resized_images'),    path('delete_images/<int:original_image_id>/', views.delete_images, name='delete_images'),
    path('logout/', views.logout, name='logout'),
]
