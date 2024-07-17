# forms.py
from django import forms
from .models import Covan, Sinhvien, Khoa, Bomon, Nganhdaotao, Hockynienkhoa, Loaihocphan, Hockychuongtrinhdaotao, Nhommon, Chuongtrinh_daotao, Bangdiem, Lop, Monhoc, Chitiet_bangdiem, thuoc_ctdt
class DuDoanDiemForm(forms.Form):
    ma_mon_hoc = forms.IntegerField(label='Mã Môn Học')
    
class HockySelectForm(forms.Form):
    Ma_HK_CTDT = forms.ModelChoiceField(queryset=Hockychuongtrinhdaotao.objects.all(), label="Chọn học kỳ", widget=forms.Select(attrs={'class': 'form-control'}))
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