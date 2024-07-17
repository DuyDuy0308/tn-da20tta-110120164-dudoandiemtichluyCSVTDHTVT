from django.urls import path
from . import views

app_name = 'CVHT'

urlpatterns = [
    path('index/<str:id_cv>/', views.index, name='index'),
    path('sv/<str:id_cv>/', views.sv, name='sv'),
    path('diem/<str:id_cv>/', views.diem, name='diem'),
    path('ct_diem/<str:id_cv>/', views.ct_diem, name='ct_diem'),
]
