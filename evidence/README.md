# Bukti pengujian Modul 7

Data pelanggan/pesanan adalah data fiktif. Bukti diperoleh dari aplikasi dan MariaDB yang benar-benar dijalankan pada lingkungan penyusunan 13 Oktober 2026.

- pytest-results.xml: 35 hasil pengujian integrasi menggunakan database adon_manis_test.
- test-run.txt: log pytest, seluruh 35 tes lulus.
- browser-results.json: 13 hasil pemeriksaan melalui browser Chromium.
- 01_login.png: halaman autentikasi.
- 02_dashboard.png: ringkasan sebelum transaksi uji browser.
- 03_pelanggan.png: hasil tambah pelanggan uji.
- 04_form_pesanan.png: input dua roti coklat dan satu brownies, total Rp65.000.
- 05_detail_pesanan.png: pesanan AM-0011 tersimpan, status diterima.
- 06_peringatan_duplikat.png: peringatan terhadap pesanan pelanggan yang sama.
- 07_mobile.png: tampilan mobile sesudah AM-0011 diselesaikan.

Pemeriksaan browser dilakukan otomatis dengan Playwright dan ditinjau secara visual. Ini bukan hasil wawancara, pengujian oleh pemilik usaha, atau bukti aplikasi sudah dijalankan di laptop mahasiswa. Screenshot desktop awal dan mobile akhir berbeda nilai karena transaksi uji sudah ditambahkan dan diselesaikan.
