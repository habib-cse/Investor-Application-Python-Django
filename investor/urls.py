from django.urls import path 
from . import views
app_name = 'investor'
urlpatterns = [
    path('investor/admin/login', views.admin_login, name="admin_login"),
    path('investor/admin/logout', views.admin_logout, name="admin_logout"),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('investor/signup',views.investor_registration, name='investor_registration'),
    path('investor/login',views.investor_login, name='investor_login'),
    path('investor/logout',views.investor_logout, name='investor_logout'),
    path('investor/request_to_invest/<int:id>/',views.request_to_invest, name='request_to_invest'),
    path('admin/approve/<int:id>/',views.approve_investment, name='approve_investment'),
    path('admin/notifications/',views.admin_notification_list, name='admin_notification_list'),
    path('investor/notification/<int:id>/',views.single_nofication, name='single_nofication'),

]
