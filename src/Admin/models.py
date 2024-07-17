from django.db import models

class Taikhoan(models.Model):
    ROLE_CHOICES = (
        ('admin', 'admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )

    User_name = models.CharField(max_length=100, primary_key=True)
    Password = models.CharField(max_length=100)
    Role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    class Meta:
        db_table = 'tai_khoan'
        
class Covan(models.Model):
    Id_cv = models.CharField(max_length=100, primary_key=True)
    Ho_ten_cv = models.CharField(max_length=100)
    Ngay_sinh_cv = models.DateField()
    Gioi_tinh_cv = models.CharField(max_length=100)
    Dia_chi_cv = models.CharField(max_length=100)
    Email_cv = models.CharField(max_length=100)

    class Meta:
        db_table = 'co_van' 
    def __str__(self):
        return self.Ho_ten_cv
        
class Khoa(models.Model):
    Ma_khoa = models.CharField(max_length=100, primary_key=True)
    Ten_khoa = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'khoa'
    def __str__(self):
        return self.Ten_khoa
        
class Bomon(models.Model):
    Ma_bo_mon = models.CharField(max_length=100, primary_key=True)
    Ten_bo_mon = models.CharField(max_length=100)
    Ma_khoa = models.ForeignKey(Khoa, on_delete=models.CASCADE, db_column='Ma_khoa')
    class Meta:
        db_table = 'bo_mon'  
    def __str__(self):
        return self.Ten_bo_mon
        
class Nganhdaotao(models.Model):
    Ma_nganh = models.CharField(max_length=100, primary_key=True)
    Ten_nganh = models.CharField(max_length=100)
    Ma_bo_mon = models.ForeignKey(Bomon, on_delete=models.CASCADE, db_column='Ma_bo_mon')
						
    class Meta:
        db_table = 'nganh_dao_tao'
    def __str__(self):
        return self.Ten_nganh
    
class Hockynienkhoa(models.Model):
    Ma_hk_nien_khoa = models.CharField(max_length=100, primary_key=True)
    Ten_hk_nien_khoa = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'hk_nien_khoa'
       
class Loaihocphan(models.Model):
    Ma_loai_hp = models.CharField(max_length=100, primary_key=True)
    Ten_loai_hp	 = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'loai_hp'
    def __str__(self):
        return self.Ten_loai_hp
        
class Hockychuongtrinhdaotao(models.Model):
    Ma_HK_CTDT = models.CharField(max_length=100, primary_key=True)
    Ten_HK_CTDT	= models.CharField(max_length=100)
    
    class Meta:
        db_table = 'hk_ctdt' 
    def __str__(self):
        return self.Ten_HK_CTDT    
    
class Nhommon(models.Model):
    Ma_nhom_mon = models.CharField(max_length=100, primary_key=True)
    Ten_nhom_mon = models.CharField(max_length=100)
						
    class Meta:
        db_table = 'nhom_mon' 
    def __str__(self):
        return self.Ten_nhom_mon
        
class Chuongtrinh_daotao(models.Model):
    Ma_CTDT = models.CharField(max_length=100, primary_key=True)
    Ten_CTDT = models.CharField(max_length=100)
    Ngay_quyet_dinh = models.DateField()
    So_quyet_dinh = models.CharField(max_length=100)
    Loai_hinh_dao_tao = models.CharField(max_length=100)
    Ma_nganh = models.ForeignKey(Nganhdaotao, on_delete=models.CASCADE, db_column='Ma_nganh')
    Tong_so_tin_chi = models.CharField(max_length=100)

    class Meta:
        db_table = 'chuong_trinh_dao_tao'  
    def __str__(self):
        return self.Ma_CTDT
        
class Lop(models.Model):
    Ma_lop = models.CharField(max_length=100, primary_key=True)
    Ten_lop	 = models.CharField(max_length=100)
    Id_cv = models.ForeignKey(Covan, on_delete=models.CASCADE, db_column='Id_cv')
    Ma_CTDT = models.ForeignKey(Chuongtrinh_daotao, on_delete=models.CASCADE, db_column='Ma_CTDT')

    class Meta:
        db_table = 'lop'
    def __str__(self):
        return self.Ten_lop
        
class Sinhvien(models.Model):
    MSSV = models.CharField(max_length=100, primary_key=True)
    Ho_ten_sv = models.CharField(max_length=100)
    Dia_chi_sv = models.CharField(max_length=100)
    Gioi_tinh_sv = models.CharField(max_length=100)
    Email_sv = models.CharField(max_length=100)
    Ma_lop = models.ForeignKey(Lop, on_delete=models.CASCADE, db_column='Ma_lop')
    Ngay_sinh_sv = models.DateField()
    
    class Meta:
        db_table = 'sinh_vien'
    def __str__(self):
        return self.MSSV
        
class Bangdiem(models.Model):
    Ma_bang_diem =  models.AutoField(primary_key=True)
    Diem_trung_binh_hoc_ky = models.CharField(max_length=100)
    Diem_tich_luy_he_4 = models.CharField(max_length=100)
    Ma_hk_nien_khoa = models.ForeignKey(Hockynienkhoa, on_delete=models.CASCADE, db_column='Ma_hk_nien_khoa')
    MSSV = models.ForeignKey(Sinhvien, on_delete=models.CASCADE, db_column='MSSV')
    class Meta:
        db_table = 'bang_diem'

class Monhoc(models.Model):
    Ma_mon_hoc = models.CharField(max_length=100, primary_key=True)
    Ten_mon_hoc	= models.CharField(max_length=100)
    Tin_chi = models.IntegerField()
    Linh_vuc = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True)
				
    class Meta:
        db_table = 'mon_hoc'
        
    def __str__(self):
        return self.Ma_mon_hoc
        
class Chitiet_bangdiem(models.Model):
    Ma_CTBD =  models.AutoField(primary_key=True)
    Diem_he_4 = models.CharField(max_length=100)
    Diem_he_10 = models.CharField(max_length=100)
    Diem_he_10_lan_2 =  models.CharField(max_length=100)
    Ma_mon_hoc = models.ForeignKey(Monhoc, on_delete=models.CASCADE, db_column='Ma_mon_hoc')
    Ma_bang_diem = models.ForeignKey(Bangdiem, on_delete=models.CASCADE, db_column='Ma_bang_diem')

    class Meta:
        db_table = 'chi_tiet_bang_diem'
        
class thuoc_ctdt(models.Model):
    Ma_HK_CTDT = models.ForeignKey(Hockychuongtrinhdaotao, on_delete=models.CASCADE, db_column='Ma_HK_CTDT')
    Ma_loai_hp = models.ForeignKey(Loaihocphan, on_delete=models.CASCADE, db_column='Ma_loai_hp')
    Ma_nhom_mon = models.ForeignKey(Nhommon, on_delete=models.CASCADE, db_column='Ma_nhom_mon')
    Ma_mon_hoc = models.ForeignKey(Monhoc, on_delete=models.CASCADE, db_column='Ma_mon_hoc')
    Ma_CTDT = models.ForeignKey(Chuongtrinh_daotao, on_delete=models.CASCADE, db_column='Ma_CTDT')
    class Meta:
        db_table = 'thuoc_ctdt'