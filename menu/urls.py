from django.urls import path
from . import views

urlpatterns = [
    path('', views.menu, name='menu'),
    path('buyurtma/<int:taom_id>/', views.buyurtma, name='buyurtma'),
    path('buyurtmalarim/', views.mening_buyurtmalarim, name='mening_buyurtmalarim'),
]
