from django.shortcuts import render, redirect
from django.template.response import TemplateResponse
from django.http import HttpResponseRedirect
from django.urls import reverse


# Nếu đã đăng nhập thì hiển thị trang chức năng, nếu chưa hiển thị trang chủ
def home_page(request):
    if request.user.is_authenticated:
        listFunction = request.user.list_function()
        # print(listFunction)
        # print('adminuet/' + listFunction[0])
        return redirect('adminuet/' + listFunction[0])
        # return HttpResponseRedirect(reverse(listFunction[0]))
    return TemplateResponse(request, 'home.html')
