from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('forums/', views.forum_list, name='forum_list'),
    path('forums/create/', views.create_forum, name='create_forum'),
    path('forums/<int:forum_id>/', views.forum_detail, name='forum_detail'),
    path('forums/<int:forum_id>/join/', views.join_forum, name='join_forum'),
    path('chat/private/<int:user_id>/', views.private_chat, name='private_chat'),
] 