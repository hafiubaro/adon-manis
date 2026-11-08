# Adon Manis — Modul 10 Final Project

Nama: Muhammad Syafi’ul Mubarok  
NIM: 240605110029  
Kelas: M  
Proyek: Sistem Informasi Pengelolaan Pesanan Multi-Channel Adon Manis

Aplikasi inti menggunakan Python Flask dan MySQL/MariaDB. Admin memasukkan pesanan dari aplikasi asal secara manual. Pengguna langsung hanya admin dan pemilik. Petugas produksi menerima informasi dari admin.

## Modul 10 Final Project

Aplikasi menggunakan versi perbaikan Modul 9 tanpa perubahan fungsional atau skema. Tambahan Modul 10 berupa dokumentasi, presentasi, panduan pengguna, skenario demo, dan bukti rehearsal. Rehearsal menghasilkan **17 pemeriksaan browser lulus** di `evidence/module10`. Hasil ini terpisah dari pengujian kelas atau pengguna nyata.

Baca `USER_GUIDE.md` dan `DEMO_SCRIPT.md`. Dokumen, presentasi serta laporan Modul 9 tersedia dalam `docs`. Riwayat Git lengkap ada di `repository.bundle`.

**Masih perlu dilengkapi:** evaluasi oleh orang lain pada Modul 9, pemeriksaan lokal sebelum presentasi, dan artefak asli Modul 1–6/prototype jika dosen memintanya. Paket tidak mengklaim prototype interaktif Modul 6 pernah dibuat. Database operasional laptop tidak termasuk dalam backup source ini. Tidak ada password bawaan atau `.env` aktif dalam paket.

## Hasil Modul 9 dan status pengujian pengguna

Versi ini melanjutkan Modul 8 tanpa perubahan skema database. Eksekusi awal 21 kasus utama menghasilkan **18 PASS dan 3 FAIL**. Ketiga bug diperbaiki dan kasus yang sama diulang: **21 PASS**. Regresi lengkap menghasilkan **75 PASS** (50 lama + 21 utama + 4 penguatan). Lima pemeriksaan browser baru juga lulus. Bukti Modul 9 ada di `evidence/module9`; hasil Modul 7/8 tetap menjadi bukti historis masing-masing.

**User testing oleh orang lain belum dilakukan.** Tidak ada responden, komentar, atau skor usability yang dikarang. Jalankan prosedur `USER_TESTING.md`, lalu lengkapi Aktivitas 8 dan LKM 9.5. Hasil otomatis bukan pengganti penguji manusia.

Perbaikan yang terverifikasi:

1. BUG01 / TC19: token CSRF non-ASCII semula menyebabkan HTTP 500; sekarang ditolak 400 dengan pesan yang sesuai.
2. BUG02 / TC20: kegagalan koneksi DB semula menjadi 500 generik; sekarang 503 dengan panduan yang aman. Hanya kode kegagalan koneksi tertentu ditangani; error SQL lain tidak disamarkan. Ini tidak memperbaiki layanan DB yang sedang mati.
3. BUG03 / TC21: masukan pencarian `%` semula berlaku sebagai pola wildcard; sekarang karakter `%`, `_`, dan `!` dicari sebagai teks literal. Pencarian sebagian nama dan nomor pesanan tetap berfungsi.

Pengujian menggunakan Python 3.12.14, Flask 3.1.3, MariaDB 10.11.14 dan Chromium 153 pada 27 Oktober 2026 di lingkungan penyusunan. Belum diuji pada laptop mahasiswa, MySQL 8 secara langsung, beban tinggi, atau UAT usaha nyata.

### Menjalankan ulang kasus Modul 9

Ikuti pemasangan dan inisialisasi database uji pada bagian di bawah. Jangan gunakan database operasional. Dari folder aplikasi:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_module9.py -v
.\.venv\Scripts\python.exe -m pytest tests -v --junitxml=evidence/module9/local-results.xml
```

Fixture hanya menerima TEST_DB_NAME yang berbeda dari DB_NAME dan berakhir `_test`. Tes menghapus data pelanggan/transaksi pada database uji. TC18 membuat lalu menghapus trigger uji rollback sehingga akun database uji perlu izin CREATE TRIGGER. TC20 memakai port 1 pada konfigurasi instance uji saja untuk memicu connection refused; tidak menghentikan layanan database utama.

`case-results.json` memetakan 21 ID LKM ke hasil sebelum dan sesudah dari XML aktual. `before.txt`/`before.xml` menyimpan tiga kegagalan asli, `after.txt`/`after.xml` menyimpan 75 kelulusan akhir, dan `fix.patch` berisi perubahan aplikasi. Screenshot berawalan before/after memuat pasangan bukti ketiga bug. `before_browser.json` mempertahankan `passed:false` untuk ketiga requirement yang belum terpenuhi.

### Riwayat yang dapat diperiksa

- `4aad415`: versi akhir Modul 8.
- `ada606e`: menambahkan 21 kasus utama, aplikasi masih sebelum fix.
- `b702b4f`: menyimpan bukti awal, aplikasi masih sebelum fix.
- `f4a5a6c`: memperbaiki tiga bug dan menambah empat tes penguatan.

Untuk reproduksi hasil sebelum fix, clone `repository.bundle` ke folder baru dan checkout `b702b4f`, buat konfigurasi .env serta database uji terpisah, lalu jalankan `tests/test_module9.py`. Jangan checkout versi lama di folder kerja berisi perubahan Anda.

`tools/module9_browser.cjs` untuk pemeriksaan teknis melalui browser. Pasang Playwright dan Chromium pada lingkungan tes, jalankan aplikasi di port 5000 dan satu instance khusus DB tidak tersedia di port 5001, isi `E2E_ADMIN_PASSWORD`, kemudian jalankan script. Instance kedua dibuat dengan `create_app({'DB_PORT':1})`; jangan mengubah .env aplikasi operasional. Script default fase `after`, memakai 10 pesanan dari seed demonstrasi baru (nilai selesai Rp180.000). `APP_URL` dan `OUTAGE_URL` dapat disesuaikan. Jangan menggunakannya pada database berisi data penting. Screenshot browser adalah bukti teknis, bukan observasi manusia.

## Fungsi aplikasi yang diteruskan


- Login, logout, session, proteksi halaman, otorisasi dua role, dan CSRF.
- CRUD pelanggan, validasi nama/telepon, normalisasi nomor Indonesia, dan perlindungan penghapusan pelanggan berelasi.
- UC-02: input pesanan dengan beberapa produk, harga dari database, total otomatis, peringatan duplikasi, dan penyimpanan pesanan + detail + log dalam satu transaksi.
- Perubahan status maju satu tahap, pembatalan dengan alasan, riwayat perubahan.
- Ringkasan operasional; nilai pesanan selesai mengecualikan pesanan diterima, diproses, dan dibatalkan. Nilai ini bukan penerimaan uang.
- Pencarian pesanan dan filter status dasar.

Modul 8 menambahkan laporan per sumber/periode, filter tanggal pencatatan atau penyelesaian, dan cetak/simpan PDF melalui browser. CRUD produk/channel, pemulihan password, dan pengujian pengguna nyata belum disertakan. Tidak ada integrasi API marketplace, pembayaran online, atau sistem persediaan. Pembatalan bahan habis berdasarkan konfirmasi admin, bukan perhitungan stok.

## Menjalankan di Windows

Gunakan Python 3.12, VS Code, Git, serta MySQL 8 atau MariaDB melalui XAMPP. Pengujian yang disertakan memakai MariaDB 10.11.14; MySQL 8 belum diuji langsung. Flask menjalankan server aplikasi sendiri. Pada XAMPP cukup jalankan layanan database; Apache tidak wajib untuk aplikasi ini.

1. Ekstrak ZIP dan buka folder `adon-manis` di VS Code. Buka **Terminal > New Terminal**.
2. Periksa `py --version`, lalu jalankan:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_hex(32))"
```

3. Buka `.env`. Ganti `SECRET_KEY` dengan hasil perintah terakhir. Sesuaikan `DB_HOST`, `DB_PORT`, `DB_USER`, dan `DB_PASSWORD` dengan database lokal. Default port database XAMPP biasanya 3306. Port 3307 yang tercatat pada bukti hanya digunakan di lingkungan pengujian.
4. Jalankan layanan MySQL/MariaDB. Buat skema dan akun aplikasi:

```powershell
.\.venv\Scripts\python.exe init_db.py
```

Masukkan password baru admin dan pemilik, masing-masing minimal 10 karakter. Input password tidak tampil di terminal. Username: `admin` dan `pemilik`. Tidak ada password bawaan untuk instalasi pengguna.

Script membuat database `adon_manis` dan tujuh tabel. Script akan **berhenti bila database sudah berisi tabel** agar data tidak tertimpa. Jika nama tersebut sudah digunakan untuk proyek lain, atur nama database baru di `.env`; jangan menghapus database lama. Script ini adalah inisialisasi, bukan migrasi untuk skema lama.

5. Opsional, tambahkan sepuluh pesanan fiktif untuk demonstrasi:

```powershell
.\.venv\Scripts\python.exe seed_demo.py
```

Seed hanya berjalan ketika tabel pesanan kosong. Data master berisi lima pelanggan fiktif, lima produk, enam sumber pesanan, dan dua akun sesuai role. Tidak dibuat akun tambahan hanya untuk memenuhi jumlah master yang tidak relevan.

6. Jalankan aplikasi:

```powershell
.\.venv\Scripts\python.exe run.py
```

Buka http://127.0.0.1:5000. Hentikan server dengan Ctrl+C. Server ini untuk praktikum lokal; paket belum dikonfigurasi untuk hosting publik.

## Alur penggunaan

1. Login sebagai admin.
2. Buka Pelanggan, tambah pelanggan bila belum terdaftar.
3. Buka Pesanan baru, pilih pelanggan dan sumber pesanan.
4. Pilih produk serta jumlah. Gunakan Tambah produk untuk baris lain.
5. Tekan Simpan pesanan. Bila ada potensi duplikat, periksa nomor pesanan yang ditampilkan, kemudian batalkan input atau konfirmasi dengan alasan.
6. Buka detail untuk mengubah diterima → diproses → selesai. Tidak boleh melompat atau mundur.
7. Pembatalan bahan baku tersedia pada status diterima/diproses. Pembatalan karena tidak merespons hanya tersedia secara bisnis untuk status diterima setelah minimal 30 menit sejak pencatatan; server menolak kondisi lainnya.
8. Login sebagai pemilik untuk melihat ringkasan dan laporan tanpa hak menambah, mengubah, atau menghapus data.

## Aturan operasional yang dipakai

- `waktu_masuk` adalah waktu pencatatan di sistem dalam WIB, bukan hasil sinkronisasi waktu marketplace.
- Potensi duplikat: ID pelanggan atau nama pelanggan yang sama, dalam 10 menit terakhir, pada sumber mana pun, dan pesanan sebelumnya tidak dibatalkan. Batas 10 menit adalah parameter implementasi awal, perlu dievaluasi bersama pengguna nyata.
- Peringatan duplikasi tidak langsung menghapus atau menolak pesanan sah. Konfirmasi admin wajib disertai alasan 5–255 karakter.
- Token input unik mencegah satu form tersimpan dua kali akibat pengiriman ulang.
- Nomor telepon opsional. Bila diisi, format dinormalisasi ke awalan 0 dan tidak boleh sama dengan pelanggan lain. Aturan keunikan ini perlu ditinjau bila beberapa pelanggan memakai satu nomor keluarga.
- Jumlah produk 1–999 per baris; maksimal 20 baris; produk sama harus digabung dalam satu baris.
- Harga satuan disalin ke detail saat transaksi agar perubahan harga master tidak mengubah riwayat harga.
- Pelanggan yang memiliki pesanan tidak dapat dihapus. Pesanan tidak dihapus; gunakan pembatalan yang tercatat.
- Jam operasional belum ditentukan sehingga tidak ada larangan waktu input yang dibuat dari asumsi availability.

## Pengujian otomatis dan hasil historis Modul 8

`TEST_DB_NAME` harus berbeda dari `DB_NAME` dan berakhir `_test`. Inisialisasikan satu kali:

```powershell
.\.venv\Scripts\python.exe init_db.py --test
.\.venv\Scripts\python.exe -m pytest tests -v --junitxml=evidence/pytest-results-local.xml
```

Tes menghapus data transaksi/pelanggan dan mengganti password akun di **database khusus pengujian** pada setiap kasus. Jangan gunakan database berisi data penting sebagai TEST_DB_NAME. Fixture menolak nama yang tidak berakhir `_test` atau sama dengan DB_NAME.

Hasil Modul 8: **50 tes pytest lulus, 0 gagal**, termasuk 35 kasus Modul 7 yang dijalankan ulang dan 15 kasus integrasi/filter/laporan. Ditambah **17 pemeriksaan browser lulus** pada Chromium 153. Python 3.12.14, Flask 3.1.3, MariaDB 10.11.14. Bukti aktual ada di `evidence/module8/`; bukti historis Modul 7 terpisah di `evidence/module7/`. Pengujian dilakukan di lingkungan penyusunan, belum di laptop mahasiswa dan belum UAT pemilik usaha.

Contoh pengujian: 2 Roti Coklat × Rp15.000 + 1 Brownies × Rp35.000 = Rp65.000. Server tetap menghitung Rp65.000 ketika client mengirim total palsu Rp1. Tes juga membuktikan rollback ketika penulisan log gagal.

## Peningkatan dari Modul 7

- Tidak ada perubahan skema: tujuh tabel dan data Module 7 tetap digunakan. Untuk upgrade, hentikan aplikasi, cadangkan database, salin source baru, pertahankan `.env` lokal lalu jalankan lagi. **Jangan jalankan init_db.py atau seed_demo.py pada database lama.**
- Daftar pesanan: nama/nomor + status + sumber + tanggal pencatatan.
- Dashboard: empat indikator, tujuh pesanan terbaru, dan rekap sumber; filter memakai seleksi data yang sama dengan laporan.
- Laporan pesanan dan sumber: data rinci, rekap status, total nilai selesai, rekap sumber, periode/filter tercetak, tombol Cetak / Simpan PDF (dialog cetak browser, bukan ekspor PDF sisi server). Tidak ada ekspor Excel.
- Dasar tanggal **Pencatatan** menyeleksi `waktu_masuk`, kemudian menampilkan status terkini. Dasar **Penyelesaian** menyeleksi `waktu_selesai` dan hanya pesanan selesai. Pilih dasar penyelesaian untuk rekap nilai pesanan selesai pada bulan tertentu. Semua waktu WIB; batas akhir tanggal inklusif.
- Filter kosong berarti seluruh data. Kombinasi filter yang tidak cocok menampilkan kosong dan nilai nol. Tanggal tidak valid atau awal melebihi akhir ditolak HTTP 400.
- Total diambil satu kali per header pesanan, bukan dijumlah ulang akibat join ke beberapa detail. Data harga historis tetap dari detail transaksi.
- Kode aturan lama dipertahankan: BR01 login; BR03 pembatalan beralasan; BR04 urutan status; BR05 log status. BR02 pembatasan jam operasional tidak diterapkan karena jam tersebut belum ditetapkan. Validasi pelanggan, jumlah, dan total merupakan penguatan teknis, bukan penggantian arti kode lama.

### Pemeriksaan browser yang dapat diulang

Jalankan pada database DEMO baru dengan nama berbeda, isi `init_db.py` dan `seed_demo.py`, lalu jalankan aplikasinya. Jangan memakai data operasional: skenario menambahkan dan menyelesaikan satu pesanan. Script mengharapkan seed awal 10 pesanan, 3 selesai, nilai Rp180.000; setelah skenario 11 pesanan, 4 selesai, nilai Rp245.000.

Instal Node.js dan Playwright pada lingkungan pengujian terpisah, kemudian `npm install playwright` dan `npx playwright install chromium`. Atur `E2E_ADMIN_PASSWORD` dan `E2E_OWNER_PASSWORD` sesuai akun database demo, lalu `node tools/e2e_browser.cjs`. `APP_URL` opsional, default http://127.0.0.1:5000. Script menyimpan hasil, screenshot dan PDF cetak pada `evidence/module8`. Instalasi browser dapat membutuhkan akses internet. Password tidak disertakan dalam paket.

## Struktur kode

| Lokasi | Fungsi |
|---|---|
| `run.py` | Menjalankan aplikasi lokal |
| `app/__init__.py` | Factory, konfigurasi, CSRF, penanganan error |
| `app/db.py` | Koneksi database dan pembacaan data |
| `app/auth.py` | Login, logout, session, otorisasi |
| `app/customers.py` | CRUD serta validasi pelanggan |
| `app/orders.py` | Route input/detail/status/ringkasan |
| `app/reporting.py` | Seleksi periode dan ringkasan bersama |
| `app/services.py` | Aturan bisnis dan transaksi database |
| `app/templates/` | Tampilan HTML Jinja |
| `app/static/` | CSS dan JavaScript |
| `database/schema.sql` | Skema revisi tujuh tabel |
| `init_db.py`, `seed_demo.py` | Inisialisasi dan data demonstrasi |
| `tests/` | Pengujian integrasi HTTP dan database |
| `evidence/` | Hasil tes serta screenshot |

## Version control

Riwayat commit lokal yang dibuat selama penyusunan disertakan dalam `repository.bundle`. Untuk melihat log tanpa mengubah folder kerja:

```powershell
git clone repository.bundle adon-manis-dengan-riwayat
cd adon-manis-dengan-riwayat
git log --oneline
```

Commit dibuat oleh Codex sebagai alat bantu pengerjaan dan tidak diklaim sebagai riwayat kerja mahasiswa sebelumnya. Belum ada repository GitHub yang dibuat atau dipublikasikan. `.env` dan virtual environment tidak disertakan. Setelah mengerjakan perubahan sendiri, gunakan commit deskriptif, misalnya `git commit -m "Tambahkan laporan nilai pesanan selesai per periode"`.

## Referensi teknis

- Modul 9 Praktikum Sistem Informasi, Kegiatan halaman 169–171 dan LKM halaman 172–174.
- Modul 8 Praktikum Sistem Informasi, Kegiatan halaman 145–149 dan LKM halaman 149–151.
- Modul 7 Praktikum Sistem Informasi, Aktivitas halaman 129–132 dan LKM halaman 133–134.
- Flask: https://flask.palletsprojects.com/en/stable/
- PyMySQL: https://pymysql.readthedocs.io/en/latest/user/examples.html
