import datetime
from flask_login import UserMixin
from flask import url_for
from bcrypt import checkpw, hashpw, gensalt
import peewee as pw
from app import db_wrapper


# Function to build the tree structure
def build_tree(items):
    # Create a dictionary to easily access items by their ID
    item_map = {item.id: {
        'id': item.id, 
        'uraian': item.uraian, 
        'is_leaf': item.is_leaf, 
        'waktu_mulai': item.waktu_mulai, 
        'durasi': item.durasi,
        'minggu_mulai': item.minggu_mulai,
        'children': []} for item in items}
    # Identify root items and link children to their parents
    roots = []
    for item in items:
        if item.parent:
            parent_id = item.parent.id
            if parent_id in item_map:
                item_map[parent_id]['children'].append(item_map[item.id])
            else:
                # Handle cases where a parent might not be in the current `items` list
                # (e.g., if you're only fetching a subset)
                # For a complete tree, all parents should be present.
                roots.append(item_map[item.id])
        else:
            roots.append(item_map[item.id])

    # Sort children for consistent display
    for item_data in item_map.values():
        item_data['children'].sort(key=lambda x: x['uraian']) # Sort by uraian
    #roots.sort(key=lambda x: x['uraian']) # Sort root items

    return roots

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

class Proyek(BaseModel):
    nama = pw.CharField(max_length=100)
    unit = pw.ForeignKeyField(UnitOrg)
    direksi = pw.ForeignKeyField(User, null=True, backref='proyek_direksi')
    cdate = pw.DateTimeField(default=datetime.datetime.now)
    mdate = pw.DateTimeField(null=True)
    cuser = pw.CharField(null=True)
    muser = pw.CharField(null=True)

class Pekerjaan(BaseModel):
    '''Pekerjaan dalam proyek'''
    proyek = pw.ForeignKeyField(Proyek, null=True, backref='pekerjaan')
    parent = pw.ForeignKeyField('self', null=True, backref='children')
    uraian = pw.CharField(max_length=250)
    satuan = pw.CharField(max_length=20, null=True)
    volume = pw.FloatField(default=0)
    waktu_mulai = pw.DateField(null=True) # tanggal mulai pekerjaan
    bobot = pw.FloatField(default=0)
    durasi = pw.IntegerField(default=0) # dalam minggu
    pic = pw.CharField(max_length=20, null=True) # diisi 'username'
    rencana = pw.TextField(null=True) # rencana pelaksanaan pekerjaan, JSON format
    realisasi = pw.TextField(null=True) # realisasi pelaksanaan pekerjaan, JSON format
    cdate = pw.DateTimeField(default=datetime.datetime.now)
    mdate = pw.DateTimeField(null=True)
    cuser = pw.CharField(null=True)
    muser = pw.CharField(null=True)
    
    @property
    def is_leaf(self):
        '''Apakah pekerjaan ini adalah leaf node (tidak memiliki anak)'''
        return not self.children.exists()
    
    @property
    def is_root(self):
        '''Apakah pekerjaan ini adalah root node (tidak memiliki parent)'''
        return self.parent is None
    
    @property
    def is_has_children(self):
        '''Apakah punya sub pekerjaan'''
        return self.children.exists()
    
    @property
    def minggu_mulai(self):
        try:
            return self.waktu_mulai.isocalendar()[1]
        except AttributeError:
            return None
    
    @property
    def waktu_akhir(self):
        '''Tanggal akhir pekerjaan, berdasarkan waktu_mulai dan durasi'''
        if self.waktu_mulai and self.durasi:
            return self.waktu_mulai + datetime.timedelta(weeks=self.durasi)
        return None

class RencanaKontrak(BaseModel):
    pekerjaan = pw.ForeignKeyField(Pekerjaan)
    waktu = pw.DateField()
    volume = pw.FloatField()
    cdate = pw.DateTimeField(default=datetime.datetime.now)
    mdate = pw.DateTimeField(null=True)
    cuser = pw.CharField(null=True)
    muser = pw.CharField(null=True)

class RencanaPelaksanaan(BaseModel):
    '''Rencana Pelaksanaan Pekerjaan'''
    pekerjaan = pw.ForeignKeyField(Pekerjaan)
    waktu = pw.DateField() # waktu mulai
    bobot = pw.FloatField() # Target bobot pekerjaan
    cdate = pw.DateTimeField(default=datetime.datetime.now)
    mdate = pw.DateTimeField(null=True)
    cuser = pw.CharField(null=True)
    muser = pw.CharField(null=True)
    
class Realisasi(BaseModel):
    pekerjaan = pw.ForeignKeyField(Pekerjaan)
    waktu = pw.DateField() # tanggal pelaporan relaisasi
    volume = pw.FloatField()
    cdate = pw.DateTimeField(default=datetime.datetime.now)
    mdate = pw.DateTimeField(null=True)
    cuser = pw.CharField(null=True)
    muser = pw.CharField(null=True)

    class Meta:
        pass
        
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
    user = pw.ForeignKeyField(User, backref='kehadiran', null=True)
    username = pw.CharField(max_length=20)
    ll = pw.CharField(max_length=50, null=True) # lokasi
    masuk = pw.DateTimeField(null=True)
    keluar = pw.DateTimeField(null=True)
    status = pw.CharField(max_length=20) # masuk|keluar
    cdate = pw.DateTimeField(default=datetime.datetime.now)
    keterangan = pw.TextField(null=True)
    lok_masuk = pw.TextField(null=True) # lokasi saat masuk
    lok_keluar = pw.TextField(null=True) # lokasi saat keluar
    ll_masuk= pw.CharField(max_length=50, null=True) # lonlat saat masuk
    ll_keluar = pw.CharField(max_length=50, null=True) # lonlat saat keluar
    ip_masuk = pw.CharField(max_length=20, null=True)
    ip_keluar = pw.CharField(max_length=20, null=True)
    ua_masuk = pw.CharField(max_length=255, null=True) # user agent saat masuk
    ua_keluar = pw.CharField(max_length=255, null=True) # user agent saat keluar
    
    @property
    def durasi(self):
        '''durasi kehadiran dalam detik'''
        if not self.keluar or not self.masuk:
            return 0
        return int((self.keluar - self.masuk).total_seconds())
    
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
        
        