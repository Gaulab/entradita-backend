from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    
    # Private endpoints >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),                                                            # 01
    # Test endpoint - Punto de conexión de prueba
    path('test/', views.TestView.as_view(), name='info'),                                                                               # 02
    # Event endpoint from an organizer - Punto de conexión para evento desde un organizador
    path('event/create/', views.CreateEventView.as_view(), name='event-create'),                                                        # 03
    path('event/<int:pk>/', views.EventDetailView.as_view(), name='event-detail'),                                                      # 04
    path('event/<int:pk>/ticket-sales/', views.UpdateTicketSalesEventView.as_view(), name='event-ticket-sales-update'),                 # 05
    path('events/', views.EventListView.as_view(), name='event-list'),                                                                  # 06
    path('event/<int:pk>/details/', views.EventDetailInfoView.as_view(), name='event-detail-info'),                                    # 07
    path('event/<int:pk>/economic-report/', views.EventEconomicReportView.as_view(), name='event-economic-report'),                   # 08

    path('events/<int:pk>/employees/', views.EventEmployeesView.as_view(), name='event-employees'),                                     # GET: Get event employees >>>>> SE USA???
    
    # endpoints of employees
    path('employee/', views.EmployeeCreateView.as_view(), name='create-employee'),                                                     # 09
    path('employee/<int:pk>/status/', views.EmployeeStatusView.as_view(), name='employee-status'),                                     # 10
    path('employee/<int:pk>/', views.EmpleadoDetailView.as_view(), name='empleado-detail'),                                            # PUT, DELETE: Manage a specific employee
    
    # endpoints of tickets
    path('tickets/', views.CreateTicketView.as_view(), name='create-ticket'),                          # POST: Create ticket
    path('tickets/<int:pk>/', views.TicketDetailView.as_view(), name='ticket-detail'),                 # DELETE: Manage a specific ticket

    # Public endpoints ------------------------------------------------------------------------------------------>
    # endpoints of sellers
    path('employee/seller/<str:uuid>/info/', views.SellerInfoView.as_view(), name='seller-info'),     # GET: Get vendedor info and validate
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
    path('event/<int:pk>/info-for-web/', views.InfoForWebView.as_view(), name='info-for-web'),                        # GET: Get info for web

    
]


# DOCS >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# 01: Token endpoint - Punto de conexión de token
# 02: Test endpoint - Punto de conexión de prueba para verificar que el servidor esta corriendo
# 03: Event endpoint from an organizer - Punto de conexión para evento desde un organizador, aqui se crean los tickets tag tambien correspondientes al evento