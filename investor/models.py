from django.db import models 
class Bank(models.Model):
    bank_name = models.CharField(max_length=50)
    status = models.BooleanField(default=True)

    class Meta: 
        verbose_name = 'Bank'
        verbose_name_plural = 'Banks'

    def __str__(self):
        return self.bank_name


# Create your models here.
class Investor(models.Model):
    username = models.CharField(max_length=150)
    password = models.CharField(max_length=100)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email= models.EmailField(max_length=254)
    phone = models.CharField(max_length=13)
    address = models.TextField()
    bank_name = models.ForeignKey(Bank, on_delete=models.CASCADE)
    account_number = models.BigIntegerField()
    agree_to_invest = models.BooleanField(default=True) 
    status = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Investor"
        verbose_name_plural = "Investors"

    def __str__(self):
        return("{} {}".format(self.first_name, self.last_name))
        

class Invest(models.Model):
    investor = models.ForeignKey(Investor, on_delete=models.CASCADE)
    amount_to_invest = models.BigIntegerField() 
    expected_interest = models.BigIntegerField()
    date_of_invest = models.DateTimeField()
    withdraw_date = models.DateTimeField(auto_now_add=False)
    payment_status = models.BooleanField(default=False)
    status = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    

    class Meta:
        verbose_name = "Invest"
        verbose_name_plural ="Invests"

    def __str__(self):
        return("{} {} = {}".format(self.investor.first_name, self.investor.last_name, self.amount_to_invest))
        
class Notification(models.Model): 
    investor = models.ForeignKey(Investor, on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    desc = models.TextField()
    is_view = models.BooleanField(default=False)
    status = models.BooleanField(default=True)
    for_admin = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    has_download = models.BooleanField(default=False)
    class Meta: 
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'

    def __str__(self):
        return self.title

class Attachment(models.Model):
    file = models.FileField(upload_to='message')

    def __str__(self):
        return self.file.name    

class Message(models.Model):
    message = models.TextField()
    investor = models.ForeignKey(Investor, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)
    is_view_admin = models.BooleanField(default=False)
    is_view_investor = models.BooleanField(default=False)
    status = models.BooleanField(default=True)
    date_time = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return self.message
    
    
