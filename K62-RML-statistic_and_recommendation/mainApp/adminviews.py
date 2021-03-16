from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, get_user_model, logout
from django.http import HttpResponseRedirect, HttpResponse
from mainApp.models import CustomUser
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.template.response import TemplateResponse
from django.urls import reverse


def login_page(request):
    return TemplateResponse(request, 'student/login.html')


# nhận request và xứ lý username và password người dùng nhập để xác minh
def user_login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            if username.strip() == "" or password.strip() == "":
                messages.error(request, 'Hãy nhập đầy đủ thông tin.')
                return TemplateResponse(request, 'student/login.html')
            users = get_user_model()
            user = users.objects.filter(username=username, password=password).first()
            if user:
                login(request, user)
                listFunction = user.list_function()
                if len(listFunction) > 0:
                    return HttpResponseRedirect(reverse(listFunction[0]))
                else:
                    return HttpResponseRedirect('/')
            else:
                context = {
                    'username': username
                }
                messages.error(request, 'Tên đăng nhập hoặc mật khẩu sai.')
                return TemplateResponse(request, 'student/login.html', context=context)
        else:
            return TemplateResponse(request, 'student/login.html')

# Hàm logout ra khỏi tài khoản nếu đang ở trang thái login thì mới cho login
@login_required(login_url='/login/')
def user_logout(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('/')
    else:
        return TemplateResponse(request, 'student/login.html')
