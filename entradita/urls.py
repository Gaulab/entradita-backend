
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('authapp.api.urls')),
    path('api/v1/main/', include('main.api.urls')),
    path('api/v1/eventpage/', include('eventpage.api.urls')),

]
