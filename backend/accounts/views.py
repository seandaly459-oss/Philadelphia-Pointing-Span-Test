from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from api.models import Doctor

@never_cache
def login_view(request):
    if request.user.is_authenticated:
        return redirect('/portal/dashboard/')
    if request.method == 'POST':
        mode = request.POST.get('mode', 'login')
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        

        if mode == 'create':
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            confirm_password = request.POST.get('confirm_password', '').strip()

            if not first_name or not last_name:
                messages.error(request, 'First name and last name are required.')
                return render(request, 'accounts/login.html')

            if password != confirm_password:
                messages.error(request, 'Passwords do not match.')
                return render(request, 'accounts/login.html')

            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already taken.')
                return render(request, 'accounts/login.html')

            try:
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                )
                Doctor.objects.create(user=user, username=username, password_hash='')
                messages.success(request, 'Account created! You can now sign in.')
            except Exception as e:
                messages.error(request, f'Error creating account: {str(e)}')
                return render(request, 'accounts/login.html')
            return render(request, 'accounts/login.html')

        else:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/portal/dashboard/')
            else:
                messages.error(request, 'Invalid username or password.')
                return render(request, 'accounts/login.html')

    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect('/accounts/login/')