from django.urls import path
from . import views

app_name = 'SV'

urlpatterns = [
    path('index/<str:MSSV>/', views.student_index, name='index'),
    path('ttcn/<str:MSSV>/', views.ttcn, name='ttcn'),
    path('dudoan/<str:MSSV>/', views.dudoan, name='dudoan'),
    path('dudoandiem/<str:MSSV>/', views.dudoandiem, name='dudoandiem'),
    path('predict/<str:MSSV>/', views.predict, name='predict'),
    # path('train/', views.train_and_save_models_view, name='train_and_save_models_view'),
]
