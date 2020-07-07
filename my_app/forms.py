from django import forms
from .models import Personal_information, Appointment


class Createform(forms.ModelForm):

    class Meta:
        model= Personal_information
        fields= ['id','name','age',
                 'sex','weight','height','bmi','children','smoker','region','charges','telephone_no','email']

class Create_appoint_form(forms.ModelForm):

    class Meta:
        model= Appointment
        fields= ['id','amka','weight','bmi','dose','date_time']

