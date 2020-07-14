from django import forms
from.models import Popup,Termscondition, Editor
from django.contrib.auth.models import User

class PopupForm(forms.ModelForm):
    class Meta:
        model =  Popup
        fields = '__all__'

class TermsconditionForm(forms.ModelForm):
    class Meta:
        model =  Termscondition
        fields = ('page_title','page_content')

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'

class EditorForm(forms.ModelForm):
    class Meta:
        model = Editor
        fields = '__all__'