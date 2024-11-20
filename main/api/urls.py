from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    
    # Private endpoints ------------------------------------------------------------------------------------------>
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # POST: Obtener token
    # endpoints of test
    path('test/', views.TestView.as_view(), name='info'),                                              # GET: Test view
    # endpoints of events
    path('events/create/', views.CreateEventView.as_view(), name='event-create'),                      # POST: Create event
    path('events/<int:pk>/', views.EventDetailView.as_view(), name='event-detail'),                    # GET, PUT, DELETE: Manage a specific event
    path('events/', views.EventListView.as_view(), name='event-list'),                                 # GET: List events
    path('events/<int:pk>/details/', views.EventDetailInfoView.as_view(), name='event-detail-info'),   # GET: Get event details
    path('events/<int:pk>/employees/', views.EventEmployeesView.as_view(), name='event-employees'),    # GET: Get event employees
    # endpoints of tickets
    path('tickets/', views.CreateTicketView.as_view(), name='create-ticket'),                          # POST: Create ticket
    path('tickets/<int:pk>/', views.TicketDetailView.as_view(), name='ticket-detail'),                 # DELETE: Manage a specific ticket
    # endpoints of employees
    path('employees/', views.CreateEmpleadoView.as_view(), name='create-employee'),                    # POST: Create employee
    path('employees/<int:pk>/', views.EmpleadoDetailView.as_view(), name='empleado-detail'),           # PUT, DELETE: Manage a specific employee
    
    # Public endpoints ------------------------------------------------------------------------------------------>
    # endpoints of sellers
    path('employees/seller/<str:uuid>/info/', views.SellerInfoView.as_view(), name='seller-info'),     # GET: Get vendedor info and validate
    path('employees/seller/<str:uuid>/create-ticket/', views.SellerCreateTicketView.as_view(), name='vendedor-create-ticket'), # POST: Create ticket by vendedor
    path('employees/seller/<str:uuid>/delete-ticket/<int:ticket_id>/', views.VendedorDeleteTicketView.as_view(), name='vendedor-delete-ticket'), # DELETE: Delete ticket by vendedor
    # endpoints of tickets
    path('tickets/public/<str:uuid>/', views.PublicTicketDetailView.as_view(), name='get-ticket'),      # GET: Get ticket by public uuid
    # endpoints of scanners
    path('employees/scanner/<str:uuid>/info/', views.ScannerInfoView.as_view(), name='scanner-info'),  # GET: Get scanner info and validate
    path('tickets/scan/<str:payload>/', views.ScanTicketView.as_view(), name='scan-ticket'),           # PUT: Scan ticket
    path('tickets/scan/dni/<str:dni>/', views.ScanTicketDniView.as_view(), name='scan-ticket-by-dni'),            # PUT: Scan ticket
    # endpoints of auth sellers
    path('events/<str:pk>/check-password/', views.CheckEventPasswordView.as_view(), name='check_event_password'), # POST: Check event password
    
]
