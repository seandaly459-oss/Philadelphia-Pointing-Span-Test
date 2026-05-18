"""
ppst URL Configuration
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('accounts/', include('accounts.urls')),
    path('patient/', include('patient.urls')),
    path('portal/', include('portal.urls')),
    path('testapp/', include('testapp.urls')),
]
