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


def register(request):
    if request.method == 'POST':
        publickey = request.POST.get('publickey')
        name = request.POST.get('name')
        address = request.POST.get('address')
        phoneno = request.POST.get('phoneno')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not (name and email and password):
            messages.error(request, "Fill all the fields!")
            return redirect(register)
        try:
            user = auth.create_user_with_email_and_password(email, password)
        except:
            messages.error(request, "Account Exists!")
            return redirect(register)

        uid = user['localId']
        usr = database.child('user').child('customer').child(request.session[uid]).get().val()
        request.session['name'] = usr['name']
        request.session['walletMoney'] = usr['wallet']
        request.session['uid'] = uid
        tokenId = user['idToken']
        data = {'publickey': publickey, "name": name, 'email': email, 'address': address, 'phoneno': phoneno, 'wallet': 0,'tokenId':tokenId}
        database.child("user").child("customer").child(uid).set(data)
        # messages.success(request, "User registration successful!")
        return redirect(homeviews.dashboard)
    return render(request, 'register.html')


def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        print(role)
        if not role:
            messages.error(request, "Please select your role!")
            return redirect(login)
        try:
            user = auth.sign_in_with_email_and_password(email, password)
        except:
            messages.error(request, "The Email or password you have entered are invalid!")
            return redirect(login)
        session_id = user['localId']
        request.session['uid'] = str(session_id)
        usr = database.child("user").child("customer").child(request.session['uid']).get().val()
        request.session['name'] = usr['name']
        request.session['walletMoney'] = usr['wallet']
        users = database.child(role).get()
        print(users)
        for u in users.each():
            print(u.key())
            print(u.val())
            context = u.val()
            if role == 'users':
                return redirect(homeviews.dashboard)
            if role == 'admin':
                return redirect(homeviews.adminhome)
        return redirect(homeviews.dashboard)
    return render(request, 'login.html')


def logout(request):
    if 'uid' in request.session:
        del request.session['uid']
        authen.logout(request)

    return redirect(login)

#########################################################################################################################
def home(request):
    customerId="To5oGatYMINP6WxEAVNBsvgTJ4F2"
    customerAddress = "0x8eeec461De8ABEcE4222a9E1d3a9E6957aC5ec6a"
    amount=10
    invoiceNumber="3"
    #
    # email = "aman@gmail.com"
    # passw = "Deepika@123"
    # user = auth.sign_in_with_email_and_password(email, passw)
    # cust_id = user['localId']
    #
    # invoiceNumber = "3"
    # shippingAddress = "Chembur"
    # sellerAddress = "Delhi"
    # panNumber = "qwertyuio"
    # GstRegNumber = "1234567"
    # orderNumber = "12345"
    # orderDate = "29/12/2019"
    # invoiceDate = "16/12/2019"
    # invoiceDetails = "goods"
    # totalPrice = 3000
    # isPaymentComplete = "N"
    # dueDate = "20/02/2020"
    # publickey = "qwertyuioiuytre"
    # dueDateNoti = '1'
    #
    # invoice = {
    #     'publickey': cust_id,
    #     'invoiceNumber': invoiceNumber,
    #     'shippingAddress': shippingAddress,
    #     'sellerAddress' :sellerAddress,
    #     'panNumber': panNumber,
    #     'GstRegNumber': GstRegNumber,
    #     'orderNumber' : orderNumber,
    #     'orderDate': orderDate,
    #     'invoiceDate': invoiceDate,
    #     'invoiceDetails': invoiceDetails,
    #     'totalPrice': totalPrice,
    #     'isPaymentComplete': isPaymentComplete,
    #     'dueDate': dueDate,
    #     'dueDateNoti':dueDateNoti
    # }
    #
    #
    #
    # count = database.child('user').child('invoiceCount').get()
    # count_val= int(count.val()) + 1
    # value = str(count_val)
    # database.child('user').child('invoiceCount').set(value)
    # database.child("invoice").child(value).set(invoice)
    # database.child('user').child("customer").child(cust_id).child('invoice').push(value)

    #storage.child("invoices").child(user['localId']).child(value).put("C:/Users/DeepiakP/Downloads/Carol.pdf",user['idToken'] )

    # #######Add to Blockchain
    # tx_hash = contract.functions.addCustomer('0x8eeec461De8ABEcE4222a9E1d3a9E6957aC5ec6a').transact()
    # web3.eth.waitForTransactionReceipt(tx_hash)
    #
    # tempHash = contract.functions.addInvoiceDetails('0x8eeec461De8ABEcE4222a9E1d3a9E6957aC5ec6a',invoiceNumber,
    #                                      shippingAddress,sellerAddress,panNumber,GstRegNumber,orderNumber,
    #                                      invoiceDetails,invoiceDate,totalPrice,dueDate).transact()
    # print(tempHash)

    # balance = addToWallet('0x8eeec461De8ABEcE4222a9E1d3a9E6957aC5ec6a',100)
    # Get Invoice Details
    # print(contract.functions.getInvoice(invoiceNumber).call())

    #getTransactionHistory(invoiceNumber)
    #getBankBalance(customerId)
    #convertMoneyToTokens(customerAddress, amount, customerId)
    #redeemWalletMoney(customerAddress, amount, customerId)
    #getTransactionHistory(invoiceNumber)
    #getCurrentDate(customerId)
    notifications =notify(customerId)
    context = {
        'notification':notifications
    }
    return render(request, 'home/homepage.html',context)
def addCustomer(customerAddress):
    tx_hash = contract.functions.addCustomer(customerAddress).transact()
    print(tx_hash)

def addCompany(companyAddress):
    tx_hash = contract.functions.addCompanyMember(companyAddress).transact()
    print(tx_hash)

def addToWallet(customerAddress,amount):

    balance = contract.functions.getBalanceAccount(customerAddress).call()
    print(balance)

    tx_hash = contract.functions.addFundsToWallet(customerAddress,amount).transact()
    web3.eth.waitForTransactionReceipt(tx_hash)

    balance = contract.functions.getBalanceAccount(customerAddress).call()
    # web3.eth.waitForTransactionReceipt(tx_hash2)
    print(balance)



def getBankBalance(customerId):
    #done
    # Fetch Account Balance
    bank = database.child("Bank").child(customerId).get()
    bank_value = bank.val()
    print("Balance",bank_value['balance'])
    balance  = bank_value['balance']
    return balance
def convertMoneyToTokens(customerAddress,amount,customerId):
    #done
    balanceInAccount = getBankBalance(customerId)
    if balanceInAccount >= amount:
        # // Amount Decrease in Firebase Bank

        newbalance= balanceInAccount - amount
        bank = database.child("Bank").child(customerId).get()
        bank_value = bank.val()
        bank_value['balance'] = newbalance
        database.child("Bank").child(customerId).set(bank_value)

        #  Increase Amount in Firebase of deployer
        addToWallet(customerAddress,amount)
        bank_admin = database.child("Bank").child("Adani").get()
        bank_admin_value =bank_admin.val()
        admin_balance = bank_admin_value['balance']
        new_adminBalance = admin_balance + amount

        bank_admin_value['balance']=new_adminBalance
        database.child("Bank").child("Adani").set(bank_admin_value)
        print("done")
    else:
        print("less money")




def redeemWalletMoney(customerAddress,amount,customerId):
    #done
    balance = contract.functions.getBalanceAccount(customerAddress).call()
    if amount <= balance :

        tx_hash = contract.functions.redeemWallet(customerAddress,amount).transact()
        web3.eth.waitForTransactionReceipt(tx_hash)

        # Reduce Deployer Money
        bank_admin = database.child("Bank").child("Adani").get()
        bank_admin_value = bank_admin.val()
        admin_balance = bank_admin_value['balance']
        new_adminBalance = admin_balance - amount
        bank_admin_value['balance']=new_adminBalance
        database.child("Bank").child("Adani").set(bank_admin_value)

        # Add Money to given CustomerId
        balanceInAccount = getBankBalance(customerId)
        newbalance = balanceInAccount + amount
        bank = database.child("Bank").child(customerId).get()
        bank_value = bank.val()
        bank_value['balance'] = newbalance
        database.child("Bank").child(customerId).set(bank_value)

        print("******************")
        return True
    return False

def paymentsWithToken(customerAddress,companyAddress,invoiceNumber,amount):
    balance = contract.functions.getBalanceAccount(customerAddress).call()
    if amount <= balance:

        tx_hash = contract.functions.makePayments(customerAddress,companyAddress,'INVO-COIN',amount).transact()
        web3.eth.waitForTransactionReceipt(tx_hash)

        return True
    return False

def paymentsWithBank(customerId,companyId,amount):
    # done
    balanceCustomer =  getBankBalance()   #Get Customer Bank Balance
    # balanceCompany = getBankBalance(companyId)     #Get Company's Bank Balance

    if amount <= balanceCustomer:
        # Reduce balance of customer
        newbalance = balanceCustomer - amount
        bank = database.child("Bank").child(customerId).get()
        bank_value = bank.val()
        bank_value['balance'] = newbalance
        database.child("Bank").child(customerId).set(bank_value)
        # Increase Company Balance

        bank_admin = database.child("Bank").child("Adani").get()
        bank_admin_value = bank_admin.val()
        admin_balance = bank_admin_value['balance']
        new_adminBalance = admin_balance + amount

        bank_admin_value['balance'] = new_adminBalance
        database.child("Bank").child("Adani").set(bank_admin_value)


        return True

    return False

def getTransactionHistory(invoiceNumber):

    history = contract.functions.getTransactionHistory(invoiceNumber).call()

    print(history)

def notify(customerId):

    invoices = database.child("user").child("customer").child(customerId).child('invoice').get()
    dict_value = invoices.val()
    now = datetime.now()
    new_invoices = []
    due_invoices = []
    count=0


    current_Date = now. strftime("%d/%m/%Y ")
    date,month,year = current_Date.split('/')
    print(date)
    for key,item in dict_value.items():
        invoice_det = database.child("invoice").child(item).get()

        invoice_val = invoice_det.val()

        due_Date = invoice_val['dueDate']
        date1,month1,year1 = due_Date.split('/')

        if invoice_val['dueDateNoti'] == "1":
            invoice_val['dueDateNoti'] = current_Date
            new_invoice_dict ={
                'invoiceNumber': invoice_val['invoiceNumber'],
                    'shippingAddress': invoice_val['shippingAddress'],
                    'sellerAddress' :invoice_val['sellerAddress'],
                    'panNumber': invoice_val['panNumber'],
                    'GstRegNumber': invoice_val['GstRegNumber'],
                    'orderNumber' : invoice_val['orderNumber'],
                    'orderDate': invoice_val['orderDate'],
                    'invoiceDate': invoice_val['invoiceDate'],
                    'invoiceDetails': invoice_val['invoiceDetails'],
                    'totalPrice': invoice_val['totalPrice'],
                    'isPaymentComplete': invoice_val['isPaymentComplete'],
                    'dueDate': invoice_val['dueDate'],
            }
            new_invoices.append(new_invoice_dict)
        else:

            if invoice_val['dueDateNoti']== current_Date:
                date_int = int(date) +1
                new_date =str(date_int)+"/"+month+"/"+year
                invoice_val['dueDateNoti'] = new_date
                #database.child("invoice").child(item).set(invoice_val)
                new_invoice_dict = {
                    'invoiceNumber': invoice_val['invoiceNumber'],
                    'shippingAddress': invoice_val['shippingAddress'],
                    'sellerAddress': invoice_val['sellerAddress'],
                    'panNumber': invoice_val['panNumber'],
                    'GstRegNumber': invoice_val['GstRegNumber'],
                    'orderNumber': invoice_val['orderNumber'],
                    'orderDate': invoice_val['orderDate'],
                    'invoiceDate': invoice_val['invoiceDate'],
                    'invoiceDetails': invoice_val['invoiceDetails'],
                    'totalPrice': invoice_val['totalPrice'],
                    'isPaymentComplete': invoice_val['isPaymentComplete'],
                    'dueDate': invoice_val['dueDate'],
                }
                due_invoices.append(new_invoice_dict)

            else:
                print("")
    print(new_invoices)


    count= count+ len(new_invoices)+len(due_invoices)
    return count



def notifications(request):
    customerId="To5oGatYMINP6WxEAVNBsvgTJ4F2"
    invoices = database.child("user").child("customer").child(customerId).child('invoice').get()
    dict_value = invoices.val()
    now = datetime.now()
    new_invoices = []
    due_invoices = []
    count = 0

    current_Date = now.strftime("%d/%m/%Y ")
    date, month, year = current_Date.split('/')
    print(date)
    for key, item in dict_value.items():
        invoice_det = database.child("invoice").child(item).get()

        invoice_val = invoice_det.val()

        due_Date = invoice_val['dueDate']
        date1, month1, year1 = due_Date.split('/')

        if invoice_val['dueDateNoti'] == "1":
            date_int = int(date) + 1
            new_date = str(date_int) + "/" + month + "/" + year
            invoice_val['dueDateNoti'] = new_date
            database.child("invoice").child(item).set(invoice_val)
            new_invoice_dict = {
                'invoiceNumber': invoice_val['invoiceNumber'],
                'shippingAddress': invoice_val['shippingAddress'],
                'sellerAddress': invoice_val['sellerAddress'],
                'panNumber': invoice_val['panNumber'],
                'GstRegNumber': invoice_val['GstRegNumber'],
                'orderNumber': invoice_val['orderNumber'],
                'orderDate': invoice_val['orderDate'],
                'invoiceDate': invoice_val['invoiceDate'],
                'invoiceDetails': invoice_val['invoiceDetails'],
                'totalPrice': invoice_val['totalPrice'],
                'isPaymentComplete': invoice_val['isPaymentComplete'],
                'dueDate': invoice_val['dueDate'],
            }
            new_invoices.append(new_invoice_dict)
            print("newwwwww",new_invoices)
        else:

            if invoice_val['dueDateNoti'] == current_Date:
                date_int = int(date) + 1
                new_date = str(date_int) + "/" + month + "/" + year
                invoice_val['dueDateNoti'] = new_date
                database.child("invoice").child(item).set(invoice_val)
                new_invoice_dict = {
                    'invoiceNumber': invoice_val['invoiceNumber'],
                    'shippingAddress': invoice_val['shippingAddress'],
                    'sellerAddress': invoice_val['sellerAddress'],
                    'panNumber': invoice_val['panNumber'],
                    'GstRegNumber': invoice_val['GstRegNumber'],
                    'orderNumber': invoice_val['orderNumber'],
                    'orderDate': invoice_val['orderDate'],
                    'invoiceDate': invoice_val['invoiceDate'],
                    'invoiceDetails': invoice_val['invoiceDetails'],
                    'totalPrice': invoice_val['totalPrice'],
                    'isPaymentComplete': invoice_val['isPaymentComplete'],
                    'dueDate': invoice_val['dueDate'],
                }
                due_invoices.append(new_invoice_dict)

            else:
                print("")

    count = count + len(new_invoices) + len(due_invoices)
    subject = 'Welcome to DataFlair'
    message = 'invoice'
    recepient = str("divyapomendkar@gmail.com")
    send_mail(subject,message, EMAIL_HOST_USER, [recepient], fail_silently=False)
    context = {
        'new_Invoice':new_invoices,
        'due_Invoice':due_invoices,
        'count':count
    }

    return render(request, 'home/notifications.html',context)







