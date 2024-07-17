import pandas as pd
from django.apps import apps
import os, base64, io
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from django.db.models import Count, Q, Avg, F
from django.http import HttpRequest, HttpResponse, FileResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from .forms import DuDoanDiemForm, HockySelectForm, create_sinhvien
from .models import  Covan, Sinhvien, Khoa, Bomon, Nganhdaotao, Hockynienkhoa, Loaihocphan, Hockychuongtrinhdaotao, Nhommon, Chuongtrinh_daotao, Bangdiem, Lop, Monhoc, Chitiet_bangdiem, thuoc_ctdt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder
import joblib
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
def student_index(request, MSSV):
    SV = get_object_or_404(Sinhvien, MSSV=MSSV)
    bangdiems = Bangdiem.objects.filter(MSSV=SV)
    chi_tiet_diem = Chitiet_bangdiem.objects.filter(Ma_bang_diem__in=bangdiems)

    # Lấy top 5 điểm cao nhất và thấp nhất
    top_5_scores = chi_tiet_diem.order_by('-Diem_he_4')[:5]
    bottom_5_scores = chi_tiet_diem.order_by('Diem_he_4')[:5]
    so_mon_da_co_diem = chi_tiet_diem.count()
    total_Monhoc = Monhoc.objects.count()
    
    total_credit_program = Monhoc.objects.aggregate(total_credit_program=Sum('Tin_chi'))['total_credit_program']
    if total_credit_program is None:
        total_credit_program = 0

    # Calculate total credits achieved by the student
    total_credit_achieved = chi_tiet_diem.aggregate(total_credit_achieved=Sum('Ma_mon_hoc__Tin_chi'))['total_credit_achieved']
    if total_credit_achieved is None:
        total_credit_achieved = 0

    # Calculate completion percentage
    if total_credit_program > 0:
        completion_percentage = (total_credit_achieved / total_credit_program) * 100
    else:
        completion_percentage = 0


    # Trích xuất dữ liệu cho biểu đồ
    top_bottom_scores = list(top_5_scores) + list(bottom_5_scores)
    score_labels = [f"{item.Ma_mon_hoc.Ma_mon_hoc} ({item.Diem_he_4})" for item in top_bottom_scores]
    score_data = [float(item.Diem_he_4) for item in top_bottom_scores]

    context = {
        'SV': SV,
        'so_mon_da_co_diem': so_mon_da_co_diem,
        'total_Monhoc': total_Monhoc,
         'total_credit_achieved': total_credit_achieved,
        'total_credit_program': total_credit_program,
        'completion_percentage': completion_percentage,
        'chi_tiet_diem': chi_tiet_diem,
        'score_labels': score_labels,
        'score_data': score_data,
    }
    return render(request, 'index_SV.html', context)
# -------------------------------------------------------------------------------------------------------------------------------------------------
def ttcn(request, MSSV):
    # Lấy sinh viên và thông tin lớp của sinh viên
    SV = get_object_or_404(Sinhvien, MSSV=MSSV)
    lop = SV.Ma_lop
    edit_success = False
    # Lấy bảng điểm mới nhất của sinh viên (sắp xếp theo thời gian)
    latest_bang_diem = Bangdiem.objects.filter(MSSV=SV).order_by('-Ma_hk_nien_khoa').first()

    if latest_bang_diem:
        latest_gpa = latest_bang_diem.Diem_tich_luy_he_4
        latest_hk_nien_khoa = latest_bang_diem.Ma_hk_nien_khoa
    else:
        latest_gpa = None
        latest_hk_nien_khoa = None
        
    if request.method == 'POST':
        form = create_sinhvien(request.POST, instance=SV)
        if form.is_valid():
            form.save()
            edit_success = True
    else:
        form = create_sinhvien(instance=SV)  
          
    context = {
        'form': form,
        'edit_success': edit_success,
        'SV': SV,
        'lop': lop,
        'latest_gpa': latest_gpa,
        'latest_hk_nien_khoa': latest_hk_nien_khoa,
    }

    return render(request, 'ttcn.html', context)
# -------------------------------------------------------------------------------------------------------------------------------------------------
def dudoan(request, MSSV):
    SV = get_object_or_404(Sinhvien, MSSV=MSSV) 
    hoc_ky_list = Hockynienkhoa.objects.all()
    selected_hoc_ky = request.GET.get('hoc_ky')
    sinhvien = get_object_or_404(Sinhvien, MSSV=MSSV)
    if selected_hoc_ky:
        selected_hoc_ky = Hockynienkhoa.objects.get(Ma_hk_nien_khoa=selected_hoc_ky)
        bang_diem_list = Bangdiem.objects.filter(Ma_hk_nien_khoa=selected_hoc_ky, MSSV=sinhvien)
    else:
        selected_hoc_ky = None
        bang_diem_list = []

    context = {
        
        'hoc_ky_list': hoc_ky_list,
        'selected_hoc_ky': selected_hoc_ky,
        'bang_diem_list': bang_diem_list,
        'SV': SV,
    }
    return render(request, 'dudoan.html', context)
# --------------------------------------------------------------------------------------------------------------------------------------------------
def dudoandiem(request, MSSV):
    SV = get_object_or_404(Sinhvien, MSSV=MSSV)
    hoc_ky_list = Bangdiem.objects.filter(MSSV=SV).values_list('Ma_hk_nien_khoa', flat=True).distinct()
    hoc_ky = request.GET.get('hoc_ky', None)
    if hoc_ky:
        bangdiem_data = Bangdiem.objects.filter(MSSV=SV, Ma_hk_nien_khoa=hoc_ky)
    else:
        bangdiem_data = Bangdiem.objects.filter(MSSV=SV)
    combined_data = []
    for bd in bangdiem_data:
        ctbd_data = Chitiet_bangdiem.objects.filter(Ma_bang_diem=bd)
        for ctbd in ctbd_data:
            thuoc_ctdt_data = thuoc_ctdt.objects.filter(Ma_mon_hoc=ctbd.Ma_mon_hoc)
            for tc in thuoc_ctdt_data:
                mon_hoc = Monhoc.objects.get(pk=ctbd.Ma_mon_hoc.pk)
                linh_vuc = mon_hoc.Linh_vuc
                if linh_vuc is None:
                    combined_data.append({
                        'MSSV': SV.MSSV,
                        'Ho_ten_sv': SV.Ho_ten_sv,
                        'Ma_lop': SV.Ma_lop.Ma_lop,
                        'Diem_he_4': bd.Diem_tich_luy_he_4,
                        'Ma_mon_hoc': ctbd.Ma_mon_hoc.Ma_mon_hoc,
                        'Ten_mon_hoc': ctbd.Ma_mon_hoc.Ten_mon_hoc,
                        'Diem_he_10': ctbd.Diem_he_10,
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
                    ctbd_linh_vuc = Chitiet_bangdiem.objects.filter(Ma_mon_hoc=linh_vuc, Ma_bang_diem__MSSV=SV).first()
                    if ctbd_linh_vuc:
                        combined_data.append({
                            'MSSV': SV.MSSV,
                            'Ho_ten_sv': SV.Ho_ten_sv,
                            'Ma_lop': SV.Ma_lop.Ma_lop,
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
                    else:
                        combined_data.append({
                            'MSSV': SV.MSSV,
                            'Ho_ten_sv': SV.Ho_ten_sv,
                            'Ma_lop': SV.Ma_lop.Ma_lop,
                            'Diem_he_4': bd.Diem_tich_luy_he_4,
                            'Ma_mon_hoc': ctbd.Ma_mon_hoc.Ma_mon_hoc,
                            'Ten_mon_hoc': ctbd.Ma_mon_hoc.Ten_mon_hoc,
                            'Linh_vuc': linh_vuc,
                            'Diem_he_10': ctbd.Diem_he_10,
                            'Diem_Linh_vuc': None,
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
        'SV' : SV,
        'combined_data': combined_data,
        'hoc_ky_list': hoc_ky_list,
        'selected_hoc_ky': hoc_ky,
        'MSSV': MSSV,
    }
    return render(request, 'dudoandiem.html', context)
# ------------------------------------------------------------------------------------------------------------------------------------------------------
def predict(request, MSSV):
    df = pd.read_csv('file.csv')
    df.dropna(inplace=True)
    X = df[['Ma_mon_hoc', 'Diem_he_10', 'Linh_vuc']]
    y = df['Diem_Linh_vuc']

    lin_reg = LinearRegression()
    lin_reg.fit(X, y)
    y_pred_lin = lin_reg.predict(X)
    r2_lin = r2_score(y, y_pred_lin)
    mse_lin = mean_squared_error(y, y_pred_lin)

    rf_reg = RandomForestRegressor()
    rf_reg.fit(X, y)
    y_pred_rf = rf_reg.predict(X)
    r2_rf = r2_score(y, y_pred_rf)
    mse_rf = mean_squared_error(y, y_pred_rf)

    # Vẽ biểu đồ Hồi quy tuyến tính
    plt.figure(figsize=(12, 6))
    plt.scatter(y, y_pred_lin, label='Dự đoán')
    plt.plot([y.min(), y.max()], [y.min(), y.max()], 'k--', lw=4, label='Hồi quy tuyến tính')
    plt.title('Biểu đồ hồi quy tuyến tính bội')
    plt.xlabel('Thực tế')
    plt.ylabel('Dự đoán')
    plt.legend()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64_lin = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()

    # Clear figure để vẽ biểu đồ Random Forest
    plt.clf()

    # Vẽ biểu đồ Random Forest
    plt.figure(figsize=(12, 6))
    plt.scatter(range(len(y)), y, label='Thực tế')
    plt.scatter(range(len(y)), y_pred_rf, label='Dự đoán')
    plt.title('Biểu đồ Random Forest')
    plt.xlabel('Index')
    plt.ylabel('Diem_Linh_vuc')
    plt.legend()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64_rf = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()

    SV = get_object_or_404(Sinhvien, MSSV=MSSV)

    if request.method == 'POST':
        ma_mon_hoc_input = request.POST.get('ma_mon_hoc')
        diem_he_10_input = float(request.POST.get('diem'))
        linh_vuc_input = request.POST.get('linh_vuc')

        new_data = pd.DataFrame([[ma_mon_hoc_input, diem_he_10_input, linh_vuc_input]],
                                columns=['Ma_mon_hoc', 'Diem_he_10', 'Linh_vuc'])

        # Dự đoán
        new_pred_lin = lin_reg.predict(new_data)
        new_pred_rf = rf_reg.predict(new_data)

        context = {
            'SV': SV,
            'linear_regression': {
                'coefficients': lin_reg.coef_.tolist(),
                'intercept': lin_reg.intercept_,
                'r2_score': r2_lin,
                'mean_squared_error': mse_lin,
                'new_prediction': new_pred_lin[0]
            },
            'random_forest': {
                'r2_score': r2_rf,
                'mean_squared_error': mse_rf,
                'new_prediction': new_pred_rf[0]
            },
            'plot_lin': image_base64_lin,
            'plot_rf': image_base64_rf
        }
        return render(request, 'ketqua.html', context)

    context = {
        'SV': SV,
        'linear_regression': {
            'coefficients': lin_reg.coef_.tolist(),
            'intercept': lin_reg.intercept_,
            'r2_score': r2_lin,
            'mean_squared_error': mse_lin
        },
        'random_forest': {
            'r2_score': r2_rf,
            'mean_squared_error': mse_rf
        },
        'plot_lin': image_base64_lin,
        'plot_rf': image_base64_rf
    }

    return render(request, 'ketqua.html', context)
#-------------------------------------------------------------------------------------------------------------------------------------
def hoc_ky_mon_hoc_view(request, MSSV):
    SV = Sinhvien.objects.get(MSSV=MSSV)
    bd = Bangdiem.objects.filter(MSSV=SV)
    mon_hoc_list = []
    
    current_bangdiem = Bangdiem.objects.filter(MSSV=MSSV).order_by('-Ma_bang_diem').first()
    current_gpa = current_bangdiem.Diem_tich_luy_he_4 if current_bangdiem else "Không có dữ liệu"
    if request.method == 'POST':
        form = HockySelectForm(request.POST)
        if form.is_valid():
            ma_hk_ctdt = form.cleaned_data['Ma_HK_CTDT']
            
            # Lấy danh sách các môn học liên quan đến kỳ CTĐT đã chọn
            thuoc_ctdt_records = thuoc_ctdt.objects.filter(Ma_HK_CTDT=ma_hk_ctdt)
            ma_mon_hoc_list = [record.Ma_mon_hoc_id for record in thuoc_ctdt_records]
            
            # Lọc chi tiết bảng điểm theo bảng điểm và môn học đã chọn
            for bangdiem in bd:
                chi_tiet_bangdiem = Chitiet_bangdiem.objects.filter(Ma_bang_diem=bangdiem, Ma_mon_hoc_id__in=ma_mon_hoc_list)
                for ctbd in chi_tiet_bangdiem:
                    mon_hoc = Monhoc.objects.get(Ma_mon_hoc=ctbd.Ma_mon_hoc_id)
                    mon_hoc_list.append({
                        'ma_mon_hoc': mon_hoc.Ma_mon_hoc,
                        'ten_mon_hoc': mon_hoc.Ten_mon_hoc,
                        'diem_he_4': ctbd.Diem_he_4,
                        'diem_he_10': ctbd.Diem_he_10,
                        'diem_he_10_lan_2': ctbd.Diem_he_10_lan_2,
                        'co_diem': True,  # Đánh dấu môn đã có điểm
                    })
            
            # Lấy danh sách các môn học chưa có điểm
            mon_hoc_all = Monhoc.objects.filter(Ma_mon_hoc__in=ma_mon_hoc_list).exclude(Ma_mon_hoc__in=[mh['ma_mon_hoc'] for mh in mon_hoc_list])
            for mon_hoc in mon_hoc_all:
                mon_hoc_list.append({
                    'ma_mon_hoc': mon_hoc.Ma_mon_hoc,
                    'ten_mon_hoc': mon_hoc.Ten_mon_hoc,
                    'diem_he_4': None,
                    'diem_he_10': None,
                    'diem_he_10_lan_2': None,
                    'co_diem': False,  # Đánh dấu môn chưa có điểm
                })
    else:
        form = HockySelectForm()
        
    all_co_diem = all(mon_hoc['co_diem'] for mon_hoc in mon_hoc_list)
    all_no_diem = all(not mon_hoc['co_diem'] for mon_hoc in mon_hoc_list)
    context = {
        'SV': SV,
        'mon_hoc_list': mon_hoc_list,
        'current_gpa': current_gpa,
        'form': form,
        'all_no_diem': all_no_diem,
        'all_co_diem': all_co_diem
    }
    return render(request, 'hoc_ky_mon_hoc.html', context)

#-------------------------------------------------------------------------------------------------------------------------------------
from django.shortcuts import render
from django.db.models import Avg
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error
import pandas as pd
from .models import Sinhvien, Bangdiem, Chitiet_bangdiem

def compare_gpa_view(request, MSSV):
    SV = Sinhvien.objects.get(MSSV=MSSV)
    current_bangdiem = Bangdiem.objects.filter(MSSV=MSSV).order_by('-Ma_bang_diem').first()
    
    if current_bangdiem:
        current_gpa_str = current_bangdiem.Diem_tich_luy_he_4
        try:
            current_gpa = float(current_gpa_str)
        except ValueError:
            current_gpa = None
    else:
        current_gpa = None
    
    # Chia điểm tích lũy hệ 4 thành 8 khung điểm
    gpa_ranges = {
        '0.0-1.0': [],
        '1.0-1.5': [],
        '1.5-2.0': [],
        '2.0-2.5': [],
        '2.5-3.0': [],
        '3.0-3.5': [],
        '3.5-4.0': [],
    }

    ma_mon_hocs = []

    if request.method == "POST":
        ma_mon_hocs = request.POST.getlist('ma_mon_hoc')
    average_linear_reg = 0
    average_random_forest = 0
    average_scores = {}
    if current_gpa is not None:
        for range_key in gpa_ranges:
            range_start, range_end = map(float, range_key.split('-'))
            if range_start <= current_gpa < range_end:
                condition = Q(Diem_tich_luy_he_4__gte=range_start) & Q(Diem_tich_luy_he_4__lt=range_end)
                bangdiem_list = Bangdiem.objects.filter(condition)
                
                for ma_mon_hoc in ma_mon_hocs:
                    avg_score = Chitiet_bangdiem.objects.filter(
                        Ma_bang_diem__in=bangdiem_list,
                        Ma_mon_hoc=ma_mon_hoc
                    ).aggregate(Avg('Diem_he_10'))['Diem_he_10__avg']
                    
                    if avg_score is not None:
                        avg_score = round(avg_score, 1)
                    average_scores[ma_mon_hoc] = avg_score

                gpa_ranges[range_key] = bangdiem_list
                break

    df = pd.read_csv('monhoc_diem10.csv')
    df.dropna(inplace=True)
    X = df[['Ma_mon_hoc']]
    y = df['Diem_he_10']

    # Huấn luyện mô hình hồi quy tuyến tính
    lin_reg = LinearRegression()
    lin_reg.fit(X, y)
    y_pred_lin = lin_reg.predict(X)
    r2_lin = r2_score(y, y_pred_lin)
    mse_lin = mean_squared_error(y, y_pred_lin)

    # Huấn luyện mô hình rừng ngẫu nhiên
    rf_reg = RandomForestRegressor()
    rf_reg.fit(X, y)
    y_pred_rf = rf_reg.predict(X)
    r2_rf = r2_score(y, y_pred_rf)
    mse_rf = mean_squared_error(y, y_pred_rf)

    # Dự đoán với từng mã môn học
    linear_reg_results = []
    random_forest_results = []

    for ma_mon_hoc in ma_mon_hocs:
        avg_score = average_scores.get(ma_mon_hoc)
        if avg_score is not None:
            new_data = pd.DataFrame({'Ma_mon_hoc': [ma_mon_hoc], 'Diem_he_10': [avg_score]})
            
            # Dự đoán với mô hình hồi quy tuyến tính
            new_pred_lin = lin_reg.predict(new_data[['Ma_mon_hoc']])
            linear_reg_results.append({
                'ma_mon_hoc': ma_mon_hoc,
                'new_prediction': new_pred_lin[0] if len(new_pred_lin) > 0 else None
            })

            # Dự đoán với mô hình rừng ngẫu nhiên
            new_pred_rf = rf_reg.predict(new_data[['Ma_mon_hoc']])
            random_forest_results.append({
                'ma_mon_hoc': ma_mon_hoc,
                'new_prediction': new_pred_rf[0] if len(new_pred_rf) > 0 else None
            })
        def convert_to_gpa_range(score):
            if 9.0 <= score <= 10.0:
                return 4
            elif 8.0 <= score < 9.0:
                return 3.5
            elif 7.0 <= score < 8.0:
                return 3
            elif 6.5 <= score < 7.0:
                return 2.5
            elif 5.5 <= score < 6.5:
                return 2
            elif 5.0 <= score < 5.5:
                return 1.5
            elif 4.0 <= score < 5.0:
                return 1
            else:
                return 0

        linear_reg_converted = [convert_to_gpa_range(res['new_prediction']) for res in linear_reg_results if res['new_prediction'] is not None]
        random_forest_converted = [convert_to_gpa_range(res['new_prediction']) for res in random_forest_results if res['new_prediction'] is not None]

        average_linear_reg = sum(linear_reg_converted) / len(linear_reg_converted) if linear_reg_converted else 0
        average_random_forest = sum(random_forest_converted) / len(random_forest_converted) if random_forest_converted else 0
    context = {
        'SV': SV,
        'current_gpa': current_gpa,
        'linear_regression_results': linear_reg_results,
        'random_forest_results': random_forest_results,
        'average_linear_reg': average_linear_reg,
        'average_random_forest': average_random_forest,
        'linear_regression': {
            'coefficients': lin_reg.coef_.tolist(),
            'intercept': lin_reg.intercept_,
            'r2_score': r2_lin,
            'mean_squared_error': mse_lin,
        },
        'random_forest': {
            'r2_score': r2_rf,
            'mean_squared_error': mse_rf,
        },
        'average_scores': average_scores,
    }

    return render(request, 'dudoanky.html', context)