from django import template
register = template.Library()  
from investor.models import Bank,Investor,Invest,Notification, Message,Popup,Editor,Access,Role
from datetime import datetime


# For Admin Dashboard
@register.filter
def total_investor(self):
    total_invest = Investor.objects.filter(status=True).count()
    return("{:,}".format(total_invest))

@register.filter
def total_interest_paid_admin(self): 
    total_invest = Invest.objects.filter(payment_status=True)
    total_amout = 0
    for item in total_invest:
        total_amout += item.expected_interest
    return("{:,}".format(total_amout))
 

@register.filter
def total_amount_invested_admin(self): 
    total_investors = Invest.objects.all()
    total_amout = 0
    for item in total_investors:
        total_amout += item.amount_to_invest
    return("{:,}".format(total_amout))


@register.filter
def active_invested_amount_admin(self):
    invests = Invest.objects.filter(status=True, payment_status=False,reinvest_status=False, delete_status=False)
    total_invest = 0
    if invests.exists():
        for invest in invests:
            total_invest += invest.amount_to_invest 
    return("{:,}".format(total_invest)) 

@register.filter
def total_interest_topay_admin(self):
    invests = Invest.objects.filter(status=True, payment_status=False,reinvest_status=False, delete_status=False)
    total_invest = 0
    if invests.exists():
        for invest in invests:
            total_invest += invest.expected_interest
        
    return("{:,}".format(total_invest)) 

@register.filter
def pending_amount_admin(self):
    invests = Invest.objects.filter(status=False, payment_status=False)
    total_invest = 0
    if invests.exists():
        for invest in invests:
            total_invest += invest.amount_to_invest
        
    return("{:,}".format(total_invest)) 


@register.filter
def pending_approval_admin(self):
    invests = Invest.objects.filter(status=False, payment_status=False).order_by('-timestamp')[0:10]
    if invests:
        return invests




# For Investor Dashboard
@register.filter
def total_invest_amount(id):
    invests = Invest.objects.filter(investor_id = id)
    total_invest = 0
    if invests.exists():
        for invest in invests:
            total_invest += invest.amount_to_invest
    return ("{:,}".format(total_invest))  

@register.filter
def total_interest_amount(id):
    invests = Invest.objects.filter(investor_id = id,payment_status=True)
    total_invest = 0
    if invests.exists():
        for invest in invests:
            total_invest += invest.expected_interest 
    return("{:,}".format(total_invest)) 

@register.filter
def active_invested_amount(id):
    invests = Invest.objects.filter(investor_id = id,status=True, payment_status=False,reinvest_status=False, delete_status=False)
    total_invest = 0
    if invests.exists():
        for invest in invests:
            total_invest += invest.amount_to_invest 
    return("{:,}".format(total_invest)) 

@register.filter
def upcoming_interest_amount(id):
    invests = Invest.objects.filter(investor_id = id,status=True,payment_status=False,reinvest_status=False, delete_status=False)
    total_invest = 0
    if invests.exists():
        for invest in invests:
            total_invest += invest.expected_interest
        
    return("{:,}".format(total_invest)) 


# @register.filter
# def upcoming_interest_amount(id):
#     invests = Invest.objects.filter(investor_id = id, status=True,payment_status=False) 
#     total_invest = 0
#     if invests.exists():
#         for invest in invests: 
#             total_invest += invest.expected_interest
        
#     return("{:,}".format(total_invest)) 

 
@register.filter
def next_payment_amount(id):
    invests = Invest.objects.filter(investor_id = id,status=True,reinvest_status=False, delete_status=False).order_by('withdraw_date').first()
    total_invest = 0
    if invests:
        total_invest = invests.expected_interest 
        
    return("{:,}".format(total_invest)) 

@register.filter
def days_left(id):
    invests = Invest.objects.filter(investor_id = id,status=True).order_by('withdraw_date').first()
    if invests:
        remaing_day = datetime.date(invests.withdraw_date) - datetime.now().date()
        remaing_day = remaing_day.days
        return remaing_day  


@register.filter
def days_remaining(id):
    invests = Invest.objects.get(id=id)
    remaing_day = datetime.date(invests.withdraw_date) - datetime.now().date()
    remaing_day = remaing_day.days  
    return remaing_day  


@register.filter
def pending_approval(id): 
    invests = Invest.objects.filter(investor_id = id, status=False, payment_status=False)
    pending_amount = 0
    for item in invests:
        pending_amount += item.amount_to_invest
    return("{:,}".format(pending_amount)) 

@register.filter
def active_invest_list(id):
    invest_list = Invest.objects.filter(investor_id = id, status=True, payment_status=False,reinvest_status=False, delete_status=False).order_by('withdraw_date')[0:10]
    return invest_list

@register.filter
def pending_invest_list(id):
    pending_invest_list = Invest.objects.filter(investor_id=id, status=False, payment_status=False).order_by('-date_of_invest')[0:10]
    return pending_invest_list

@register.filter
def coma_separator_value(value):
    return("{:,}".format(value))


@register.filter
def investor_notifications(id):
    notications = Notification.objects.filter(investor_id=id, is_view=False, for_admin=False).count()
    if notications > 0:
        return notications
    else:
        return ""

@register.filter
def investor_notification_list(id):
    notication_list = Notification.objects.filter(investor_id=id, is_view=False, for_admin=False).order_by('-date')[0:10]
    if notication_list:
        return notication_list



@register.filter
def admin_notifications(self):
    notications = Notification.objects.filter(is_view=False, for_admin=True).count()
    if notications:
        return notications
    else:
        return ""

@register.filter
def admin_notification_list(self):
    notication_list = Notification.objects.filter(is_view=False, for_admin=True).order_by('-date')[0:7]

    if notication_list:
        return notication_list

 
@register.filter
def top_investor_list(self):
    investor_list = Investor.objects.filter(status=True)
    invest_list = Invest.objects.all().order_by('investor')
    dict = {}  
    for investor in investor_list: 
        total_value = 0
        for invest in invest_list:
            if investor.id ==  invest.investor.id:
                total_value += invest.amount_to_invest
        full_name = "{} {}".format(investor.first_name, investor.last_name)
        dict[full_name]= total_value  
        

    sort_orders = sorted(dict.items(), key=lambda x: x[1], reverse=True)[0:10] 
    return sort_orders

@register.filter
def top_investor_name(item):
    return item[0]

@register.filter
def top_investor_amount(item):
    total_amount =  item[1]
    return("{:,}".format(total_amount))


@register.filter
def investor_invest_amount(id):
    amount = 0
    investor = Invest.objects.filter(investor_id=id)
    for item in investor:
        amount += item.amount_to_invest


    return("{:,}".format(amount))


@register.filter
def active_invested_list(self): 
    investor = Invest.objects.filter(status=True, payment_status=False,reinvest_status=False).order_by('withdraw_date')[0:20]
    return investor 

@register.filter
def show_unread_message(id): 
    unread_messages = Message.objects.filter(status=True,investor_id = id, is_view_admin=False).count()
    if unread_messages:
        return unread_messages


@register.filter
def show_unread_admin_message(id): 
    unread_messages = Message.objects.filter(status=True, is_view_admin=False).count()
    if unread_messages:
        return unread_messages


@register.filter
def show_unread_investor_message(id): 
    unread_messages = Message.objects.filter(investor_id = id,is_view_investor=False,is_admin=True).count()
    if unread_messages:
        return unread_messages



@register.filter
def active_popup_list(request):
    popup_list = Popup.objects.filter(status=True).order_by('-timestamp') 
    return popup_list


@register.filter
def user_has_access(id,access_name):
    user_access = Editor.objects.filter(id=id, role__access__has_access=access_name)
    if user_access.exists():
        return True
    else:
        return False

@register.filter  
def check_access(access_id,role): 
    check_access = Access.objects.get(id = access_id)
    role_access = Role.objects.filter(access = check_access,id=role.id)
    if role_access.exists():
        return True
    else:
        return False
