import pyrebase

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

def getReferences():
    return auth, database
