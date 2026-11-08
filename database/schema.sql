-- Skema revisi Modul 5. Tidak menghapus tabel/data yang sudah ada.
-- init_db.py hanya boleh dijalankan pada database kosong.
CREATE TABLE pelanggan (
 id_pelanggan INT PRIMARY KEY AUTO_INCREMENT,
 nama VARCHAR(100) NOT NULL,
 no_telepon VARCHAR(20) NULL,
 UNIQUE KEY uq_pelanggan_telepon (no_telepon)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE channel (
 id_channel INT PRIMARY KEY AUTO_INCREMENT,
 nama_channel VARCHAR(50) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE produk (
 id_produk INT PRIMARY KEY AUTO_INCREMENT,
 nama_produk VARCHAR(100) NOT NULL,
 harga DECIMAL(10,2) NOT NULL CHECK (harga > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE pengguna (
 id_pengguna INT PRIMARY KEY AUTO_INCREMENT,
 nama VARCHAR(100) NOT NULL,
 username VARCHAR(50) NOT NULL UNIQUE,
 password_hash VARCHAR(255) NOT NULL,
 role VARCHAR(20) NOT NULL CHECK (role IN ('admin','pemilik'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE pesanan (
 id_pesanan INT PRIMARY KEY AUTO_INCREMENT,
 id_pelanggan INT NOT NULL,
 id_channel INT NOT NULL,
 waktu_masuk DATETIME NOT NULL,
 status VARCHAR(20) NOT NULL DEFAULT 'diterima'
   CHECK (status IN ('diterima','diproses','selesai','dibatalkan')),
 total_harga DECIMAL(14,2) NOT NULL DEFAULT 0 CHECK (total_harga >= 0),
 waktu_selesai DATETIME NULL,
 alasan_pembatalan VARCHAR(255) NULL,
 id_pencatat INT NOT NULL,
 kunci_input VARCHAR(64) NOT NULL UNIQUE,
 catatan_duplikat VARCHAR(255) NULL,
 FOREIGN KEY (id_pelanggan) REFERENCES pelanggan(id_pelanggan) ON DELETE RESTRICT,
 FOREIGN KEY (id_channel) REFERENCES channel(id_channel) ON DELETE RESTRICT,
 FOREIGN KEY (id_pencatat) REFERENCES pengguna(id_pengguna) ON DELETE RESTRICT,
 INDEX idx_pesanan_pelanggan_waktu (id_pelanggan,waktu_masuk)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE detail_pesanan (
 id_detail INT PRIMARY KEY AUTO_INCREMENT,
 id_pesanan INT NOT NULL,
 id_produk INT NOT NULL,
 jumlah INT NOT NULL CHECK (jumlah BETWEEN 1 AND 999),
 harga_satuan DECIMAL(10,2) NOT NULL CHECK (harga_satuan > 0),
 subtotal DECIMAL(14,2) NOT NULL CHECK (subtotal > 0),
 UNIQUE KEY uq_item (id_pesanan,id_produk),
 FOREIGN KEY (id_pesanan) REFERENCES pesanan(id_pesanan) ON DELETE RESTRICT,
 FOREIGN KEY (id_produk) REFERENCES produk(id_produk) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE status_log (
 id_log INT PRIMARY KEY AUTO_INCREMENT,
 id_pesanan INT NOT NULL,
 id_pengguna INT NOT NULL,
 status_lama VARCHAR(20) NULL,
 status_baru VARCHAR(20) NOT NULL,
 waktu_perubahan DATETIME NOT NULL,
 alasan VARCHAR(255) NULL,
 FOREIGN KEY (id_pesanan) REFERENCES pesanan(id_pesanan) ON DELETE RESTRICT,
 FOREIGN KEY (id_pengguna) REFERENCES pengguna(id_pengguna) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
