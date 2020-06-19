from django.shortcuts import render, redirect
from django.contrib import messages
from .models import *
import hashlib,datetime
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404
# Create your views here. 


# Admin functionality
def admin_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        try:
            if request.session['investor']: 
                messages.error(request, 'You already login as Investor')
                return redirect('investor:admin_login') 
            else:
                if user is not None:
                    login(request, user)
                    return redirect('investor:dashboard')
                else:
                    messages.error(request, 'Username or password is  incorrect')
        except:
            return redirect('investor:admin_login') 
    return render(request, 'account/admin_login.html')

def admin_logout(request):
    logout(request)
    return redirect('investor:admin_login')
    
    



# investor functionality
def investor_registration(request):
    bank_list = Bank.objects.all().order_by('bank_name')
    if request.method == 'POST':
        username = request.POST['username']
        user_password = request.POST['password'] 
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        phone = request.POST['phone']
        address = request.POST['address']
        amount_invest = request.POST['amount_invest']
        earning_amount = request.POST['earning_amount']
        invest_date = request.POST['invest_date']
        withdraw_date= request.POST['withdraw_date']
        bank_nameId = int(request.POST['bank_name'])
        bank_account = request.POST['bank_account'] 

        encripted_pass = hashlib.md5(user_password.encode())
        password = encripted_pass.hexdigest() 

        investor = Investor.objects.create(username=username, password=password, first_name=fname,last_name=lname, email= email, phone = phone, address=address,bank_name_id=bank_nameId, account_number=bank_account,agree_to_invest=True)

        invest = Invest.objects.create(investor_id=investor.id, amount_to_invest=amount_invest, expected_interest=earning_amount, date_of_invest=invest_date,withdraw_date= withdraw_date)

    context = {
        'bank_list':bank_list
    }
    
    return render(request,'account/registration.html',context)

def investor_login(request):
    try:
        if request.method == 'POST':
            user_email     = request.POST['username'].lower()
            user_password  = request.POST['password']  
            enc_pass = hashlib.md5(user_password.encode())
            user_pass = enc_pass.hexdigest()

            if request.user.is_authenticated:
                messages.error(request ,"You already login as Admin") 
                return redirect('investor:investor_login') 
            else:

                chk_user = Investor.objects.filter(Q(username = user_email, password = user_pass) | Q(email = user_email, password = user_pass)).first()
                if chk_user:
                    request.session['investor'] = chk_user.id 
                    return redirect('investor:dashboard') 
                else:     
                    messages.error(request ,"Username or Password is incorrect") 
                    return render(request, "account/investor_login.html")
        else:        
            return render(request, "account/investor_login.html")
    except:
        return redirect("investor:investor_login")  


def investor_logout(request):
    request.session['investor'] = None
    return redirect('investor:investor_login')

def request_to_invest(request, id):
    investor = Investor.objects.get(id=id)
    if request.method == 'POST':
        amount_invest = request.POST['amount_invest']
        earning_amount = request.POST['earning_amount']
        invest_date = request.POST['invest_date']
        withdraw_date= request.POST['withdraw_date']

        invest = Invest.objects.create(investor_id=id, amount_to_invest=amount_invest, expected_interest=earning_amount, date_of_invest=invest_date,withdraw_date= withdraw_date)
        
        investor_id = investor.id
        nfc_title = "Invest request of {}".format(amount_invest)
        nfc_msg = "{} {}, wants to invest {} on {} and expected interest is {}, Expected withdraw date is {}.".format(investor.first_name, investor.last_name, amount_invest ,invest_date,earning_amount,withdraw_date)

        Notification.objects.create(investor_id=investor_id, title=nfc_title, desc=nfc_msg, for_admin=True) 
        messages.success(request,'Request Send Successfully, Admin will review this')

    return render(request, 'dashboard/request_to_invest.html')

def dashboard(request):
    return render(request,'dashboard/dashboard.html')


def all_active_invest(request, id):
    active_invest = Invest.objects.filter(investor_id=id, status=True)
    context = {
        'active_invest':active_invest
    }
    return render(request, 'dashboard/all_active_invest.html',context)


def approve_investment(request,id):
    invest = Invest.objects.get(id=id) 
    invest.status = True
    invest.save()
    investor_id = invest.investor.id

    complete_invest_date = "{}/{}/{}".format(invest.date_of_invest.month,invest.date_of_invest.day, invest.date_of_invest.year )
    complete_widthdraw_date = "{}/{}/{}".format(invest.withdraw_date.month,invest.withdraw_date.day, invest.withdraw_date.year )
    nfc_title = "Invest Request of {} is approved".format(invest.amount_to_invest)
    nfc_msg = "Congratulations!! \n Admin approved your Invest Request made on {}, Total amount is {}. Expected Interest is {}. Interest will be available on {}".format(complete_invest_date, invest.amount_to_invest,invest.expected_interest,complete_widthdraw_date )
    Notification.objects.create(investor_id=investor_id, title=nfc_title, desc=nfc_msg)
    return redirect('investor:dashboard')
    
def single_nofication(request, id):
    notification = get_object_or_404(Notification, id=id)
    context = {
        'notification':notification
    }
    return render(request, 'dashboard/nofication_details.html', context)

def admin_notification_list(request):
    notifications = Notification.objects.filter(for_admin=True).order_by('-date')
    context = {
        "notifications":notifications
    }
    return render(request, 'dashboard/admin_notification_list.html',context)