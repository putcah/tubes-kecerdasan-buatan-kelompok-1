PROPOSAL AWAL TUGAS BESAR
KECERDASAN BUATAN

INTELLIGENT PREDICTIVE MAINTENANCE SYSTEM

Progres Minggu ke-12
Semester Gasal 2026/2027

Disusun untuk memenuhi tugas mata kuliah
Kecerdasan Buatan (TE2514031)

Dosen Pengampu:
Ir. Muhammad Ridho Dewanto, S.T., M.T.

Disusun oleh:
Kelompok 1 — Kelas B

Putri Cahaya Lestari — 04231072

Hendra Firmansyah — 04231038

Nur Rahmad — 04231070

Ricky Alfian Ronaldo — 04221045

INSTITUT TEKNOLOGI KALIMANTAN
2026

# BAB I
PENDAHULUAN

## 1.1 Latar Belakang

Kondisi mesin dapat dilihat dari beberapa variabel operasi, seperti suhu, kecepatan putaran, torsi, dan keausan alat. Data tersebut dapat digunakan untuk mengenali kondisi yang berkaitan dengan kegagalan mesin. Pada tugas besar ini, kelompok kami mengerjakan Intelligent Predictive Maintenance System untuk memprediksi status kegagalan dan, pada tahap akhir, memberikan prioritas perawatan.

Data yang digunakan adalah AI4I 2020 Predictive Maintenance Dataset dari UCI. Dataset ini berisi 10.000 pengamatan sintetis, dengan 339 kasus kegagalan (UCI Machine Learning Repository, 2020). Karena jumlah kegagalan jauh lebih sedikit daripada kondisi normal, model yang sering menjawab “tidak gagal” dapat memperoleh akurasi tinggi. Oleh sebab itu, kemampuan model mendeteksi kegagalan juga perlu dilihat dari precision, recall, dan F1-score.

## 1.2 Rumusan Masalah

Bagaimana menyiapkan data agar label kegagalan tidak ikut menjadi masukan model, dan bagaimana hasil awal Neural Network dalam mengenali kegagalan pada data yang tidak seimbang?

## 1.3 Tujuan Pengerjaan

Pada minggu ke-12, pengerjaan ditujukan untuk memahami isi dataset, menetapkan fitur dan target, menyiapkan pembagian data, serta melatih baseline Neural Network. Selain itu, disiapkan kerangka dashboard Streamlit dan rencana integrasi GA, PSO, serta Fuzzy Logic untuk minggu berikutnya.

## 1.4 Batasan Masalah

Target yang dipakai adalah Machine failure dengan dua kelas, yaitu gagal dan tidak gagal. Model memprediksi status pada satu pengamatan, bukan waktu menuju kerusakan atau sisa umur mesin. Data bersifat sintetis sehingga hasilnya belum dapat langsung diterapkan pada mesin nyata. Progres minggu ke-12 dibatasi pada data, baseline MLP, dan dashboard awal; GA, PSO, Fuzzy, serta deployment publik masih menjadi pekerjaan selanjutnya.

# BAB II
METODE PENGERJAAN

## 2.1 Data dan Variabel yang Digunakan

Dari 14 kolom dataset, enam variabel dipakai sebagai masukan dan satu kolom sebagai target. Rinciannya disajikan pada Tabel 1.

Tabel 1. Variabel masukan dan target

| Variabel | Jenis data/satuan | Keterangan |
|---|---|---|
| Type | Kategori H, L, M | Jenis/kualitas produk |
| Air temperature | Numerik, K | Suhu udara |
| Process temperature | Numerik, K | Suhu proses |
| Rotational speed | Numerik, rpm | Kecepatan rotasi |
| Torque | Numerik, Nm | Torsi |
| Tool wear | Numerik, menit | Keausan alat |
| Machine failure | Biner, 0 atau 1 | Target kegagalan |

UDI dan Product ID tidak digunakan sebagai fitur. Kolom TWF, HDF, PWF, OSF, dan RNF juga dikeluarkan karena merupakan label jenis kegagalan yang dapat membocorkan informasi target.

## 2.2 Pembagian Data dan Preprocessing

Data dibagi berdasarkan urutan UDI: 6.000 baris untuk train, 2.000 untuk validation, dan 2.000 untuk test. UDI hanya menjadi acuan urutan, bukan timestamp yang terverifikasi. Imputer dan StandardScaler dihitung dari train saja. Type diubah menjadi tiga kolom one-hot, sehingga NN menerima delapan input. Ketidakseimbangan kelas ditangani dengan bobot kelas dari train. Test disimpan untuk evaluasi akhir.

## 2.3 Model Awal dan Rancangan Sistem

Baseline menggunakan MLP dengan susunan 8–32–16–1, aktivasi ReLU pada hidden layer, dan output sigmoid. Pelatihan memakai Adam, learning rate 0,001, batch size 128, maksimum 150 epoch, dan seed 42. Checkpoint dipilih dari log loss validation; batas klasifikasi ditetapkan 0,5.

Pada sistem akhir, GA akan memilih fitur, PSO mengoptimalkan hyperparameter NN, dan Fuzzy mengubah hasil prediksi menjadi prioritas Normal, Inspection, Maintenance, atau Critical. Alur yang direncanakan adalah:

Data → Preprocessing → GA → PSO → NN → Fuzzy → Streamlit

# BAB III
PROGRES AWAL DAN RENCANA KERJA

## 3.1 Hasil Sementara Minggu ke-12

Pemeriksaan data menunjukkan 9.661 non-failure dan 339 failure, tanpa nilai kosong maupun duplikasi baris. Hasil baseline pada data validation ditunjukkan pada Tabel 2.

Tabel 2. Evaluasi baseline MLP pada validation

| Accuracy | Precision | Recall | F1-score |
|---|---|---|---|
| 96,10% | 30,12% | 55,56% | 0,3906 |

Confusion matrix berisi TN=1.897, FP=58, FN=20, dan TP=25. Sebanyak 25 dari 45 kegagalan terdeteksi, tetapi masih ada 58 false alarm. Deteksi kegagalan masih perlu diperbaiki.

Script, model, dan bukti dashboard tersedia di repository. Prediksi manual/CSV berjalan lokal; aplikasi belum di-deploy publik.

## 3.2 Pembagian Tugas

Tabel 3. Usulan pembagian kerja kelompok

| Anggota | Tanggung jawab |
|---|---|
| Putri Cahaya Lestari | Pengolahan data, EDA, dan laporan |
| Hendra Firmansyah | GA dan seleksi fitur |
| Nur Rahmad | Baseline NN, PSO, dan evaluasi |
| Ricky Alfian Ronaldo | Fuzzy, dashboard, dan deployment |

Pembagian kerja ini masih perlu disepakati bersama.

## 3.3 Rencana Selanjutnya dan Risiko

Pengerjaan dilanjutkan dengan GA pada minggu ke-13, PSO pada minggu ke-14, Fuzzy dan deployment pada minggu ke-15, serta laporan dan demo pada minggu ke-16. Risiko jumlah failure yang sedikit dan overfitting validation ditangani melalui pembatasan percobaan, beberapa seed GA/PSO, dan test yang tetap terpisah.

## DAFTAR PUSTAKA

UCI Machine Learning Repository. (2020). AI4I 2020 Predictive Maintenance Dataset. https://doi.org/10.24432/C5HS5C.

Panduan Deliverables Tugas Besar Kecerdasan Buatan Minggu 12–16. (2026). Dokumen mata kuliah TE2514031, Gasal 2026/2027.

Tugas Besar Kecerdasan Buatan: 16 Kelompok UCI Streamlit. (2026). Dokumen mata kuliah TE2514031, Gasal 2026/2027.