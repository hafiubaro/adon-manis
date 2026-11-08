# Panduan pengguna Adon Manis

1. Jalankan database dan aplikasi lokal sesuai README. Instalasi baru: virtual environment, requirements, .env dengan secret acak, init_db.py pada database kosong. Akun admin dan pemilik menggunakan password yang Anda buat saat inisialisasi. Jalankan run.py dan buka http://127.0.0.1:5000.
2. Login admin untuk menu Ringkasan, Pesanan, Pelanggan, Laporan. Pemilik hanya membaca Ringkasan dan Laporan.
3. Tambah pelanggan bila diperlukan. Buat pesanan, pilih pelanggan serta sumber, pilih produk dan jumlah. Total akhir dihitung ulang server dari master harga. Maksimal 20 baris, jumlah 1–999 tiap baris. Produk sama digabung dalam satu baris.
4. Tinjau peringatan duplikasi sebelum meneruskan. Jika ini pesanan berbeda, isi konfirmasi dan alasan.
5. Pada detail pesanan, jalankan diterima, diproses, lalu selesai. Status tidak boleh melompat atau mundur. Pembatalan bahan habis berlaku pada diterima/diproses. Tidak merespons hanya pada diterima setelah minimal 30 menit sejak pencatatan.
6. Laporan mendukung filter sumber, status dan periode. Dasar pencatatan memilih tanggal masuk dengan status terkini. Dasar penyelesaian memilih tanggal selesai dan hanya pesanan selesai. Tanggal akhir termasuk dan waktu WIB. Gunakan Cetak / Simpan PDF melalui browser.
7. Nilai pesanan selesai belum menyatakan penerimaan uang atau laba. Pembayaran, biaya dan stok belum dicatat.
8. Klik Keluar untuk mengakhiri sesi. Jika database terputus, pulihkan koneksi dan periksa apakah pesanan sudah tersimpan sebelum mengirim ulang.

Untuk upgrade Modul 9 ke Modul 10 tidak ada perubahan aplikasi atau migrasi database. Pertahankan .env dan data lokal. Cadangkan source, konfigurasi privat serta ekspor database dengan alat MySQL/MariaDB. ZIP berisi skema/seed, bukan salinan data laptop.
