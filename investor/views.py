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
from django.contrib.auth.models import User
from .forms import PopupForm,TermsconditionForm,EditorForm,UserForm
from .decorators import investor_login_required,investor_or_admin_login_required,editor_admin_login_required

from django.contrib.auth.decorators import login_required 
# Create your views here.  
# Admin functionality
host = 'http://127.0.0.1:8000/'
admin_email = "habib@shuttle.digital"

def sendemail(request):
    inverst = Invest.objects.filter(status=True, payment_status=False,reinvest_status=False,email_send_status=False)
    for item in inverst:
        widthdraw_date = item.withdraw_date.day
        if widthdraw_date < 7:  
            item.email_send_status = True
            item.save()
            nfc_and_email_msg = """  
            <p>Hello PFA,<br>
            You have an upcoming payment. Find Bellow the full details<p>
            Full Name:  {} {} <br> 
            Amount Invested: {} <br>
            Date of investment:  {}<br>
            Expected Interest:  {}<br>
            Payment Date: {} <br>
            Account Number:  {}<br>
            Bank Name: {} <br> 
            """.format(item.investor.first_name,item.investor.last_name,item.amount_to_invest,item.date_of_invest, item.expected_interest,item.withdraw_date, item.investor.account_number, item.investor.bank_name ) 

            email_subject = "Upcoming payment for #{}".format(item.expected_interest)  
            form_email = admin_email

            send_mail(
                email_subject,
                nfc_and_email_msg,
                form_email,
                [admin_email],
                fail_silently=False, 
                html_message=nfc_and_email_msg, 
            ) 


def admin_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password) 
        request.session['investor'] = None 
        if user is not None:
            login(request, user)
            return redirect('investor:dashboard')
        else:
            messages.error(request, 'Username or password is  incorrect') 
            return redirect('investor:admin_login')
    return render(request, 'account/admin_login.html')


def admin_logout(request):
    logout(request)
    return redirect('investor:admin_login') 



# investor functionality
def investor_registration(request): 
    interest = Interest.objects.filter(status=True).first()  
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
        amount_invest = amount_invest.replace(",","")
        amount_invest = float(amount_invest)
        amount_invest = int(round(amount_invest))  
        earning_amount = request.POST['earning_amount'] 
        earning_amount = earning_amount.replace(",","")
        earning_amount = float(earning_amount)
        earning_amount = int(round(earning_amount)) 
        invest_date = request.POST['invest_date']
        withdraw_date= request.POST['withdraw_date']
        bank_nameId = int(request.POST['bank_name'])
        bank_account = request.POST['bank_account'] 

        bank_name = Bank.objects.get(id=bank_nameId)

        encripted_pass = hashlib.md5(user_password.encode())
        password = encripted_pass.hexdigest() 
        username_check = Investor.objects.filter(username =username ) 
        email_check = Investor.objects.filter(email =email) 
        if username_check.exists():
            messages.error(request, "Username already exists")
        elif email_check.exists():
            messages.error(request, "Email already exists")
        else:
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

            nfc_title = "New PFA INVESTOR {} {}, wants to invest <strong>₦{}</strong> on {}".format(fname,lname, amount_invest ,invest_date)
            # Notification for Admin
            Notification.objects.create(investor_id=investor.id, title=nfc_title, desc=nfc_and_email_msg,for_admin=True) 
            # Email For Admin 
            email_subject = "New deposit request of ₦{}".format(amount_invest)  
            form_email = admin_email
            to_email = admin_email 

            send_mail(
                email_subject,
                nfc_and_email_msg,
                form_email,
                [to_email],
                fail_silently=False, 
                html_message=nfc_and_email_msg, 
            )  

            investor_email_subject = "Active Your PFA Investor Account"
            investor_active_link = host+"investor-account/{}/active".format(investor.id)
            investor_nfc_and_email_msg = """
                <p><strong>Hello {} {},</strong> <br> 
                Click the following link to Active Your PFA Investor Account <br>
                <a target="_blank" href="{}">{}</a>

            """ .format(fname,lname,investor_active_link,investor_active_link)
            form_email = admin_email
            send_mail(
                investor_email_subject, 
                investor_nfc_and_email_msg,
                form_email,
                [email],
                fail_silently=False, 
                html_message=investor_nfc_and_email_msg, 
            ) 

            # Notification for Investor
            new_title = "You have successfully completed your investment form for PFA® INVEST"
            new_msg = """
                Thank you {} {}. <br> You have successfully completed your investment form for PFA® INVEST. An email will be sent to the email address with complete details of this investment after our admin approves your submission and you will be notified.
            """.format(investor.first_name, investor.last_name,)
            Notification.objects.create(investor_id=investor.id, title=new_title, desc=new_msg, for_admin=False,has_download=True)
            messages.success(request, "Signup Completed. Please check your email to Activate your account.")
            return redirect('investor:investor_login')


    context = {
        'bank_list':bank_list,
        'amount':interest
    }
    
    return render(request,'account/registration.html',context)

def investor_account_active(request,id):
    investor = Investor.objects.get(id=id)
    investor.status = True
    investor.save()
    messages.success(request, "Your account is activated. Now you can login")
    return redirect('investor:investor_login')

def investor_password_resets(request):
    if request.method == 'POST':
        email = request.POST['email']
        email_check = Investor.objects.filter(email = email) 
        if email_check.exists(): 
            email_check = email_check.first()
            email_subject = "PFA Investor Password reset"
            active_link = host+"investor-password/{}/reset".format(email_check.id)
            nfc_and_email_msg = """
                <p><strong>Hello {} {},</strong> <br> 
                Click the following link to reset your password <br>
                <a target="_blank" href="{}">{}</a>

            """ .format(email_check.first_name,email_check.last_name,active_link,active_link)
            form_email = admin_email
            send_mail(
                email_subject, 
                nfc_and_email_msg,
                form_email,
                [email],
                fail_silently=False, 
                html_message=nfc_and_email_msg, 
            ) 
            messages.success(request, "Password reset link sent to your email, check you email")

        else:
            messages.error(request, "Email address not found")
    return render(request, 'account/investor_password_resets.html')

def investor_password_reset_link(request, id):
    investor = Investor.objects.get(id=id)
    if request.method == 'POST':
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']
        if pass1 == pass2:
            encripted_pass = hashlib.md5(pass1.encode())
            new_pass = encripted_pass.hexdigest()
            investor.password = new_pass
            investor.save()
            messages.error(request,"Password changed successfully")
            return redirect('investor:investor_login')
        else:
            messages.error(request,"Password doesn't matched")
    return render(request, 'account/investor_password_reset_link.html')

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
                    if chk_user.status:
                        if request.session['editor']:
                            request.session['editor'] = None

                        request.session['investor'] = chk_user.id 
                        return redirect('investor:dashboard') 
                    else:  
                        messages.error(request ,"Your Account is Not activated") 
                        return render(request, "account/investor_login.html")
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
    interest = Interest.objects.filter(status=True).first()  
    investor = Investor.objects.get(id=id)
    if request.method == 'POST':
        amount_invest = request.POST['amount_invest']
        earning_amount = request.POST['earning_amount']
        invest_date = request.POST['invest_date']
        withdraw_date= request.POST['withdraw_date'] 
        invest = Invest.objects.create(investor_id=id, amount_to_invest=amount_invest, expected_interest=earning_amount, date_of_invest=invest_date,withdraw_date= withdraw_date)
        
        investor_id = investor.id
        nfc_title = "New PFA INVESTOR {} {}, wants to invest <strong>₦{:}</strong> on {}".format(investor.first_name, investor.last_name, amount_invest ,invest_date)
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
        email_subject = "New deposit request of ₦{}".format(amount_invest)  
        form_email = 'pfa.erudite@gmail.com'
        to_email = admin_email 

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

    context = {
        'amount':interest
    }

    return render(request, 'dashboard/request_to_invest.html',context)


# @investor_or_admin_login_required
def dashboard(request):
    sendemail(request)
    rols = Editor.objects.filter(role__access__has_access="Invest Management")
    for item in rols: 
        print(item)
    return render(request,'dashboard/dashboard.html')


def all_active_invest(request, id):
    active_invest = Invest.objects.filter(investor_id=id, status=True)
    context = {
        'active_invest':active_invest
    }
    return render(request, 'dashboard/all_active_invest.html',context)


@editor_admin_login_required 
def approve_investment(request,id):
    invest = Invest.objects.get(id=id) 
    invest.status = True
    invest.save()
    investor_id = invest.investor.id

    complete_invest_date = "{}/{}/{}".format(invest.date_of_invest.month,invest.date_of_invest.day, invest.date_of_invest.year )
    complete_widthdraw_date = "{}/{}/{}".format(invest.withdraw_date.month,invest.withdraw_date.day, invest.withdraw_date.year )
    
    nfc_title = "Congratulations!! Your deposit request for <strong>₦{}</strong> is approved by Admin".format(invest.amount_to_invest)
    
    new_msg = """
        <h4 class='m-0'>Congratulations!! {} {} </h4>
        <p> On <strong>{}</strong>, you made a deposit of <strong>₦{}</strong>. You are entitled to 15% <strong>₦{}</strong> of your investment and your withdrawal date is on <strong>{}</strong>.
        <br>Thank your for your Investment </p>
        <p>
            ERUDiTE <br>
            CEO<br>
            Pfaccounts.com<br>
        <p>""".format(invest.investor.first_name,invest.investor.last_name, complete_invest_date,invest.amount_to_invest,invest.expected_interest,complete_widthdraw_date)
    Notification.objects.create(investor_id=investor_id, title=nfc_title, desc=new_msg)

    email_subject = "Deposit request for ₦{} is approved by Admin".format(invest.amount_to_invest)  
    form_email = admin_email
    to_email = invest.investor.email 

    send_mail(
        email_subject,
        new_msg,
        form_email,
        [to_email],
        fail_silently=False, 
        html_message=new_msg,

    )
    message = "Deposit request for ₦{} is approved".format(invest.amount_to_invest)
    messages.success(request,message)
    
    return redirect('investor:all_pending_request')


@editor_admin_login_required
def cancle_investment(request,id):
    invest = Invest.objects.get(id=id) 
    investor_id = invest.investor.id

    complete_invest_date = "{}/{}/{}".format(invest.date_of_invest.month,invest.date_of_invest.day, invest.date_of_invest.year )
    complete_widthdraw_date = "{}/{}/{}".format(invest.withdraw_date.month,invest.withdraw_date.day, invest.withdraw_date.year )
    
    nfc_title = "Deposit request for ₦{} was declined by Admin".format(invest.amount_to_invest)
    
    new_msg = """ 
        <p>We extremely sorry to say that your deposit request for <strong>₦{}</strong> was declined by Admin</p>
        <p>
            ERUDiTE <br>
            CEO<br>
            Pfaccounts.com<br>
        <p>""".format(invest.amount_to_invest)
    Notification.objects.create(investor_id=investor_id, title=nfc_title, desc=new_msg)

    email_subject = "Deposit request declined for ₦{} by Admin".format(invest.amount_to_invest)  
    form_email = admin_email
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
    message = "Deposit request for ₦{} was Declined".format(invest.amount_to_invest)
    messages.success(request,message)
    
    return redirect('investor:dashboard') 

# body
def single_nofication(request, id):
    notification = get_object_or_404(Notification, id=id)
    notification.is_view = True
    notification.save()
    context = {
        'notification':notification
    }
    return render(request, 'dashboard/nofication_details.html', context)

@editor_admin_login_required
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



@investor_login_required
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
    
@investor_login_required
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

@login_required(login_url='/investor/admin/login')
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

@editor_admin_login_required
def all_investor_list(request):
    investor_list = Investor.objects.filter(status=True).order_by('first_name')
    
    context = {
        "investor_list":investor_list
    }
    return render(request, 'dashboard/all_investor_list.html',context)

@editor_admin_login_required
def investor_delete(request, id):
    investor = Investor.objects.get(id=id)
    investor.delete() 
    messages.success(request, "Investor Deleted Successfully")
    return redirect('investor:all_investor_list')

@editor_admin_login_required
def all_pending_request(request):
    pending_request = Invest.objects.filter(status=False, payment_status=False).order_by('-timestamp')
    context = {
        'pending_request':pending_request
    }
    return render(request, 'dashboard/all_pending_request.html',context)
    
@editor_admin_login_required
def all_active_invest_list(request):
    active_invest = Invest.objects.filter(status=True, payment_status=False,reinvest_status=False).order_by('withdraw_date')
    context = {
        'active_invest_list':active_invest
    }
    return render(request, 'dashboard/all_active_invest_list.html',context)
    
@editor_admin_login_required
def upcoming_payment(request):
    active_invest = Invest.objects.filter(status=True, payment_status=False,reinvest_status=False).order_by('withdraw_date')
    context = {
        'active_invest_list':active_invest
    }
    return render(request, 'dashboard/all_active_invest_list.html',context)


@editor_admin_login_required
def admin_chat(request, id): 
    messages = Message.objects.filter(status=True,investor_id = id).order_by('date_time')
    if id != 0:
        message_count = messages.count()  
        if message_count > 0:  
            messages.update(is_view_admin = True) 
        else: 
            Message.objects.create(message="Hello There", investor_id = id, is_admin=True, is_view_admin=True) 

    investor = Message.objects.filter(status=True).values('investor_id','investor_id__first_name','investor_id__last_name').distinct()
    if request.method == 'POST':
        message = request.POST['message'] 
        Message.objects.create(message=message, investor_id = id, is_admin=True, is_view_admin=True) 
        
    context = {
        'messages':messages,
        'investor':investor
    }
    return render(request,'dashboard/admin_chat.html',context) 

def investor_chat(request, id):
    messages = Message.objects.filter(investor_id=id).order_by('date_time')
    messages.update(is_view_investor = True)
    if request.method == 'POST':
        message = request.POST['message'] 
        Message.objects.create(message=message, investor_id = id, is_admin=False, is_view_admin=False,is_view_investor=True) 
    
    context = {
        'messages':messages
    }
    return render(request, 'dashboard/investor_chat.html', context)

@editor_admin_login_required
def make_payment(request,id):
    invest = Invest.objects.get(id=id) 
    investor_id = invest.investor.id
    nfc_title = "Admin made a payment of ₦{} ".format(invest.amount_to_invest)
    complete_invest_date = "{}/{}/{}".format(invest.date_of_invest.month,invest.date_of_invest.day, invest.date_of_invest.year )
    complete_widthdraw_date = "{}/{}/{}".format(invest.withdraw_date.month,invest.withdraw_date.day, invest.withdraw_date.year )
    
    nfc_and_email_msg = """  
        <p style="font-size:18px;margin-bottom:10px;"><strong>Congratulations!! {} {},</strong> <br>
        You have received a payment from PFA. Find below the more details of your last payment:<p>  
        Amount Invested: {} <br>
        Date of investment:  {}<br>
        Amount Paid:  {}<br>
        Paid Date: {} <br>
        Account Number:  {}<br>
        Bank Name: {} <br><br> 
    """.format(invest.investor.first_name, invest.investor.last_name,invest.amount_to_invest,complete_invest_date,invest.expected_interest,complete_widthdraw_date,invest.investor.account_number,invest.investor.bank_name) 

    Notification.objects.create(investor_id=investor_id, title=nfc_title, desc=nfc_and_email_msg, for_admin=False) 
    email_subject = "Admin made a payment of ₦{} ".format(invest.amount_to_invest)
    form_email = admin_email
    to_email = invest.investor.email

    send_mail(
        email_subject, 
        nfc_and_email_msg,
        form_email,
        [to_email],
        fail_silently=False, 
        html_message=nfc_and_email_msg,

    )  
    invest.reinvest_status = True
    invest.save()
    messages.success(request, "You have make a payment ")
    return redirect('investor:all_active_invest_list')

@editor_admin_login_required
def interest_paid_admin(request):
    interest_paid = Invest.objects.filter(payment_status=True).order_by('-withdraw_date')
    context = {
        'interest_paid':interest_paid
    }
    return render(request, 'dashboard/interest_paid_admin.html', context)

 
def interest_paid_admin_delete(request,id):
    interest_paid = Invest.objects.get(payment_status=True,id=id) 
    interest_paid.delete()
    return redirect('investor:interest_paid_admin')


@editor_admin_login_required
def admin_password_change(request):
    user_id = request.user.id 
    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        old_pass = request.POST['old_pass']
        password = request.POST['pass']
        cpassword = request.POST['cpass']  

        user_has = authenticate(request, username=user.username, password = old_pass)
        if user_has is not None:
            if password == cpassword:
                user.set_password(password)
                user.save()
                messages.success(request,"Password Updated Successfully") 
            else: 
                messages.error(request,"Password doesn't Matched")
        else:
            messages.error(request,"Old Password doesn't Matched")

    return render(request, 'dashboard/admin_password_change.html')


@editor_admin_login_required
def add_new_investor(request):
    bank_list = Bank.objects.filter(status=True)
    if request.method == 'POST':
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        password = "123456"
        email = request.POST['email']
        phone = request.POST['phone']
        address = request.POST['address']
        bank_name_id = int(request.POST['bank'])
        bank_account = request.POST['bank_account']
        bank_name = Bank.objects.get(id = bank_name_id)

        check_username = Investor.objects.filter(username = username)
        check_email = Investor.objects.filter(email = email)
        if check_username.exists():
            messages.success(request, "This username is already used")
        elif check_email:
            messages.success(request, "This Email Address is already used")
        else: 
            investor = Investor.objects.create(username = username, password = password, first_name = fname, last_name =lname, email = email, phone=phone, address = address,bank_name_id = bank_name_id, account_number = bank_account)
            email_subject = "PFA has created your account"
            active_link = host+"investor-active-link/{}/activate".format(investor.id)
            nfc_and_email_msg = """
                <p style="font-size:18px;margin-bottom:10px;"><strong>Hello {} {},</strong> <br>
                Find below details of your  PFA INVESTOR account:<p>
                Full Name:  {} {} <br>
                User Name:  {} <br>
                Email:  {}<br>
                Phone:  {} <br>
                Address:  {}<br> 
                Bank Name: {} <br>
                Account Number:  {}<br><br>
                Click the following link to set your password and active your account <br>
                <a href="{}">{}</a>

            """ .format(fname,lname,fname,lname,username,email,phone,address,bank_name,bank_account,active_link,active_link)
            form_email = admin_email
            send_mail(
                email_subject, 
                nfc_and_email_msg,
                form_email,
                [email],
                fail_silently=False, 
                html_message=nfc_and_email_msg, 
            )
            messages.success(request, "Investor added successfully. All Information send to the given Email Address")
            return redirect('investor:add_new_investor')
    
    context = {
        'bank_list':bank_list
    }
    
    return render(request, 'dashboard/add_new_investor.html',context)


def investor_active_link(request, id):
    investor = Investor.objects.get(id=id)
    if request.method == 'POST':
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        if password1 == password2:
            encripted_pass = hashlib.md5(password1.encode())
            password = encripted_pass.hexdigest() 
            investor.password = password
            investor.status = True
            investor.save()
            messages.success(request, "Your account is activated and password changed successfully")
            return redirect('investor:investor_login')
        else:
            messages.success(request, "Password doesn't Match")

    return render(request, 'account/investor_active_link.html')


@editor_admin_login_required
def add_bank(request):
    if request.method == 'POST':
        bank = request.POST['bank'] 
        Bank.objects.create(bank_name=bank)
        messages.success(request, "Bank Added Successfully")
    return render(request,'dashboard/add_bank.html')


@editor_admin_login_required
def bank_list(request):
    bank_list = Bank.objects.all().order_by('bank_name')
    context = {
        'bank_list':bank_list
    }
    return render(request, 'dashboard/bank_list.html',context)

@editor_admin_login_required
def bank_edit(request, id):
    bank = Bank.objects.filter(id = id) 
    old_name = bank[0].bank_name
    if request.method == 'POST':
        bank_name = request.POST['bank']
        bank.update(bank_name = bank_name)  
        messages.success(request, "Bank updated uccessfully")
        return redirect("investor:bank_list") 
    context = {
        'bank_name':old_name
    }
    return render(request,'dashboard/edit_bank.html',context)

@editor_admin_login_required
def bank_active(request, id):
    bank = Bank.objects.get(id = id)
    bank.status = True
    bank.save() 
    messages.success(request, "Bank status changed uccessfully")
    return redirect("investor:bank_list") 


@editor_admin_login_required
def bank_deactive(request, id):
    bank = Bank.objects.get(id = id)
    bank.status = False
    bank.save() 
    messages.success(request, "Bank status changed uccessfully")
    return redirect("investor:bank_list") 

@investor_login_required
def investor_password_change(request, id):
    investor = Investor.objects.get(id = id)
    if request.method == 'POST':
        old_pass = request.POST['old_pass']
        password1 = request.POST['pass']
        cpassword = request.POST['cpass']  

        encripted_pass = hashlib.md5(old_pass.encode())
        password = encripted_pass.hexdigest()

        encripted_pass1 = hashlib.md5(password1.encode())
        new_pass = encripted_pass1.hexdigest()

        if investor.password == password:
            if password1 == cpassword:
                investor.password = new_pass
                investor.save()
                messages.success(request,"Password Updated Successfully")  
            else: 
                messages.error(request,"Password doesn't Matched")
        else:
            messages.error(request,"Old Password doesn't Matched")

    return render(request, 'dashboard/admin_password_change.html')

@investor_login_required
def investor_profile_update(request, id):
    investor = Investor.objects.get(id = id)
    bank_list = Bank.objects.filter(status=True)
    if request.method == 'POST':
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname'] 
        email = request.POST['email']
        phone = request.POST['phone']
        address = request.POST['address']
        bank_name_id = int(request.POST['bank'])
        bank_account = request.POST['bank_account'] 

        update_investor = Investor.objects.filter(id=id)
        update_investor.update(username = username,first_name = fname, last_name =lname, email = email, phone=phone, address = address,bank_name_id = bank_name_id, account_number = bank_account)

        messages.success(request, "Investor Profile Updated Successfully")
    context = {
        'investor':investor,
        'bank_list':bank_list, 
    }
    return render(request, 'dashboard/investor_profile_update.html',context)

@investor_login_required
def interest_received_investor(request, id):
    invests = Invest.objects.filter(investor_id = id,payment_status=True)
    context = {
        'invests':invests
    }
    return render(request, 'dashboard/nterest_received_investor.html',context)

@investor_login_required
def investor_active_invest(request, id):
    invests = Invest.objects.filter(investor_id = id, status=True, payment_status=False,reinvest_status=False, delete_status=False).order_by('date_of_invest')
    context = {
        'invests':invests
    }
    return render(request, 'dashboard/investor_active_invest.html',context)
@investor_login_required
def investor_pending_invest(request, id):
    pending_invest_list = Invest.objects.filter(investor_id=id, status=False, payment_status=False).order_by('-date_of_invest')
    context = {
        'pending_invest_list':pending_invest_list
    }
    return render(request, 'dashboard/investor_pending_invest.html', context)

@investor_login_required
def investor_cancle_investment(request, id):
    invest = Invest.objects.get(id = id)
    invest.delete()
    messages.success(request, "Invest removed successfully")
    return redirect('investor:investor_pending_invest', request.session['investor'])

@editor_admin_login_required
def add_popup(request):
    form = PopupForm()
    if request.method == 'POST':
        form = PopupForm(request.POST)
        if form.is_valid():
            popup = form.save(commit=False)
            popup.timestamp = datetime.datetime.now()
            popup.status = False
            popup.save()
            messages.success(request, 'Popup Created Successfully')
            return redirect('investor:popup_list')
    context = {
        'form':form
    }
    return render(request, 'dashboard/add_popup.html', context)

@editor_admin_login_required
def popup_list(request):
    popup_list = Popup.objects.all().order_by('-timestamp')
    context = {
        'popup_list':popup_list
    }
    return render(request, 'dashboard/popup_list.html', context) 

@editor_admin_login_required   
def popup_edit(request, id):
    popup = Popup.objects.get(id=id)
    form = PopupForm(instance=popup)
    if request.method == 'POST':
        form = PopupForm(request.POST, instance=popup)
        if form.is_valid():
            form.save()
            messages.success(request, 'Popup Updated Successfully')
            return redirect('investor:popup_list')
    context = {
        'form':form,
        'update':True
    }
    return render(request, 'dashboard/add_popup.html', context)

@editor_admin_login_required
def popup_delete(request, id):
    popup = Popup.objects.get(id=id)
    popup.delete()
    messages.success(request, 'Popup Deleted Successfully')
    return redirect('investor:popup_list') 

@editor_admin_login_required
def popup_active(request, id):
    popup = Popup.objects.get(id=id)
    popup.status = True
    popup.save()
    messages.success(request, 'Popup Activated')
    return redirect('investor:popup_list')

@editor_admin_login_required
def popup_deactive(request, id):
    popup = Popup.objects.get(id=id)
    popup.status = False
    popup.save()
    messages.success(request, 'Popup Deactivated')
    return redirect('investor:popup_list') 

@editor_admin_login_required
def send_bulk_email(request): 
    investor_list = Investor.objects.filter(status=True).order_by('first_name') 
    if request.method == 'POST': 
        email_list = request.POST.getlist('email[]') 
        form_email = admin_email
        email_subject = request.POST['subject']
        email_msg = request.POST['message']
        send_mail(
            email_subject, 
            email_msg,
            form_email,
            email_list,
            fail_silently=False, 
        )  
        messages.success(request, "Email Send Successfully") 
        
    context = {
        "investor_list":investor_list
    }
    return render(request, 'dashboard/send_bulk_email.html',context)

@investor_login_required
def investor_pending_payment(request, id):
    pending_payment = Invest.objects.filter(investor_id = id, reinvest_status=True)

    context = {
        'pending_payment':pending_payment
    }
    return render(request, 'dashboard/investor_pending_payment.html',context)


@investor_login_required
def invest_all_balance(request, id):
    old_invest = Invest.objects.get(id = id, reinvest_status=True)
    old_invest.reinvest_status = False
    old_invest.payment_status = True
    old_invest.delete_status=True
    old_invest.status=False
    old_invest.save()

    investor_id =old_invest.investor.id
    amount_to_invest = old_invest.expected_interest + old_invest.amount_to_invest
    expected_interest = (amount_to_invest * 15)/100
    date_of_invest = datetime.datetime.now()
    withdraw_date = date_of_invest + datetime.timedelta(days=30)
    
    Invest.objects.create(investor_id=investor_id,amount_to_invest=amount_to_invest,expected_interest=expected_interest,date_of_invest=date_of_invest, withdraw_date=withdraw_date)

    return redirect('investor:investor_pending_payment', request.session['investor'])

# @investor_login_required
def investor_widthdraw_all(request, id):
    invest = Invest.objects.get(id = id, reinvest_status=True) 
    invest.reinvest_status=False
    invest.payment_status=True
    invest.widthdrawn_status=True
    invest.delete_status=True
    invest.save() 
    messages.success(request,"You have successfully withdrawn all of your amount and terminated your PFA INVEST contract. Your payment would be completed in 30 days.") 
    investor_id = invest.investor.id
   
    date_of_invest = datetime.datetime.now()
    new_date_of_invest = "{} / {} / {}".format(date_of_invest.day, date_of_invest.month, date_of_invest.year)
    new_payment_date = date_of_invest + datetime.timedelta(days=30)
    payment_date = "{} / {} / {}".format(new_payment_date.day, new_payment_date.month, new_payment_date.year)

    nfc_title = "Requested to terminate PFA invest contract."
    nfc_and_email_msg = """  
        <p style="font-size:16px;margin-bottom:10px;"><strong>Hi PFA INVEST,</strong> <br>
        {} {} has requested to terminate PFA invest contract. Find below the details of his contract: <br>
        Full Name: {} {} <br>
        Amount Withdrawn : {} <br>
        Date of Termination {}<br>
        Payment date: {} <br>
        Account Number: {} <br>
        Bank Name: {}<br><br>
        Regards,<br>
        PFA INVEST System
    """.format(invest.investor.first_name, invest.investor.last_name,invest.investor.first_name, invest.investor.last_name,invest.amount_to_invest,new_date_of_invest,payment_date,invest.investor.account_number,invest.investor.bank_name) 

    Notification.objects.create(investor_id=investor_id, title=nfc_title, desc=nfc_and_email_msg, for_admin=True) 
    email_subject = nfc_title
    form_email = 'pfa.erudite@gmail.com'
    to_email = admin_email 

    send_mail(
        email_subject,
        nfc_and_email_msg,
        form_email,
        [to_email],
        fail_silently=False, 
        html_message=nfc_and_email_msg,

    ) 


    invstor_title = "You have requested to terminate PFA invest contract."
    investor_email_msg = """   
        Hi {} {},<br>
        You have requested to terminate PFA invest contract Find below the details of your contract: <br>
        Amount Withdrawn: {} <br>
        Date of Termination : {} <br>
        Payment date: {} <br>

        Regards,
        PFA INVEST
    """.format(invest.investor.first_name, invest.investor.last_name,invest.amount_to_invest,new_date_of_invest,payment_date) 

    Notification.objects.create(investor_id=investor_id, title=invstor_title, desc=investor_email_msg, for_admin=False) 
    investor_email_subject = invstor_title
    invest_form_email = admin_email
    to_email = invest.investor.email 

    send_mail(
        email_subject,
        investor_email_msg,
        form_email,
        [to_email],
        fail_silently=False, 
        html_message=investor_email_msg,

    )  
    return redirect('investor:investor_pending_payment', request.session['investor'])

@investor_login_required
def investor_widthdraw_interest(request, id):
    old_invest = Invest.objects.get(id = id, reinvest_status=True)
    old_invest.reinvest_status = False
    old_invest.payment_status = True
    old_invest.delete_status=True
    old_invest.status=False
    old_invest.save()

    investor_id =old_invest.investor.id
    amount_to_invest = old_invest.amount_to_invest
    expected_interest = (amount_to_invest * 15)/100
    date_of_invest = datetime.datetime.now()
    withdraw_date = date_of_invest + datetime.timedelta(days=30)
    
    Invest.objects.create(investor_id=investor_id,amount_to_invest=amount_to_invest,expected_interest=expected_interest,date_of_invest=date_of_invest, withdraw_date=withdraw_date)

    return redirect('investor:investor_pending_payment', request.session['investor'])


def terms_condition(request):
    terms_conditons = Termscondition.objects.filter(status=True).first()
    context = {
        'terms_conditons':terms_conditons
    }
    return render(request, 'dashboard/terms_condition.html',context)

@editor_admin_login_required
def dashboard_terms_condition(request):
    terms_conditons = Termscondition.objects.filter(status=True).first()
    context = {
        'terms_conditons':terms_conditons
    }
    return render(request, 'dashboard/dashboard_terms_condition.html',context)

@editor_admin_login_required
def add_terms_condition(request):
    form = TermsconditionForm()
    if request.method == 'POST':
        form = TermsconditionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('investor:dashboard_terms_condition') 
    context = {
        'form':form
    }
    return render(request, 'dashboard/add_terms_condition.html',context)

@editor_admin_login_required
def update_terms_condition(request,id):
    terms = Termscondition.objects.get(id = id)
    form = TermsconditionForm(instance=terms)
    if request.method == 'POST':
        form = TermsconditionForm(request.POST, instance=terms)
        if form.is_valid():
            form.save()
            messages.success(request, "Terms and Condition updated")
            return redirect('investor:dashboard_terms_condition') 
    context = {
        'form':form,
        'update':True
    }
    return render(request, 'dashboard/update_terms_condition.html',context)

@login_required
def add_interest(request):
    interest = Interest.objects.filter(status=True).first() 
    if request.method == 'POST':
        amount = request.POST['interest'] 
        update_interest =  Interest.objects.get(id=interest.id)
        update_interest.amount=amount
        update_interest.save()
        messages.success(request, "Interest Updated Successfully")
        return redirect('investor:add_interest')
    context = {
        'amount':interest
    }
    return render(request,'dashboard/add_interest.html',context)

def interest_list(request):
    interest = Interest.objects.filter(status=True).first() 
    context = {
        'amount':interest
    }
    return render(request, 'dashboard/interest_list.html',context)

def add_user(request): 
    if request.method == "POST":
        username = request.POST['username']
        full_name = request.POST['full_name']
        email = request.POST['email'] 
        password = "a;lskdjfjrue94858568AAS@!@$$$#@39587589asldfkalskdf"
        if Editor.objects.filter(email=email).exists():
            messages.success(request,"Email already Exists") 
            return redirect("investor:add_user")
        else:
            new_user = Editor.objects.create(username=username,full_name=full_name,email=email,password=password,status=False) 
            investor_email_subject = "Active Your PFA User Account"
            investor_active_link = host+"investor/user/{}/active-account/password-set/".format(new_user.id)
            investor_nfc_and_email_msg = """
                <p><strong>Hello {},</strong> <br> 
                PFA Admin created your User Account with the following details:<br>
                Email: {} <br>
                Username:  {} <br>
                Click the following link to Active Your PFA User Account and setup your password<br>
                <a target="_blank" href="{}">{}</a>

            """ .format(full_name,email,username,investor_active_link,investor_active_link)
            form_email = admin_email
            send_mail(
                investor_email_subject, 
                investor_nfc_and_email_msg,
                form_email,
                [email],
                fail_silently=False, 
                html_message=investor_nfc_and_email_msg, 
            )  
            messages.success(request, "User Created Successfully and all information send to at the user email")
            return redirect("investor:add_user")
        
    role = Role.objects.all()
    context = {
        'role_list':role
    }
    return render(request, "dashboard/add_user.html",context)

def active_user(request,id):
    user = Editor.objects.get(id=id)
    if request.method == "POST":
        password = request.POST['password']
        pass2 = request.POST['pass2']
        if password == pass2:
            encripted_pass = hashlib.md5(password.encode())
            password = encripted_pass.hexdigest()
            user.password = password
            user.status = True
            user.save()
            messages.success(request,"Password setup and now you can login")
            return redirect("investor:user_login") 
        else:
            messages.error(request,"Password doesn't matched")
            return redirect("investor:active_user", id)  
    return render(request, "account/user_active_account.html")

def user_login(request):
    try:
        if request.method == 'POST':
            user_email     = request.POST['username'].lower()
            user_password  = request.POST['password']  
            enc_pass = hashlib.md5(user_password.encode())
            user_pass = enc_pass.hexdigest()

            if request.user.is_authenticated:
                messages.error(request ,"You already login as Admin") 
                return redirect('investor:user_login') 
            else: 
                chk_user = Editor.objects.filter(Q(username = user_email, password = user_pass) | Q(email = user_email, password = user_pass)).first()
                if chk_user:
                    if chk_user.status:

                        if request.session['investor']:
                            request.session['investor'] = None

                        request.session['editor'] = chk_user.id 
                        return redirect('investor:dashboard') 
                    else:  
                        messages.error(request ,"Your Account is Not activated") 
                        return render(request, "account/eiditor_login.html")
                else:     
                    messages.error(request ,"Username or Password is incorrect") 
                    return render(request, "account/eiditor_login.html")
        else:        
            return render(request, "account/eiditor_login.html")
    except:
        return redirect("investor:user_login")  
  
def user_logout(request):
    request.session['investor'] = None
    return redirect('investor:user_login')
    
def user_list(request):
    editors = Editor.objects.all()
    context = {
        'editor':editors
    }
    return render(request, 'dashboard/user_list.html',context)

def user_delete(request,id):
    editor = Editor.objects.get(id=id)
    editor.delete() 
    messages.success(request, "User Deleted Sucessfully ")
    return redirect('investor:user_list')

def edit_user(request,id):
    editor = Editor.objects.get(id=id) 
    if request.method == "POST":
        username = request.POST['username']
        full_name = request.POST['full_name']
        email = request.POST['email']
        role = int(request.POST['role'])
        editor.username = username
        editor.full_name = full_name
        editor.email = email
        editor.role_id = role
        editor.save()
        messages.success(request, "User Updated Successfully")
    role = Role.objects.all() 
    context = {
        'role_list':role,
        'editor':editor, 
    }
    return render(request, "dashboard/edit_user.html",context)


def user_password_resets(request):
    if request.method == 'POST':
        email = request.POST['email']
        email_check = Editor.objects.filter(email = email) 
        if email_check.exists(): 
            email_check = email_check.first()
            email_subject = "PFA User Password reset"
            active_link = host+"investor/user-password/{}/reset".format(email_check.id)
            nfc_and_email_msg = """
                <p><strong>Hello {},</strong> <br> 
                Click the following link to reset your password <br>
                <a target="_blank" href="{}">{}</a> 
            """ .format(email_check.full_name,active_link,active_link)
            form_email = admin_email
            send_mail(
                email_subject, 
                nfc_and_email_msg,
                form_email,
                [email],
                fail_silently=False, 
                html_message=nfc_and_email_msg, 
            ) 
            messages.success(request, "Password reset link sent to your email, check you email")

        else:
            messages.error(request, "Email address not found")
    return render(request, 'account/user_password_resets.html')

def user_password_reset_link(request, id):
    user = Editor.objects.get(id=id)
    if request.method == 'POST':
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']
        if pass1 == pass2:
            encripted_pass = hashlib.md5(pass1.encode())
            new_pass = encripted_pass.hexdigest()
            user.password = new_pass
            user.save()
            messages.error(request,"Password changed successfully")
            return redirect('investor:user_login')
        else:
            messages.error(request,"Password doesn't matched")
    return render(request, 'account/user_password_reset_link.html')

def role_list(request):
    role_list = Role.objects.all()
    context = {
        'role_list':role_list
    }
    return render(request,'dashboard/role_list.html', context)

def add_role(request):
    access = Access.objects.all()
    if request.method == "POST":
        role_name = request.POST['role_name'] 
        access_ids = request.POST.getlist('access[]') 
        role = Role.objects.create(role_name=role_name)
        for id in access_ids:
            single_access = Access.objects.get(id=id)
            role.access.add(single_access)
        
        messages.success(request,"Role Added Successfully")

    context = {
        'access_list':access, 
    }
    return render(request,'dashboard/add_role.html', context)






def edit_role(request,id):
    access_list = Access.objects.all() 
    user_role = Role.objects.get(id=id) 
    if request.method == "POST":
        role_name = request.POST['role_name'] 
        # access_ids = request.POST.getlist('access[]')  
        user_role.role_name = role_name
        

        access_ids = [int(i) for i in request.POST.getlist("access[]")] 
        if len(access_ids) > 0:
            user_role.access.remove(*user_role.access.all())
            user_role.access.add(*access_ids)  
            messages.success(request,"Role Updated Successfully")
            user_role.save() 
            return redirect("investor:role_list")

    context = {
        'access_list':access_list,
        'role':user_role
    }
    return render(request,'dashboard/edit_role.html', context)
