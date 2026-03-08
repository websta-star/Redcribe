from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('age-gate/', views.age_gate, name='age_gate'),
    path('age-accept/', views.age_accept, name='age_accept'),
    path('', views.home, name='home'),
    path('video/<int:pk>/', views.video_detail, name='video_detail'),  # fixed
    path('session-test/', views.session_test, name='session_test'),  # optional
    path('upload/', views.upload_video, name='upload_video'),
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('my-videos/', views.my_videos, name='my_videos'),
    path('video/<int:pk>/like/', views.toggle_like, name='toggle_like'),
    path('video/<int:pk>/edit/', views.edit_video, name='edit_video'),
    path('video/<int:pk>/delete/', views.delete_video, name='delete_video'),
    path('photos/', views.photo_gallery, name='photo_gallery'),
    path('photo/upload/', views.upload_photo, name='upload_photo'),
    path('photo/<int:pk>/', views.photo_detail, name='photo_detail'),
    path('photo/<int:pk>/edit/', views.edit_photo, name='edit_photo'),
    path('photo/<int:pk>/delete/', views.delete_photo, name='delete_photo'),
    path('contact/', views.contact, name='contact'),
    path('privacy/', views.privacy_policy, name='privacy'),
    path('terms/', views.terms_policy, name='terms'),
    path('dmca/', views.dmca, name='dmca'),
    path('removal/', views.removal, name='removal'),
    path('2257/', views.compliance, name='compliance'),
]    