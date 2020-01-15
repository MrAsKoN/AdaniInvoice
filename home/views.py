from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import users.views as usersviews


def dashboard(request):
    # try:
    #     print(request.session['uid'])
    # except:
    #     return redirect(usersviews.login)
    # return render(request, 'newhome.html')
    if 'uid' in request.session:
        return render(request,'newhome.html')
    return redirect(usersviews.login)

def adminhome(request):
    try:
        print(request.session['uid'])
    except:
        return redirect(usersviews.showlogin)
    return render(request,'adminhome.html')

def invoices(request):
    if 'uid' in request.session:
        return render(request,'invoices.html')
    return redirect(usersviews.login)
