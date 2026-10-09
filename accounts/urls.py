from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.royxatdan_otish, name='royxatdan_otish'),
    path('login/', views.kirish, name='login'),
    path('logout/', views.chiqish, name='logout'),
]
