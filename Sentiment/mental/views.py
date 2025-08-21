from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            messages.error(request, "Passwords don't match!")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return redirect('signup')

        user = User.objects.create_user(username=username, email=email, password=password1)
        messages.success(request, "Account created successfully! Please login to continue.")
        return redirect('login')

    return render(request, 'signup.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('prediction')
        else:
            messages.error(request, "Invalid username or password!")
            return redirect('login')

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect('signup')

@login_required(login_url='login')
def prediction_view(request):
    return render(request, 'Prediction.html')

@login_required(login_url='login')
def about_view(request):
    return render(request, 'about.html')

@login_required(login_url='login')
def contact_view(request):
    return render(request, 'contact.html')

def home_view(request):
    return render(request, 'index.html') 