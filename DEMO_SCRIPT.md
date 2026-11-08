# Skenario demonstrasi Modul 10

Target: presentasi 5 menit, demo 5 menit, tanya jawab 3 menit, evaluasi 2 menit.

Sebelum kelas: nyalakan database dan aplikasi, periksa akun admin/pemilik, siapkan data demo, buka slide, hasil tes, screenshot dan skema SQL. Pastikan dependensi sudah terpasang agar alur inti bisa berjalan tanpa internet. Jangan jalankan init/seed pada database lama.

## Demo 5 menit

- 0:00–0:30 login admin, buka dashboard dan catat jumlah serta nilai selesai awal.
- 0:30–1:00 pilih atau tambah pelanggan uji unik, sumber WhatsApp.
- 1:00–2:00 input 2 Roti Coklat dan 1 Brownies. Total server Rp65.000. Simpan, catat nomor aktual.
- 2:00–2:35 cari nomor aktual, ubah diterima menjadi diproses lalu selesai, tunjukkan 3 log.
- 2:35–3:20 buka dashboard dan laporan. Selesai naik satu, nilai naik Rp65.000. Gunakan filter yang mencakup pesanan.
- 3:20–4:00 logout, login pemilik, buka laporan lalu akses /pesanan/baru untuk menunjukkan penolakan 403.
- 4:00–5:00 tunjukkan TC03 PASS dan TC21 FAIL sebelum fix lalu PASS sesudah fix dari evidence/module9.

Jika jumlah 0 terhalang validasi HTML, jelaskan bahwa bukti server ada pada TC11 yang mengirim POST langsung. Jangan mengklaim interaksi browser tersebut membuktikan validasi server.

Rehearsal lingkungan penyusunan Modul 10: 17 pemeriksaan browser lulus, AM-0011 Rp65.000, nilai awal Rp180.000 menjadi Rp245.000, selesai 3 menjadi 4, total 11 pesanan. Nomor dan angka pada laptop dapat berbeda karena data berbeda. Bandingkan selisih terhadap baseline lokal.

Hasil evaluasi manusia Modul 9 belum tersedia. Prototype interaktif asli Modul 6 belum tersedia; UI aktual digunakan sebagai demonstrasi implementasi. Bukti screenshot adalah cadangan, bukan demo langsung. Jika gangguan terjadi, jelaskan kondisi aktual sebelum beralih ke cadangan.
