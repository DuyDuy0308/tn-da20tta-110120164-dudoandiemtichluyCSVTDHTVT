import pandas as pd
from django.apps import apps
import os, base64
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from django.db.models import Count
from django.http import HttpRequest, HttpResponse, FileResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from .forms import  create_covan, UploadFileForm, create_sinhvien, create_khoa, create_bomon, create_nganhdaotao, create_hknienkhoa, create_loaihocphan, create_hk_ctdt, create_nhommon, create_ctdt, create_lop, create_bangdiem, create_monhoc, create_ctbd
from .models import  Covan, Sinhvien, Khoa, Bomon, Nganhdaotao, Hockynienkhoa, Loaihocphan, Hockychuongtrinhdaotao, Nhommon, Chuongtrinh_daotao, Bangdiem, Lop, Monhoc, Chitiet_bangdiem, thuoc_ctdt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder
import joblib

# Create your views here.
def index(request, id_cv):
     # Lấy giảng viên dựa vào ID
    giang_vien = get_object_or_404(Covan, Id_cv=id_cv)
    lops = Lop.objects.all()
    # Lấy lớp của giảng viên
    lop = Lop.objects.filter(Id_cv=giang_vien).first()
    danh_sach_lop = Sinhvien.objects.filter(Ma_lop=lop.Ma_lop)    
    return render(request, 'cv_main.html', {
        'giang_viens': giang_vien,
        'lops': lops,
        'danh_sach_lop': danh_sach_lop})
    
def sv(request, id_cv):
     # Lấy giảng viên dựa vào ID
    giang_vien = get_object_or_404(Covan, Id_cv=id_cv)
    lops = Lop.objects.all()
    # Lấy lớp của giảng viên
    lop = Lop.objects.filter(Id_cv=giang_vien).first()
    danh_sach_lop = Sinhvien.objects.filter(Ma_lop=lop.Ma_lop)
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
               
    return render(request, 'hienthi_cv.html', {
        'form_sinhvien': form_sinhvien,
        'form_file': form_file,
        'giang_viens': giang_vien,
        'lops': lops,
        'delete_success': delete_success,
        'edit_success': edit_success,
        'add_success': add_success,
        'import_success': import_success
        , 'danh_sach_lop': danh_sach_lop})
    
def diem(request, id_cv):
     # Lấy giảng viên dựa vào ID
    giang_vien = get_object_or_404(Covan, Id_cv=id_cv)
    lops = Lop.objects.all()
    # Lấy lớp của giảng viên
    lop = Lop.objects.filter(Id_cv=giang_vien).first()
    danh_sach_lop = Sinhvien.objects.filter(Ma_lop=lop.Ma_lop)
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

                df = df.rename(columns={
                    'Mã bảng điểm': 'Ma_bang_diem',
                    'Điểm hệ 4': 'Diem_tich_luy_he_4',
                    'Mã số sinh viên': 'MSSV',
                    'Mã học kỳ niên khóa': 'Ma_hk_nien_khoa',
                })
                for index, row in df.iterrows():
                    try:
                        mssv = row['MSSV']
                        MSSVien = Sinhvien.objects.get(MSSV=mssv)
                    except Sinhvien.DoesNotExist:
                        print(f"Sinh viên với MSSV {mssv} không tồn tại.")
                        continue 

                    try:
                        ma_hk_nien_khoa = row['Ma_hk_nien_khoa']
                        Ma_hk_nien_khoa = Hockynienkhoa.objects.get(Ma_hk_nien_khoa=ma_hk_nien_khoa)
                    except Hockynienkhoa.DoesNotExist:
                        print(f"Sinh viên với MSSV {ma_hk_nien_khoa} không tồn tại.")
                        continue 
    
                    Bangdiem.objects.create(
                        MSSV=MSSVien,
                        Ma_hk_nien_khoa=Ma_hk_nien_khoa,
                        Ma_bang_diem=row['Ma_bang_diem'],
                        Diem_tich_luy_he_4=row['Diem_tich_luy_he_4'], 
                                    )
                    add_success = True
               
    bangdiems = Bangdiem.objects.filter(MSSV__Ma_lop=lop.Ma_lop)
    hknks = Hockynienkhoa.objects.all()
    sinhviens = Sinhvien.objects.all()
    return render(request, 'diem_cv.html', {
        'form_bangdiem': form_bangdiem,
        'form_file': form_file,
        'sinhviens': sinhviens,
        'bangdiems': bangdiems,
        'hknks': hknks,
        'delete_success': delete_success,
        'edit_success': edit_success,
        'add_success': add_success,
        'import_success': import_success,
        'giang_viens': giang_vien,
        'lops': lops,
        'danh_sach_lop': danh_sach_lop
    })
# -=----------------------------------------------------------------------------------------------
def ct_diem(request, id_cv):
    giang_vien = get_object_or_404(Covan, Id_cv=id_cv) 
    lop = Lop.objects.filter(Id_cv=giang_vien).first()
    danh_sach_lop = Sinhvien.objects.filter(Ma_lop=lop.Ma_lop)
    
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
               
    bangdiems = Bangdiem.objects.filter(MSSV__Ma_lop=lop.Ma_lop)
    hknks = Hockynienkhoa.objects.all()
    sinhviens = Sinhvien.objects.all()
    ctbds = Chitiet_bangdiem.objects.filter(Ma_bang_diem__in=bangdiems)
    monhocs = Monhoc.objects.all()
    return render(request, 'ct_diem.html', {
        'form_ctbd': form_ctbd,
        'form_file': form_file,
        'sinhviens': sinhviens,
        'ctbds': ctbds,
        'hknks': hknks,
        'monhocs': monhocs,
        'bangdiems': bangdiems,
        'delete_success': delete_success,
        'edit_success': edit_success,
        'add_success': add_success,
        'import_success': import_success,
        'giang_viens': giang_vien,
        'danh_sach_lop': danh_sach_lop
    })
    
