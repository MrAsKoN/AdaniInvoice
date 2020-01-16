from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import users.views as usersviews
from firebase import getReferences
from datetime import datetime
auth, database = getReferences()

def dashboard(request):
    if 'uid' in request.session:
        check = False
        invoices = database.child('invoice').get().val()
        usr = database.child('user').child('customer').child(request.session['uid']).get().val()
        uname = usr['name']
        wallet = usr['wallet']
        user_invoices = []

        if request.method == 'POST':
            btn = request.POST['filter']
            if btn == 'filtered':
                check = True
                invoices = database.child('invoice').get().val()
                if invoices !=None:
                    for invoice in invoices:
                        if invoice and invoice['publickey'] == request.session['uid'] and int(invoice['remaining']) != 0:
                            user_invoices.append(invoice)

                return render(request,'newhome.html',{
                    'invoices': user_invoices,
                    'name': uname,
                    'wallet': wallet,
                    'check': check
                })
            else:
                check = False
                invoices = database.child('invoice').get().val()
                if invoices != None:
                    for invoice in invoices:
                        if invoice and invoice['publickey'] == request.session['uid']:
                            user_invoices.append(invoice)

                return render(request, 'newhome.html', {
                    'invoices': user_invoices,
                    'name': uname,
                    'wallet': wallet,
                    'check':check
                })
        if invoices != None:
            for invoice in invoices:
                if invoice and invoice['publickey'] == request.session['uid']:
                    user_invoices.append(invoice)


    # customerId="To5oGatYMINP6WxEAVNBsvgTJ4F2"
            
        # customerAddress = "0x8eeec461De8ABEcE4222a9E1d3a9E6957aC5ec6a"
        # amount=10
        # invoiceNumber="1"
        
        # # email = "ajinkya@gmail.com"
        # # passw = "Deepika@123"
        
        # cust_id=request.session['uid']
        
        # invoiceNumber = "1"
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
        
        # count = database.child('user').child('invoiceCount').get()
        # count_val= int(count.val()) + 1
        # value = str(count_val)
        # database.child('user').child('invoiceCount').set(value)
        # database.child("invoice").child(value).set(invoice)
        # database.child('user').child("customer").child(cust_id).child('invoice').push(value)
        #storage.child("invoices").child(user['localId']).child(value).put("C:/Users/DeepiakP/Downloads/Carol.pdf",user['idToken'] )
        customerId = request.session['uid']
        count = notify(customerId)
        return render(request, 'newhome.html', {'invoices': user_invoices, 'name': uname,'wallet':wallet,'check':False,'count':count})

    return redirect(usersviews.login)


def adminhome(request):
    try:
        print(request.session['uid'])
    except:
        return redirect(usersviews.showlogin)
    return render(request,'adminhome.html')


def wallet(request):
    if 'uid' in request.session:
        return render(request,'wallet.html')
    return redirect(usersviews.login)

def pay(request,id):
    if 'uid' in request.session:
        usr = database.child('user').child('customer').child(request.session['uid']).get().val()
        wallet = int(usr['wallet'])
        invoice = database.child('invoice').child(id).get().val()
        remaining = int(invoice['remaining'])
        diff = None
        context = None
        if wallet >= remaining:
            diff = wallet - remaining
            context = {
                'diff': 'Rs. {}'.format(wallet - remaining),
                'remaining': 'Rs. {}'.format(remaining),
                'wallet': 'Rs. {}'.format(wallet)
            }
        else:
            diff = 0
            context = {
                'diff': 'Rs. 0',
                'remaining': 'Rs. {}'.format(remaining),
                'wallet': 'Rs. {}'.format(wallet)
            }
        if request.method == 'POST':
            if wallet != 0:
                if wallet >= remaining:
                    transactions = database.child('transactions').child(request.session['uid']).child(id).get().val()
                    tid = None
                    if(transactions == None):
                        tid = 1
                    else:
                        tid = len(transactions)
                    database.child('transactions').child(request.session['uid']).child(id).child(tid).set({
                        'invoiceId':id,
                        'amount': remaining,
                        'modeOfPayment': 'Wallet'
                    })
                    database.child('user').child('customer').child(request.session['uid']).update({
                        'wallet': wallet-remaining
                    })
                    database.child('invoice').child(id).update({
                        'remaining': 0
                    })
                else:
                    transactions = database.child('transactions').child(request.session['uid']).child(id).get().val()
                    tid = None
                    if (transactions == None):
                        tid = 1
                    else:
                        tid = len(transactions)
                    database.child('transactions').child(request.session['uid']).child(id).child(tid).set({
                        'invoiceId': id,
                        'amount': wallet,
                        'modeOfPayment': 'Wallet'
                    })
                    database.child('user').child('customer').child(request.session['uid']).update({
                        'wallet': 0
                    })
                    database.child('invoice').child(id).update({
                        'remaining': remaining-wallet
                    })
                return redirect(dashboard)
            else:
                return redirect(wallet)

        return render(request,'pay.html',context)

    return redirect(usersviews.login)

def getTransactionData(arr):
    data = []
    for i in range(len(arr)):
        data.append({
            'id': i+1,
            'data': arr[i]
        })
    return data

def transactions(request):
    if 'uid' in request.session:
        transactions = database.child('transactions').child(request.session['uid']).get().val()
        if transactions == None:
            return redirect(dashboard)

        user_transaction = []
        for id in range(1,len(transactions)):
            arr = []
            for details in range(1,len(transactions[id])):
                arr.append(transactions[id][details])
            user_transaction.append(arr)

        return render(request,'transactions.html',{'transactions':getTransactionData(user_transaction)})
    return redirect(usersviews.login)

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
    customerId=request.session['uid']
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
    # subject = 'Welcome to DataFlair'
    # message = 'invoice'
    # recepient = str("divyapomendkar@gmail.com")
    # send_mail(subject,message, EMAIL_HOST_USER, [recepient], fail_silently=False)
    context = {
        'new_Invoice':new_invoices,
        'due_Invoice':due_invoices,
        'count':count
    }

    return render(request, 'notifications.html',context)

