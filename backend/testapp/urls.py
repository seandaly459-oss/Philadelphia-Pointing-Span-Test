from django.urls import path
from . import views
 
urlpatterns = [
    path('<str:link>/intro/',        views.test_intro,        name='test_intro'),
    path('<str:link>/tutorial/',     views.tutorial,           name='tutorial'),
    path('<str:link>/instructions/', views.test_instructions,  name='test_instructions'),
    path('<str:link>/keypad/',       views.test_keypad,         name='test_keypad'),
    path('<str:link>/submit/',       views.test_submit,         name='test_submit'),
]
