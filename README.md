# LapangIN

## 👥 Nama-nama Anggota Kelompok
- **Flora Cahaya Putri** – 2406350955  
- **Marlond Leanderd Batara** – 2406496201  
- **Muhammad Fauzan** – 2406496302  
- **Nadila Salsabila Fauziyyah** – 2406425590  
- **Rayyan Akbar Gumilang** – 2406496422  

---

## 📝 Deskripsi Aplikasi
**LapangIN** adalah aplikasi yang dikembangkan untuk mempermudah proses penyewaan lapangan olahraga.  
Aplikasi ini berfungsi sebagai penghubung antara **mitra (pemilik lapangan)** dan **penyewa** yang ingin melakukan pemesanan lapangan olahraga seperti futsal, badminton, basket, padel, dan tenis.  

Dengan **LapangIN**, mitra mendapatkan peluang untuk menambah pemasukan serta meningkatkan visibilitas lapangan mereka.  
Sementara itu, penyewa mendapatkan kemudahan dalam mencari, memilih, dan melakukan reservasi secara online.  
**Admin** berperan penting dalam menjaga kualitas sistem dengan memverifikasi mitra serta memantau aktivitas transaksi dan data.  


---

## ⚙️ **Daftar Modul yang Akan Diimplementasikan**

### 1. Modul Booking & Pembayaran (User) -> Muhammad Fauzan

Menangani seluruh proses pemesanan lapangan oleh **Penyewa (User)**, mulai dari pemilihan jadwal hingga konfirmasi pembayaran.
**Fitur Utama:**

* Pemesanan lapangan dengan memilih venue, jenis lapangan, dan jadwal tersedia
* Melihat daftar & riwayat booking beserta detail waktu, harga, dan status pembayaran
* Mengubah atau membatalkan booking selama belum melewati batas waktu yang ditentukan
* Melakukan proses pembayaran agar lapangan berstatus *ter-booking* secara resmi

---

### 2. Modul Manajemen Lapangan (Mitra) -> Rayyan Akbar Gumilang

Digunakan oleh **Mitra** untuk mengelola lapangan yang berada di dalam venue miliknya serta memantau aktivitas penyewaan.
**Fitur Utama:**

* Tambah, edit, dan hapus data lapangan (court) di dalam venue
* Mengatur detail lapangan: jenis olahraga, harga, jadwal ketersediaan, dan status aktif
* Sistem otomatis mencatat pendapatan berdasarkan hasil booking yang dilakukan pengguna
* Melihat riwayat dan catatan seluruh pesanan untuk setiap lapangan

---

### 3. Modul Admin & Verifikasi Mitra -> Flora Cahaya Putri

Digunakan oleh **Admin** untuk mengelola aktivitas sistem, khususnya terkait verifikasi Mitra, transaksi, dan refund.
**Fitur Utama:**

* Verifikasi Mitra & Venue (ACC atau tolak pendaftaran setelah meninjau detail deskripsi dan gambar)
* Melihat total pendapatan Mitra berdasarkan hasil transaksi penyewaan lapangan
* Membuat create manual refund untuk pengembalian dana booking
* Membatalkan atau menghapus permintaan refund yang tidak disetujui
* Meninjau seluruh data Mitra yang terdaftar beserta detail venue dan status verifikasi

---

### 4. Modul Manajemen Profil & Venue (User & Mitra) -> Marlond Leanderd Batara

Digunakan oleh **User dan Mitra** untuk mengelola data profil serta mengatur informasi venue yang dimiliki oleh Mitra.
**Fitur Utama:**

* **Edit Profil:** Mengubah username, nama depan & belakang, serta foto profil
* **Hapus Akun:** Menghapus akun secara permanen dari sistem
* **Manajemen Venue (Mitra):**

  * Tambah venue baru dengan data seperti nama, lokasi, jenis olahraga, harga, dan deskripsi
  * Edit venue (nama, harga rata-rata, deskripsi, kategori olahraga, dan maintenance)
  * Hapus venue (otomatis menghapus seluruh court yang terkait dengan venue tersebut)

---

### 5. Modul Katalog & Detail Venue -> Nadila Salsabila Fauziyyah

Menampilkan daftar venue olahraga yang tersedia dan menyediakan fitur pencarian serta informasi detail setiap venue.
**Fitur Utama:**

* Menampilkan daftar venue lengkap (foto, nama, lokasi, rating, dan harga)
* Pencarian & filter berdasarkan nama, lokasi, rating, dan rentang harga
* Halaman detail menampilkan foto, deskripsi, fasilitas, harga, jadwal ketersediaan, dan review pengguna
* **Review:** Pengguna yang sudah booking dapat membuat, mengubah, dan menghapus review secara langsung di halaman detail venue

---

## 📊 Sumber Initial Dataset Kategori Utama Produk
- [https://www.gelora.id/](https://www.gelora.id/)  
- [https://ayo.co.id/](https://ayo.co.id/)  
- [https://www.google.com/maps](https://www.google.com/maps)  

---

## 👤 Role atau Peran Pengguna

### Mitra
Pemilik atau pengelola lapangan olahraga yang ingin menyewakan fasilitasnya kepada masyarakat.  
**Fitur Mitra:**
- Menambahkan data lapangan (nama, jenis olahraga, harga, lokasi)  
- Melihat status booking yang masuk  
- Memantau pemasukan dan laporan transaksi  

---

### Penyewa (User)
Pengguna aplikasi yang ingin mencari dan menyewa lapangan olahraga sesuai kebutuhan.  
**Fitur Penyewa:**
- Mencari lapangan berdasarkan olahraga, lokasi, atau harga  
- Melakukan booking lapangan  
- Melakukan pembayaran secara online  

---

### Admin
Pengelola sistem yang bertugas menjaga kelancaran operasional dan keamanan data.  
**Fitur Admin:**
- Verifikasi mitra dan data lapangan  
- Mengelola aktivitas dan transaksi  
- Melakukan logging aktivitas mitra dan penyewa  

---

## Tautan Deployment & Desain
- **Link Design (Figma):** [https://www.figma.com/team_invite/redeem/H4djMUeJW2NmihEoMSnvd2](https://www.figma.com/team_invite/redeem/H4djMUeJW2NmihEoMSnvd2)  
- **Deployment (PWS):** [https://muhammad-fauzan44-lapangin.pbp.cs.ui.ac.id/] (https://muhammad-fauzan44-lapangin.pbp.cs.ui.ac.id/)

---

## 🚀 Cara Menjalankan Aplikasi di Lokal

### 1️⃣ Prerequisites
Pastikan sudah terinstall:
- **Python 3.8+** ([Download Python](https://www.python.org/downloads/))
- **Git** ([Download Git](https://git-scm.com/downloads))
- **pip** (biasanya sudah include dengan Python)

### 2️⃣ Clone Repository
```bash
git clone https://github.com/PBP-03/LapangIN-PBP.git
cd LapangIN-PBP
```

### 3️⃣ Buat Virtual Environment
**Windows (PowerShell):**
```powershell
python -m venv env
.\env\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
python -m venv env
env\Scripts\activate.bat
```

**macOS/Linux:**
```bash
python3 -m venv env
source env/bin/activate
```

### 4️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 5️⃣ Setup Database
```bash
# Jalankan migrations
python manage.py migrate

# (Optional) Buat superuser untuk admin
python manage.py createsuperuser
```

### 6️⃣ Jalankan Development Server
```bash
python manage.py runserver
```

Server akan berjalan di: **http://localhost:8000**

### 7️⃣ Akses Aplikasi
- **Homepage**: [http://localhost:8000](http://localhost:8000)
- **Admin Panel**: [http://localhost:8000/admin-django/](http://localhost:8000/admin-django/)
- **API Documentation**: Lihat file `test_api.html` untuk testing API

---

## 👨‍💼 Login sebagai Admin

Untuk login sebagai admin, ikuti 3 langkah berikut secara berurutan:

### Langkah 1: Ubah Password Admin Melalui Terminal
Jalankan command berikut di terminal:
```bash
python manage.py changepassword admin
```
- Masukkan password baru saat diminta
- Konfirmasi password baru
- **Penting**: Username yang digunakan adalah `admin` (sudah tersedia di database)

### Langkah 2: Verifikasi Login di Django Administration
1. Buka browser dan akses **http://localhost:8000/admin-django/**
2. Login dengan:
   - **Username**: `admin`
   - **Password**: Password baru yang baru saja dibuat di Langkah 1
3. Jika berhasil masuk, berarti password sudah ter-update dengan benar

### Langkah 3: Login di Aplikasi Utama
1. Buka **http://localhost:8000** di browser
2. Klik tombol **"Login"** pada navbar
3. Masukkan kredensial yang sama:
   - **Username**: `admin`
   - **Password**: Password yang sudah diubah di Langkah 1
4. Klik **"Login"** dan Anda akan masuk sebagai **Admin**

### 💡 Catatan Penting:
- Username `admin` sudah tersedia di database (tidak perlu buat user baru)
- Password **wajib diubah** melalui command `changepassword` sebelum bisa login
- Password yang sama digunakan untuk Django Admin dan aplikasi utama
- Pastikan menjalankan ketiga langkah secara berurutan

---

## 🧪 Menjalankan Unit Tests

### Test Semua Modul
```bash
python manage.py test
```

### Test Modul Spesifik (contoh: reviews)
```bash
python manage.py test app.reviews.tests
```

### Test dengan Coverage
```bash
pip install coverage

coverage run --source='.' manage.py test

coverage report

coverage html
```