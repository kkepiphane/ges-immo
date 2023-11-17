from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"), 

    # Landlords urls
    path('landlords/list', views.getLandlords, name="landlordList"),  
    path('landlords/create', views.createLandlord, name="landlordCreate"),  
    path('landlords/add', views.addLandlord, name="landlordAdd"),  
    path('landlords/account/activate/<int:pk>/<str:is_active>', views.activateLandlordAccount, name="landlordActivate"),  
    path('account/<int:pk>/edit', views.editLandlord, name="landlordEdit"),  
    path('account/save', views.saveLandlord, name="landlordSave"),  
    path('landlords/account/<int:pk>/details', views.getLandlordDetails, name="landlordDetail"),  
    path('landlords/wallet', views.walletLandlord, name="landlordWallet"),

    # Tenants urls
    path('tenants/list', views.getTenants, name="tenantList"),  
    path('tenants/create', views.createTenant, name="tenantCreate"),
    path('tenants/add', views.addTenant, name="tenantAdd"),    
    #  path('account/<int:pk>/edit', views.editTenant, name="TenantEdit"),  
    # path('account/save', views.saveTenant, name="TenantSave"),
    path('tenants/account/<int:pk>/details', views.getTenantDetails, name="tenantDetail"), 
    path('tenants/account/activate/<int:pk>/<str:is_active>', views.activateTenantAccount, name="tenantActivate"),  
        
    # Buildings urls
    path('building/<int:pk>/edit', views.editBuilding, name="buildingEdit"),  
    path('building/save', views.saveBuilding, name="buildingSave"), 
    path('building/<int:pk>/details', views.getBuildingDetails, name="buildingDetail"),  
    path('building/list', views.getBuildings, name="buildingList"),  
    path('building/landlord/<int:pk>/create', views.createBuilding, name="buildingCreate"),
    path('building/add', views.addBuilding, name="buildingAdd"),
    path('delbuilding/<pk>', views.deleteBuilding, name="deletebuilding"), 


    # Appartments urls
    path('appartment/list', views.getAppartments, name="appartmentList"),  
    path('appartment/<int:pk>/edit', views.editAppartment, name="appartmentEdit"),  
    path('appartment/save', views.saveAppartment, name="appartmentSave"), 
    path('appartment/<int:pk>/details', views.getAppartmentDetails, name="appartmentDetail"),
    path('appartment/<int:pk>/create', views.createAppartment, name="appartmentCreate"),
    path('appartment/add', views.addAppartment, name="appartmentAdd"), 
    path('editimage/edit', views.editPic, name="editpic"),  
    path('editimage/<pk>', views.deletePic, name="deletepic"), 
     
    path('addimage/add', views.addOnlyPic, name="addpic"),  

      # Contracts urls
    path('contract/<int:pk>/edit', views.editContract, name="contractEdit"),  
    path('contract/save', views.saveContract, name="contractSave"), 

    # Bill urls
    path('bill/list', views.getBills, name="billList"), 
    path('bill/generate', views.generateBills, name="billGenerate"),  

    # Payment urls
    path('payment/list', views.getPayments, name="paymentList"),
    path('payment/create', views.createPayment, name="paymentCreate"),  
    path('payment/add', views.addPayment, name="paymentAdd"),  
    path('payment/<int:pk>/details', views.getPaymentsByUsersD, name="paymentDetail"),
    
    path('payment/createu', views.createPaymentU, name="paymentCreateu"),  
    path('payments/addu', views.addPaymentBIU, name="paymentAddu"),

    # Retrait urls
    
    path('retrait/list', views.getRetrait, name="retraiList"),
    path('retrait/list_ask', views.getRetraitConn, name="retraiListConn"),
    path('retrait/add', views.addRetrait, name="retraitAdd"),
    path('retrait/validate/<int:pk>/<str:status>', views.validateRetrait, name="retaitActivate"),   
    path('retrait/<int:pk>/edit', views.editRetrait, name="retraitEdit"),  
    path('retrait/save', views.saveRetrait, name="saveRetrait"),
    path('retrait/<int:pk>/details', views.getRetraitDetails, name="retraitDetail"), 
       
    # User urls\
    path('signin', views.signin, name="signin"),  
    path('login', views.loginUser, name="loginUser"),
    path("password_change", views.password_change, name="password_change"),  
    path('logout', views.custom_logout, name='logout'), 
    
    path('ask', views.getDemandes, name='ask'),
    path('ask/validate/<int:pk>/<str:status>', views.validateDemand, name="askActivate"),
    # path('profil/<username>', views.profil, name='profil'),  

    path('api/appartments_list', views.api_get_appartments, name='apiAppartmentsList'),
    path('api/appartment_pics/<int:pk>', views.api_get_appartment_images, name='apiAppartmentsPics'),
    path('api/buildings_list', views.api_get_buildings, name='apiBuildingList'),
    path('api/building_appartments/<int:pk>', views.api_get_building_appartments, name='apiBuildingAppartments'),
    path('api/demand', views.DemandCreateAPIView.as_view(), name='apiDemandCreate'),
    path('api/demands_list/<int:pk>', views.api_get_demands_by_number, name='apiDemandsList'),

]