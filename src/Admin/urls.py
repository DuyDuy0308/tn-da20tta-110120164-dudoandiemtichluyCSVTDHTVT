from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.login, name='login'),
    #  đăng nhập
    path('login/', views.login, name='login'),
    path('taotaikhoan/', views.Taotaikhoan, name='taotaikhoan'),
    # danh mục 
    path('main/', views.main_admin, name='main'),
    # Sinh viên
    path('student/', views.student, name='student'),
    # Cố vấn
    path('teacher/', views.teacher, name='teacher'),
    # Khoa
    path('khoa/', views.khoa, name='khoa'),
    # Bộ môn
    path('bomon/', views.bomon, name='bomon'),
    # ngành đào tạo
    path('nganhdaotao/', views.nganhdaotao, name='nganhdaotao'),
    # Học kỳ niên khóa
    path('hknienkhoa/', views.hknienkhoa, name='hknienkhoa'),
    # Loại học phần
    path('loaihocphan/', views.loaihocphan, name='loaihocphan'),
    # Học kỳ chương trình đào tạo
    path('hkctdt/', views.hkctdt, name='hkctdt'),
    # Nhóm môn
    path('nhommon/', views.nhommon, name='nhommon'),
    # Chương trình đào tạo
    path('ctdt/', views.ctdt, name='ctdt'),
    # Lớp
    path('lop/', views.lop, name='lop'),
    # Bảng điểm
    path('bangdiem/', views.bangdiem, name='bangdiem'),
    # Môn học
    path('monhoc/', views.monhoc, name='monhoc'),
    # Chi tiết bảng điểm
    path('ctbd/', views.ctbd, name='ctbd'),
    # # Thuộc chương trình đào tạo
    path('tctdt/', views.tctdt, name='tctdt'),
    
    path('student-dlm/', views.dlm, name='dlm'),
     
    path('upload/', views.export_monhoc_diem10_csv, name='upload'),
    
    path('CVHT/', include('CVHT.urls')),
    path('SV/', include('SV.urls')),

]
