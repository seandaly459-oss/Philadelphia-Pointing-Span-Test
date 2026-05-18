from django.urls import path

from . import views
from .views_doctor_dashboard import filter_tests_view
from .views_ajax import filter_sessions_ajax

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('stats/', views.dashboard_stats, name='dashboard_stats'),
    path('sessions-filter/', filter_sessions_ajax, name='sessions_filter'),
    path('create_test/', views.create_test, name='create_test'),
]
