import pandas as pd
from django.apps import apps
import os, base64, json
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from django.db import transaction, IntegrityError
from django.db.models import Count
from django.http import HttpRequest, HttpResponse, FileResponse,JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from .forms import create_taikhoan, create_covan, UploadFileForm, create_sinhvien, create_khoa, create_bomon, create_nganhdaotao, create_hknienkhoa, create_loaihocphan, create_hk_ctdt, create_nhommon, create_ctdt, create_lop, create_bangdiem, create_monhoc, create_ctbd, create_thuoc_ctdt, PredictForm
from .models import Taikhoan, Covan, Sinhvien, Khoa, Bomon, Nganhdaotao, Hockynienkhoa, Loaihocphan, Hockychuongtrinhdaotao, Nhommon, Chuongtrinh_daotao, Bangdiem, Lop, Monhoc, Chitiet_bangdiem,  thuoc_ctdt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder
import joblib


# Create your views here.
def index(request):
    return render(request, 'login.html')
  
def main_admin(request):
    # Đếm số sinh viên trong mỗi lớp
    lops = Lop.objects.annotate(sinh_vien_count=Count('sinhvien'))
    labels = [lop.Ma_lop for lop in lops]
    total_giangvien = Covan.objects.count()
    total_Nganhdaotao = Nganhdaotao.objects.count()
    total_Monhoc = Monhoc.objects.count()
    data = [lop.sinh_vien_count for lop in lops]

    # Tính tổng số sinh viên
    total_sinh_vien = sum(data)
    bangdiem_data = Chitiet_bangdiem.objects.all()
    # Lấy tất cả các bảng điểm
    class_id = request.GET.get('class', None)
    all_bangdiem = Bangdiem.objects.all()
    diem_he_4_list = []

    for bangdiem in all_bangdiem:
        try:
            diem_he_4 = float(bangdiem.Diem_tich_luy_he_4)
            diem_he_4_list.append(diem_he_4)
        except ValueError:
            pass
    
    if class_id:
        combined_scores = Chitiet_bangdiem.objects.filter(Ma_bang_diem__MSSV__Ma_lop_id=class_id)
    else:
        combined_scores = Chitiet_bangdiem.objects.all()

    top_5_scores = combined_scores.order_by('-Diem_he_4')[:5]
    bottom_5_scores = combined_scores.order_by('Diem_he_4')[:5]
    combined_scores = list(top_5_scores) + list(bottom_5_scores)

    # Chuẩn bị dữ liệu cho biểu đồ
    score_labels = [f"{score.Ma_mon_hoc.Ma_mon_hoc} ({score.Diem_he_4})" for score in combined_scores]
    score_data = [float(score.Diem_he_4) for score in combined_scores]
    
    ds_lop = Lop.objects.all()

    context1 = {
        'labels': labels,
        'data': data,
        'score_labels': score_labels,
        'score_data': score_data,
        'diem_he_4_list': diem_he_4_list,
        'total_sinh_vien': total_sinh_vien,
        'total_giangvien': total_giangvien,
        'total_Nganhdaotao' : total_Nganhdaotao,
        'total_Monhoc' :  total_Monhoc,
        'ds_lop': ds_lop,
    }

    return render(request, 'hienthi.html', context1)
# Tạo tài khoản ------------------------------------------------------------------------------------------------------------------
def Taotaikhoan(request: HttpRequest):
    if request.method == 'POST':
        form = create_taikhoan(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = create_taikhoan()  # Khởi tạo form nếu phương thức là GET
    taikhoan = Taikhoan.objects.all()
    return render(request, 'taotaikhoan.html', {'form': form, 'taikhoan': taikhoan,})
# Đăng nhập ------------------------------------------------------------------------------------------------------------------        
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        try:
            user = Taikhoan.objects.get(User_name=username, Password=password)
            # Kiểm tra role và điều hướng tương ứng
            if user.Role == 'admin':
                return redirect('main') 
            elif user.Role == 'teacher':
                giang_vien = get_object_or_404(Covan, Email_cv=username)
                return redirect('CVHT:index', id_cv=giang_vien.Id_cv)
            elif user.Role == 'student':
                sinh_vien = get_object_or_404(Sinhvien, MSSV=username)
                return redirect('SV:index', MSSV=sinh_vien.MSSV)
            else:
                return HttpResponse("Tài khoản không có quyền truy cập.")
        except Taikhoan.DoesNotExist:
            return HttpResponse("Sai tài khoản hoặc mật khẩu.")
    return render(request, 'login.html')

# Cố vấn học tập ------------------------------------------------------------------------------------------------------------------
def teacher(request: HttpRequest):
    form_covan = create_covan()
    form_file = UploadFileForm()
    delete_success = False
    edit_success = False
    add_success = False
    import_success = False

    if request.method == 'POST':
        if 'delete' in request.POST:
            ids_to_delete = request.POST.getlist('selected_ids')
            Covan.objects.filter(Id_cv__in=ids_to_delete).delete()
            delete_success = True
            
        if 'edit' in request.POST:
            id_cv = request.POST.get('Id_cv')
            Id_cv_instance = get_object_or_404(Covan, Id_cv=id_cv)
            form_covan = create_covan(request.POST, instance=Id_cv_instance)
            if form_covan.is_valid():
                form_covan.save()
                edit_success = True
            
        elif 'add' in request.POST:
            form_covan = create_covan(request.POST)
            if form_covan.is_valid():
                form_covan.save()
                add_success = True
               
        elif 'import' in request.POST:
            form_file = UploadFileForm(request.POST, request.FILES)
            if form_file.is_valid():
                df = pd.read_excel(request.FILES['file'])

                # Ánh xạ các tên cột mới đến các trường trong mô hình
                df = df.rename(columns={
                    'Mã cố vấn': 'Id_cv',
                    'Tên cố vấn': 'Ho_ten_cv',
                    'Ngày sinh': 'Ngay_sinh_cv',
                    'Giới tính': 'Gioi_tinh_cv',
                    'Địa chỉ': 'Dia_chi_cv',
                    'Email': 'Email_cv',
                })

                for index, row in df.iterrows():
                    Covan.objects.create(
                        Id_cv=row['Id_cv'],
                        Ho_ten_cv=row['Ho_ten_cv'],
                        Ngay_sinh_cv=row['Ngay_sinh_cv'],
                        Gioi_tinh_cv=row['Gioi_tinh_cv'],
                        Dia_chi_cv=row['Dia_chi_cv'],
                        Email_cv=row['Email_cv'],
                    )
                add_success = True
                

    covans = Covan.objects.all()
    return render(request, 'teacher.html', {
        'form_covan': form_covan,
        'form_file': form_file,
        'covans': covans,
        'delete_success': delete_success,
        'edit_success': edit_success,
        'add_success': add_success,
    })

# ---------------------------------------------------------------------------------------------------------------------------------------
# Khoa 
def khoa(request: HttpRequest):
    form_khoa = create_khoa()
    delete_success = False
    edit_success = False
    add_success = False

    if request.method == 'POST':
        if 'delete' in request.POST:
            ids_to_delete = request.POST.getlist('selected_ids')
            Khoa.objects.filter(Ma_khoa__in=ids_to_delete).delete()
            delete_success = True
            
        elif 'edit' in request.POST:
            ma_khoa = request.POST.get('Ma_khoa')
            khoa_instance = get_object_or_404(Khoa, Ma_khoa=ma_khoa)
            form_khoa = create_khoa(request.POST, instance=khoa_instance)
            if form_khoa.is_valid():
                form_khoa.save()
                edit_success = True
        else:
            form_khoa = create_khoa(request.POST)
            if form_khoa.is_valid():
                form_khoa.save()
                add_success = True
            
    khoas = Khoa.objects.all()
    return render(request, 'khoa.html', {
        'form_khoa': form_khoa,
        'khoas': khoas,
        'delete_success': delete_success,
        'edit_success': edit_success,
        'add_success': add_success
    })
# ---------------------------------------------------------------------------------------------------------------------------------------
# Bộ môn
def bomon(request: HttpRequest):
    form_bomon = create_bomon()
    delete_success = False
    edit_success = False
    add_success = False

    if request.method == 'POST':
        if 'delete' in request.POST:
            ids_to_delete = request.POST.getlist('selected_ids')
            Bomon.objects.filter(Ma_bo_mon__in=ids_to_delete).delete()
            delete_success = True
            
        elif 'edit' in request.POST:
            ma_bomon = request.POST.get('Ma_bo_mon')
            bomon_instance = get_object_or_404(Bomon, Ma_bo_mon=ma_bomon)
            ma_khoa = request.POST.get('Ma_khoa')
            khoa_instance = get_object_or_404(Khoa, Ma_khoa=ma_khoa)
            bomon_instance.Ma_khoa = khoa_instance
            form_bomon = create_bomon(request.POST, instance=bomon_instance)
            if form_bomon.is_valid():
                form_bomon.save()
                edit_success = True
        else:
            form_bomon = create_bomon(request.POST)
            if form_bomon.is_valid():
                form_bomon.save()
                add_success = True
            
    bomons = Bomon.objects.all()
    khoas = Khoa.objects.all()
    return render(request, 'bomon.html', { 
        'form_bomon': form_bomon,
        'bomons': bomons,
        'khoas': khoas,
        'delete_success': delete_success,
        'edit_success': edit_success,
        'add_success': add_success
    })
# ---------------------------------------------------------------------------------------------------------------------------------------
# Ngành đào tạo
def nganhdaotao(request: HttpRequest):
    form_nganhdaotao = create_nganhdaotao()
    delete_success = False
    edit_success = False
    add_success = False

    if request.method == 'POST':
        if 'delete' in request.POST:
            ids_to_delete = request.POST.getlist('selected_ids')
            Nganhdaotao.objects.filter(Ma_nganh__in=ids_to_delete).delete()
            delete_success = True
            
        elif 'edit' in request.POST:
            ma_nganh = request.POST.get('Ma_nganh')
            nganh_dao_tao_instance = get_object_or_404(Nganhdaotao, Ma_nganh=ma_nganh)
            ma_bomon = request.POST.get('Ma_bo_mon')
            bomon_instance = get_object_or_404(Bomon, Ma_bo_mon=ma_bomon)
            nganh_dao_tao_instance.Ma_bo_mon = bomon_instance
            form_nganhdaotao = create_nganhdaotao(request.POST, instance=nganh_dao_tao_instance)
            if form_nganhdaotao.is_valid():
                form_nganhdaotao.save()
                edit_success = True
        else:
            form_nganhdaotao = create_nganhdaotao(request.POST)
            if form_nganhdaotao.is_valid():
                form_nganhdaotao.save()
                add_success = True
    bomons = Bomon.objects.all()
    Nganhdaotaos = Nganhdaotao.objects.all()
    return render(request, 'nganhdaotao.html', {
        'form_nganhdaotao': form_nganhdaotao,
        'Nganhdaotaos': Nganhdaotaos,
        'bomons': bomons,
        'delete_success': delete_success,
        'edit_success': edit_success,
        'add_success': add_success
    })
# ---------------------------------------------------------------------------------------------------------------------------------------
# Học kỳ niên khóa
def hknienkhoa(request: HttpRequest):
    form_hknienkhoa = create_hknienkhoa()
    delete_success = False
    edit_success = False
    add_success = False

    if request.method == 'POST':
        if 'delete' in request.POST:
            ids_to_delete = request.POST.getlist('selected_ids')
            Hockynienkhoa.objects.filter(Ma_hk_nien_khoa__in=ids_to_delete).delete()
            delete_success = True
            
        elif 'edit' in request.POST:
            ma_hk_nien_khoa = request.POST.get('Ma_hk_nien_khoa')
            hk_nien_khoa_instance = get_object_or_404(Hockynienkhoa, Ma_hk_nien_khoa=ma_hk_nien_khoa)
            form_hknienkhoa = create_hknienkhoa(request.POST, instance=hk_nien_khoa_instance)
            if form_hknienkhoa.is_valid():
                form_hknienkhoa.save()
                edit_success = True
        else:
            form_hknienkhoa = create_hknienkhoa(request.POST)
            if form_hknienkhoa.is_valid():
                form_hknienkhoa.save()
                add_success = True
    semesters = list(Hockynienkhoa.objects.all().values('Ma_hk_nien_khoa', 'Ten_hk_nien_khoa'))
    
    # Hàm để chuyển đổi học kỳ thành giá trị có thể so sánh được
    def hk_key(hk):
        parts = hk['Ma_hk_nien_khoa'].split()
        term = 0 if parts[0] == "HKI" else 1
        year = parts[1].split("-")[0]
        return (year, term)
    
    # Sắp xếp danh sách học kỳ
    sorted_semesters = sorted(semesters, key=hk_key)
    # Truyền dữ liệu đã sắp xếp vào context để hiển thị trên template
    context = {
        'hknienkhoas': sorted_semesters,
        'form_hknienkhoa': form_hknienkhoa,
        'delete_success': delete_success,
        'edit_success': edit_success,
        'add_success': add_success,
    }    
    return render(request, 'hknienkhoa.html', context)
# ---------------------------------------------------------------------------------------------------------------------------------------
# Loại học phần
def loaihocphan(request: HttpRequest):
    form_loaihocphan = create_loaihocphan()
    delete_success = False
    edit_success = False
    add_success = False

    if request.method == 'POST':
        if 'delete' in request.POST:
            ids_to_delete = request.POST.getlist('selected_ids')
            Loaihocphan.objects.filter(Ma_loai_hp__in=ids_to_delete).delete()
            delete_success = True
            
        elif 'edit' in request.POST:
            Ma_loai_hp = request.POST.get('Ma_loai_hp')
            Ma_loai_hp_instance = get_object_or_404(Loaihocphan, Ma_loai_hp=Ma_loai_hp)
            form_loaihocphan = create_loaihocphan(request.POST, instance=Ma_loai_hp_instance)
            if form_loaihocphan.is_valid():
                form_loaihocphan.save()
                edit_success = True
        else:
            form_loaihocphan = create_loaihocphan(request.POST)
            if form_loaihocphan.is_valid():
                form_loaihocphan.save()
                add_success = True
            
    loaihocphans = Loaihocphan.objects.all()
    return render(request, 'loaihocphan.html', {
        'form_loaihocphan': form_loaihocphan,
        'loaihocphans': loaihocphans,
        'delete_success': delete_success,
        'edit_success': edit_success,
        'add_success': add_success
    })
# --------------------------------------------------------------------------------------------------------------------------------------- 
# Học kỳ chương trình đào tạo
def hkctdt(request: HttpRequest):
    form_hk_ctdt = create_hk_ctdt()
    delete_success = False
    edit_success = False
    add_success = False

    if request.method == 'POST':
        if 'delete' in request.POST:
            ids_to_delete = request.POST.getlist('selected_ids')
            Hockychuongtrinhdaotao.objects.filter(Ma_HK_CTDT__in=ids_to_delete).delete()
            delete_success = True
            
        elif 'edit' in request.POST:
            Ma_HK_CTDT = request.POST.get('Ma_HK_CTDT')
            Ma_HK_CTDT_instance = get_object_or_404(Hockychuongtrinhdaotao, Ma_HK_CTDT=Ma_HK_CTDT)
            form_hk_ctdt = create_hk_ctdt(request.POST, instance=Ma_HK_CTDT_instance)
            if form_hk_ctdt.is_valid():
                form_hk_ctdt.save()
                edit_success = True
        else:
            form_hk_ctdt = create_hk_ctdt(request.POST)
            if form_hk_ctdt.is_valid():
                form_hk_ctdt.save()
                add_success = True
    hkctdts = Hockychuongtrinhdaotao.objects.all()
    return render(request, 'hk_ctdt.html', {
        'form_hk_ctdt': form_hk_ctdt,
        'hkctdts': hkctdts,
        'delete_success': delete_success,
        'edit_success': edit_success,
        'add_success': add_success
    })
# --------------------------------------------------------------------------------------------------------------------------------------- 
# Nhóm môn
def nhommon(request: HttpRequest):
    form_nhommon = create_nhommon()
    delete_success = False
    edit_success = False
    add_success = False

    if request.method == 'POST':
        if 'delete' in request.POST:
            ids_to_delete = request.POST.getlist('selected_ids')
            Nhommon.objects.filter(Ma_nhom_mon__in=ids_to_delete).delete()
            delete_success = True
            
        elif 'edit' in request.POST:
            Ma_nhom_mon = request.POST.get('Ma_nhom_mon')
            Ma_nhom_mon_instance = get_object_or_404(Nhommon, Ma_nhom_mon=Ma_nhom_mon)
            form_nhommon = create_nhommon(request.POST, instance=Ma_nhom_mon_instance)
            if form_nhommon.is_valid():
                form_nhommon.save()
                edit_success = True
        else:
            form_nhommon = create_nhommon(request.POST)
            if form_nhommon.is_valid():
                form_nhommon.save()
                add_success = True
            
    nhommons = Nhommon.objects.all()
    return render(request, 'nhommon.html', {
        'form_nhommon': form_nhommon,
        'nhommons': nhommons,
        'delete_success': delete_success,
        'edit_success': edit_success,
        'add_success': add_success
    })
# --------------------------------------------------------------------------------------------------------------------------------------- 
# Chương trình đào tạo
def ctdt(request: HttpRequest):
    form_ctdt = create_ctdt()
    delete_success = False
    edit_success = False
    add_success = False

    if request.method == 'POST':
        if 'delete' in request.POST:
            ids_to_delete = request.POST.getlist('selected_ids')
            Chuongtrinh_daotao.objects.filter(Ma_CTDT__in=ids_to_delete).delete()
            delete_success = True
            
        elif 'edit' in request.POST:
            Ma_CTDT = request.POST.get('Ma_CTDT')
            Ma_CTDT_instance = get_object_or_404(Chuongtrinh_daotao, Ma_CTDT=Ma_CTDT)
            Ma_nganh = request.POST.get('Ma_nganh')
            Ma_nganh_instance = get_object_or_404(Nganhdaotao, Ma_nganh=Ma_nganh)
            Ma_CTDT_instance.Ma_nganh = Ma_nganh_instance
            form_ctdt = create_ctdt(request.POST, instance=Ma_CTDT_instance)
            if form_ctdt.is_valid():
                form_ctdt.save()
                edit_success = True
        else:
            form_ctdt = create_ctdt(request.POST)
            if form_ctdt.is_valid():
                form_ctdt.save()
                add_success = True
            
    ctdts = Chuongtrinh_daotao.objects.all()
    Nganhdaotaos = Nganhdaotao.objects.all()
    return render(request, 'ctdt.html', {
        'form_ctdt': form_ctdt,
        'ctdts': ctdts,
        'Nganhdaotaos': Nganhdaotaos,
        'delete_success': delete_success,
        'edit_success': edit_success,
        'add_success': add_success
    })
# ---------------------------------------------------------------------------------------------------------------------------------------   
# Lớp
def lop(request: HttpRequest):
    form_lop = create_lop()
    delete_success = False
    edit_success = False
    add_success = False

    if request.method == 'POST':
        if 'delete' in request.POST:
            ids_to_delete = request.POST.getlist('selected_ids')
            Lop.objects.filter(Ma_lop__in=ids_to_delete).delete()
            delete_success = True
            
        elif 'edit' in request.POST:
            Ma_lop = request.POST.get('Ma_lop')
            Ma_lop_instance = get_object_or_404(Lop, Ma_lop=Ma_lop)
            
            Ma_CTDT = request.POST.get('Ma_CTDT')
            Ma_CTDT_instance = get_object_or_404(Chuongtrinh_daotao, Ma_CTDT=Ma_CTDT)
            
            Id_cv = request.POST.get('Id_cv')
            Id_cv_instance = get_object_or_404(Covan, Id_cv=Id_cv)
            
            Ma_lop_instance.Ma_CTDT = Ma_CTDT_instance
            Ma_lop_instance.Id_cv = Id_cv_instance
            form_lop = create_lop(request.POST, instance=Ma_lop_instance)
            if form_lop.is_valid():
                form_lop.save()
                edit_success = True
        else:
            form_lop = create_lop(request.POST)
            if form_lop.is_valid():
                form_lop.save()
                add_success = True
    ctdts = Chuongtrinh_daotao.objects.all()
    covans = Covan.objects.all()
    lops = Lop.objects.all()
    return render(request, 'lop.html', {
        'form_lop': form_lop,
        'lops': lops,
        'covans': covans,
        'ctdts': ctdts,
        'delete_success': delete_success,
        'edit_success': edit_success,
        'add_success': add_success
    })
# ---------------------------------------------------------------------------------------------------------------------------------------  
# Sinh viên
def student(request: HttpRequest):
    form_sinhvien = create_sinhvien()
    form_file = UploadFileForm()
    delete_success = False
    edit_success = False
    add_success = False
    import_success = False

    if request.method == 'POST':
        if 'delete' in request.POST:
            ids_to_delete = request.POST.getlist('selected_ids')
            Sinhvien.objects.filter(MSSV__in=ids_to_delete).delete()
            delete_success = True
            

        elif 'edit' in request.POST:
            mssv = request.POST.get('MSSV')
            MSSV_instance = get_object_or_404(Sinhvien, MSSV=mssv)
            form_sinhvien = create_sinhvien(request.POST, instance=MSSV_instance)
            if form_sinhvien.is_valid():
                form_sinhvien.save()
                edit_success = True
               
        elif 'add' in request.POST:
            form_sinhvien = create_sinhvien(request.POST)
            if form_sinhvien.is_valid():
                form_sinhvien.save()
                add_success = True
               

        elif 'import' in request.POST:
            form_file = UploadFileForm(request.POST, request.FILES)
            if form_file.is_valid():
                df = pd.read_excel(request.FILES['file'])

                # Ánh xạ các tên cột mới đến các trường trong mô hình
                df = df.rename(columns={
                    'Mã số sinh viên': 'MSSV',
                    'Họ tên sinh viên': 'Ho_ten_sv',
                    'Địa chỉ': 'Dia_chi_sv',
                    'Giới tính': 'Gioi_tinh_sv',
                    'Email': 'Email_sv',
                    'Mã lớp': 'Ma_lop',
                    'Ngày sinh': 'Ngay_sinh_sv',
                })
                for index, row in df.iterrows():
                    ma_lop = row['Ma_lop']
                    malop, created = Lop.objects.get_or_create(Ma_lop=ma_lop)
                    Sinhvien.objects.create(
                        MSSV=row['MSSV'],
                        Ho_ten_sv=row['Ho_ten_sv'],
                        Dia_chi_sv=row['Dia_chi_sv'],
                        Gioi_tinh_sv=row['Gioi_tinh_sv'],
                        Email_sv=row['Email_sv'],
                        Ma_lop=malop,
                        Ngay_sinh_sv=row['Ngay_sinh_sv'],
                    )
                add_success = True
               
    lops = Lop.objects.all()
    sinhviens = Sinhvien.objects.all()
    return render(request, 'sinhvien.html', {
        'form_sinhvien': form_sinhvien,
        'form_file': form_file,
        'sinhviens': sinhviens,
        'lops': lops,
        'delete_success': delete_success,
        'edit_success': edit_success,
        'add_success': add_success,
        'import_success': import_success
    })

# ---------------------------------------------------------------------------------------------------------------------------------------
# Bảng điểm
def bangdiem(request: HttpRequest):
    form_bangdiem = create_bangdiem()
    form_file = UploadFileForm()
    delete_success = False
    edit_success = False
    add_success = False
    import_success = False

    if request.method == 'POST':
        if 'delete' in request.POST:
            ids_to_delete = request.POST.getlist('selected_ids')
            Bangdiem.objects.filter(Ma_bang_diem__in=ids_to_delete).delete()
            delete_success = True
            

        elif 'edit' in request.POST:
            Ma_bang_diem = request.POST.get('Ma_bang_diem')
            Ma_bang_diem_instance = get_object_or_404(Bangdiem, Ma_bang_diem=Ma_bang_diem)
            form_bangdiem = create_bangdiem(request.POST, instance=Ma_bang_diem_instance)
            if form_bangdiem.is_valid():
                form_bangdiem.save()
                edit_success = True
               
        elif 'add' in request.POST:
            form_bangdiem = create_bangdiem(request.POST)
            if form_bangdiem.is_valid():
                form_bangdiem.save()
                add_success = True
               
        elif 'import' in request.POST:
            form_file = UploadFileForm(request.POST, request.FILES)
            if form_file.is_valid():
                df = pd.read_excel(request.FILES['file'])
                
                start = df[df.iloc[:, 0] == 'Họ tên:'].index.tolist()
                end = df[df.iloc[:, 0] == 'NGƯỜI LẬP BIỂU:'].index.tolist()
                try:
                    with transaction.atomic():
                        for i in range(min(len(start), len(end))):
                            start_index = start[i]
                            end_index = end[i]
                            phan1 = df.iloc[start_index:end_index, :]
                            loc_phan_1 = phan1.iloc[:, [0, 1, 2, 3, 4 ,5, 6, 7]]
                            ma_sv = phan1.loc[phan1.iloc[:, 0] == 'MSSV:', phan1.columns[1]].values[0]
                            hk = phan1.loc[phan1.iloc[:, 0] == 'HK', phan1.columns[1]].values[0]
                            tbhk = phan1.loc[phan1.iloc[:, 0] == 'ĐTBHK (H4):', phan1.columns[1]].values[0]
                            tlh4 = phan1.loc[phan1.iloc[:, 0] == 'ĐTBTL (H4):', phan1.columns[1]].values[0]
                            try:
                                hk_instance = Hockynienkhoa.objects.get(Ma_hk_nien_khoa=hk)
                            except Hockynienkhoa.DoesNotExist:
                                    print(f"Môn học với tên '{hk_instance}' không tồn tại.")
                                    continue
                                
                            try:
                                MSSV_instance = Sinhvien.objects.get(MSSV=ma_sv)
                            except Sinhvien.DoesNotExist:
                                    print(f"Môn học với tên '{MSSV_instance}' không tồn tại.")
                                    continue 
                            new_bangdiem = Bangdiem.objects.create(
                                MSSV=MSSV_instance,
                                Ma_hk_nien_khoa=hk_instance,
                                Diem_tich_luy_he_4=tlh4, 
                                Diem_trung_binh_hoc_ky = tbhk
                                            )
                            add_success = True
                            new_bangdiem_id = new_bangdiem.Ma_bang_diem
                            for index, row in phan1.iterrows():
                                if isinstance(row.iloc[0], int):
                                    try:
                                        Ma_mon_hoc_instance = Monhoc.objects.get(Ma_mon_hoc=row[1])
                                    except Monhoc.DoesNotExist:
                                        print(f"Môn học với mã '{row[1]}' không tồn tại.")
                                        continue
                                    
                                    try:
                                        Ma_bang_diem_instance = Bangdiem.objects.get(Ma_bang_diem=new_bangdiem_id)
                                    except Bangdiem.DoesNotExist:
                                        print(f"Bảng điểm với mã '{new_bangdiem_id}' không tồn tại.")
                                        continue
                                    if np.isnan(row[5]):
                                        diem_10_lan2 = "Null"  # hoặc bạn có thể thay thế bằng giá trị mặc định khác
                                    else:
                                        diem_10_lan2 = row[5]
                                    if np.isnan(row[6]):
                                        diem_he_4 = "Null" 
                                    else:
                                        diem_he_4 = row[6]    
                                
                                    Chitiet_bangdiem.objects.create(
                                        Diem_he_4=row[6],
                                        Diem_he_10=row[4],
                                        Diem_he_10_lan_2=diem_10_lan2,
                                        Ma_mon_hoc=Ma_mon_hoc_instance,
                                        Ma_bang_diem=Ma_bang_diem_instance,
                                        )
                except IntegrityError:
                    print("Có lỗi xảy ra trong quá trình nhập dữ liệu. Toàn bộ giao dịch đã bị hủy bỏ.")      
  
    bangdiems = Bangdiem.objects.all()
    hknks = Hockynienkhoa.objects.all()
    sinhviens = Sinhvien.objects.all()
    return render(request, 'bangdiem.html', {
        'form_bangdiem': form_bangdiem,
        'form_file': form_file,
        'sinhviens': sinhviens,
        'bangdiems': bangdiems,
        'hknks': hknks,
        'delete_success': delete_success,
        'edit_success': edit_success,
        'add_success': add_success,
        'import_success': import_success
    })

# ---------------------------------------------------------------------------------------------------------------------------------------
# Môn học
def monhoc(request):
    form_monhoc = create_monhoc()
    form_file = UploadFileForm()
    delete_success = False
    edit_success = False
    add_success = False
    import_success = False

    if request.method == 'POST':
        if 'delete' in request.POST:
            ids_to_delete = request.POST.getlist('selected_ids')
            Monhoc.objects.filter(Ma_mon_hoc__in=ids_to_delete).delete()
            delete_success = True
            
        elif 'edit' in request.POST:
            Ma_mon_hoc = request.POST.get('Ma_mon_hoc')
            Ma_mon_hoc_instance = get_object_or_404(Monhoc, Ma_mon_hoc=Ma_mon_hoc)
            form_monhoc = create_monhoc(request.POST, instance=Ma_mon_hoc_instance)
            if form_monhoc.is_valid():
                form_monhoc.save()
                edit_success = True
        
        elif 'add' in request.POST:
            form_monhoc = create_monhoc(request.POST)
            if form_monhoc.is_valid():
                form_monhoc.save()
                add_success = True
               
        elif 'import' in request.POST:
            form_file = UploadFileForm(request.POST, request.FILES)
            if form_file.is_valid():
                df = pd.read_excel(request.FILES['file'])

                # Ánh xạ các tên cột mới đến các trường trong mô hình
                df = df.rename(columns={
                    'Mã môn học': 'Ma_mon_hoc',
                    'Tên môn học': 'Ten_mon_hoc',
                    'Tín chỉ': 'Tin_chi',
                    'Môn tiên quyết': 'Linh_vuc',
                })

                for index, row in df.iterrows():
                    ma_mon_hoc = row['Ma_mon_hoc']
                    ten_mon_hoc = row['Ten_mon_hoc']
                    tin_chi = row['Tin_chi']
                    linh_vuc_value = row['Linh_vuc']
                    if isinstance(linh_vuc_value, str):
                        linh_vuc_value = linh_vuc_value.strip()
                    # Kiểm tra nếu giá trị là NaN thì gán None
                    if pd.isna(linh_vuc_value):
                        linh_vuc_instance = None
                    else:
                        try:
                            linh_vuc_instance = Monhoc.objects.get(Ma_mon_hoc=linh_vuc_value)
                        except Monhoc.DoesNotExist:
                            print(f"Môn học với tên '{linh_vuc_value}' không tồn tại.")
                            continue

                    Monhoc.objects.create(
                        Ma_mon_hoc=ma_mon_hoc,
                        Ten_mon_hoc=ten_mon_hoc,
                        Tin_chi=tin_chi,
                        Linh_vuc=linh_vuc_instance,
                    )

    monhocs = Monhoc.objects.all()
    return render(request, 'monhoc.html', {
        'form_monhoc': form_monhoc,
        'form_file': form_file,
        'monhocs': monhocs,
        'delete_success': delete_success,
        'edit_success': edit_success,
        'add_success': add_success,
        'import_success': import_success
    })
# ---------------------------------------------------------------------------------------------------------------------------------------
#  Chi tiết bảng điểm
def ctbd(request):
    form_ctbd = create_ctbd()
    form_file = UploadFileForm()
    delete_success = False
    edit_success = False
    add_success = False
    import_success = False

    if request.method == 'POST':
        if 'delete' in request.POST:
            ids_to_delete = request.POST.getlist('selected_ids')
            Chitiet_bangdiem.objects.filter(Ma_CTBD__in=ids_to_delete).delete()
            delete_success = True
            
        elif 'edit' in request.POST:
            Ma_CTBD = request.POST.get('Ma_CTBD')
            Ma_CTBD_instance = get_object_or_404(Chitiet_bangdiem, Ma_CTBD=Ma_CTBD)
            form_ctbd = create_ctbd(request.POST, instance=Ma_CTBD_instance)
            if form_ctbd.is_valid():
                form_ctbd.save()
                edit_success = True
        
        elif 'add' in request.POST:
            form_ctbd = create_ctbd(request.POST)
            if form_ctbd.is_valid():
                form_ctbd.save()
                add_success = True
               
        elif 'import' in request.POST:
            form_file = UploadFileForm(request.POST, request.FILES)
            if form_file.is_valid():
                df = pd.read_excel(request.FILES['file'])

                # Ánh xạ các tên cột mới đến các trường trong mô hình
                df = df.rename(columns={
                    'Mã chi tiết bảng điểm': 'Ma_CTBD',
                    'Điểm hệ 4': 'Diem_he_4',
                    'Điểm hệ 10': 'Diem_he_10',
                    'Điểm hệ 10 lần 2': 'Diem_he_10_lan_2',
                    'Mã môn học': 'Ma_mon_hoc',
                    'Mã bảng điểm': 'Ma_bang_diem'   
                           
                })
                for index, row in df.iterrows():
                    try:
                        ma_mon_hoc = row['Ma_mon_hoc']
                        Ma_monhoc = Monhoc.objects.get(Ma_mon_hoc=ma_mon_hoc)
                    except Monhoc.DoesNotExist:
                        print(f"Sinh viên với Ma_monhoc {Ma_monhoc} không tồn tại.")
                        continue   
                    
                    try:
                        ma_bang_diem = row['Ma_bang_diem']
                        Ma_bang_diem = Bangdiem.objects.get(Ma_bang_diem=ma_bang_diem)
                    except Bangdiem.DoesNotExist:
                        print(f"Sinh viên với Ma_bang_diem {Ma_bang_diem} không tồn tại.")
                        continue   
                    
                    Chitiet_bangdiem.objects.create(
                        Ma_CTBD=row['Ma_CTBD'],
                        Diem_he_4=row['Diem_he_4'],
                        Diem_he_10=row['Diem_he_10'],
                        Diem_he_10_lan_2=row['Diem_he_10_lan_2'],
                        Ma_mon_hoc=Ma_monhoc,
                        Ma_bang_diem=Ma_bang_diem,
                    )
                add_success = True
                
    monhocs = Monhoc.objects.all()
    bangdiems = Bangdiem.objects.all()
    ctbds = Chitiet_bangdiem.objects.all()
    return render(request, 'ctbd.html', {
        'form_ctbd': form_ctbd,
        'form_file': form_file,
        'monhocs': monhocs,
        'bangdiems': bangdiems,
        'ctbds': ctbds,
        'delete_success': delete_success,
        'edit_success': edit_success,
        'add_success': add_success,
        'import_success': import_success
    })
# ---------------------------------------------------------------------------------------------------------------------------------------
 #  Thuộc chương trình đào tạo
def tctdt(request):
    form_thuoc_ctdt = create_thuoc_ctdt()
    form_file = UploadFileForm()
    delete_success = False
    edit_success = False
    add_success = False
    import_success = False

    if request.method == 'POST':
        if 'delete' in request.POST:
            ids_to_delete = request.POST.getlist('selected_ids')
            thuoc_ctdt.objects.filter(id__in=ids_to_delete).delete()
            delete_success = True
            
        elif 'edit' in request.POST:
            id = request.POST.get('id')
            Ma_thuoc_CT_DT_instance = get_object_or_404(thuoc_ctdt, id=id)
            form_thuoc_ctdt = create_thuoc_ctdt(request.POST, instance=Ma_thuoc_CT_DT_instance)
            if form_thuoc_ctdt.is_valid():
                form_thuoc_ctdt.save()
                edit_success = True
        
        elif 'add' in request.POST:
            form_thuoc_ctdt = create_thuoc_ctdt(request.POST)
            if form_thuoc_ctdt.is_valid():
                form_thuoc_ctdt.save()
                add_success = True
               
        elif 'import' in request.POST:
            form_file = UploadFileForm(request.POST, request.FILES)
            if form_file.is_valid():
                df = pd.read_excel(request.FILES['file'])

                # Ánh xạ các tên cột mới đến các trường trong mô hình
                df = df.rename(columns={
                    'Mã học kỳ chương trình đào tạo': 'Ma_HK_CTDT',
                    'Mã loại học phần': 'Ma_loai_hp',
                    'Mã nhóm môn': 'Ma_nhom_mon',
                    'Mã môn học': 'Ma_mon_hoc',
                    'Mã chương trình đào tạo' : 'Ma_CTDT'
                })
                for index, row in df.iterrows():
                    try:
                        Ma_HK_CTDT = row['Ma_HK_CTDT']
                        Ma_HK_CTDT = Hockychuongtrinhdaotao.objects.get(Ma_HK_CTDT=Ma_HK_CTDT)
                    except Hockychuongtrinhdaotao.DoesNotExist:
                        print(f"Sinh viên với Ma_HK_CTDT {Ma_HK_CTDT} không tồn tại.")
                        continue   
                    
                    try:
                        Ma_loai_hp = row['Ma_loai_hp']
                        Ma_loai_hp = Loaihocphan.objects.get(Ma_loai_hp=Ma_loai_hp)
                    except Loaihocphan.DoesNotExist:
                        print(f"Sinh viên với Ma_loai_hp {Ma_loai_hp} không tồn tại.")
                        continue  
                    
                    try:
                        Ma_nhom_mon = row['Ma_nhom_mon']
                        Ma_nhom_mon = Nhommon.objects.get(Ma_nhom_mon=Ma_nhom_mon)
                    except Nhommon.DoesNotExist:
                        print(f"Sinh viên với Ma_nhom_mon {Ma_nhom_mon} không tồn tại.")
                        continue    
                     
                    try:
                        Ma_mon_hoc = row['Ma_mon_hoc']
                        Ma_mon_hoc = Monhoc.objects.get(Ma_mon_hoc=Ma_mon_hoc)
                    except Monhoc.DoesNotExist:
                        print(f"Sinh viên với Ma_mon_hoc {Ma_mon_hoc} không tồn tại.")
                        continue 
                    
                    try:
                        Ma_CTDT = row['Ma_CTDT']
                        Ma_CTDT = Chuongtrinh_daotao.objects.get(Ma_CTDT=Ma_CTDT)
                    except Chuongtrinh_daotao.DoesNotExist:
                        print(f"Sinh viên với Ma_CTDT {Ma_CTDT} không tồn tại.")
                        continue  
                    
                    thuoc_ctdt.objects.create(
                        Ma_HK_CTDT=Ma_HK_CTDT,
                        Ma_loai_hp=Ma_loai_hp,
                        Ma_nhom_mon=Ma_nhom_mon,
                        Ma_mon_hoc=Ma_mon_hoc,
                        Ma_CTDT=Ma_CTDT,
                    )
                add_success = True
                
    tctdts = thuoc_ctdt.objects.all()
    hkctdts = Hockychuongtrinhdaotao.objects.all()
    loaihocphans = Loaihocphan.objects.all()
    monhocs = Monhoc.objects.all()
    nhommons = Nhommon.objects.all()
    ctdts = Chuongtrinh_daotao.objects.all()
    return render(request, 'tctdt.html', {
        'form_thuoc_ctdt': form_thuoc_ctdt,
        'form_file': form_file,
        'monhocs': monhocs,
        'tctdts': tctdts,
        'hkctdts': hkctdts,
        'loaihocphans': loaihocphans,
        'nhommons': nhommons,
        'ctdts': ctdts,
        'delete_success': delete_success,
        'edit_success': edit_success,
        'add_success': add_success,
        'import_success': import_success
    })
# ---------------------------------------------------------------------------------------------------------------------------------------
def dlm(request):
    sinhvien_data = Sinhvien.objects.all().select_related('Ma_lop')
    bangdiem_data = Bangdiem.objects.all().select_related('MSSV', 'Ma_hk_nien_khoa')
    ctbd_data = Chitiet_bangdiem.objects.all().select_related('Ma_mon_hoc', 'Ma_bang_diem')
    thuoc_ctdt_data = thuoc_ctdt.objects.all().select_related(
        'Ma_HK_CTDT', 'Ma_loai_hp', 'Ma_nhom_mon', 'Ma_CTDT', 'Ma_mon_hoc'
    )
    msv = None
    mh = None
    lv = None
    combined_data = []
    
    for sv in sinhvien_data:
        for bd in bangdiem_data.filter(MSSV=sv):
            for ctbd in ctbd_data.filter(Ma_bang_diem=bd):
                for tc in thuoc_ctdt_data.filter(Ma_mon_hoc=ctbd.Ma_mon_hoc):
                    # Truy vấn dữ liệu từ cột 'Linh_vuc' của bảng Mon_hoc
                    mon_hoc = Monhoc.objects.get(pk=ctbd.Ma_mon_hoc.pk)
                    linh_vuc = mon_hoc.Linh_vuc
                    if linh_vuc == None:
                        
                       combined_data.append({
                                    'MSSV': sv.MSSV,
                                    'Ho_ten_sv': sv.Ho_ten_sv,
                                    'Ma_lop': sv.Ma_lop.Ma_lop,
                                    'Diem_he_4': bd.Diem_tich_luy_he_4,
                                    'Ma_mon_hoc': ctbd.Ma_mon_hoc.Ma_mon_hoc,
                                    'Ten_mon_hoc': ctbd.Ma_mon_hoc.Ten_mon_hoc,
                                    # 'Linh_vuc': linh_vuc,
                                    'Diem_he_10': ctbd.Diem_he_10,
                                    # 'Diem_Linh_vuc': ctbd_linh_vuc.Diem_he_10,
                                    'Ma_HK_CTDT': tc.Ma_HK_CTDT.Ma_HK_CTDT,
                                    'Ten_HK_CTDT': tc.Ma_HK_CTDT.Ten_HK_CTDT,
                                    'Ma_loai_hp': tc.Ma_loai_hp.Ma_loai_hp,
                                    'Ten_loai_hp': tc.Ma_loai_hp.Ten_loai_hp,
                                    'Ma_nhom_mon': tc.Ma_nhom_mon.Ma_nhom_mon,
                                    'Ten_nhom_mon': tc.Ma_nhom_mon.Ten_nhom_mon,
                                    'Ma_CTDT': tc.Ma_CTDT.Ma_CTDT,
                                    'Ten_CTDT': tc.Ma_CTDT.Ten_CTDT,
                                })
                    else:
                        for ctbd_linh_vuc in ctbd_data.filter(Ma_bang_diem__MSSV=sv , Ma_mon_hoc=linh_vuc):
                            
                            if  mh != ctbd.Ma_mon_hoc and lv != linh_vuc :
                                
                                msv = sv.MSSV
                                mh = ctbd.Ma_mon_hoc
                                lv = linh_vuc
                                combined_data.append({
                                    'MSSV': sv.MSSV,
                                    'Ho_ten_sv': sv.Ho_ten_sv,
                                    'Ma_lop': sv.Ma_lop.Ma_lop,
                                    'Diem_he_4': bd.Diem_tich_luy_he_4,
                                    'Ma_mon_hoc': ctbd.Ma_mon_hoc.Ma_mon_hoc,
                                    'Ten_mon_hoc': ctbd.Ma_mon_hoc.Ten_mon_hoc,
                                    'Linh_vuc': linh_vuc,
                                    'Diem_he_10': ctbd.Diem_he_10,
                                    'Diem_Linh_vuc': ctbd_linh_vuc.Diem_he_10,
                                    'Ma_HK_CTDT': tc.Ma_HK_CTDT.Ma_HK_CTDT,
                                    'Ten_HK_CTDT': tc.Ma_HK_CTDT.Ten_HK_CTDT,
                                    'Ma_loai_hp': tc.Ma_loai_hp.Ma_loai_hp,
                                    'Ten_loai_hp': tc.Ma_loai_hp.Ten_loai_hp,
                                    'Ma_nhom_mon': tc.Ma_nhom_mon.Ma_nhom_mon,
                                    'Ten_nhom_mon': tc.Ma_nhom_mon.Ten_nhom_mon,
                                    'Ma_CTDT': tc.Ma_CTDT.Ma_CTDT,
                                    'Ten_CTDT': tc.Ma_CTDT.Ten_CTDT,
                                })

    context = {
        'combined_data': combined_data
    }

    return render(request, 'test.html', context)
# ---------------------------------------------------------------------------------------------------------------------------------------
def export_monhoc_diem10_csv(request):
    # Lấy tất cả các bản ghi từ bảng Chitiet_bangdiem kèm theo mã môn và điểm hệ 10
    chitiet_data = Chitiet_bangdiem.objects.values('Ma_mon_hoc__Ma_mon_hoc', 'Diem_he_10')

    # Tạo DataFrame từ dữ liệu thu được
    df = pd.DataFrame(list(chitiet_data))

    # Chuyển đổi dữ liệu nếu cần thiết, ví dụ: chuyển đổi điểm hệ 10 thành số nếu là float
    df['Diem_he_10'] = df['Diem_he_10'].astype(float)

    # Tạo tên cho file CSV
    csv_filename = "monhoc_diem10.csv"

    # Tạo response để trả về file CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{csv_filename}"'

    # Xuất DataFrame sang file CSV
    df.to_csv(path_or_buf=response, index=False)

    return response