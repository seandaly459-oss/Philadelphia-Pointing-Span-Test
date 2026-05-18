from django.urls import path
from . import views

urlpatterns = [
    # Define your accounts app routes here.
     path('login/',views.login_view,name='login'),
    path('logout/', views.logout_view, name='logout'),
]
