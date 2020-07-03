from django import forms
from.models import Popup,Termscondition

class PopupForm(forms.ModelForm):
    class Meta:
        model =  Popup
        fields = '__all__'

class TermsconditionForm(forms.ModelForm):
    class Meta:
        model =  Termscondition
        fields = ('page_title','page_content')
