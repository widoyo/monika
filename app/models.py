import datetime
from flask_login import UserMixin
from flask import url_for
from bcrypt import checkpw, hashpw, gensalt
import peewee as pw
from app import db_wrapper

class BaseModel(db_wrapper.Model):
    pass

class UnitOrg(BaseModel):
    nama = pw.CharField(max_length=50)
    cdate = pw.DateTimeField(default=datetime.datetime.now)
    mdate = pw.DateTimeField(null=True)
    
class Proyek(BaseModel):
    nama = pw.CharField(max_length=50)
    unit = pw.ForeignKeyField(UnitOrg)
    cdate = pw.DateTimeField(default=datetime.datetime.now)
    mdate = pw.DateTimeField(null=True)
    cuser = pw.CharField(null=True)
    muser = pw.CharField(null=True)

class Pekerjaan(BaseModel):
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
    unitorg = pw.ForeignKeyField(UnitOrg, null=True, default=None)
    is_adm = pw.BooleanField(default=False)
    is_supervisi = pw.BooleanField(default=False)
    last_login = pw.DateTimeField(null=True)
    active = pw.BooleanField(default=True)
    cdate = pw.DateTimeField(default=datetime.datetime.now)
    
    def check_password(self, password):
        return checkpw(password.encode(), self.password.encode())
    
    def set_password(self, password):
        self.password = hashpw(password.encode('utf-8'), gensalt())
        self.save()

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
    id = pw.CharField(primary_key=True, max_length=22, default=shortuuid.uuid)
    username = pw.CharField(max_length=20)
    cdate = pw.DateTimeField(default=datetime.datetime.now)
    fname = pw.CharField(max_length=25)
    msg = pw.TextField(null=True)


