from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import users.views as usersviews


def dashboard(request):
    # try:
    #     print(request.session['uid'])
    # except:
    #     return redirect(usersviews.login)
    # return render(request, 'newhome.html')
    if 'uid' not in request.session:
        return redirect(usersviews.login)
    return render(request,'newhome.html')

def adminhome(request):
    try:
        print(request.session['uid'])
    except:
        return redirect(usersviews.showlogin)
    return render(request,'adminhome.html')
