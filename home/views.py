from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import users.views as usersviews


def home(request):
    try:
        print(request.session['uid'])
    except:
        return redirect(usersviews.showlogin)
    return render(request, 'newhome.html')


def adminhome(request):
    try:
        print(request.session['uid'])
    except:
        return redirect(usersviews.showlogin)
    return render(request,'adminhome.html')
