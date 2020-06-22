from django.shortcuts import render, redirect
from django.contrib import messages
from .models import *
import hashlib,datetime
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, JsonResponse
from django.core.mail import send_mail
from .pdfgenerator import renderPDF
import datetime
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

        bank_name = Bank.objects.get(id=bank_nameId)

        encripted_pass = hashlib.md5(user_password.encode())
        password = encripted_pass.hexdigest() 

        investor = Investor.objects.create(username=username, password=password, first_name=fname,last_name=lname, email= email, phone = phone, address=address,bank_name_id=bank_nameId, account_number=bank_account,agree_to_invest=True)

        invest = Invest.objects.create(investor_id=investor.id, amount_to_invest=amount_invest, expected_interest=earning_amount, date_of_invest=invest_date,withdraw_date= withdraw_date)

        nfc_and_email_msg = """  
            <p style="font-size:18px;margin-bottom:10px;"><strong>Hello PFA,</strong> <br>
            Find below details of New PFA INVESTOR:<p>
            Full Name:  {} {} <br>
            Email:  {}<br>
            Phone:  {} <br>
            Address:  {}<br>
            Amount Invested: {} <br>
            Date of investment:  {}<br>
            Expected Interest:  {}<br>
            Withdrawal Date: {} <br>
            Account Number:  {}<br>
            Bank Name: {} <br><br>
            Investor Accepted Terms 
        """.format(fname,lname,email,phone,address, amount_invest,invest_date,earning_amount,withdraw_date,bank_account,bank_name) 

        nfc_title = "New PFA INVESTOR {} {}, wants to invest <strong>₦ {}</strong> on {}".format(fname,lname, amount_invest ,invest_date)
        # Notification for Admin
        Notification.objects.create(investor_id=investor.id, title=nfc_title, desc=nfc_and_email_msg,for_admin=True) 
        # Email For Admin 
        email_subject = "New deposit request of ₦ {}".format(amount_invest)  
        form_email = 'pfa.erudite@gmail.com'
        to_email = 'wealcode@gmail.com' 

        send_mail(
            email_subject,
            nfc_and_email_msg,
            form_email,
            [to_email],
            fail_silently=False, 
            html_message=nfc_and_email_msg, 
        ) 

        # Notification for Investor
        new_title = "You have successfully completed your investment form for PFA® INVEST"
        new_msg = """
            Thank you {} {}. <br> You have successfully completed your investment form for PFA® INVEST. An email will be sent to the email address with complete details of this investment after our admin approves your submission and you will be notified.
         """.format(investor.first_name, investor.last_name,)
        Notification.objects.create(investor_id=investor.id, title=new_title, desc=new_msg, for_admin=False,has_download=True)
        messages.success(request, "Signup Completed")
        return redirect('investor:investor_login')


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
        nfc_title = "New PFA INVESTOR {} {}, wants to invest <strong>₦ {}</strong> on {}".format(investor.first_name, investor.last_name, amount_invest ,invest_date)
        nfc_and_email_msg = """  
            <p style="font-size:18px;margin-bottom:10px;"><strong>Hello PFA,</strong> <br>
            Find below details of New PFA INVESTOR:<p>
            Full Name:  {} {} <br>
            Email:  {}<br>
            Phone:  {} <br>
            Address:  {}<br>
            Amount Invested: {} <br>
            Date of investment:  {}<br>
            Expected Interest:  {}<br>
            Withdrawal Date: {} <br>
            Account Number:  {}<br>
            Bank Name: {} <br><br>
            Investor Accepted Terms 
        """.format(investor.first_name, investor.last_name,investor.email,investor.phone, investor.address, amount_invest,invest_date,earning_amount,withdraw_date,investor.account_number,investor.bank_name) 

        Notification.objects.create(investor_id=investor_id, title=nfc_title, desc=nfc_and_email_msg, for_admin=True) 
        email_subject = "New deposit request of ₦ {}".format(amount_invest)  
        form_email = 'pfa.erudite@gmail.com'
        to_email = 'wealcode@gmail.com' 

        send_mail(
            email_subject,
            nfc_and_email_msg,
            form_email,
            [to_email],
            fail_silently=False, 
            html_message=nfc_and_email_msg,

        ) 

        new_title = "You have successfully completed your investment form for PFA® INVEST"
        new_msg = """
            Thank you {} {}. <br> You have successfully completed your investment form for PFA® INVEST. An email will be sent to the email address with complete details of this investment after our admin approves your submission and you will be notified.
         """.format(investor.first_name, investor.last_name,)
        Notification.objects.create(investor_id=investor_id, title=new_title, desc=new_msg, for_admin=False,has_download=True) 

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
    
    nfc_title = "Congratulations!! Your deposit request for <strong>₦ {}</strong> is approved by Admin".format(invest.amount_to_invest)
    
    new_msg = """
        <h4 class='m-0'>Congratulations!! {} {} </h4>
        <p> On <strong>{}</strong>, you made a deposit of <strong>₦ {}</strong>. You are entitled to 15% <strong>₦ {}</strong> of your investment and your withdrawal date is on <strong>{}</strong>.
        <br>Thank your for your Investment </p>
        <p>
            ERUDiTE <br>
            CEO<br>
            Pfaccounts.com<br>
        <p>""".format(invest.investor.first_name,invest.investor.last_name, complete_invest_date,invest.amount_to_invest,invest.expected_interest,complete_widthdraw_date)
    Notification.objects.create(investor_id=investor_id, title=nfc_title, desc=new_msg)

    email_subject = "Deposit request for ₦ {} is approved by Admin".format(invest.amount_to_invest)  
    form_email = 'pfa.erudite@gmail.com'
    to_email = invest.investor.email 

    send_mail(
        email_subject,
        new_msg,
        form_email,
        [to_email],
        fail_silently=False, 
        html_message=new_msg,

    )
    message = "Deposit request for ₦ {} is approved".format(invest.amount_to_invest)
    messages.success(request,message)
    
    return redirect('investor:dashboard')





def cancle_investment(request,id):
    invest = Invest.objects.get(id=id) 
    investor_id = invest.investor.id

    complete_invest_date = "{}/{}/{}".format(invest.date_of_invest.month,invest.date_of_invest.day, invest.date_of_invest.year )
    complete_widthdraw_date = "{}/{}/{}".format(invest.withdraw_date.month,invest.withdraw_date.day, invest.withdraw_date.year )
    
    nfc_title = "Deposit request for <strong>₦ {}</strong> was declined by Admin".format(invest.amount_to_invest)
    
    new_msg = """ 
        <p>We extremely sorry to say that your deposit request for <strong>₦ {}</strong> was declined by Admin</p>
        <p>
            ERUDiTE <br>
            CEO<br>
            Pfaccounts.com<br>
        <p>""".format(invest.amount_to_invest)
    Notification.objects.create(investor_id=investor_id, title=nfc_title, desc=new_msg)

    email_subject = "Deposit request declined for ₦ {} by Admin".format(invest.amount_to_invest)  
    form_email = 'pfa.erudite@gmail.com'
    to_email = invest.investor.email 

    send_mail(
        email_subject,
        new_msg,
        form_email,
        [to_email],
        fail_silently=False, 
        html_message=new_msg,

    ) 

    invest.delete()
    message = "Deposit request for ₦ {} was Declined".format(invest.amount_to_invest)
    messages.success(request,message)
    
    return redirect('investor:dashboard')






def single_nofication(request, id):
    notification = get_object_or_404(Notification, id=id)
    notification.is_view = True
    notification.save()
    context = {
        'notification':notification
    }
    return render(request, 'dashboard/nofication_details.html', context)


def admin_notification_list(request):
    notifications = Notification.objects.filter(for_admin=True).order_by('-date')
    page = request.GET.get('page', 1)
    paginator = Paginator(notifications, 10) 
    try:
        notifications = paginator.page(page)
    except PageNotAnInteger:
        notifications = paginator.page(1)
    except EmptyPage:
        notifications = paginator.page(paginator.num_pages)

    context = {
        "notifications":notifications
    }
    return render(request, 'dashboard/admin_notification_list.html',context)




def investor_notification_list(request,id):
    notifications = Notification.objects.filter(investor_id=id,for_admin=False).order_by('-date')
    page = request.GET.get('page', 1)
    paginator = Paginator(notifications, 10) 
    try:
        notifications = paginator.page(page)
    except PageNotAnInteger:
        notifications = paginator.page(1)
    except EmptyPage:
        notifications = paginator.page(paginator.num_pages)


    context = {
        "investor_notifications":notifications
    }
    return render(request, 'dashboard/investor_notification_list.html',context)

def investor_unread_notification_list(request,id):
    notifications = Notification.objects.filter(investor_id=id,for_admin=False, is_view=False).order_by('-date')
    page = request.GET.get('page', 1)
    paginator = Paginator(notifications, 10) 
    try:
        notifications = paginator.page(page)
    except PageNotAnInteger:
        notifications = paginator.page(1)
    except EmptyPage:
        notifications = paginator.page(paginator.num_pages)

    context = {
        "investor_unread_notifications":notifications
    }
    return render(request, 'dashboard/investor_notification_list.html',context)

def admin_unread_notifications(request):
    notifications = Notification.objects.filter(for_admin=True, is_view=False).order_by('-date')
    page = request.GET.get('page', 1)
    paginator = Paginator(notifications, 10) 
    try:
        notifications = paginator.page(page)
    except PageNotAnInteger:
        notifications = paginator.page(1)
    except EmptyPage:
        notifications = paginator.page(paginator.num_pages)

    context = {
        "admin_unread_notifications":notifications
    }
    return render(request, 'dashboard/admin_notification_list.html',context)


def ajax_notification_delete(request):
    if request.is_ajax():
        notification_id = int(request.GET.get('notification_id'))
        notification = Notification.objects.get(id=notification_id)
        notification.delete()
        return JsonResponse({'message':'Notification Delte Successfully'}) 

def ajax_notification_markas_read(request):
    if request.is_ajax():
        notification_id = int(request.GET.get('notification_id'))
        notification = Notification.objects.get(id=notification_id)
        notification.is_view = True
        notification.save() 
        return JsonResponse({'message':'Marked as Read'})


def terms_condition_pdf(request,id):
    investor = Investor.objects.get(id=id)
    date = datetime.date.today()
    new_date = "{} {}, {} ".format(date.strftime('%B'), date.day, date.year) 
    context = {
        'date':new_date,
        'investor':investor
    }
    bdonor_pdf = renderPDF('dashboard/terms_condition_pdf.html',context)
    return HttpResponse(bdonor_pdf, content_type='application/pdf')