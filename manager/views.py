from django.shortcuts import render, redirect
from manager.forms import *
from django.contrib.auth.models import User
from .models import *
import os
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from decimal import Decimal
from datetime import datetime, timedelta
from django.contrib import messages
from django.shortcuts import redirect
from dateutil.relativedelta import relativedelta
from manager.serializers import *
from django.core.mail import BadHeaderError, send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


# Create your views here.
# Function for design web site

# User views
def signin(request):
    return render(request, 'components/auth/signin.html')

def loginUser(request):
    if request.method == 'POST':
        form = AuthForm(request.POST)

        if form.is_valid():
            username = request.POST.get('username', None)
            password = request.POST.get('password', None)

            user = User.objects.filter(username=username).first()

            if user:
                auth_user = authenticate(username=user.username, password=password)

                if auth_user:
                    login(request, auth_user)
                    return redirect('home')
                else:
                    return redirect('signin')
            else:
                print('Error')
    return render(request, 'components/auth/signin.html')          

def custom_logout(request):
    logout(request)
    return redirect('/')

@login_required(login_url='login') 
def password_change(request):
    user = request.user
    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your password has been changed")
            return redirect('login')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

    form = SetPasswordForm(user)
    return render(request, 'components/auth/change_password.html', {'form': form})


@login_required(login_url='/login')
def home(request):
    auth_user = request.user
    context = {}

    if auth_user.is_staff:
        building_count = []
        landlord_count = []
        tenant_count = []
        appartment_count = []
        ask_count = []
        
        building_count = Building.objects.all().count()
        appartment_count = Appartment.objects.all().count()
        ask_count = Demand.objects.all().count()
        immo_role = ImmoRole.objects.get(slug='landlord')
        landlord_count = ImmoUser.objects.select_related('user').filter(role=immo_role).count()
        immo_role = ImmoRole.objects.get(slug='tenant')
        tenant_count = ImmoUser.objects.select_related('user').filter(role=immo_role).count()
        payments = Payment.objects.filter(payment_type=2)
        retrait = Retrait.objects.filter(status="valide")
        sum_retrait = 0
        wallet = 0

        for p in payments:
            wallet = wallet + (p.bill.contract.appartment.price*10)/100

        for ret in retrait:
                    sum_retrait = sum_retrait + ret.montant

        total_wallet = float(wallet) - float(sum_retrait)   
        context = {
            'landlord_count' : landlord_count,
            'tenant_count': tenant_count,
            'building_count': building_count,
            'appartment_count': appartment_count,
            'ask_count' : ask_count,
            'wallet': total_wallet
        }
    else:
        immo_user = ImmoUser.objects.get(user=auth_user)
        immo_role = ImmoRole.objects.get(slug='landlord')
        
        if immo_user.role == immo_role:
            building_count = 0
            tenant_count = 0
            appartment_count = 0

            building_count = Building.objects.filter(landlord=immo_user).count()
            temp_contracts = Contract.objects.all()
            temp_appartments = Appartment.objects.all()
            payments = Payment.objects.filter(payment_type=1)
            retrait = Retrait.objects.filter(status="valide", landlord=immo_user)
            sum_retrait = 0
            wallet = 0

            for contr in temp_contracts:
                if contr.appartment.building.landlord == immo_user:                    
                    tenant_count = tenant_count + 1  

            for app in temp_appartments:
                if app.building.landlord == immo_user:
                    appartment_count = appartment_count + 1
            
            for pay in payments:
                if pay.bill.contract.appartment.building.landlord == immo_user:
                    wallet = wallet + pay.bill.contract.appartment.price - (pay.bill.contract.appartment.price*10)/100
                    
            for ret in retrait:
                if ret.landlord == immo_user:
                    sum_retrait = sum_retrait + ret.montant

            # total_wallet = wallet - sum_retrait
            total_wallet = float(wallet) - float(sum_retrait) 
            context = {
                'tenant_count': tenant_count,
                'building_count': building_count,
                'appartment_count': appartment_count,
                'wallet': total_wallet
            }
        else:
            temp_contract = Contract.objects.get(tenant=immo_user)
            
            context = {
                'appartment': temp_contract.appartment,
            }

    return render(request, 'index.html',context)

def walletLandlord(request):
    immo_role = ImmoRole.objects.get(slug='landlord')
    immo_user = ImmoUser.objects.select_related('user', '').filter(role=immo_role)
    payments = Payment.objects.filter(payment_type=1)
    sum_retrait = 0
    wallet = 0

    building = Appartment.objects.all()
    
    for pay in payments:
        wallet = wallet + pay.bill.contract.appartment.price - (pay.bill.contract.appartment.price*10)/100
        

    total_wallet = wallet - sum_retrait
    context = {
        'wallets': building
        
    }
    return render(request, 'components/landlord/walletland.html',context)

@login_required(login_url='/login')
def getLandlords(request):
    immo_role = ImmoRole.objects.get(slug='landlord')

    landlords = ImmoUser.objects.select_related('user').filter(role=immo_role)

    context = {
        'landlords' : landlords
    }
    return render(request, 'components/landlord/list.html', context)

@login_required(login_url='/login')
def createLandlord(request):
    return render(request, 'components/landlord/ajouter.html')

@login_required(login_url='/login')
def addLandlord(request):
    if request.method == 'POST':
        # form = ImmoUserLandlordForm(request.POST, request.FILES)

        # if form.is_valid():
            reqP = request.POST
            reqF = request.FILES

            if reqF.get('id_file') and reqF.get('contract_file'):
                
                last_user_id = User.objects.latest('id').id
                usname=reqP.get('last_name')[:2]+reqP.get('first_name')
                
                user_add = User.objects.create_user(
                    username=usname.lower()+str(last_user_id+1),
                    email=reqP.get('email'),
                    password='password',
                    first_name=reqP.get('first_name'),
                    last_name=reqP.get('last_name'),
                    is_active=False
                )
                user_add.save()

                user_saved = User.objects.get(id=user_add.id)

                id_file_path = reqF.get('id_file')
                contract_file_path = reqF.get('contract_file')
                
                immo_role = ImmoRole.objects.get(slug="landlord")
                    
                landlord = ImmoUser(
                    user = user_saved,
                    phone_number = reqP.get('phone'),
                    address = reqP.get('address'),
                    id_file_path = id_file_path,
                    role=immo_role
                )

                landlord.save()

                landlord_saved = ImmoUser.objects.get(user=user_saved)

                building_type = BuildingType.objects.get(slug=reqP.get('building_type'))

                building = Building(
                    name = reqP.get('building_name'),
                    slug = reqP.get('building_name'),
                    address = reqP.get('building_address'),
                    description = reqP.get('building_description'),
                    contract_file_path = contract_file_path,
                    building_type=building_type,
                    landlord = landlord_saved,
                )

                building.save()
                
                htmly = get_template('components/auth/email_register.html')
                d = { 'username': user_add.username, 'first_name':user_add.first_name}
                subject, from_email, to = 'immo', 'your_email@gmail.com', user_add.email
                html_content = htmly.render(d)
                msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
                msg.attach_alternative(html_content, "text/html")
                msg.send()

                return HttpResponseRedirect('/landlords/list')
        # else:
        #     return render(request, 'components/landlord/ajouter.html', {'form': form})
    else :
        return HttpResponseRedirect('/landlords/list')

@login_required(login_url='/login')
def activateLandlordAccount(request, pk, is_active):
    if pk and is_active:
        user = User.objects.get(id=pk)
        user.is_active=is_active
        user.save()
        
    return redirect('landlordList')

@login_required(login_url='/login')
def editLandlord(request, pk):
    landlord = ImmoUser.objects.select_related('user').get(id=pk)

    context = {
        'landlord' : landlord
    }

    return render(request, 'components/landlord/edit.html', context)

@login_required(login_url='/login')
def saveLandlord(request):
    if request.method == 'POST':
    
        form = ImmoUserForm(request.POST, request.FILES)

        if form.is_valid():
            reqP = request.POST
            reqF = request.FILES
            landlord = ImmoUser.objects.get(id=reqP.get('id'))
            
            immo_role = ImmoRole.objects.get(slug='tenant')

            user = User.objects.get(id=landlord.user.id)
            user.first_name = reqP.get('first_name')
            user.last_name = reqP.get('last_name')
            user.email = reqP.get('email')
            user.save()

            if reqF.get('id_file'):
                id_file_path = reqF.get('id_file')
            else:
                id_file_path = landlord.id_file_path

            landlord.address = reqP.get('address')
            landlord.phone_number = reqP.get('phone')
            landlord.id_file_path = id_file_path
            landlord.save()

            if(immo_role.id == landlord.role.id):
                return redirect('tenantList')
            else:
                return redirect('landlordList')
    else:
        return HttpResponseRedirect('/landlords/list')       

@login_required(login_url='/login')
def getLandlordDetails(request, pk):
    landlord_user = ImmoUser.objects.select_related('user').get(id=pk)

    buildings = Building.objects.select_related('building_type').filter(landlord=landlord_user)

    context = {
        'landlord' : landlord_user,
        'buildings' : buildings
    }
    return render(request, 'components/landlord/details.html', context)


# Tenants views
@login_required(login_url='/login')
def getTenants(request):
    auth_user = request.user
    tenants = []
    immo_role = ImmoRole.objects.get(slug='tenant')

    if auth_user.is_staff: 
        tenants = ImmoUser.objects.select_related('user').filter(role=immo_role)
    else:
        # tenants = ImmoUser.objects.select_related('user').filter(role=immo_role)
        contracts = Contract.objects.all()

        for contract in contracts:
            if contract.appartment.iBuilding().user.id == auth_user.id:
                tenant = ImmoUser.objects.select_related('user').get(id=contract.tenant.id)
                print(tenant)
                tenants.append(contract.tenant)

    context = {
        'tenants' : tenants
    }
    return render(request, 'components/tenant/list.html', context)

@login_required(login_url='/login')
def createTenant(request):
    appartments = Appartment.objects.filter(status="Disponible").all()

    context = {
        'appartments': appartments
    }
    return render(request, 'components/tenant/add.html', context)

@login_required(login_url='/login')
def addTenant(request):
    if request.method == 'POST':
        form = ImmoUserTenantForm(request.POST, request.FILES)

        # if form.is_valid():
        reqP = request.POST
        reqF = request.FILES

        if reqF.get('id_file') and reqF.get('contract_file'):
            
            last_user_id = User.objects.latest('id').id
            usname=reqP.get('last_name')[:2]+reqP.get('first_name')
            user_add = User.objects.create_user(
                username=usname.lower()+str(last_user_id+1),
                email=reqP.get('email'),
                password='password',
                first_name=reqP.get('first_name'),
                last_name=reqP.get('last_name'),
                is_active=False
            )
            user_add.save()

            user_saved = User.objects.get(id=user_add.id)

            id_file_path = reqF.get('id_file')
            contract_file_path = reqF.get('contract_file')

            # os.makedirs(os.path.dirname(id_file_path), exist_ok=True)
            # os.makedirs(os.path.dirname(contract_file_path), exist_ok=True)

            # with open(id_file_path, 'wb') as destination:
            #     for chunk in reqF.get('id_file').chunks():
            #         destination.write(chunk)

            # with open(contract_file_path, 'wb') as destination:
            #     for chunk in reqF.get('contract_file').chunks():
            #         destination.write(chunk)
            
            immo_role = ImmoRole.objects.get(slug="tenant")
                
            tenant = ImmoUser(
                user = user_saved,
                phone_number = reqP.get('phone'),
                address = reqP.get('address'),
                id_file_path = id_file_path,
                role=immo_role
            )

            tenant.save()

            tenant_saved = ImmoUser.objects.get(user=user_saved)

            appartment = Appartment.objects.get(id=reqP.get('appartment'))

            contract = Contract(
                code = 'CT-T'+str(tenant.id)+'A'+str(appartment.id),
                date_begin =  reqP.get('date_begin'),
                date_end =  reqP.get('date_end'),
                contract_file_path = contract_file_path,
                tenant = tenant_saved,
                appartment = appartment
            )
            
            contract.save()
            
            # appartment.status="Disponible"
            appartment.status="Occupée"
            appartment.save()
            
            bill = Bill(
                title = 'Facture de caution',
                description = 'Facture de caution de location',
                due_date = reqP.get('date_begin'),
                paid = True,
                contract = contract
            )
            bill.save()

            payment = Payment(
                code = 'I-PAY-L'+str(bill.id),
                payment_type = 1,
                description = 'Paiement de caution',
                status = 1,
                pay_method = '---',
                bill = bill
            )
            payment.save()

            payment = Payment(
                code = 'I-PAY-I'+str(bill.id),
                payment_type = 2,
                description = 'Paiement de commission pour caution de location',
                status = 1,
                pay_method = '---',
                bill = bill
            )
            payment.save()

            for i in range(int(reqP.get('avance'))-1):
                bill = Bill(
                    title = 'Facture de loyer',
                    description = 'Facture de loyer',
                    due_date = datetime.strptime(reqP.get('date_begin'), '%Y-%m-%d').date() + relativedelta(months=1),
                    paid = True,
                    contract = contract
                )
                bill.save()           

                payment = Payment(
                    code = 'I-PAY-LL'+str(bill.id),
                    payment_type = 1,
                    description = 'Paiement de loyer',
                    status = 1,
                    pay_method = '---',
                    bill = bill
                )
                payment.save()

                payment = Payment(
                    code = 'I-PAY-LI'+str(bill.id),
                    payment_type = 2,
                    description = 'Paiement de commission pour loyer',
                    status = 1,
                    pay_method = '---',
                    bill = bill
                )
                payment.save()       
                
            htmly = get_template('components/auth/email_register.html')
            d = { 'username': user_add.username, 'first_name':user_add.first_name}
            subject, from_email, to = 'immo', 'your_email@gmail.com', user_add.email
            html_content = htmly.render(d)
            msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send() 

            return redirect('tenantList')
        # else:
        #     return render(request, 'components/tenant/add.html', {'form': form})
    else :
        return render(request, 'components/tenant/add.html')

@login_required(login_url='/login')
def activateTenantAccount(request, pk, is_active):
    if pk and is_active:
        user = User.objects.get(id=pk)
        user.is_active=is_active
        user.save()
    return redirect('tenantList')

@login_required(login_url='/login')
def getTenantDetails(request, pk):
    tenant_user = ImmoUser.objects.select_related('user').get(id=pk)

    contracts = Contract.objects.filter(tenant=tenant_user).all()

    context = {
        'tenant' : tenant_user,
        'contracts' : contracts
    }
    return render(request, 'components/tenant/details.html', context)


# Building views
@login_required(login_url='/login')
def editBuilding(request, pk):
    building = Building.objects.get(id=pk)
    
    context = {
        'building' : building
    }

    return render(request, 'components/building/edit.html', context)

@login_required(login_url='/login')
def saveBuilding(request):
    if request.method == 'POST':
    
        form = BuildingForm(request.POST, request.FILES)

        # if form.is_valid():
        reqP = request.POST
        reqF = request.FILES
        building = Building.objects.get(id=reqP.get('id'))

        if reqF.get('contract_file'):
            id_file_path = reqF.get('id_file')
            contract_file_path = reqF.get('contract_file')
        else:
            contract_file_path = building.contract_file_path

        building_type = BuildingType.objects.get(slug=reqP.get('building_type'))

        building.name = reqP.get('building_name')
        building.slug = reqP.get('building_name')
        building.building_type = building_type
        building.address = reqP.get('building_address')
        building.description = reqP.get('building_description')
        building.contract_file_path = contract_file_path
        building.save()

        return redirect('buildingDetail', pk=reqP.get('id'))
    else:
        return render(request, 'components/landlord/ajouter.html')        

@login_required(login_url='/login')
def getBuildingDetails(request, pk):
    building_saved = Building.objects.select_related('landlord').get(id=pk)

    appartments = Appartment.objects.filter(building=building_saved)

    context = {
        'building' : building_saved,
        'appartments' : appartments
    }
    return render(request, 'components/building/details.html', context)    

@login_required(login_url='/login')
def getBuildings(request):
    auth_user = request.user
    buildings = []

    if auth_user.is_staff: 
        buildings = Building.objects.all()
    else:
        immou = ImmoUser.objects.get(user=auth_user)
        temp_buildings = Building.objects.filter(landlord=immou).all()

        for building in temp_buildings:
            # if building.landlord.user == auth_user:
                buildings.append(building)

    context = {
        'buildings' : buildings
    }
    return render(request, 'components/building/list.html', context)

@login_required(login_url='/login')
def createBuilding(request, pk):
    landlord = ImmoUser.objects.get(id=pk)

    context = {
        'landlord': landlord
    }
    return render(request, 'components/building/add.html', context)

@login_required(login_url='/login')
def addBuilding(request):
    if request.method == 'POST':
        form = BuildingForm(request.POST, request.FILES)

        # if form.is_valid():
        reqP = request.POST
        reqF = request.FILES

        if reqF.get('contract_file'):
            contract_file_path = 'contracts/' + reqF.get('contract_file').name

            os.makedirs(os.path.dirname(contract_file_path), exist_ok=True)

            with open(contract_file_path, 'wb') as destination:
                for chunk in reqF.get('contract_file').chunks():
                    destination.write(chunk)
            
        landlord = ImmoUser.objects.get(id=reqP.get('landlord'))
        building_type = BuildingType.objects.get(slug=reqP.get('building_type'))

        building = Building(
            name = reqP.get('building_name'),
            building_type =  building_type,
            address =  reqP.get('building_address'),
            description =  reqP.get('building_description'),
            contract_file_path = contract_file_path,
            landlord = landlord,
        )

        building.save()

        return redirect('landlordDetail', pk=reqP.get('landlord'))
        # else:
        #     return render(request, 'components/building/add.html', {'form' : form})
        
    else :
        return render(request, 'components/building/add.html')


# Appartments views
@login_required(login_url='/login')
def getAppartments(request):
    auth_user = request.user
    appartments = []
    
    if auth_user.is_staff: 
        appartments = Appartment.objects.all()
    else:
        immou = ImmoUser.objects.get(user=auth_user)
        immo_role = ImmoRole.objects.get(slug='tenant')
        if(immou.role == immo_role):
            temp_appartments = Contract.objects.filter(tenant=immou).all()

        else:
            temp_buildings = Building.objects.filter(landlord=immou).first()
            temp_appartments = Appartment.objects.filter(building=temp_buildings).all()

        for appartment in temp_appartments:
                appartments.append(appartment)

    context = {
        'appartments' : appartments
    }
    return render(request, 'components/appartment/list.html', context)

@login_required(login_url='/login')
def editAppartment(request, pk):
    appartment = Appartment.objects.get(id=pk)
    image_fil = AppPic.objects.filter(appartment=appartment.id)

    context = {
        'appartment' : appartment,
        'image_fil' : image_fil,
    }
    return render(request, 'components/appartment/edit.html', context)

@login_required(login_url='/login')
def deleteBuilding(request, pk):
    delpic = Building.objects.get(id=pk)
    delpic.delete() 

@login_required(login_url='/login')
def saveAppartment(request):
    if request.method == 'POST':
    
        form = AppartmentForm(request.POST)

        if form.is_valid():
            reqP = request.POST
            appartment = Appartment.objects.get(id=reqP.get('id'))

            appartment.name = reqP.get('appartment_name')
            # price = ,
            appartment.price = Decimal(reqP.get('appartment_price'))
            appartment.bail = Decimal(reqP.get('appartment_bail'))
            appartment.address =  reqP.get('appartment_address')
            appartment.description =  reqP.get('appartment_description')
            appartment.save()
            
        
            return redirect('appartmentEdit', pk=reqP.get('id'))
    else:
        return render(request, 'components/appartment/add.html')

@login_required(login_url='/login')
def getAppartmentDetails(request, pk):
    appartment = Appartment.objects.select_related('building').get(id=pk)
    image_fil = AppPic.objects.filter(appartment=appartment.id)
    
    context = {
        'appartment' : appartment,
        'image_fil' : image_fil
    }
    return render(request, 'components/appartment/details.html', context)

@login_required(login_url='/login')
def createAppartment(request, pk):
    building = Building.objects.get(id=pk)

    context = {
        'building' : building
    }
    return render(request, 'components/appartment/add.html', context)

@login_required(login_url='/login')
def addAppartment(request):
    if request.method == 'POST':
        form = AppartmentForm(request.POST, request.FILES)
        form_img = ImageForm(request.POST, request.FILES)
        
        # if form.is_valid() and form_img.is_valid():
        reqP = request.POST
            
        building = Building.objects.get(id=reqP.get('building'))

        appartment = Appartment(
            name = reqP.get('appartment_name'),
            price = reqP.get('appartment_price'),
            bail = reqP.get('appartment_bail'),
            address =  reqP.get('appartment_address'),
            description =  reqP.get('appartment_description'),
            bail_required = 1,
            status="disponible",
            building = building,
        )

        appartment.save()
        
        image_fil = request.FILES.getlist('image_fil')

        for uploaded_file in image_fil:
            obj = AppPic.objects.create(
                image_fil=uploaded_file, 
                appartment=appartment
            )
            obj.save()

        return redirect('buildingDetail', pk=reqP.get('building'))
                
        # else:
        #     return render(request, 'components/appartment/add.html', {'form' : form})
        
    else :
        return HttpResponseRedirect('/appartment/list')

@login_required(login_url='/login')
def editPic(request):
    if request.method == 'POST':
    
        form_img = ImageForm(request.POST, request.FILES)
        if form_img.is_valid():
            
            reqP = request.POST
            
            apppic = AppPic.objects.get(pk=reqP.get('id'))
            
            apppic.image_fil = request.FILES.get('image_fil')
            apppic.save()
            
            
            return redirect('appartmentEdit', pk=apppic.appartment.id)
        
def addOnlyPic(request):
    if request.method == 'POST':
    
        form_img = ImageForm(request.POST, request.FILES)
        if form_img.is_valid():
            app = Appartment.objects.get(id=request.POST.get('id'))
            
            image_fil = request.FILES.getlist('image_fil')

            for uploaded_file in image_fil:
                obj = AppPic.objects.create(
                    image_fil=uploaded_file, 
                    appartment=app
                )
                obj.save()
                
            return redirect('appartmentEdit', pk=request.POST.get('id'))
 
@login_required(login_url='/login')
def deletePic(request, pk):
    delpic = AppPic.objects.get(id=pk)
    delpic.delete()  
    
    return redirect('appartmentEdit', pk=delpic.appartment.id)
# Contract views
@login_required(login_url='/login')
def editContract(request, pk):
    contract = Contract.objects.get(id=pk)

    context = {
        'contract' : contract
    }
    return render(request, 'components/contract/edit.html', context)

@login_required(login_url='/login')
def saveContract(request):
    if request.method == 'POST':
        form = ContractForm(request.POST, request.FILES)

        if form.is_valid():
            reqP = request.POST
            reqF = request.FILES
            contract = Contract.objects.get(id=reqP.get('id'))

            if reqF.get('contract_file'):

                contract_file_path = reqF.get('contract_file')

                # os.makedirs(os.path.dirname(contract_file_path), exist_ok=True)

                # with open(contract_file_path, 'wb') as destination:
                #     for chunk in reqF.get('contract_file').chunks():
                #         destination.write(chunk)
            else:
                contract_file_path = contract.contract_file_path
            
            contract.date_begin = reqP.get('date_begin'),
            contract.date_end = reqP.get('date_end'),
            contract_file_path = contract_file_path
            contract.save()

            return redirect('tenantList')
        else:
            return render(request, 'components/tenant/add.html')
    else :
        return render(request, 'components/tenant/add.html')

# Bill views
@login_required(login_url='/login')
def getBills(request):
    auth_user = request.user
    payments = []

    if auth_user.is_staff: 
        bills = Bill.objects.all()
    else:
        immou = ImmoUser.objects.get(user=auth_user)
        immo_role = ImmoRole.objects.get(slug='tenant')
        if(immou.role == immo_role):
            temp_cont = Contract.objects.filter(tenant=immou).first()
            bills = Bill.objects.filter(contract=temp_cont).all()

        else:
            temp_buildings = Building.objects.filter(landlord=immou).first()
            temp_appartments = Appartment.objects.filter(building=temp_buildings).first()
            
            temp_cont = Contract.objects.filter(appartment=temp_appartments).first()
            bills = Bill.objects.filter(contract=temp_cont).all()
            
    context = {
        'bills' : bills
    }
    return render(request, 'components/bill/list.html', context)

@login_required(login_url='/login')
def generateBills(request):
    contracts = Contract.objects.all()
    temp = 0

    for contract in contracts:
        if datetime.today().date().day == contract.date_end.date().day:
            temp = temp + 1
            future_date = datetime.today().date() + timedelta(days=14)

            bill = Bill(
                title = 'Facture '+str(datetime.today().date().month)+'/'+str(datetime.today().date().year)+'/'+str(contract.tenant),
                description = 'Facture du loyer de '+str(contract.tenant)+' du '+str(datetime.today().date().day)+'/'+str(datetime.today().date().month)+'/'+str(datetime.today().date().year),
                due_date = future_date,
                paid = False,
                contract = contract
            )

            bill.save()
    
    if temp != 0:
        messages.success(request, 'Factures générés avec succès')
    else:
        messages.warning(request, 'Aucune facture à générer')

    return HttpResponseRedirect('/bill/list')

# Payment views
@login_required(login_url='/login')
def getPayments(request):
    auth_user = request.user
    payments = []

    if auth_user.is_staff: 
        payments = Payment.objects.all()
    else:
        immou = ImmoUser.objects.get(user=auth_user)
        immo_role = ImmoRole.objects.get(slug='tenant')
        
        if(immou.role == immo_role):
            temp_cont = Contract.objects.filter(tenant=immou).first()
            temp_bill = Bill.objects.filter(contract=temp_cont).first()
            temp_payments = Payment.objects.filter(bill=temp_bill).all()

        else:
            temp_buildings = Building.objects.filter(landlord=immou).first()
            temp_appartments = Appartment.objects.filter(building=temp_buildings).first()
            
            temp_cont = Contract.objects.filter(appartment=temp_appartments).first()
            temp_bill = Bill.objects.filter(contract=temp_cont).first()
            temp_payments = Payment.objects.filter(bill=temp_bill).all()

        for payment in temp_payments:
                payments.append(payment)
                

    context = {
        'payments' : payments
    }
    return render(request, 'components/payment/list.html', context)

@login_required(login_url='/login')
def createPayment(request):
    bills = Bill.objects.filter(paid=False)

    context = {
        'bills' : bills
    }
    return render(request, 'components/payment/add.html', context)

@login_required(login_url='/login')
def createPaymentU(request):
    
    auth_user = request.user
    immo_user = ImmoUser.objects.get(user=auth_user)
        
    contrat = Contract.objects.get(tenant=immo_user.id)
    bills = Bill.objects.filter(paid=False, contract=contrat.id)

    context = {
        'bills' : bills
    }
    return render(request, 'components/payment/addu.html', context)

@login_required(login_url='/login')
def addPaymentBIU(request):
    auth_user = request.user
    req = request.POST
    
    immo_user = ImmoUser.objects.get(user=auth_user)
    
    contrat = Contract.objects.get(tenant=immo_user.id)
    bill = Bill.objects.filter(id=req.get('bill'), contract=contrat.id)
    bill.paid = True
    bill.save()

    payment = Payment(
        code = 'I-PAY-I'+str(bill.id),
        payment_type = 1,
        description = 'Paiement de loyer',
        status = 1,
        pay_method = req.get('pay_method'),
        bill = bill
    )
    payment.save()

    # payment = Payment(
    #     code = 'I-PAY-I'+str(bill.id),
    #     payment_type = 2,
    #     description = 'Paiement de commission',
    #     status = 1,
    #     pay_method = '---',
    #     bill = bill
    # )

    # payment.save()
    
    htmly = get_template('components/retrait/email_dem_pay.html')
    d = { 'first_name':request.user.first_name, 'last_name':request.user.last_name}
    subject, from_email, to = 'immo', 'your_email@gmail.com', request.user.email
    html_content = htmly.render(d)
    msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

    messages.success(request, 'Paiement effectué avec succès')

    return HttpResponseRedirect('/payments/create')

@login_required(login_url='/login')
def addPayment(request):
    req = request.POST

    bill = Bill.objects.get(id=req.get('bill'))
    bill.paid = True
    bill.save()

    payment = Payment(
        code = req.get('code'),
        payment_type = 1,
        description = 'Paiement de loyer',
        status = 1,
        pay_method = req.get('pay_method'),
        bill = bill
    )
    payment.save()

    messages.success(request, 'Paiement effectué avec succès')

    return HttpResponseRedirect('/payment/create')

@login_required(login_url='/login')
def getPaymentsByUsersD(request, pk):
    payments = Payment.objects.get(id=pk)
    context = {
        'payment' : payments
    }
    return render(request, 'components/payment/detailPaie.html', context)


# Retrait
@login_required(login_url='/login')
def getRetrait(request):
    
    retrait = Retrait.objects.all()
    
    context = {
        'retraits' : retrait
    }

    return render(request, 'components/retrait/list.html', context)

@login_required(login_url='/login')
def getRetraitConn(request):
    
    auth_user = request.user
    immo_user = ImmoUser.objects.get(user=auth_user)
    
    user_connt = Retrait.objects.filter(landlord=immo_user).all()
    
    payments = Payment.objects.filter(payment_type=1)
    retrait = Retrait.objects.filter(status="valide", landlord=immo_user)
    sum_retrait = 0
    wallet = 0
    
    for pay in payments:
            wallet = wallet + pay.bill.contract.appartment.price - (pay.bill.contract.appartment.price*10)/100
            
    for ret in retrait:
            sum_retrait = sum_retrait + ret.montant

    
    # total_wallet = wallet - sum_retrait
    total_wallet = float(wallet) - float(sum_retrait) 
    context = {
        'user_retaits' : user_connt,
        
        'wallet': total_wallet
    }

    return render(request, 'components/retrait/list_conn.html', context)

@login_required(login_url='/login')
def addRetrait(request):
    if request.method == 'POST':
    
        # form = RetraitFrom(request.POST)
        
            
            retrait = Retrait(
                code = request.POST.get('code'),
                montant = request.POST.get('montant'),
                description = request.POST.get('description'),
                status = "encours",
                landlord = request.user.immouser
            )
            retrait.save()
            
            email = "immocabinethuissier@gmail.com"
            
            htmly = get_template('components/retrait/email_dem_retrait.html')
            d = { 'first_name':request.user.first_name, 'last_name':request.user.last_name, 'code':retrait.code, 'montant': retrait.montant, 'date_create': retrait.date_create}
            subject, from_email, to = 'immo', 'your_email@gmail.com', email
            html_content = htmly.render(d)
            msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            return redirect('retraiListConn')
    else:
        return render(request, 'components/retrait/add.html')  
    
@login_required(login_url='/login')
def validateRetrait(request, pk, status):
    if pk and status:
        retrait = Retrait.objects.get(id=pk)
        retrait.status=status
        retrait.save()
        
        try:
            user = ImmoUser.objects.get(id=retrait.landlord.id)
            htmly = get_template('components/retrait/email_message_val.html')
            d = { 'first_name':user.user.first_name, 'last_name':user.user.last_name, 'montant': retrait.montant, 'status':retrait.status}
            subject, from_email, to = 'immo', 'your_email@gmail.com', user.user.email
            html_content = htmly.render(d)
            msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        except BadHeaderError:
            return HttpResponse('Invalid header found.')
        return redirect('retraiList')
        
    return redirect('retraiList')

@login_required(login_url='/login')
def editRetrait(request, pk):
    
    retrait = Retrait.objects.get(id=pk) 
    context = {
        'retrait' : retrait
    }
    return render(request, 'components/retrait/edit.html', context)

@login_required(login_url='/login')
def saveRetrait(request):
    if request.method == 'POST':
    
        form = RetraitFrom(request.POST)

        if form.is_valid():
            reqP = request.POST
            retrait = Retrait.objects.get(id=reqP.get('id'))

            retrait.code = reqP.get('code')
            retrait.montant = reqP.get('montant')
            retrait.description = reqP.get('description')
            retrait.save()
            
            # return redirect('retraiListConn', pk=reqP.get('id'))
            return redirect('retraiListConn')
    else:
        return HttpResponseRedirect('/retrait/list_ask')       

@login_required(login_url='/login')
def getRetraitDetails(request, pk):
    retrait = Retrait.objects.get(id=pk)

    context = {
        'retrait' : retrait
    }
    return render(request, 'components/retrait/details.html', context)

@login_required(login_url='/login')
def getDemandes(request):
    ask = Demand.objects.all()

    context = {
        'asks' : ask
    }
    return render(request, 'components/tenant/ask.html', context)

@login_required(login_url='/login')
def validateDemand(request, pk, status):
    if pk and status:
        ask = Demand.objects.get(id=pk)
        ask.status=status
        ask.save()
        
        try:
            htmly = get_template('components/tenant/email_message_val.html')
            d = { 'first_name':ask.first_name, 'last_name':ask.last_name, 'appartement': ask.appartment, 'status':ask.status, 'datedemand':ask.date_create}
            subject, from_email, to = 'immo', 'your_email@gmail.com', ask.email
            html_content = htmly.render(d)
            msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        except BadHeaderError:
            return HttpResponse('Invalid header found.')
        return redirect('ask')
        
    return redirect('ask')

def api_get_appartments(request):
    appartments = Appartment.objects.all()
    serializer = AppartmentSerializer(appartments, many=True)
    return JsonResponse(serializer.data, safe=False)

def api_get_buildings(request):
    buildings = Building.objects.all()
    serializer = BuildingSerializer(buildings, many=True)
    return JsonResponse(serializer.data, safe=False)

def api_get_appartment_images(request, pk):
    appartment = Appartment.objects.get(id=pk)
    images = AppPic.objects.filter(appartment=appartment)
    serializer = AppPicSerializer(images, many=True)
    return JsonResponse(serializer.data, safe=False)

def api_get_building_appartments(request, pk):
    building = Building.objects.get(id=pk)
    appartments = Appartment.objects.filter(building=building).all()
    serializer = AppartmentSerializer(appartments, many=True)
    return JsonResponse(serializer.data, safe=False)

class DemandCreateAPIView(APIView):
    def post(self, request, format=None):
         # Extract appartment_id from the request data
        appartment_id = request.data.get('appartment_id')
        
        # Check if the appartment_id is provided
        if not appartment_id:
            return Response({'error': 'appartment_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Attempt to get the corresponding Appartment
            appartment = Appartment.objects.get(pk=appartment_id)
        except Appartment.DoesNotExist:
            return Response({'error': 'Appartment does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
        # Create a Demand associated with the retrieved Appartment
        demand_data = request.data.copy()
        demand_data['appartment'] = appartment.id
        serializer = DemandCreateSerializer(data=demand_data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def api_get_demands_by_number(request, pk):
    demands = Demand.objects.filter(phone_number=pk).all()
    serializer = DemandSerializer(demands, many=True)
    return JsonResponse(serializer.data, safe=False)
