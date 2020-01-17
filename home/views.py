from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import users.views as usersviews
from Invoice import settings
from firebase import getReferences
from datetime import datetime
# import datetime
from django.contrib import messages

auth, database = getReferences()


def dashboard(request):
    if 'uid' in request.session:
        check = False
        invoices = database.child('invoice').get().val()

        user_invoices = []

        if request.method == 'POST':
            btn = request.POST['filter']
            if btn == 'filtered':
                check = True
                invoices = database.child('invoice').get().val()
                if invoices != None:
                    for invoice in invoices:
                        if invoice and invoice['publickey'] == request.session['uid'] and int(
                                invoice['remaining']) != 0:
                            user_invoices.append(invoice)

                return render(request, 'newhome.html', {
                    'invoices': user_invoices,
                    'name': request.session['name'],
                    'walletMoney': request.session['walletMoney'],
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
                    'name': request.session['name'],
                    'walletMoney': request.session['walletMoney'],
                    'check': check
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
        # storage.child("invoices").child(user['localId']).child(value).put("C:/Users/DeepiakP/Downloads/Carol.pdf",user['idToken'] )
        customerId = request.session['uid']
        count = notify(customerId)
        return render(request, 'newhome.html', {'invoices': user_invoices, 'name': request.session['name'],
                                                'walletMoney': request.session['walletMoney'], 'check': False,
                                                'count': count})

    return redirect(usersviews.login)


def adminhome(request):
    try:
        print(request.session['uid'])
        adminData = database.child("user").child("admin").child("1").get()
        print(adminData.val())
        for key, value in adminData.val().items():
            print(key, value)
    except:
        return redirect(usersviews.login)

    month = datetime.now().month
    print('Month--------------------', month)
    data = getTotalRevenue(int(month))
    print('data---------------------', data)
    if month == 1:
        previousMonth = 12
    else:
        previousMonth = month - 1

    previousData = getTotalRevenue(previousMonth)['revenue']
    print(previousData)

    return render(request, 'adminhome.html', data)


def mywallet(request):
    if 'uid' in request.session:
        curr_balance = int(database.child('Bank').child(request.session['uid']).child('balance').get().val())
        if request.method == 'POST':
            credit = int(request.POST['credit'])
            if credit <= 0 or credit > curr_balance:
                messages.error(request, 'Invalid Credit Amount')
                return redirect(mywallet)
            curr_balance -= credit
            database.child('Bank').child(request.session['uid']).update({
                'balance': curr_balance
            })
            currWallet = int(
                database.child('user').child('customer').child(request.session['uid']).child('wallet').get().val())
            currWallet += credit
            database.child('user').child('customer').child(request.session['uid']).update({
                'wallet': currWallet
            })

            email = database.child('user').child('customer').child(request.session['uid']).child(
                'email').get().val()
            # send_mail('Amount Credited to Your Wallet',
            #           'An amount of Rs. {} was credited to your account. \nFinal Wallet Balance = Rs. {}'.format(
            #               credit, currWallet),
            #           settings.EMAIL_HOST_USER,
            #           [email],
            #           fail_silently=False)

            date = str(datetime.today().strftime('%d-%m-%Y'))
            time = str(datetime.today().strftime('%H-%M-%S'))
            database.child('transactions').child(request.session['uid']).child(date).child('credit').child(
                time).set({
                'amount': credit,
                'closing_balance': currWallet
            })
            request.session['walletMoney'] = currWallet
            return redirect(dashboard)

        return render(request, 'wallet.html', {'curr_balance': curr_balance, 'name': request.session['name'],
                                               'walletMoney': request.session['walletMoney'],
                                               'count': notify(request.session['uid'])})
    return redirect(usersviews.login)


def pay(request, id):
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
                'wallet': 'Rs. {}'.format(wallet),
                'name': request.session['name'],
                'walletMoney': request.session['walletMoney'],
            }
        else:
            diff = 0
            context = {
                'diff': 'Rs. 0',
                'remaining': 'Rs. {}'.format(remaining),
                'wallet': 'Rs. {}'.format(wallet),
                'name': request.session['name'],
                'walletMoney': request.session['walletMoney'],
            }
        if request.method == 'POST':
            if wallet != 0:
                email = database.child('user').child('customer').child(request.session['uid']).child(
                    'email').get().val()
                if wallet >= remaining:
                    date = str(datetime.today().strftime('%d-%m-%Y'))
                    time = str(datetime.today().strftime('%H-%M-%S'))
                    database.child('transactions').child(request.session['uid']).child(date).child('payment').child(
                        time).set({
                        'invoiceId': id,
                        'amount': remaining,
                        'closing_balance': wallet - remaining
                    })
                    database.child('user').child('customer').child(request.session['uid']).update({
                        'wallet': wallet - remaining
                    })
                    database.child('invoice').child(id).update({
                        'remaining': 0
                    })

                    adani = database.child('Bank').child('Adani').child('balance').get().val()
                    adani = int(adani)
                    database.child('Bank').child('Adani').update({
                        'balance': adani + remaining
                    })
                    request.session['walletMoney'] = wallet - remaining

                    # send_mail('Amount Debited from your wallet',
                    #           'An amount of Rs. {} was debited from your account.\nTransaction made for Invoice {}.\nRemaining Wallet Balance is Rs. {}.\nOutstanding Due Amount = Rs. 0'.format(
                    #               remaining, id, wallet - remaining),
                    #           settings.EMAIL_HOST_USER,
                    #           [email],
                    #           fail_silently=False)

                else:
                    date = str(datetime.today().strftime('%d-%m-%Y'))
                    time = str(datetime.today().strftime('%H-%M-%S'))
                    database.child('transactions').child(request.session['uid']).child(date).child('payment').child(
                        time).set({
                        'invoiceId': id,
                        'amount': wallet,
                        'closing_balance': 0
                    })
                    database.child('user').child('customer').child(request.session['uid']).update({
                        'wallet': 0
                    })
                    database.child('invoice').child(id).update({
                        'remaining': remaining - wallet
                    })

                    adani = database.child('Bank').child('Adani').child('balance').get().val()
                    adani = int(adani)
                    database.child('Bank').child('Adani').update({
                        'balance': wallet + adani
                    })
                    request.session['walletMoney'] = 0
                    # send_mail('Amount Debited from your wallet',
                    #           'An amount of Rs. {} was debited from your account.\nTransaction made for Invoice {}.\nRemaining Wallet Balance is Rs. 0.\nOutstanding Due Amount = Rs. {}'.format(
                    #               wallet, id, remaining - wallet),
                    #           settings.EMAIL_HOST_USER,
                    #           [email],
                    #           fail_silently=False)
                return redirect(dashboard)
            else:
                return redirect(mywallet)
        print(context)
        return render(request, 'pay.html', context)

    return redirect(usersviews.login)


def getTransactionData(arr):
    if not arr:
        return None

    data = []
    for date, other in arr.items():
        credit = []
        payment = []
        for type, transac in other.items():
            if type == 'credit':
                for time, details in transac.items():
                    credit.append({'time': time, 'details': details})
            if type == 'payment':
                for time, details in transac.items():
                    payment.append({'time': time, 'details': details})
        data.append({'date': date, 'credit': credit, 'payment': payment})
    # print (data)
    return data


def transactions(request):
    if 'uid' in request.session:
        transactions = database.child('transactions').child(request.session['uid']).get().val()
        return render(request, 'transactions.html', {'transactions': getTransactionData(transactions),
                                                     'name': request.session['name'],
                                                     'walletMoney': request.session['walletMoney'],
                                                     'count': notify(request.session['uid'])
                                                     })
    # return redirect(usersviews.login)
    return redirect(dashboard)


def notify(customerId):
    invoices = database.child("user").child("customer").child(customerId).child('invoice').get()
    dict_value = invoices.val()
    print("dict_value:::", dict_value)
    now = datetime.now()
    new_invoices = []
    due_invoices = []
    count = 0

    current_Date = now.strftime("%d/%m/%Y ")
    date, month, year = current_Date.split('/')
    print("##############date:::::", date)
    for key, item in dict_value.items():
        invoice_det = database.child("invoice").child(item).get()

        invoice_val = invoice_det.val()
        print("########invoice_val", invoice_val)
        due_Date = invoice_val['dueDate']
        date1, month1, year1 = due_Date.split('/')

        if invoice_val['dueDateNoti'] == "1":
            invoice_val['dueDateNoti'] = current_Date
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
        else:

            if invoice_val['dueDateNoti'] == current_Date:
                date_int = int(date) + 1
                new_date = str(date_int) + "/" + month + "/" + year
                invoice_val['dueDateNoti'] = new_date
                # database.child("invoice").child(item).set(invoice_val)
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

    count = count + len(new_invoices) + len(due_invoices)
    return count


def notifications(request):
    customerId = request.session['uid']
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
            print("newwwwww", new_invoices)
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
        'new_Invoice': new_invoices,
        'due_Invoice': due_invoices,
        'count': count,
        'walletMoney': request.session['walletMoney'],
        'name': request.session['name'],
    }

    return render(request, 'notifications.html', context)


#################ADMIN
def adminTransactionHistory(request):
    transaction = database.child("transactions").get().val()
    print(transaction)
    dict = {}
    transactionList = []
    userList = []
    i = 0
    for uid, dateOb in transaction.items():
        gmail = database.child("user").child("customer").child(uid).child("email").get().val()
        for date, typeOb in dateOb.items():
            for type, timeOb in typeOb.items():
                if type == 'payment':
                    for time, value in timeOb.items():
                        userList.append(
                            {'date': date, 'time': time, 'amount': value['amount'], 'invoiceId': value['invoiceId']})
                        dict['gmail'] = gmail
                        dict['i'] = i
                    dict['payment'] = userList
                    userList = []
        i += 1
        if bool(dict):
            transactionList.append(dict)
        dict = {}
        print("userList---------------", userList)
        print("dict------------------", dict)

    print("ISDUHSDSHDUHSHSUDHSHSDJHSJJSJHHsldklakd--------------------------")
    print(transactionList)
    return render(request, "admintransactions.html", {'transactionList': transactionList})


def timepass(request):
    return render(request, "timepass.html")


def getTotalRevenue(month=-1):
    invoices = database.child('invoice').get().val()
    print(invoices)
    revenue = 0
    pendingOutstanding = 0
    # pendingInvoicesPayment = 0
    pendingInvoices = 0
    currentDate = datetime.now()
    month = currentDate.month

    monthWiseRevenue = {'January': 0,
                        'February': 0,
                        'March': 0,
                        'April': 0,
                        'May': 0,
                        'June': 0,
                        'July': 0,
                        'August': 0,
                        'September': 0,
                        'October': 0,
                        'November': 0,
                        'December': 0}

    monthWiseOutstanding = {'January': 0,
                            'February': 0,
                            'March': 0,
                            'April': 0,
                            'May': 0,
                            'June': 0,
                            'July': 0,
                            'August': 0,
                            'September': 0,
                            'October': 0,
                            'November': 0,
                            'December': 0}

    monthWisePendingInvoices = {'January': 0,
                                'February': 0,
                                'March': 0,
                                'April': 0,
                                'May': 0,
                                'June': 0,
                                'July': 0,
                                'August': 0,
                                'September': 0,
                                'October': 0,
                                'November': 0,
                                'December': 0}

    for invoice in invoices:
        if invoice is None:
            continue
        print('harami')
        if month != -1 and invoice != None:
            print('harami111111111111')
            dueDateInvoice = invoice['dueDate']
            monthdueDate = dueDateInvoice.split('/')[1]
            if month != int(monthdueDate):
                continue
        print('harami22222222222')
        revenue += (invoice['totalPrice'] - invoice['remaining'])
        pendingOutstanding += invoice['remaining']

        if invoice['remaining'] > 0:
            pendingInvoices += 1

    return {'pendingInvoices': pendingInvoices,
            'pendingOutstanding': pendingOutstanding,
            'revenue': revenue}


def getDistributedInsights():
    invoices = database.child('invoice').get().val()
    print(invoices)

    monthWiseRevenue = {'January': 0,
                        'February': 0,
                        'March': 0,
                        'April': 0,
                        'May': 0,
                        'June': 0,
                        'July': 0,
                        'August': 0,
                        'September': 0,
                        'October': 0,
                        'November': 0,
                        'December': 0}

    monthWiseOutstanding = {'January': 0,
                            'February': 0,
                            'March': 0,
                            'April': 0,
                            'May': 0,
                            'June': 0,
                            'July': 0,
                            'August': 0,
                            'September': 0,
                            'October': 0,
                            'November': 0,
                            'December': 0}

    monthWisePendingInvoices = {'January': 0,
                                'February': 0,
                                'March': 0,
                                'April': 0,
                                'May': 0,
                                'June': 0,
                                'July': 0,
                                'August': 0,
                                'September': 0,
                                'October': 0,
                                'November': 0,
                                'December': 0}

    labels = list(monthWisePendingInvoices.keys())
    for invoice in invoices:
        if invoice is None:
            continue
        print('harami')
        dueDateInvoice = invoice['dueDate']
        monthdueDate = int(dueDateInvoice.split('/')[1])

        print('harami22222222222')
        monthWiseRevenue[labels[monthdueDate - 1]] += (invoice['totalPrice'] - invoice['remaining'])
        monthWiseOutstanding[labels[monthdueDate - 1]] += invoice['remaining']

        if invoice['remaining'] > 0:
            monthWisePendingInvoices[labels[monthdueDate - 1]] += 1

    return monthWiseRevenue, monthWiseOutstanding, monthWisePendingInvoices


def yearWiseDistribution():
    currentDate = datetime.now()
    year = currentDate.year
    yearWiseRevenue = {}
    yearWisePendingInvoices = {}
    yearWiseOutstandings = {}

    for i in range(10):
        yearWiseRevenue[year - i] = 0
        yearWisePendingInvoices[year - i] = 0
        yearWiseOutstandings[year - i] = 0

    print(yearWiseOutstandings)
    print(yearWiseOutstandings.keys())
    invoices = database.child('invoice').get().val()
    for invoice in invoices:
        if invoice is None:
            continue
        print('harami')
        dueDateInvoice = invoice['dueDate']
        yearDueDate = int(dueDateInvoice.split('/')[2])
        print('harami1')
        print(yearDueDate)
        if yearDueDate in yearWiseOutstandings.keys():
            print('harami2')
            yearWiseRevenue[yearDueDate] += (invoice['totalPrice'] - invoice['remaining'])
            yearWiseOutstandings[yearDueDate] += invoice['remaining']
            if invoice['remaining'] > 0:
                yearWisePendingInvoices[yearDueDate] += 1

    return yearWiseRevenue, yearWiseOutstandings, yearWisePendingInvoices


from django.http import JsonResponse


def ChartData(request):
    qs_count = 10
    a, b, c = getDistributedInsights()
    print('tatttiiii', a)
    # labels_months = ['Jan','Feb','March','April','May','June','July','August','Sept','Oct','Nov','Dec']
    # # labels = ["Users", "Blue", "Yellow", "Green", "Purple", "Orange"]
    # month_data = [10, 23, 2, 3, 12, 2,57,44,33,77,11,7]
    labels_months = list(a.keys())
    month_data = list(a.values())

    # labels_years = ['2010','2011','2012','2013','2014']
    # years_data = [10,40,30,20,60]

    a, b, c = yearWiseDistribution()

    labels_years = list(a.keys())
    years_data = list(a.values())
    data_monthly = {
        "labels": labels_months,
        "default": month_data,
    }
    bcolors = {'info': 'rgba(23, 162, 184, 0.4)', 'success': 'rgba(40, 167, 69, 0.4)',
               'warning': 'rgba(255, 193, 7, 0.4)',
               'danger': 'rgba(220, 53, 69, 0.4)'}
    data_yearly_revenue = {
        "label": 'Revenue',
        "data": list(a.values()),
        "backgroundColor": bcolors['danger']
    }
    data_yearly_pendingInvoices = {
        "label": "Outstanding",
        "data": list(c.values()),
        "backgroundColor": bcolors['warning']
    }
    data_yearly_pendingOutstanding = {
        "label": "Pending Invoice",
        "data": list(b.values()),
        "backgroundColor": bcolors['info']
    }
    a, b, c = getDistributedInsights()

    month_data_revenue = {
        "label": 'Revenue',
        "data": list(a.values()),
        "backgroundColor": bcolors['danger']
    }
    month_data_pendingInvoices = {
        "label": 'Pending Invoices',
        "data": list(c.values()),
        "backgroundColor": bcolors['info']
    }
    month_data_pendingOutstanding = {
        "label": 'Pending Outstanding',
        "data": list(b.values()),
        "backgroundColor": bcolors['warning']
    }
    years_data = [data_yearly_revenue, data_yearly_pendingInvoices, data_yearly_pendingOutstanding]
    month_data = [month_data_revenue, month_data_pendingInvoices, month_data_pendingOutstanding]
    # colors = ['#17a2b8', '#28a745', '#ffc107', '#dc3545']
    # bcolors= {'info': 'rgba(23, 162, 184, 1)', 'success': 'rgba(40, 167, 69, 1)', 'warning': 'rgba(255, 193, 7, 1)', 'danger':'rgba(220, 53, 69, 1)'}
    data_yearly = {
        "labels": labels_years,
        "default": years_data,
    }
    data_monthly = {
        "labels": labels_months,
        "default": month_data
    }
    data = {
        "yearly": data_yearly,
        "monthly": data_monthly,
    }
    print(data)
    return JsonResponse(data, safe=False)


def invoices(request):
    if request.method == 'POST':
        invoiceNumber = request.POST.get('filterInvoice')
        print(type(invoiceNumber))
        invoiceTemp = database.child('invoice').child(invoiceNumber).get().val()
        invoiceTemp['name'] = database.child('user').child('customer').child(invoiceTemp['publickey']).child(
            'name').get().val()
        temp = []
        temp.append(invoiceTemp)
        if invoiceTemp is not None and invoiceNumber:
            return render(request, 'invoices.html', {'data': temp})

    InvoiceData = []
    invoices = database.child('invoice').get().val()
    for invoice in invoices:
        if invoice != None:
            invoice['name'] = database.child('user').child('customer').child(invoice['publickey']).child(
                'name').get().val()
            InvoiceData.append(invoice)

    return render(request, 'invoices.html', {'data': InvoiceData})
