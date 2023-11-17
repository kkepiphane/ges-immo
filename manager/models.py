from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
import re

# Create your models here.
class ImmoRole(models.Model):
    name = models.CharField(max_length=200)
    slug = models.CharField(max_length=200)
    description = models.CharField(max_length=200, null=True, blank=True)
    date_create = models.DateTimeField(auto_now_add=True, null=True)
    
    def description_(self):
        des = re.sub('<[^<]+?>', ' ', self.description)
        des2 = re.sub('&nbsp;', ' ', des)
        return re.sub('&amp;', ' ', des2)
    
    def __str__(self):
        return self.name
    
class ImmoUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    date_create = models.DateTimeField(auto_now_add=True, null=True)
    id_file_path = models.FileField(upload_to="document")
    role = models.ForeignKey(
        ImmoRole, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.user.first_name +  ' ' + self.user.last_name

class BuildingType(models.Model):
    name = models.CharField(max_length=200)
    slug = models.CharField(max_length=200)
    description = models.CharField(max_length=200, null=True, blank=True)
    date_create = models.DateTimeField(auto_now_add=True, null=True)
    
    def description_(self):
        des = re.sub('<[^<]+?>', ' ', self.description)
        des2 = re.sub('&nbsp;', ' ', des)
        return re.sub('&amp;', ' ', des2)

    def __str__(self):
        return self.name

class Building(models.Model):
    name = models.CharField(max_length=200)
    slug = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    description = models.TextField()
    date_create = models.DateTimeField(auto_now_add=True, null=True)
    contract_file_path = models.FileField(upload_to="contrat")
    building_type = models.ForeignKey(
        BuildingType, on_delete=models.SET_NULL, null=True, blank=True)
    landlord = models.ForeignKey(
        ImmoUser, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name +  ' ' + self.address

    def iLandlord(self):
        return self.landlord
    
    def description_(self):
        des = re.sub('<[^<]+?>', ' ', self.description)
        des2 = re.sub('&nbsp;', ' ', des)
        return re.sub('&amp;', ' ', des2)

class Appartment(models.Model):
    name = models.CharField(max_length=200)
    slug = models.CharField(max_length=200)
    price = models.DecimalField( 
                         max_digits = 10, 
                         decimal_places = 1) 
    bail = models.DecimalField( 
                         max_digits = 10, 
                         decimal_places = 1) 
    address = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField()
    bail_required =  models.BooleanField(default=True)
    status = models.CharField(max_length=200, null=True) 
    date_create = models.DateTimeField(auto_now_add=True, null=True)
    building = models.ForeignKey(
        Building, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name +  ' (' + self.building.name + ', ' + self.address + ')'
    
    def iBuilding(self):
        return self.building.iLandlord()
    
    def description_(self):
        des = re.sub('<[^<]+?>', ' ', self.description)
        des2 = re.sub('&nbsp;', ' ', des)
        return re.sub('&amp;', ' ', des2)
        

class AppPic(models.Model):
    image_fil = models.FileField(upload_to="images")
    appartment = models.ForeignKey(
        Appartment, on_delete=models.SET_NULL, null=True, blank=True)
    

    
    def image_url(self):
        try:
            url = self.image_fil.url
        except:
            url = ''
        return url
    
class Contract(models.Model):
    code = models.CharField(max_length=200)
    date_begin =  models.DateTimeField()
    date_end =  models.DateTimeField()
    date_create = models.DateTimeField(auto_now_add=True, null=True)
    contract_file_path = models.FileField(upload_to="contrat")
    tenant = models.ForeignKey(
        ImmoUser, on_delete=models.SET_NULL, null=True, blank=True)
    appartment = models.ForeignKey(
        Appartment, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.code

    def duration(self):
        date_format = "%m/%d/%Y"
        # a = datetime.strptime(str(self.date_begin.date()), date_format)
        # b = datetime.strptime(str(self.date_end.date.date), date_format)
        delta = self.date_end.date() - self.date_begin.date()
        return round(delta.days/365)
    
    def iAppartment(self):
        return self.appartment.iBuilding()
    
class Bill(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateTimeField()  
    paid = models.BooleanField(default=False)   
    date_create = models.DateTimeField(auto_now_add=True, null=True)
    contract = models.ForeignKey(
        Contract, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title
    
    def iContract(self):
        return self.contract.iAppartment()
    
    def description_(self):
        des = re.sub('<[^<]+?>', ' ', self.description)
        des2 = re.sub('&nbsp;', ' ', des)
        return re.sub('&amp;', ' ', des2)
    
class Payment(models.Model):
    code = models.CharField(max_length=200)
    payment_type = models.IntegerField(default=False)   
    description = models.CharField(max_length=200, null=True)  
    status = models.IntegerField()  
    pay_method = models.CharField(max_length=200, null=True)
    date_create = models.DateTimeField(auto_now_add=True, null=True)
    bill = models.ForeignKey(
        Bill, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return self.code + ' ' + self.description

    def iBill(self):
        return self.bill.iContract()
    
    def description_(self):
        des = re.sub('<[^<]+?>', ' ', self.description)
        des2 = re.sub('&nbsp;', ' ', des)
        return re.sub('&amp;', ' ', des2)
    
class Retrait(models.Model):
    code = models.CharField(max_length=200)
    montant = models.DecimalField(max_digits=10, decimal_places=2) 
    description = models.CharField(max_length=200, null=True)  
    status = models.CharField(max_length=200) 
    date_create = models.DateTimeField(auto_now_add=True, null=True)
    landlord = models.ForeignKey(
        ImmoUser, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return self.code + ' ' + self.description
    
    def description_(self):
        des = re.sub('<[^<]+?>', ' ', self.description)
        des2 = re.sub('&nbsp;', ' ', des)
        return re.sub('&amp;', ' ', des2)

class Demand(models.Model):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=200)
    note = models.CharField(max_length=200, null=True, blank=True)
    status = models.CharField(max_length=200, default="encours")  
    date_create = models.DateTimeField(auto_now_add=True, null=True)
    appartment = models.ForeignKey(
        Appartment, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return self.code
