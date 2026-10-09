from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages


def royxatdan_otish(request):
    if request.user.is_authenticated:
        return redirect('menu')
    if request.method == 'POST':
        ism = request.POST.get('first_name', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        parol = request.POST.get('password1', '')
        parol2 = request.POST.get('password2', '')

        if not all([ism, username, parol]):
            messages.error(request, "Barcha maydonlarni to'ldiring!")
            return render(request, 'accounts/royxat.html')
        if parol != parol2:
            messages.error(request, "Parollar mos kelmadi!")
            return render(request, 'accounts/royxat.html')
        if User.objects.filter(username=username).exists():
            messages.error(request, "Bu username band!")
            return render(request, 'accounts/royxat.html')
        if len(parol) < 8:
            messages.error(request, "Parol kamida 8 ta belgi bo'lishi kerak!")
            return render(request, 'accounts/royxat.html')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=parol,
            first_name=ism,
        )
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        messages.success(request, f"Xush kelibsiz, {ism}! 🎉")
        return redirect('menu')

    return render(request, 'accounts/royxat.html')


def kirish(request):
    if request.user.is_authenticated:
        return redirect('menu')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        parol = request.POST.get('password', '')
        user = authenticate(request, username=username, password=parol)
        if user:
            login(request, user)
            messages.success(request, f"Xush kelibsiz, {user.first_name or user.username}!")
            return redirect(request.GET.get('next', 'menu'))
        messages.error(request, "Username yoki parol noto'g'ri!")
    return render(request, 'accounts/kirish.html')


def chiqish(request):
    logout(request)
    messages.info(request, "Tizimdan chiqdingiz.")
    return redirect('menu')
