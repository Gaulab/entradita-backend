
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('authapp.api.urls')),
    path('api/v1/', include('main.api.urls')),
    path('api/v1/', include('eventpage.api.urls')),

]
