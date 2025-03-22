from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Profile
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
