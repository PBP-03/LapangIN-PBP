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

## ⚙️ Daftar Modul yang Akan Diimplementasikan

### 1. Modul Autentikasi & Manajemen Pengguna
Menangani seluruh proses login, register, dan manajemen peran pengguna (**Admin**, **Mitra**, **Penyewa**).  
**Fitur Utama:**
- Register & login dengan validasi email unik  
- Role-based access control (Admin / Mitra / Penyewa)  
- Manajemen profil pengguna (update nama, foto, kontak)  
- Middleware untuk membedakan halaman per role  
- Logout & session management  

---

### 2. Modul Manajemen Lapangan (Mitra & Admin)
Digunakan oleh Mitra untuk mengelola data lapangan serta oleh Admin untuk memverifikasi sebelum lapangan tampil di katalog.  
**Fitur Utama:**
- CRUD data lapangan  
- Upload foto (thumbnail utama)  
- Input detail lapangan: nama, jenis olahraga, harga per jam, lokasi, fasilitas, aturan venue, kebijakan refund/reschedule  
- Tambah tipe lapangan (misal: Court 1, Court 2)  
- Jadwal ketersediaan (hari & jam buka)  
- Admin dapat memverifikasi (ACC / tolak) lapangan sebelum tampil di katalog  

---

### 3. Modul Katalog & Pencarian Lapangan (Penyewa)
Menampilkan daftar semua lapangan yang telah diverifikasi dengan fitur pencarian dan filter.  
**Fitur Utama:**
- Menampilkan daftar lapangan (nama, foto, harga, lokasi)  
- Filter berdasarkan lokasi, jenis olahraga, dan rentang harga  
- Fitur pencarian lapangan  
- Halaman detail lapangan menampilkan foto, fasilitas, deskripsi, jadwal, dan daftar court tersedia  

---

### 4. Modul Booking & Jadwal (Penyewa & Mitra)
Mengatur seluruh proses pemesanan (booking) dan jadwal lapangan.  
**Fitur Utama:**
- **Penyewa:** Pilih lapangan & waktu yang tersedia  
- **Mitra:** Melihat & memperbarui status booking (Pending, Diterima, Selesai)  
- **Admin:** Memantau seluruh data booking  

---

### 5. Modul Pembayaran & Laporan Keuangan (Penyewa, Mitra, Admin)
Mengatur sistem pembayaran dan laporan keuangan.  
**Fitur Utama:**
- Simulasi pembayaran (dummy/virtual payment)  
- Update status pembayaran (belum/sudah bayar)  
- **Mitra:** Lihat riwayat transaksi & laporan pendapatan mingguan/bulanan  
- **Admin:** Pantau total transaksi global dan filter laporan berdasarkan waktu/lapangan  

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
