from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import users.views as usersviews
from firebase import getReferences

auth, db = getReferences()

def dashboard(request):
    if 'uid' in request.session:
        check = False
        invoices = db.child('invoice').get().val()
        usr = db.child('user').child('customer').child(request.session['uid']).get().val()
        uname = usr['name']
        wallet = usr['wallet']
        user_invoices = []

        if request.method == 'POST':
            btn = request.POST['filter']
            if btn == 'filtered':
                check = True
                invoices = db.child('invoice').get().val()
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
                invoices = db.child('invoice').get().val()
                for invoice in invoices:
                    if invoice and invoice['publickey'] == request.session['uid']:
                        user_invoices.append(invoice)

                return render(request, 'newhome.html', {
                    'invoices': user_invoices,
                    'name': uname,
                    'wallet': wallet,
                    'check':check
                })

        for invoice in invoices:
            if invoice and invoice['publickey'] == request.session['uid']:
                user_invoices.append(invoice)

        return render(request, 'newhome.html', {'invoices': user_invoices, 'name': uname,'wallet':wallet,'check':False})

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
        usr = db.child('user').child('customer').child(request.session['uid']).get().val()
        wallet = int(usr['wallet'])
        invoice = db.child('invoice').child(id).get().val()
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
                    transactions = db.child('transactions').child(request.session['uid']).child(id).get().val()
                    tid = None
                    if(transactions == None):
                        tid = 1
                    else:
                        tid = len(transactions)
                    db.child('transactions').child(request.session['uid']).child(id).child(tid).set({
                        'invoiceId':id,
                        'amount': remaining,
                        'modeOfPayment': 'Wallet'
                    })
                    db.child('user').child('customer').child(request.session['uid']).update({
                        'wallet': wallet-remaining
                    })
                    db.child('invoice').child(id).update({
                        'remaining': 0
                    })
                else:
                    transactions = db.child('transactions').child(request.session['uid']).child(id).get().val()
                    tid = None
                    if (transactions == None):
                        tid = 1
                    else:
                        tid = len(transactions)
                    db.child('transactions').child(request.session['uid']).child(id).child(tid).set({
                        'invoiceId': id,
                        'amount': wallet,
                        'modeOfPayment': 'Wallet'
                    })
                    db.child('user').child('customer').child(request.session['uid']).update({
                        'wallet': 0
                    })
                    db.child('invoice').child(id).update({
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
        transactions = db.child('transactions').child(request.session['uid']).get().val()
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