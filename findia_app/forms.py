from django import forms
from .models import Movement
from django.forms import ModelForm
from .models import Credit

class MovementForm(forms.ModelForm):
    class Meta:
        model = Movement
        fields = ('type', 'value', 'description')


class CreditForm(ModelForm):
    class Meta:
        model = Credit
        fields = ['principal', 'interest_rate', 'term']
