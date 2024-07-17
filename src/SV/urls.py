from django.urls import path
from . import views

app_name = 'SV'

urlpatterns = [
    path('index/<str:MSSV>/', views.student_index, name='index'),
    path('ttcn/<str:MSSV>/', views.ttcn, name='ttcn'),
    path('dudoan/<str:MSSV>/', views.dudoan, name='dudoan'),
    path('dudoandiem/<str:MSSV>/', views.dudoandiem, name='dudoandiem'),
    path('predict/<str:MSSV>/', views.predict, name='predict'),
    path('hoc_ky_mon_hoc/<str:MSSV>/', views.hoc_ky_mon_hoc_view, name='hoc_ky_mon_hoc'),
    path('compare-gpa/<str:MSSV>/', views.compare_gpa_view, name='compare_gpa'),
]
