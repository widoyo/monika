# Monika -- Monitoring Proyek

Manajemen perlu dapat dengan mudah memantau perkembangan proyek yang sedang berjalan

## Product Backlog

- [ ] (250702) Semua login user kantor, view Proyek grafik bandingan Rencana, Action-Plan dan Realisasi
- [ ] (250703) Direksi input Action plan, mengubah nilai Rencana Bobot mingguan
- [ ] (250704) Direksi input Realisasi, input Tanggal (lapor, dalam rentang minggu ini), Volume. Laporan dapat dilakukan 1 - 7 kali dalam seminggu
- [ ] (250701) Admin perlu download Kehadiran dalam sebulan untuk semua personil (nama, banyak hadir, banyak jam hadir, banyak lupa pulang) 
- [x] (250601) Admin perlu dapat melihat kehadiran setiap individu
- [ ] (250602) Admin perlu mampu melihat kehadiran per individu dalam sebulan (rekap)
- [ ] (250603) Pengguna dari tim proyek dapat melakukan absen Masuk dan Keluar, serta dapat melihat riwayat kehadiran
- [x] (241101) Aplikasi web dapat diakses melalui Internet dan menggunakan HP
- [x] (241102) Proyek dikerjakan oleh Kontraktor dengan konsultan supervisi, proyek punya waktu terbatas dan berkait dengan organisasi dalam Balai
- [x] (250501) Manajemen perlu dapat memantau kehadiran anggota tim proyek di lapangan

## Sprint Backlog

### (241101) Aplikasi web dapat diakses melalui Internet dan menggunakan HP
- [x] Sewa hosting VPS Cloud, Ubuntu, 2 GB Memory, 40 GB Storage
- [x] Konfigurasi Nginx web server dengan domain ppm.prinus.net
- [x] Konfigurasi Gunicorn dan systemd untuk automatic run
- [x] Konfigurasi / Create database dan table-table Postgresql
- [x] Buat dasar web app menggunakan Flask
- [x] Buat sistem authentikasi menggunakan flask-login, session base auth
- [x] Buat class-class untuk model data

### (250501) Manajemen perlu dapat memantau kehadiran anggota tim proyek di lapangan
