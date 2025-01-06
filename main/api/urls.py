# entraditaBackend/main/api/urls.py
from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    
    # { Private endpoints } ---------------------------------------------------------------------------------------------------------------------->
    
      # Token endpoints - Puntos de conexión de tokens (POST)
      path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
      path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
      
      # Test endpoint - Punto de conexión de prueba (GET)
      path('test/', views.TestView.as_view(), name='info'),
      
      # Crear evento por un organizador - Create event by an organizer (POST)
      path('event/', views.CreateEventView.as_view(), name='event-create'),
      
      # Obtener eventos de un organizador y el ticket limit - Get events of an organizer and the ticket limit (GET)
      path('events/', views.EventListView.as_view(), name='event-list'),
      
      # Manejar un evento específico - Manage a specific event (GET, PUT, DELETE)
      path('event/<int:pk>/', views.EventDetailView.as_view(), name='event-detail'),
      
      # Habilitar o deshabilitar la venta de entradas de un evento - Enable or disable ticket sales for an event (PUT)
      path('event/<int:pk>/ticket-sales/', views.UpdateTicketSalesEventView.as_view(), name='event-ticket-sales-update'),
      
      # Obtener la información de un evento específico con sus detalles - Get the information of a specific event with its details (GET)
      path('event/<int:pk>/details/', views.EventDetailInfoView.as_view(), name='event-detail-info'),
      
      # Obtener la informacion de un evento para el reporte economico - Get the information of an event for the economic report (GET)
      path('event/<int:pk>/economic-report/', views.EventEconomicReportView.as_view(), name='event-economic-report'),
      
      # Obtener un evento junto con sus empleados - Get an event along with its employees (GET) (Reload)
      path('event/<int:pk>/employees/', views.EventEmployeesView.as_view(), name='event-employees'),
      
      # Crear un empleado - Create an employee (POST)
      path('employee/', views.EmployeeCreateView.as_view(), name='create-employee'),
      
      # Manejar un empleado específico - Manage a specific employee (GET, PUT, DELETE)
      path('employee/<int:pk>/', views.EmployeeDetailView.as_view(), name='employee-detail'),
      
      # Habilitar o deshabilitar un empleado - Enable or disable an employee (PUT)
      path('employee/<int:pk>/status/', views.EmployeeStatusView.as_view(), name='employee-status'),
      
      # Crear un ticket por el organizador - Create a ticket by the organizer (POST)      
      path('ticket/', views.CreateTicketView.as_view(), name='create-ticket'),
      
      # Eliminar un ticket específico - Delete a specific ticket (DELETE)
      path('ticket/<int:pk>/', views.TicketDetailView.as_view(), name='ticket-detail'),      
    
    # { Public endpoints } ---------------------------------------------------------------------------------------------------------------------->
    
      # Obtener la información para la pagina de un vendedor - Get the information for the seller's page (GET)
      path('employee/seller/<str:uuid>/info/', views.SellerInfoView.as_view(), name='seller-info'),
      
      # Crear un ticket por un vendedor - Create a ticket by a seller (POST)
      path('employees/seller/<str:uuid>/create-ticket/', views.SellerCreateTicketView.as_view(), name='vendedor-create-ticket'), # POST: Create ticket by vendedor
      
      # Eliminar un ticket por un vendedor - Delete a ticket by a seller (DELETE)
      path('employees/seller/<str:uuid>/delete-ticket/<int:ticket_id>/', views.SellerDeleteTicketView.as_view(), name='vendedor-delete-ticket'), # DELETE: Delete ticket by vendedor
      
      # Obtener la información para la pagina de un scanner - Get the information for the scanner's page (GET)
      path('employees/scanner/<str:uuid>/info/', views.ScannerInfoView.as_view(), name='scanner-info'),
      
      # Escanear un ticket a través de su payload (qr) - Scan a ticket through its payload (qr) (PUT)
      path('ticket/scan-qr/<str:payload>/', views.ScanTicketView.as_view(), name='scan-ticket'),
      
      # Escanear un ticket a través de su dni - Scan a ticket through its dni (PUT)
      path('ticket/scan-dni/<str:dni>/', views.ScanTicketDniView.as_view(), name='scan-ticket-by-dni'),  

      # Obtener la información de un ticket a través de su uuid público - Get the information of a ticket through its public uuid (GET)
      path('ticket/<str:uuid>/', views.PublicTicketDetailView.as_view(), name='get-ticket'),
      
      # Obtener la información de un evento para la web - Get the information of an event for the web (GET)
      path('event/<int:pk>/info-for-web/', views.InfoForWebView.as_view(), name='info-for-web'),

      # Verificar la contraseña de un evento para un empleado - Check the password of an event for an employee (POST)
      path('event/<str:uuid>/check-password/', views.CheckEventPasswordView.as_view(), name='check_event_password'),
      
  ]

