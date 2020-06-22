from django import template
register = template.Library()  
from investor.models import Bank,Investor,Invest,Notification
from datetime import datetime


# For Admin Dashboard
@register.filter
def total_investor(self):
    total_invest = Investor.objects.all().count()
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
    invests = Invest.objects.filter(status=True, payment_status=False)
    total_invest = 0
    if invests.exists():
        for invest in invests:
            total_invest += invest.amount_to_invest 
    return("{:,}".format(total_invest)) 

@register.filter
def total_interest_topay_admin(self):
    invests = Invest.objects.filter(status=True, payment_status=False)
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
    invests = Invest.objects.filter(investor_id = id,status=True, payment_status=False)
    total_invest = 0
    if invests.exists():
        for invest in invests:
            total_invest += invest.amount_to_invest 
    return("{:,}".format(total_invest)) 

@register.filter
def upcoming_interest_amount(id):
    invests = Invest.objects.filter(investor_id = id,status=True,payment_status=False)
    total_invest = 0
    if invests.exists():
        for invest in invests:
            total_invest += invest.expected_interest
        
    return("{:,}".format(total_invest)) 


@register.filter
def upcoming_interest_amount(id):
    invests = Invest.objects.filter(investor_id = id, status=True,payment_status=False) 
    total_invest = 0
    if invests.exists():
        for invest in invests: 
            total_invest += invest.expected_interest
        
    return("{:,}".format(total_invest)) 

 
@register.filter
def next_payment_amount(id):
    invests = Invest.objects.filter(investor_id = id,status=True).order_by('withdraw_date').first()
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
    invest_list = Invest.objects.filter(investor_id=id, status=True, payment_status=False).order_by('withdraw_date')[0:10]
    return invest_list

@register.filter
def pending_invest_list(id):
    pending_invest_list = Invest.objects.filter(investor_id=id, status=False, payment_status=False).order_by('-date_of_invest')
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
