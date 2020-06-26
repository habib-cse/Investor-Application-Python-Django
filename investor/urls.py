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
    path('admin/cancle/<int:id>/',views.cancle_investment, name='cancle_investment'),
    path('admin/notifications/',views.admin_notification_list, name='admin_notification_list'),
    path('admin/notifications/unread',views.admin_unread_notifications, name='admin_unread_notifications'),
    path('admin/notifications/<int:id>/',views.investor_notification_list, name='investor_notification_list'),
    path('admin/notifications/unread/<int:id>/',views.investor_unread_notification_list, name='investor_unread_notification_list'),
    path('investor/notification/<int:id>/',views.single_nofication, name='single_nofication'),
    path('investor/notification/delete',views.ajax_notification_delete, name='ajax_notification_delete'),
    path('investor/notification/mark-read',views.ajax_notification_markas_read, name='ajax_notification_markas_read'),
    path('investor/<int:id>/terms-condition-pdf',views.terms_condition_pdf, name='terms_condition_pdf'),
    path('investor/investors-list',views.all_investor_list, name='all_investor_list'),
    path('investor/investor/<int:id>/delete',views.investor_delete, name='investor_delete'),
    path('investor/all_pending_request',views.all_pending_request, name='all_pending_request'),
    path('investor/all_active_invest_list',views.all_active_invest_list, name='all_active_invest_list'),
    path('investor/admin-chat/<int:id>',views.admin_chat, name='admin_chat'),
    path('investor/investor-chat/<int:id>',views.investor_chat, name='investor_chat'),
    path('investor/make-payment/<int:id>',views.make_payment, name='make_payment'),
    path('investor/interest-paid-admin',views.interest_paid_admin, name='interest_paid_admin'),
    path('investor/interest-paid/<int:id>/delete',views.interest_paid_admin_delete, name='interest_paid_admin_delete'),

]
