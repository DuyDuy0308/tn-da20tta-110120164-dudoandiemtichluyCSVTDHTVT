average_scores = {}
                for ma_mon_hoc in ma_mon_hocs:
                    avg_score = Chitiet_bangdiem.objects.filter(
                        Ma_bang_diem__in=bangdiem_list,
                        Ma_mon_hoc=ma_mon_hoc
                    ).aggregate(Avg('Diem_he_10'))['Diem_he_10__avg']
                    average_scores[ma_mon_hoc] = avg_score
                    if avg_score is not None:
                        avg_score = round(avg_score, 1) 
                        average_scores[ma_mon_hoc] = avg_score
                    else:
                        average_scores[ma_mon_hoc] = None
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

    # Chuẩn bị dữ liệu cho dự đoán mới từ dữ liệu nhập vào
    new_data = pd.DataFrame({'Ma_mon_hoc': ma_mon_hocs, 'Diem_he_10': [avg_score]})

    # Dự đoán với mô hình hồi quy tuyến tính và rừng ngẫu nhiên
    new_pred_lin = lin_reg.predict(new_data[['Ma_mon_hoc']])
    new_pred_rf = rf_reg.predict(new_data[['Ma_mon_hoc']])

    context = {
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
    }

    return render(request, 'dudoanky.html', context)

    
    
