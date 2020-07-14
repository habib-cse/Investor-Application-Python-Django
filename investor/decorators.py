from investor.models import Investor
from django.shortcuts import redirect
from django.contrib import messages

def investor_login_required(view_func):
    def wrapper_func(request, *args, **kwargs):
        try:
            if request.session['investor']: 
                return view_func(request, *args, **kwargs)
            else:
                messages.warning(request, "You must be login before view the page")
                return redirect('investor:investor_login')
        except:
            return redirect('investor:investor_login')
        
    return wrapper_func

def investor_or_admin_login_required(view_func):
    def wrapper_func(request, *args, **kwargs):
        try:
            if request.session['investor'] or request.user.is_authenticated: 
                return view_func(request, *args, **kwargs)
            else:
                messages.warning(request, "You must be login before view the page")
                return redirect('investor:investor_login')
        except:
            return redirect('investor:investor_login')
        
    return wrapper_func


def editor_admin_login_required(view_func):
    def wrapper_func(request, *args, **kwargs):
        try:
            if request.user.is_authenticated or request.session['editor'] : 
                return view_func(request, *args, **kwargs)
            else:
                messages.warning(request, "You must be login before view the page")
                return redirect('investor:admin_login')
        except:
            return redirect('investor:admin_login')
        
    return wrapper_func

