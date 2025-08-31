from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
# ✅ 登入功能

def login_view(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'accounts/login.html', {'form': form})  # 有錯時也回傳 form
    return render(request, 'accounts/login.html', {'form': form})


# ✅ 註冊功能
def register_view(request):
    form = UserCreationForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('/accounts/login/')
    return render(request, 'accounts/register.html', {'form': form})

# ✅ 登出功能
@login_required
def logout_view(request):
    logout(request)
    return redirect('/accounts/login/')
