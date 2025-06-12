import datetime
from flask_login import UserMixin
from flask import url_for
from bcrypt import checkpw, hashpw, gensalt
import peewee as pw
from app import db_wrapper

class BaseModel(db_wrapper.Model):
    class Meta:
        database = db_wrapper.database  # Ensure db_wrapper has a 'database' attribute

class Perusahaan(BaseModel):
    '''Perusahaan'''
    nama = pw.CharField(max_length=100)
    kategori = pw.CharField(max_length=20, null=True) # kontraktor|supervisi
    alamat = pw.CharField(max_length=250, null=True)
    telepon = pw.CharField(max_length=20, null=True)
    fax = pw.CharField(max_length=20, null=True)
    email = pw.CharField(max_length=50, null=True)
    cdate = pw.DateTimeField(default=datetime.datetime.now)
    mdate = pw.DateTimeField(null=True)
    
    
class UnitOrg(BaseModel):
    nama = pw.CharField(max_length=100)
    cdate = pw.DateTimeField(default=datetime.datetime.now)
    mdate = pw.DateTimeField(null=True)
    
class Proyek(BaseModel):
    nama = pw.CharField(max_length=100)
    unit = pw.ForeignKeyField(UnitOrg)
    cdate = pw.DateTimeField(default=datetime.datetime.now)
    mdate = pw.DateTimeField(null=True)
    cuser = pw.CharField(null=True)
    muser = pw.CharField(null=True)

class Pekerjaan(BaseModel):
    proyek = pw.ForeignKeyField(Proyek)
    uraian = pw.CharField(max_length=250)
    satuan = pw.CharField(max_length=20, null=True)
    volume = pw.FloatField(default=0)
    bobot = pw.FloatField(default=0)
    pic = pw.CharField(max_length=20, null=True) # diisi 'username'
    cdate = pw.DateTimeField(default=datetime.datetime.now)
    mdate = pw.DateTimeField(null=True)
    cuser = pw.CharField(null=True)
    muser = pw.CharField(null=True)
    
class RencanaKontrak(BaseModel):
    pekerjaan = pw.ForeignKeyField(Pekerjaan)
    waktu = pw.DateField()
    volume = pw.FloatField()
    cdate = pw.DateTimeField(default=datetime.datetime.now)
    mdate = pw.DateTimeField(null=True)
    cuser = pw.CharField(null=True)
    muser = pw.CharField(null=True)

class RencanaPelaksanaan(BaseModel):
    pekerjaan = pw.ForeignKeyField(Pekerjaan)
    waktu = pw.DateField()
    volume = pw.FloatField()
    cdate = pw.DateTimeField(default=datetime.datetime.now)
    mdate = pw.DateTimeField(null=True)
    cuser = pw.CharField(null=True)
    muser = pw.CharField(null=True)
    
class Realisasi(BaseModel):
    pekerjaan = pw.ForeignKeyField(Pekerjaan)
    waktu = pw.DateField()
    volume = pw.FloatField()
    cdate = pw.DateTimeField(default=datetime.datetime.now)
    mdate = pw.DateTimeField(null=True)
    cuser = pw.CharField(null=True)
    muser = pw.CharField(null=True)

    class Meta:
        pass
        
class User(BaseModel, UserMixin):
    username = pw.CharField(max_length=20, unique=True, index=True)
    password = pw.CharField(max_length=100)
    fullname = pw.CharField(max_length=100, null=True)
    unitorg = pw.ForeignKeyField(UnitOrg, null=True, default=None)
    perusahaan = pw.ForeignKeyField(Perusahaan, null=True, default=None)
    is_adm = pw.BooleanField(default=False)
    is_supervisi = pw.BooleanField(default=False)
    last_login = pw.DateTimeField(null=True)
    active = pw.BooleanField(default=True)
    cdate = pw.DateTimeField(default=datetime.datetime.now)
    jabatan = pw.CharField(max_length=50, null=True)  # Jabatan di perusahaan
    
    def check_password(self, password):
        return checkpw(password.encode(), self.password if isinstance(self.password, bytes) else self.password.encode())
    
    def set_password(self, password):
        self.password = hashpw(password.encode('utf-8'), gensalt())
        self.save() # 

class Notes(BaseModel):
    '''Komentar/Catatan terhadap'''
    username = pw.CharField(max_length=20)
    cdate = pw.DateTimeField(default=datetime.datetime.now)
    msg = pw.TextField()
    obj_name = pw.CharField() # 
    obj_id = pw.IntegerField()
    parent_id = pw.IntegerField(null=True)
    
    def to_dict(self):
        data = {
            'id': self.id,
            'username': self.username,
            'msg': self.msg,
            'cdate': self.cdate.isoformat(),
            '_links': {
                'self': url_for('api.get_note', id=self.id)
            }
        }
    
    def from_dict(self, data):
        pass

class Foto(BaseModel):
    '''Foto-foto object'''
    username = pw.CharField(max_length=20)
    cdate = pw.DateTimeField(default=datetime.datetime.now)
    fname = pw.CharField(max_length=25)
    msg = pw.TextField(null=True)


class Kehadiran(BaseModel):
    '''Kehadiran user'''
    username = pw.CharField(max_length=20)
    ll = pw.CharField(max_length=50, null=True) # lokasi
    masuk = pw.DateTimeField(null=True)
    keluar = pw.DateTimeField(null=True)
    status = pw.CharField(max_length=20) # masuk|keluar
    cdate = pw.DateTimeField(default=datetime.datetime.now)
    keterangan = pw.TextField(null=True)
    ip = pw.CharField(max_length=20, null=True)
    user_agent = pw.CharField(max_length=100, null=True)
    
    class Meta:
        indexes = (
            (('username',), False),
            (('username', 'cdate'), False),
        )
    
    @property
    def late(self):
        '''apakah terlambat'''
        ref = self.masuk.replace(hour=8, minute=0)
        if self.masuk.hour < 8:
            return (0, 0, 0)
        delta = self.masuk - ref
        total_seconds = int(delta.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return (hours, minutes, total_seconds)

    @property
    def is_inside(self, tgl=datetime.datetime.now().date):
        '''apakah user sudah checkin'''
        return not self.keluar
        
        