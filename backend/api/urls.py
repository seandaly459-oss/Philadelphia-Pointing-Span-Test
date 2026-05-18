from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'test-data', views.TestDataViewSet)
router.register(r'tests', views.TestViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('tests/<int:pk>/complete/', views.complete_test_view, name='complete_test'),
    path('tests/<int:pk>/export-csv/', views.export_csv_view, name='export_csv'),
    path('tests/<int:pk>/export-excel/', views.export_excel_view, name='export_excel'),
    path('sessions/available-csvs/', views.available_csvs_view, name='available_csvs'),
    path('test-data-summary/', views.test_data_summary, name='test-data-summary'),
]
