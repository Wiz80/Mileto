from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.utils import IntegrityError

# Create your views here.

def miletoLogin(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = User.objects.get(email=email)
        user = authenticate(request, username=user.username, password = password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 
                         'users/login.html', 
                         {'error': 'La combinación de usuario y contraseña no es correcta.'})

    return render(request, 'users/login.html')

def miletoSignUp(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        firstName = request.POST['first_name']
        lastName = request.POST['last_name']
        password = request.POST['password']
        is_further = len(password) >= 8
        is_upper = len([i for i in password if i.isupper() == 1]) >= 1
        is_lower = len([i for i in password if i.islower() == 1]) >= 1
        is_num = len([i for i in password if i.isdigit() == 1]) >= 1
        if not(is_further and is_upper and is_lower and is_num):
            return render(request, 
                        'users/signup.html',
                        {'error_pass': True})
        try: 
            user = User.objects.create_user(username = username, password = password)
        except IntegrityError:
            return render(request, 
                         'users/signup.html',
                         {'error_user': 'El usuario ya ha sido creado previamente'})

        user.email = email
        user.first_name = firstName
        user.last_name = lastName
        user.save()

        return redirect('home')
    
    return render(request, 'users/signup.html')