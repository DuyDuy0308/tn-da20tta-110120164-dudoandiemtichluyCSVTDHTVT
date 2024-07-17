# forms.py
from django import forms
from .models import Taikhoan, Covan, Sinhvien, Khoa, Bomon, Nganhdaotao, Hockynienkhoa, Loaihocphan, Hockychuongtrinhdaotao, Nhommon, Chuongtrinh_daotao, Bangdiem, Lop, Monhoc, Chitiet_bangdiem, thuoc_ctdt

class LoginForm(forms.ModelForm):
    class Meta:
        model = Taikhoan
        fields = ['User_name', 'Password']
        widgets = {
            'Password': forms.PasswordInput(),
        }
# ---------------------------------------------------------------------------------------------------------------------------------------
# tạo tài khoản
class create_taikhoan(forms.ModelForm):
    class Meta:
        model = Taikhoan
        fields = ['User_name', 'Password', 'Role']
        widgets = {
            'User_name' : forms.TextInput(attrs={'class': 'form-control'}),
            'Password': forms.PasswordInput(attrs={'class': 'form-control'}),
            'Role': forms.Select(attrs={'class': 'form-control'}),
        }
# Cố vấn
class create_covan(forms.ModelForm):
    class Meta:
        model = Covan
        fields = ['Id_cv', 'Ho_ten_cv', 'Ngay_sinh_cv', 'Gioi_tinh_cv', 'Dia_chi_cv', 'Email_cv']
        labels = {
            'Id_cv': 'ID',
            'Ho_ten_cv': 'Họ Tên',
            'Ngay_sinh_cv': 'Ngày Sinh',
            'Gioi_tinh_cv': 'Giới Tính',
            'Dia_chi_cv': 'Địa Chỉ',
            'Email_cv': 'Email',
        }
        widgets = {
            'Id_cv': forms.TextInput(attrs={'class': 'form-control'}),
            'Ho_ten_cv': forms.TextInput(attrs={'class': 'form-control'}),
            'Ngay_sinh_cv': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'Gioi_tinh_cv': forms.TextInput(attrs={'class': 'form-control'}),
            'Dia_chi_cv': forms.TextInput(attrs={'class': 'form-control'}),
            'Email_cv': forms.EmailInput(attrs={'class': 'form-control'}),
        }
        
class UploadFileForm(forms.Form):
    file = forms.FileField()
# ---------------------------------------------------------------------------------------------------------------------------------------
# Khoa
class create_khoa(forms.ModelForm):
    class Meta:
         model = Khoa
         fields = ['Ma_khoa', 'Ten_khoa']
         labels = {
            'Ma_khoa': 'Mã khoa',
            'Ten_khoa': 'Tên khoa',
         }
         widgets = {
            'Ma_khoa': forms.TextInput(attrs={'class': 'form-control'}),
            'Ten_khoa': forms.TextInput(attrs={'class': 'form-control'}),
        }
# ---------------------------------------------------------------------------------------------------------------------------------------
#  Bộ môn
class create_bomon(forms.ModelForm):
    class Meta:
         model = Bomon
         fields = ['Ma_bo_mon','Ten_bo_mon','Ma_khoa']
         labels = {
            'Ma_bo_mon': 'Mã bộ môn',
            'Ten_bo_mon': 'Tên bộ môn',
            'Ma_khoa': 'Tên khoa',
         }
         widgets = {
            'Ma_bo_mon': forms.TextInput(attrs={'class': 'form-control'}),
            'Ten_bo_mon': forms.TextInput(attrs={'class': 'form-control'}),
            'Ma_khoa': forms.Select(attrs={'class': 'form-control'}),
        }
# ---------------------------------------------------------------------------------------------------------------------------------------
#  Ngành đào tạo
class create_nganhdaotao(forms.ModelForm):
    class Meta:
         model = Nganhdaotao
         fields = ['Ma_nganh','Ten_nganh','Ma_bo_mon']
         labels = {
            'Ma_nganh': 'Mã ngành',
            'Ten_nganh': 'Tên ngành',
            'Ma_bo_mon': 'Mã bộ môn',
         }
         widgets = {
            'Ma_nganh': forms.TextInput(attrs={'class': 'form-control'}),
            'Ten_nganh': forms.TextInput(attrs={'class': 'form-control'}),
            'Ma_bo_mon': forms.Select(attrs={'class': 'form-control'}),
        }
# ---------------------------------------------------------------------------------------------------------------------------------------
# Học kỳ niên khóa
class create_hknienkhoa(forms.ModelForm):
    class Meta:
         model = Hockynienkhoa
         fields = ['Ma_hk_nien_khoa', 'Ten_hk_nien_khoa']
         labels = {
            'Ma_hk_nien_khoa': 'Mã học kỳ niên khóa',
            'Ten_hk_nien_khoa': 'Tên học kỳ niên khóa',
         }
         widgets = {
           'Ma_hk_nien_khoa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Vd: HKI 2019-2020'}),

            'Ten_hk_nien_khoa': forms.TextInput(attrs={'class': 'form-control'}),
        }

# ---------------------------------------------------------------------------------------------------------------------------------------
# Loại học phần
class create_loaihocphan(forms.ModelForm):
    class Meta:
         model = Loaihocphan
         fields = ['Ma_loai_hp', 'Ten_loai_hp']
         labels = {
            'Ma_loai_hp': 'Mã loại học phần',
            'Ten_loai_hp': 'Tên loại học phần',
         }
         widgets = {
            'Ma_loai_hp': forms.TextInput(attrs={'class': 'form-control'}),
            'Ten_loai_hp': forms.TextInput(attrs={'class': 'form-control'}),
        }
# ---------------------------------------------------------------------------------------------------------------------------------------
# học kỳ chương trình đào tạo
class create_hk_ctdt(forms.ModelForm):
    class Meta:
         model = Hockychuongtrinhdaotao
         fields = ['Ma_HK_CTDT', 'Ten_HK_CTDT']
         labels = {
            'Ma_HK_CTDT': 'Mã học kỳ chương trình đào tạo',
            'Ten_HK_CTDT': 'Tên học kỳ chương trình đào tạo',
         }
         widgets = {
            'Ma_HK_CTDT': forms.TextInput(attrs={'class': 'form-control'}),
            'Ten_HK_CTDT': forms.TextInput(attrs={'class': 'form-control'}),
        }
# ---------------------------------------------------------------------------------------------------------------------------------------
# Nhóm môn
class create_nhommon(forms.ModelForm):
    class Meta:
         model = Nhommon
         fields = ['Ma_nhom_mon', 'Ten_nhom_mon']
         labels = {
            'Ma_nhom_mon': 'Mã nhóm môn',
            'Ten_nhom_mon': 'Tên nhóm môn',
         }
         widgets = {
            'Ma_nhom_mon': forms.TextInput(attrs={'class': 'form-control'}),
            'Ten_nhom_mon': forms.TextInput(attrs={'class': 'form-control'}),
        }
# ---------------------------------------------------------------------------------------------------------------------------------------
# Chương trình đào tạo
class create_ctdt(forms.ModelForm):
    class Meta:
         model = Chuongtrinh_daotao
         fields = ['Ma_CTDT', 'Ten_CTDT','Ngay_quyet_dinh','So_quyet_dinh','Loai_hinh_dao_tao','Ma_nganh','Tong_so_tin_chi']
         labels = {
            'Ma_CTDT' : 'Mã chương trình đào tạo',
            'Ten_CTDT': 'Tên chương trình đào tạo',
            'Ngay_quyet_dinh': 'Ngày quyết định',
            'So_quyet_dinh' : 'Số quyết định',
            'Loai_hinh_dao_tao': 'Loại hình đào tạo',
            'Ma_nganh' : 'Mã ngành',
            'Tong_so_tin_chi': 'Tổng số tín chỉ',
         }
         widgets = {
            'Ma_CTDT' : forms.TextInput(attrs={'class': 'form-control'}),
            'Ten_CTDT': forms.TextInput(attrs={'class': 'form-control'}),
            'Ngay_quyet_dinh': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'So_quyet_dinh' : forms.TextInput(attrs={'class': 'form-control'}),
            'Loai_hinh_dao_tao': forms.TextInput(attrs={'class': 'form-control'}),
            'Ma_nganh' : forms.Select(attrs={'class': 'form-control'}),
            'Tong_so_tin_chi': forms.TextInput(attrs={'class': 'form-control'}),
        }
# ---------------------------------------------------------------------------------------------------------------------------------------
# Lớp
class create_lop(forms.ModelForm):
    class Meta:
         model = Lop
         fields = ['Ma_lop','Ten_lop','Id_cv','Ma_CTDT']
         labels = {
            'Ma_lop' : 'Mã lớp',
            'Ten_lop': 'Tên lớp',
            'Id_cv': 'Mã cố vấn',
            'Ma_CTDT' : 'Mã chương trình đào tạo',
         }
         widgets = {
            'Ma_lop' : forms.TextInput(attrs={'class': 'form-control'}),
            'Ten_lop': forms.TextInput(attrs={'class': 'form-control'}),
            'Id_cv' : forms.Select(attrs={'class': 'form-control'}),
            'Ma_CTDT' : forms.Select(attrs={'class': 'form-control'}),
        }
# ---------------------------------------------------------------------------------------------------------------------------------------
#sinh viên
class create_sinhvien(forms.ModelForm):
    class Meta:
        model = Sinhvien
        fields = ['MSSV', 'Ho_ten_sv', 'Dia_chi_sv', 'Gioi_tinh_sv', 'Email_sv', 'Ma_lop', 'Ngay_sinh_sv']
        labels = {
            'MSSV': 'ID',
            'Ho_ten_sv': 'Họ Tên',
            'Dia_chi_sv': 'Địa Chỉ',
            'Gioi_tinh_sv': 'Giới Tính',
            'Email_sv': 'Email',
            'Ma_lop': 'Mã lớp',
            'Ngay_sinh_sv': 'Ngày sinh',
        }
        widgets = {
            'MSSV': forms.TextInput(attrs={'class': 'form-control'}),
            'Ho_ten_sv': forms.TextInput(attrs={'class': 'form-control'}),
            'Dia_chi_sv': forms.TextInput(attrs={'class': 'form-control'}),
            'Gioi_tinh_sv': forms.TextInput(attrs={'class': 'form-control'}),
            'Email_sv': forms.EmailInput(attrs={'class': 'form-control'}),
            'Ma_lop': forms.Select(attrs={'class': 'form-control'}),
            'Ngay_sinh_sv': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
        }
# ---------------------------------------------------------------------------------------------------------------------------------------
# Bảng điểm
class create_bangdiem(forms.ModelForm):
    class Meta:
         model = Bangdiem
         fields = ['Ma_bang_diem','Diem_tich_luy_he_4','MSSV','Ma_hk_nien_khoa']
         labels = {
            'Ma_bang_diem' : 'Mã bảng điểm',
            'Diem_tich_luy_he_4': 'Điểm hệ 4',
            'MSSV': 'Mã số sinh viên',
            'Ma_hk_nien_khoa' : 'Học kỳ niên khóa',
         }
         widgets = {
            'Ma_bang_diem' : forms.TextInput(attrs={'class': 'form-control'}),
            'Diem_tich_luy_he_4': forms.TextInput(attrs={'class': 'form-control'}),
            'MSSV' : forms.Select(attrs={'class': 'form-control'}),
            'Ma_hk_nien_khoa' : forms.Select(attrs={'class': 'form-control'}),
        }
# ---------------------------------------------------------------------------------------------------------------------------------------
# Môn học
class create_monhoc(forms.ModelForm):
    class Meta:
         model = Monhoc
         fields = ['Ma_mon_hoc','Ten_mon_hoc','Tin_chi','Linh_vuc']
         labels = {
            'Ma_mon_hoc' : 'Mã môn học',
            'Ten_mon_hoc': 'Tên môn',
            'Tin_chi': 'Tín chỉ',
             'Linh_vuc': 'Lĩnh vực',
            
         }
         widgets = {
            'Ma_mon_hoc' : forms.TextInput(attrs={'class': 'form-control' }),
            'Ten_mon_hoc': forms.TextInput(attrs={'class': 'form-control'}),
            'Tin_chi' : forms.TextInput(attrs={'class': 'form-control'}),
            'Linh_vuc' : forms.Select(attrs={'class': 'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super(create_monhoc, self).__init__(*args, **kwargs)
        self.fields['Linh_vuc'].queryset = Monhoc.objects.all()
# ---------------------------------------------------------------------------------------------------------------------------------------
# Chi tiết bảng điểm
class create_ctbd(forms.ModelForm):
    Ma_mon_hoc = forms.ModelChoiceField(
    queryset=Monhoc.objects.all(),
    widget=forms.Select(attrs={'class': 'form-control'}),
    label='Mã môn học',
    to_field_name='Ma_mon_hoc',
    empty_label="..."
    )
    class Meta:
         model = Chitiet_bangdiem
         fields = ['Ma_CTBD','Diem_he_4','Diem_he_10','Diem_he_10_lan_2','Ma_mon_hoc','Ma_bang_diem']
         labels = {
            'Ma_CTBD' : 'Mã chi tiết bảng điểm',
            'Diem_he_4': 'Điểm hệ 4',
            'Diem_he_10': 'Điểm hệ 10',
            'Diem_he_10_lan_2' : 'Điểm hệ 10 lần 2',
            'Ma_mon_hoc': 'Mã môn học',
            'Ma_bang_diem' : 'Mã bảng điểm',
         }
         widgets = {
            'Ma_CTBD' : forms.TextInput(attrs={'class': 'form-control'}),
            'Diem_he_4': forms.TextInput(attrs={'class': 'form-control'}),
            'Diem_he_10' : forms.TextInput(attrs={'class': 'form-control'}),
            'Diem_he_10_lan_2' :forms.TextInput(attrs={'class': 'form-control'}),
            'Ma_mon_hoc' : forms.Select(attrs={'class': 'form-control'}),
            'Ma_bang_diem' : forms.Select(attrs={'class': 'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['Ma_mon_hoc'].queryset = Monhoc.objects.all()
        self.fields['Ma_mon_hoc'].label_from_instance = lambda obj: f"{obj.Ma_mon_hoc} - {obj.Ten_mon_hoc}"
# ---------------------------------------------------------------------------------------------------------------------------------------

class create_thuoc_ctdt(forms.ModelForm):
    class Meta:
        model = thuoc_ctdt
        fields = ['Ma_HK_CTDT', 'Ma_loai_hp', 'Ma_nhom_mon', 'Ma_mon_hoc','Ma_CTDT']
        labels = {
            'Ma_HK_CTDT': 'Mã học kỳ chương trình đào tạo',
            'Ma_loai_hp': 'Mã loại học phần',
            'Ma_nhom_mon': 'Mã nhóm môn',
            'Ma_mon_hoc': 'Mã môn học',
            'Ma_CTDT': 'Mã chương trình đào tạo',
        }
        widgets = {
            'Ma_HK_CTDT': forms.Select(attrs={'class': 'form-control'}),
            'Ma_loai_hp': forms.Select(attrs={'class': 'form-control'}),
            'Ma_nhom_mon': forms.Select(attrs={'class': 'form-control'}),
            'Ma_mon_hoc': forms.Select(attrs={'class': 'form-control'}),   
            'Ma_CTDT': forms.Select(attrs={'class': 'form-control'}),      
        }
# ---------------------------------------------------------------------------------------------------------------------------------------
class PredictForm(forms.Form):
    Ma_mon_hoc = forms.CharField(label='Mã môn học', max_length=100)
    Diem_he_10 = forms.FloatField(label='Điểm hệ 10 hiện tại')




