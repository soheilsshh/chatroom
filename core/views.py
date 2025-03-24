from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Profile, Forum, Message
import re

# Create your views here.

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validation
        errors = []
        
        # Username validation
        if not username or len(username) < 3:
            errors.append('Username must be at least 3 characters long')
        elif User.objects.filter(username=username).exists():
            errors.append('Username already exists')
            
        # Email validation
        if not email or not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            errors.append('Please enter a valid email address')
        elif User.objects.filter(email=email).exists():
            errors.append('Email already exists')
            
        # Password validation
        if not password or len(password) < 8:
            errors.append('Password must be at least 8 characters long')
        elif password != confirm_password:
            errors.append('Passwords do not match')
            
        if not errors:
            user = User.objects.create_user(username=username, email=email, password=password)
            Profile.objects.create(user=user)
            login(request, user)
            return redirect('profile')
            
        return render(request, 'core/register.html', {'errors': errors})
        
    return render(request, 'core/register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            return render(request, 'core/login.html', {'error': 'Please fill in all fields'})
            
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('profile')
        else:
            return render(request, 'core/login.html', {'error': 'Invalid username or password'})
            
    return render(request, 'core/login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def profile_view(request):
    # this section will be done later , cleaer context
    context = {
        'user': request.user,
        'profile': request.user.profile,
        'bio': request.user.profile.bio,
        'avatar': request.user.profile.avatar,
        'created_at': request.user.profile.created_at,
        'updated_at': request.user.profile.updated_at,
    }
    return render(request, 'core/profile.html', context)

@login_required
def edit_profile(request):
    if request.method == 'POST':
        bio = request.POST.get('bio')
        avatar = request.FILES.get('avatar')
        
        profile = request.user.profile
        profile.bio = bio
        if avatar:
            profile.avatar = avatar
        profile.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
        
    context = {
        'user': request.user,
        'profile': request.user.profile,
        'bio': request.user.profile.bio,
        'avatar': request.user.profile.avatar,
    }
    return render(request, 'core/edit_profile.html', context)

@login_required
def create_forum(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        is_private = request.POST.get('is_private') == 'on'
        
        if not name or not description:
            messages.error(request, 'Please fill in all required fields')
            return render(request, 'core/create_forum.html')
            
        forum = Forum.objects.create(
            name=name,
            description=description,
            is_private=is_private,
            created_by=request.user
        )
        forum.members.add(request.user)
        return redirect('forum_detail', forum_id=forum.id)
        
    return render(request, 'core/create_forum.html')

@login_required
def forum_list(request):
    forums = Forum.objects.all()
    return render(request, 'core/forum_list.html', {'forums': forums})

@login_required
def join_forum(request, forum_id):
    forum = get_object_or_404(Forum, id=forum_id)
    if request.user not in forum.members.all():
        forum.members.add(request.user)
        messages.success(request, f'Successfully joined {forum.name}')
    return redirect('forum_detail', forum_id=forum_id)

@login_required
def forum_detail(request, forum_id):
    forum = get_object_or_404(Forum, id=forum_id)
    if request.user not in forum.members.all():
        forum.members.add(request.user)
    messages = Message.objects.filter(forum=forum).order_by('-created_at')[:50]
    return render(request, 'core/forum_detail.html', {
        'forum': forum,
        'messages': messages
    })
