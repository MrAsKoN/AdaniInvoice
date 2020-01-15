from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
import pyrebase
from django.contrib import messages
from django.contrib import auth as authen
from home import views as homeviews

firebaseconfig = {
    'apiKey': "AIzaSyBK47B4fI4MRmn-V5gFhYjp6vLvBQkwEFg",
    'authDomain': "invoice-1c721.firebaseapp.com",
    'databaseURL': "https://invoice-1c721.firebaseio.com",
    'projectId': "invoice-1c721",
    'storageBucket': "invoice-1c721.appspot.com",
    'messagingSenderId': "102900029497",
    'appId': "1:102900029497:web:8321eff6bbe1183fce55e8",
    'measurementId': "G-Q90ESMX42R"
}

firebase = pyrebase.initialize_app(firebaseconfig)
auth = firebase.auth()
database = firebase.database()


def showregister(request):
    return render(request, 'register.html')


def register(request):
    if request.method == 'POST':
        publickey = request.POST.get('publickey')
        name = request.POST.get('name')
        address = request.POST.get('address')
        phoneno = request.POST.get('phoneno')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not (name and email and password):
            return render(request, 'register.html')
        try:
            user = auth.create_user_with_email_and_password(email, password)
        except:
            messages.error(request, "Invalid Credentials!")
            return render(request, 'register.html')
        uid = user['localId']
        data = {'publickey': publickey, "name": name, 'email': email, 'address': address, 'phoneno': phoneno, 'wallet': 0}
        database.child("users").child(uid).set(data)
        messages.success(request, "User registration successful!")
        return render(request, 'login.html')
    return render(request, 'register.html')


def showlogin(request):
    return render(request, 'login.html')


def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        print(role)
        if not role:
            messages.error(request, "Please select your role!")
            return render(request, 'login.html')
        try:
            user = auth.sign_in_with_email_and_password(email, password)
        except:
            messages.error(request, "The Email and password you have entered are invalid!")
            return render(request, 'login.html')
        session_id = user['localId']
        request.session['uid'] = str(session_id)
        users = database.child(role).get()
        print(users)
        for u in users.each():
            print(u.key())
            print(u.val())
            context = u.val()
            if role == 'users':
                return redirect(homeviews.home)
            if role == 'admin':
                return redirect(homeviews.adminhome)
        return redirect(homeviews.home)
    return render(request, 'register.html')


def logout(request):
    try:
        del request.session['uid']
        request.session.modified = True
    except KeyError:
        pass
    authen.logout(request)
    auth.current_user = None
    return render(request, 'login.html')

# def home(request):
#     try:
#         print(request.session['uid'])
#     except:
#         return redirect(showlogin)
#     return render(request, 'home.html')
