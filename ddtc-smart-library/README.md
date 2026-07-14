# SIPAKAR AHP — DDTC Library

Sistem Pendukung Keputusan (SPK) untuk menentukan **prioritas pengembangan
koleksi buku pajak** di Danny Darussalam Tax Center (DDTC) Library,
menggunakan metode **Analytical Hierarchy Process (AHP)** multi-pakar dengan
8 kriteria (K1–K8) berbasis rubrik data objektif.

Dibangun sesuai *Blueprint SPK AHP DDTC Library* (BRD/PRD/SRD/ERD) dengan
stack **Python 3.11+ · Streamlit · SQLite · Pandas · NumPy**.

## Fitur Utama

- **3 Form Master**: Data Buku, Kriteria & Rubrik, Data Pakar
- **Perbandingan Berpasangan Kriteria** per pakar (skala Saaty 1–9) dengan
  indikator Consistency Ratio (CR) real-time
- **Mesin AHP**: agregasi multi-pakar (rata-rata geometrik), eigenvector,
  uji konsistensi, sintesis skor akhir tiap buku (Rating-Scale AHP)
- **Rule Engine** otomatis: skor K1–K8 dihitung dari data mentah buku sesuai
  rubrik resmi (lihat `core/rule_engine.py`)
- **Modul Anggaran**: alokasi & cut-off anggaran pengadaan berbasis peringkat
- **4 Laporan Utama**: Matriks AHP, Penilaian Alternatif Buku, Peringkat
  Prioritas, Analisis Grafik Anggaran — dapat diekspor ke Excel
- **Riwayat Perhitungan** (histori batch), **Manajemen Pengguna**, dan
  **Log Aktivitas** (audit trail)
- Akses internal-only (Admin & Pustakawan), password di-hash dengan bcrypt

## Struktur Proyek

```
sipakar_ahp_ddtc/
├── app.py                          # Entry point: login + st.navigation (menu sidebar)
├── app_pages/                       # Halaman-halaman aplikasi (dirouting via st.navigation)
│   ├── dashboard.py
│   ├── data_buku.py                 # Form Master 1
│   ├── kriteria_rubrik.py           # Form Master 2
│   ├── data_pakar.py                # Form Master 3
│   ├── perbandingan_kriteria.py
│   ├── proses_hasil_ahp.py
│   ├── analisis_anggaran.py
│   ├── laporan.py                   # 4 Laporan Utama
│   ├── riwayat_perhitungan.py
│   ├── manajemen_pengguna.py        # khusus Admin
│   └── log_aktivitas.py             # khusus Admin
├── core/
│   ├── ahp_engine.py                # normalisasi, eigenvector, CI/CR, sintesis
│   ├── rule_engine.py               # pemetaan data mentah buku -> skor 1-5
│   └── auth.py                      # login, hashing, session guard
├── db/
│   ├── schema.sql                   # DDL 13 tabel (lihat Blueprint ERD §4)
│   ├── database.py                  # koneksi SQLite, init skema
│   ├── repository.py                # query CRUD terparameterisasi
│   └── seed.py                      # seed users, kriteria, rubrik, 100 buku
├── data/
│   ├── 100_data_buku_sisca_update.xlsx  # sumber data seed
│   └── db_ahp_ddtc.sqlite3          # (dibuat otomatis, di-gitignore)
├── tests/
│   ├── test_ahp_engine.py           # 9 unit test
│   └── test_rule_engine.py          # 42 unit test (parametrized)
├── requirements.txt
└── README.md
```

Navigasi sidebar didefinisikan secara eksplisit di `app.py` memakai
`st.Page`/`st.navigation` (bukan mengandalkan urutan nama file), dikelompokkan
menjadi 4 bagian: **Utama**, **Master Data**, **Proses AHP**, **Laporan** —
ditambah **Administrasi** yang hanya muncul untuk role Admin. Pengguna tanpa
hak admin bahkan tidak bisa membuka URL halaman admin secara langsung karena
halaman tersebut tidak terdaftar di navigasi mereka.

## Instalasi & Menjalankan

```bash
# 1. Buat virtual environment (disarankan)
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 2. Install dependensi
pip install -r requirements.txt

# 3. Jalankan aplikasi (database & data awal otomatis dibuat saat pertama kali run)
streamlit run app.py
```

Aplikasi akan terbuka di `http://localhost:8501`.

### Akun Default

| Username     | Password            | Role        |
|--------------|----------------------|-------------|
| `admin`      | `ubah_password_ini`  | admin       |
| `pustakawan` | `ubah_password_ini`  | pustakawan  |

**⚠️ Segera ganti password default ini setelah login pertama** melalui
halaman *Manajemen Pengguna* (khusus Admin) — kredensial default hanya untuk
uji coba awal, sesuai catatan keamanan pada Blueprint ERD §4.2.

### Reset Database (opsional, untuk pengembangan)

```bash
python -m db.seed --reset
```

Perintah ini menghapus seluruh data dan menyeed ulang dari awal (users, 8
kriteria + rubrik, lookup topik/penerbit, dan 100 buku dari
`data/100_data_buku_sisca_update.xlsx`).

## Menjalankan Unit Test

```bash
pip install pytest
pytest tests/ -v
```

51 unit test mencakup fungsi murni pada `core/ahp_engine.py` (perhitungan
matriks, eigenvector, CR, agregasi multi-pakar, sintesis skor, alokasi
anggaran) dan `core/rule_engine.py` (pemetaan skor K1–K8 sesuai rubrik resmi).

## Alur Kerja Singkat

1. **Login** sebagai admin/pustakawan.
2. Lengkapi **Form Master**: Data Buku (sudah terisi 100 buku dari seed),
   Kriteria & Rubrik (sudah terisi K1–K8), Data Pakar (sudah ada 3 contoh —
   sesuaikan dengan pakar sesungguhnya).
3. Buka **Perbandingan Kriteria**, pilih pakar, isi matriks 8×8, perhatikan
   indikator CR (harus < 0,10 agar konsisten). Ulangi untuk tiap pakar.
4. Buka **Proses & Hasil AHP**, klik **Jalankan Perhitungan AHP Sekarang**.
5. Buka **Analisis Anggaran**, masukkan total anggaran, lihat rekomendasi
   buku yang terjangkau.
6. Buka **Laporan** untuk mengunduh 4 laporan resmi (Excel).
7. Riwayat setiap perhitungan tersimpan di **Riwayat Perhitungan**.

## Catatan Desain

- **Rating-Scale AHP**: bobot kriteria (K1–K8) dihitung dengan AHP klasik
  (pairwise comparison, multi-pakar), sedangkan skor tiap buku dihasilkan
  otomatis dari rule engine berbasis data objektif (bukan pairwise manual
  antar-buku) — supaya sistem tetap scalable untuk ratusan judul usulan.
  Lihat Blueprint SRD §3.4 untuk detail algoritma.
- Rubrik K1–K8 dan seluruh keputusan desain didokumentasikan lengkap pada
  *Blueprint SPK AHP DDTC Library* (BRD/PRD/SRD/ERD).
