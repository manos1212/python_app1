from django.db import models
from django.core.validators import MaxValueValidator
from django import forms


class Personal_information(models.Model):
    # Smoker_choices = (
    #     ('yes', 'yes'),
    #     ('no', 'no'),)
    id = models.BigIntegerField(primary_key=True)
    name=models.CharField(max_length=30)
    age = models.IntegerField()
    sex = models.CharField(max_length=100)
    weight = models.FloatField()
    height = models.FloatField()
    bmi = models.FloatField()
    children = models.IntegerField()
    smoker = models.CharField(max_length=3) #, choices=Smoker_choices
    region = models.CharField(max_length=100)
    charges = models.DecimalField(max_digits=20, decimal_places=2)
    telephone_no = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)


    def __str__(self):
        return '{}'.format(self.age)

    class Meta:
        verbose_name_plural = 'personal_information'


class Appointment (models.Model):
    id = models.AutoField(primary_key=True)
    amka = models.ForeignKey(Personal_information,on_delete=models.PROTECT)
    weight = models.FloatField()
    bmi = models.FloatField()
    dose = models.FloatField()
    date_time = models.DateTimeField()

    def __str__(self):
        return '{}'.format(self.dose)

    class Meta:
        verbose_name_plural = 'appointment'