from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, SetPasswordForm, PasswordResetForm
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth import get_user_model

class ImmoUserForm(forms.Form):
    last_name = forms.CharField(max_length=100)
    first_name = forms.CharField(max_length=100)
    address = forms.CharField(max_length=100)
    email = forms.EmailField()
    phone = forms.CharField(max_length=100)
    id_file = forms.FileField(required=False)

class ImmoUserLandlordForm(forms.Form):
    last_name = forms.CharField(max_length=100)
    first_name = forms.CharField(max_length=100)
    address = forms.CharField(max_length=100)
    email = forms.EmailField()
    phone = forms.CharField(max_length=100)
    id_file = forms.FileField()
    contract_file = forms.FileField()
    building_name = forms.CharField(max_length=100)
    building_type = forms.CharField(max_length=100)
    building_address = forms.CharField(max_length=100)
    building_description = forms.CharField(widget=forms.Textarea)

class ImmoUserTenantForm(forms.Form):
    last_name = forms.CharField(max_length=100)
    first_name = forms.CharField(max_length=100)
    address = forms.CharField(max_length=100)
    email = forms.EmailField()
    phone = forms.CharField(max_length=100)
    id_file = forms.FileField()
    contract_file = forms.FileField()
    appartment = forms.CharField(max_length=100)
    date_begin = forms.CharField(max_length=100)
    date_end = forms.CharField(max_length=100)
    avance = forms.DecimalField()


class BuildingForm(forms.Form):
    building_name = forms.CharField(max_length=100)
    building_type = forms.CharField(max_length=100)
    building_address = forms.CharField(max_length=100)
    building_description = forms.CharField(widget=forms.Textarea)
    contract_file = forms.FileField(required=False)
    landlord = forms.CharField(max_length=100, required=False)

class AppartmentForm(forms.Form):
    appartment_name = forms.CharField(max_length=100)
    appartment_price = forms.DecimalField(max_digits=10, decimal_places=2)
    appartment_bail = forms.DecimalField()
    appartment_address = forms.CharField(max_length=100)
    appartment_description = forms.CharField(widget=forms.Textarea)
    building = forms.CharField(max_length=100, required=False)

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result
    
class ImageForm(forms.Form):
    image_fil = MultipleFileField()

class ContractForm(forms.Form):
    date_begin = forms.DateTimeField()
    date_end = forms.DateTimeField()
    contract_file = forms.FileField(required=False)

class AuthForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(max_length=100)

class RetraitFrom(forms.Form):
    code = forms.CharField(max_length=100)
    montant = forms.CharField(max_length=100)
    description = forms.CharField(max_length=100)

class UpdateProfileForm(forms.Form):
    last_name = forms.CharField(max_length=100)
    first_name = forms.CharField(max_length=100)
    
class SetPasswordForm(SetPasswordForm):
    old_password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', }))
    new_password1 = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', }))
    new_password2 = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', }))
    class Meta:
        model = get_user_model()
        fields = ['new_password1', 'new_password2']

class PasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(PasswordResetForm, self).__init__(*args, **kwargs)