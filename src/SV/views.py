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
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.feature_selection import SelectKBest, f_regression
from django.db.models import Sum
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
from django.shortcuts import render, get_object_or_404
from .models import Sinhvien, Bangdiem, Chitiet_bangdiem, Monhoc, thuoc_ctdt

def dudoandiem(request, MSSV):
    SV = get_object_or_404(Sinhvien, MSSV=MSSV)
    hoc_ky_list = Bangdiem.objects.filter(MSSV=SV).values_list('Ma_hk_nien_khoa', flat=True).distinct()
    hoc_ky = request.GET.get('hoc_ky', None)
    
    if hoc_ky:
        bangdiem_data = Bangdiem.objects.filter(MSSV=SV, Ma_hk_nien_khoa=hoc_ky)
    else:
        bangdiem_data = Bangdiem.objects.filter(MSSV=SV)
    
    all_monhoc_data = Monhoc.objects.all()
    combined_data = []
    
    for mon_hoc in all_monhoc_data:
        linh_vuc = mon_hoc.Linh_vuc
        ctbd_data = Chitiet_bangdiem.objects.filter(Ma_mon_hoc=mon_hoc, Ma_bang_diem__MSSV=SV)
        
        if ctbd_data.exists():
            ctbd = ctbd_data.first()
            bd = ctbd.Ma_bang_diem
            thuoc_ctdt_data = thuoc_ctdt.objects.filter(Ma_mon_hoc=ctbd.Ma_mon_hoc, Ma_CTDT=SV.Ma_lop.Ma_CTDT).first()
            combined_data.append({
                'MSSV': SV.MSSV,
                'Ho_ten_sv': SV.Ho_ten_sv,
                'Ma_lop': SV.Ma_lop.Ma_lop,
                'Diem_he_4': bd.Diem_tich_luy_he_4 if bd else None,
                'Ma_mon_hoc': mon_hoc.Ma_mon_hoc,
                'Ten_mon_hoc': mon_hoc.Ten_mon_hoc,
                'Linh_vuc': linh_vuc,
                'Diem_he_10': ctbd.Diem_he_10 if ctbd else None,
                'Ma_HK_CTDT': thuoc_ctdt_data.Ma_HK_CTDT.Ma_HK_CTDT if thuoc_ctdt_data else None,
                'Ten_HK_CTDT': thuoc_ctdt_data.Ma_HK_CTDT.Ten_HK_CTDT if thuoc_ctdt_data else None,
                'Ma_loai_hp': thuoc_ctdt_data.Ma_loai_hp.Ma_loai_hp if thuoc_ctdt_data else None,
                'Ten_loai_hp': thuoc_ctdt_data.Ma_loai_hp.Ten_loai_hp if thuoc_ctdt_data else None,
                'Ma_nhom_mon': thuoc_ctdt_data.Ma_nhom_mon.Ma_nhom_mon if thuoc_ctdt_data else None,
                'Ten_nhom_mon': thuoc_ctdt_data.Ma_nhom_mon.Ten_nhom_mon if thuoc_ctdt_data else None,
                'Ma_CTDT': thuoc_ctdt_data.Ma_CTDT.Ma_CTDT if thuoc_ctdt_data else None,
                'Ten_CTDT': thuoc_ctdt_data.Ma_CTDT.Ten_CTDT if thuoc_ctdt_data else None,
            })
        else:
            thuoc_ctdt_data = thuoc_ctdt.objects.filter(Ma_mon_hoc=mon_hoc, Ma_CTDT=SV.Ma_lop.Ma_CTDT).first()
            combined_data.append({
                'MSSV': SV.MSSV,
                'Ho_ten_sv': SV.Ho_ten_sv,
                'Ma_lop': SV.Ma_lop.Ma_lop,
                'Diem_he_4': None,
                'Ma_mon_hoc': mon_hoc.Ma_mon_hoc,
                'Ten_mon_hoc': mon_hoc.Ten_mon_hoc,
                'Linh_vuc': linh_vuc,
                'Diem_he_10': None,
                'Diem_Linh_vuc': None,
                'Ma_HK_CTDT': thuoc_ctdt_data.Ma_HK_CTDT.Ma_HK_CTDT if thuoc_ctdt_data else None,
                'Ten_HK_CTDT': thuoc_ctdt_data.Ma_HK_CTDT.Ten_HK_CTDT if thuoc_ctdt_data else None,
                'Ma_loai_hp': thuoc_ctdt_data.Ma_loai_hp.Ma_loai_hp if thuoc_ctdt_data else None,
                'Ten_loai_hp': thuoc_ctdt_data.Ma_loai_hp.Ten_loai_hp if thuoc_ctdt_data else None,
                'Ma_nhom_mon': thuoc_ctdt_data.Ma_nhom_mon.Ma_nhom_mon if thuoc_ctdt_data else None,
                'Ten_nhom_mon': thuoc_ctdt_data.Ma_nhom_mon.Ten_nhom_mon if thuoc_ctdt_data else None,
                'Ma_CTDT': thuoc_ctdt_data.Ma_CTDT.Ma_CTDT if thuoc_ctdt_data else None,
                'Ten_CTDT': thuoc_ctdt_data.Ma_CTDT.Ten_CTDT if thuoc_ctdt_data else None,
            })
    
    context = {
        'SV': SV,
        'combined_data': combined_data,
        'hoc_ky_list': hoc_ky_list,
        'selected_hoc_ky': hoc_ky,
        'MSSV': MSSV,
    }
    return render(request, 'dudoandiem.html', context)

# ------------------------------------------------------------------------------------------------------------------------------------------------------
# from sklearn.feature_selection import SelectKBest, f_regression
# from sklearn.preprocessing import StandardScaler
# from sklearn.impute import SimpleImputer
# df = pd.read_csv('DA19TT_he10.csv')
# def predict(request, MSSV):
#     SV = get_object_or_404(Sinhvien, MSSV=MSSV)
#     df.fillna(df.mean(), inplace=True)
#     if request.method == 'POST':
#         target_column = request.POST.get('linh_vuc')
        
#         # Chọn dữ liệu cho đặc trưng và nhãn
#         X = df.drop(columns=['110002'])
#         y = df['110002']
        
#         # Kiểm tra và xử lý dữ liệu bị thiếu
#         imputer = SimpleImputer(strategy='mean')
#         X = imputer.fit_transform(X)
#         y = y.fillna(y.mean())
        
#         # Chuẩn hóa dữ liệu
#         scaler = StandardScaler()
#         X = scaler.fit_transform(X)
        
#         # Chia tách dữ liệu thành tập huấn luyện và tập kiểm tra
#         X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
#         # Chọn 5 đặc trưng tốt nhất trên tập huấn luyện
#         selector = SelectKBest(score_func=f_regression, k=5)
#         X_train_selected = selector.fit_transform(X_train, y_train)
#         X_test_selected = selector.transform(X_test)
        
#         # Kiểm tra kết quả của SelectKBest
#         print("X_train_selected:", X_train_selected)
#         print("X_test_selected:", X_test_selected)
        
#         # Huấn luyện mô hình Linear Regression
#         lin_reg = LinearRegression()
#         lin_reg.fit(X_train_selected, y_train)
#         y_pred_lin = lin_reg.predict(X_test_selected)
#         r2_lin = r2_score(y_test, y_pred_lin)
#         mse_lin = mean_squared_error(y_test, y_pred_lin)
        
#         print("Linear Regression R2:", r2_lin)
#         print("Linear Regression MSE:", mse_lin)
#         print("Linear Regression Predictions:", y_pred_lin)
        
#         # Huấn luyện mô hình Random Forest Regressor
#         rf_reg = RandomForestRegressor()
#         rf_reg.fit(X_train_selected, y_train)
#         y_pred_rf = rf_reg.predict(X_test_selected)
#         r2_rf = r2_score(y_test, y_pred_rf)
#         mse_rf = mean_squared_error(y_test, y_pred_rf)
        
#         print("Random Forest R2:", r2_rf)
#         print("Random Forest MSE:", mse_rf)
#         print("Random Forest Predictions:", y_pred_rf)


#         context = {
#             'SV': SV,
#             'linear_regression': {
#                 'coefficients': lin_reg.coef_.tolist(),
#                 'intercept': lin_reg.intercept_,
#                 'r2_score': r2_lin,
#                 'mean_squared_error': mse_lin,
#             },
#             'random_forest': {
#                 'r2_score': r2_rf,
#                 'mean_squared_error': mse_rf,
#             },
           
#         }
#         return render(request, 'ketqua.html', context)

    

#     return render(request, 'ketqua.html', context)
#-------------------------------------------------------------------------------------------------------------------------------------
# def predict(request, MSSV):
#     dfnew = pd.read_csv('dlm_data.csv')
    
#     df = dfnew[['Diem_he_10', 'Diem_Linh_vuc']]
#     df.dropna(inplace=True)
#     df = dfnew[(dfnew['Ma_mon_hoc'] == 110000) & (dfnew['Linh_vuc'] == 110002)]
#     X = df[['Diem_he_10']]
#     y = df['Diem_Linh_vuc']

#     lin_reg = LinearRegression()
#     lin_reg.fit(X, y)
#     y_pred_lin = lin_reg.predict(X)
#     r2_lin = r2_score(y, y_pred_lin)
#     mse_lin = mean_squared_error(y, y_pred_lin)

#     rf_reg = RandomForestRegressor()
#     rf_reg.fit(X, y)
#     y_pred_rf = rf_reg.predict(X)
#     r2_rf = r2_score(y, y_pred_rf)
#     mse_rf = mean_squared_error(y, y_pred_rf)

#     # Vẽ biểu đồ Hồi quy tuyến tính
#     plt.figure(figsize=(12, 6))
#     plt.scatter(y, y_pred_lin, label='Dự đoán')
#     plt.plot([y.min(), y.max()], [y.min(), y.max()], 'k--', lw=4, label='Hồi quy tuyến tính')
#     plt.title('Biểu đồ hồi quy tuyến tính bội')
#     plt.xlabel('Thực tế')
#     plt.ylabel('Dự đoán')
#     plt.legend()

#     buf = io.BytesIO()
#     plt.savefig(buf, format='png')
#     buf.seek(0)
#     image_base64_lin = base64.b64encode(buf.read()).decode('utf-8')
#     buf.close()

#     # Clear figure để vẽ biểu đồ Random Forest
#     plt.clf()

#     # Vẽ biểu đồ Random Forest
#     plt.figure(figsize=(12, 6))
#     plt.scatter(range(len(y)), y, label='Thực tế')
#     plt.scatter(range(len(y)), y_pred_rf, label='Dự đoán')
#     plt.title('Biểu đồ Random Forest')
#     plt.xlabel('Index')
#     plt.ylabel('Diem_Linh_vuc')
#     plt.legend()

#     buf = io.BytesIO()
#     plt.savefig(buf, format='png')
#     buf.seek(0)
#     image_base64_rf = base64.b64encode(buf.read()).decode('utf-8')
#     buf.close()

#     SV = get_object_or_404(Sinhvien, MSSV=MSSV)

#     if request.method == 'POST':
#         diem_he_10_input = float(request.POST.get('diem'))

#         new_data = pd.DataFrame([ diem_he_10_input],
#                                 columns=['Diem_he_10'])

#         # Dự đoán
#         new_pred_lin = lin_reg.predict(new_data)
#         new_pred_rf = rf_reg.predict(new_data)

#         context = {
#             'SV': SV,
#             'linear_regression': {
#                 'coefficients': lin_reg.coef_.tolist(),
#                 'intercept': lin_reg.intercept_,
#                 'r2_score': r2_lin,
#                 'mean_squared_error': mse_lin,
#                 'new_prediction': new_pred_lin[0]
#             },
#             'random_forest': {
#                 'r2_score': r2_rf,
#                 'mean_squared_error': mse_rf,
#                 'new_prediction': new_pred_rf[0]
#             },
#             'plot_lin': image_base64_lin,
#             'plot_rf': image_base64_rf
#         }
#         return render(request, 'ketqua.html', context)

#     context = {
#         'SV': SV,
#         'linear_regression': {
#             'coefficients': lin_reg.coef_.tolist(),
#             'intercept': lin_reg.intercept_,
#             'r2_score': r2_lin,
#             'mean_squared_error': mse_lin
#         },
#         'random_forest': {
#             'r2_score': r2_rf,
#             'mean_squared_error': mse_rf
#         },
#         'plot_lin': image_base64_lin,
#         'plot_rf': image_base64_rf
#     }

#     return render(request, 'ketqua.html', context)
# ------------------------------------------------------------------------------------------------------------------------------------
import pandas as pd
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Sinhvien, Monhoc, thuoc_ctdt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.impute import SimpleImputer
from sklearn.feature_selection import SelectKBest, f_regression

def predict(request, MSSV):
    SV = get_object_or_404(Sinhvien, MSSV=MSSV)
    data = pd.read_csv('DA19TT_he10.csv')
    imputer = SimpleImputer(strategy='mean')
    data_daloc = pd.DataFrame(imputer.fit_transform(data), columns=data.columns)
    
    if request.method == 'POST':
        try:
            ma_mon_hoc_input = request.POST.get('ma_mon_hoc')
            
            if ma_mon_hoc_input not in data_daloc.columns:
                raise KeyError(f"Mã môn học '{ma_mon_hoc_input}' không tồn tại trong dữ liệu.")
            
            monhoc = get_object_or_404(Monhoc, Ma_mon_hoc=ma_mon_hoc_input)
            hocky = thuoc_ctdt.objects.filter(Ma_mon_hoc=monhoc).values_list('Ma_HK_CTDT', flat=True).first()
            
            if not hocky:
                raise KeyError(f"Kỳ học của mã môn '{ma_mon_hoc_input}' không tìm thấy trong cơ sở dữ liệu.")
            
            # Tất cả các môn học thuộc kỳ học đó trở về trước
            monhoctontai = thuoc_ctdt.objects.filter(Ma_HK_CTDT__lte=hocky).values_list('Ma_mon_hoc', flat=True).distinct()
            cot = [col for col in data.columns if col in monhoctontai]
            
            if ma_mon_hoc_input not in cot:
                raise KeyError(f"Mã môn học '{ma_mon_hoc_input}' không có trong dữ liệu CSV sau khi lọc.")
            data_filtered = data_daloc[cot]
            results = []

            # Linear Regression
            X_lr = data_filtered.drop(columns=ma_mon_hoc_input)
            y_lr = data_filtered[ma_mon_hoc_input]
            X_train_lr, X_test_lr, y_train_lr, y_test_lr = train_test_split(X_lr, y_lr, test_size=0.3, random_state=42)

            selector_lr = SelectKBest(score_func=f_regression, k=9)
            selector_lr.fit(X_train_lr, y_train_lr)
            top_k_feature_names_lr = [X_lr.columns[i] for i in selector_lr.get_support(indices=True)]

            lr_model = LinearRegression()
            lr_model.fit(X_train_lr[top_k_feature_names_lr], y_train_lr)
            lr_predictions = lr_model.predict(X_test_lr[top_k_feature_names_lr])

            lr_r2 = r2_score(y_test_lr, lr_predictions)
            lr_mae = mean_absolute_error(y_test_lr, lr_predictions)
            lr_mse = mean_squared_error(y_test_lr, lr_predictions)
                
            # Random Forest
            X_rf = data_filtered.drop(columns=ma_mon_hoc_input)
            y_rf = data_filtered[ma_mon_hoc_input]
            X_train_rf, X_test_rf, y_train_rf, y_test_rf = train_test_split(X_rf, y_rf, test_size=0.3, random_state=42)

            selector_rf = SelectKBest(score_func=f_regression, k=9)
            selector_rf.fit(X_train_rf, y_train_rf)
            top_k_feature_names_rf = [X_rf.columns[i] for i in selector_rf.get_support(indices=True)]

            rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
            rf_model.fit(X_train_rf[top_k_feature_names_rf], y_train_rf)
            rf_predictions = rf_model.predict(X_test_rf[top_k_feature_names_rf])

            rf_r2 = r2_score(y_test_rf, rf_predictions)
            rf_mae = mean_absolute_error(y_test_rf, rf_predictions)
            rf_mse = mean_squared_error(y_test_rf, rf_predictions)
            
            lr_sample_prediction = lr_predictions[0] if len(lr_predictions) > 0 else None
            rf_sample_prediction = rf_predictions[0] if len(rf_predictions) > 0 else None

            results.append({
                'top_features_lr': top_k_feature_names_lr,
                'lr_predictions': lr_sample_prediction,
                'lr_r2': lr_r2,
                'lr_mae': lr_mae,
                'lr_mse': lr_mse,
                'top_features_rf': top_k_feature_names_rf,
                'rf_predictions': rf_sample_prediction,
                'rf_r2': rf_r2,
                'rf_mae': rf_mae,
                'rf_mse': rf_mse
            })
            
            mon_hoc_name = Monhoc.objects.filter(Ma_mon_hoc=ma_mon_hoc_input).first()
            mon_hoc_name = mon_hoc_name.Ten_mon_hoc if mon_hoc_name else "Không xác định"
            
            context = {
                'ma_mon_hoc_input': ma_mon_hoc_input,
                'mon_hoc_name': mon_hoc_name,
                'results': results,
                'SV': SV,
                'top_features_lr': top_k_feature_names_lr,
                'top_features_rf': top_k_feature_names_rf
            }

            return render(request, 'predict_results.html', context)
        except KeyError as e:
            return HttpResponse(f"Lỗi: {str(e)}", content_type="text/plain")
    
    return render(request, 'predict_form.html', {'SV': SV})

# ------------------------------------------------------------------------------------------------------------------------