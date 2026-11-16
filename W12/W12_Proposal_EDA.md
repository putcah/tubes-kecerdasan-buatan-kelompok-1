Proposal Progres Minggu 12

Tugas Besar Kecerdasan Buatan
Intelligent Predictive Maintenance System

Kelompok 1 · Kelas B · Institut Teknologi Kalimantan

Putri Cahaya Lestari — 04231072

Hendra Firmansyah — 04231038

Nur Rahmad — 04231070

Ricky Alfian Ronaldo — 04221045

Pengampu: Ir. Muhammad Ridho Dewanto, S.T., M.T.
TE2514031 · Semester Gasal 2026/2027

## 1. Gambaran Tugas

Kelompok kami mengerjakan prediksi kegagalan mesin menggunakan data suhu, putaran, torsi, dan keausan alat. Hasil prediksi nantinya ditampilkan di dashboard Streamlit dan digunakan untuk membantu menentukan prioritas perawatan. Untuk progres minggu 12, fokus kami masih pada memahami data, menyiapkan pengolahan data, dan membuat model Neural Network (NN) awal sebagai pembanding untuk percobaan berikutnya.

## 2. Data yang Dipakai

Kami menggunakan AI4I 2020 Predictive Maintenance Dataset dari UCI. Data ini berisi 10.000 baris dan 14 kolom. Enam variabel menjadi masukan model, sedangkan Machine failure menjadi target: 0 untuk tidak gagal dan 1 untuk gagal.

Variabel yang digunakan

| Variabel | Jenis data/satuan | Keterangan |
|---|---|---|
| Type | Kategori H, L, M | Jenis/kualitas produk |
| Air temperature | Numerik, K | Suhu udara |
| Process temperature | Numerik, K | Suhu proses |
| Rotational speed | Numerik, rpm | Kecepatan rotasi |
| Torque | Numerik, Nm | Torsi |
| Tool wear | Numerik, menit | Keausan alat |
| Machine failure | Biner, 0 atau 1 | Target kegagalan |

UDI dan Product ID tidak dijadikan input. TWF, HDF, PWF, OSF, dan RNF juga tidak dipakai karena sudah menunjukkan jenis kegagalan dan bisa membocorkan jawaban yang ingin diprediksi model. Data ini bersifat sintetis, sehingga hasilnya belum mewakili semua kondisi mesin nyata.

## 3. Cara Pengerjaan

Kami membagi data sesuai urutan UDI: 6.000 baris untuk train, 2.000 untuk validation, dan 2.000 untuk test. UDI hanya dipakai sebagai acuan urutan, bukan waktu pengukuran yang pasti. Imputer dan StandardScaler dihitung dari train saja. Type diubah menjadi tiga kolom one-hot, sehingga total input NN menjadi delapan. Bobot kelas juga dihitung dari train untuk membantu model memperhatikan kasus kegagalan.

Model awal memakai MLP 8–32–16–1 dengan ReLU dan output sigmoid. Pengaturannya adalah Adam, learning rate 0,001, batch size 128, maksimum 150 epoch, serta seed 42. Model terbaik dipilih dari log loss validation, dengan batas prediksi 0,5. Data test belum digunakan untuk memilih atau menilai model.

## 4. Hasil Sementara

Dari pemeriksaan awal, ada 9.661 baris tidak gagal dan 339 baris gagal. Tidak ditemukan nilai kosong atau baris duplikat. Berikut hasil model awal pada data validation.

Hasil baseline MLP

| Accuracy | Precision | Recall | F1-score |
|---|---|---|---|
| 96,10% | 30,12% | 55,56% | 0,3906 |

Confusion matrix-nya adalah TN=1.897, FP=58, FN=20, dan TP=25. Artinya, 25 dari 45 kasus kegagalan berhasil dikenali, tetapi 20 kasus masih terlewat dan ada 58 false alarm. Jadi, meskipun akurasinya tinggi, hasil deteksi kegagalannya masih perlu diperbaiki.

Script pengolahan data, model tersimpan, dan dashboard awal sudah tersedia di repository. Input manual dan unggah CSV sudah bisa menghasilkan prediksi secara lokal. Aplikasi belum di-deploy publik. Model ini memprediksi status kegagalan pada satu pengamatan, bukan sisa umur mesin.

## 5. Pembagian Tugas Awal

Usulan pembagian kerja

| Anggota | Tanggung jawab |
|---|---|
| Putri Cahaya Lestari | Pengolahan data, EDA, dan laporan |
| Hendra Firmansyah | GA dan seleksi fitur |
| Nur Rahmad | Baseline NN, PSO, dan evaluasi |
| Ricky Alfian Ronaldo | Fuzzy, dashboard, dan deployment |

Pembagian kerja ini masih perlu disepakati bersama.

## 6. Rencana Selanjutnya

Minggu 13 akan difokuskan pada GA untuk memilih fitur. Minggu 14 dilanjutkan dengan PSO untuk mencari pengaturan NN dan membandingkan hasil model. Pada minggu 15, Fuzzy akan dipakai untuk menentukan prioritas Normal, Inspection, Maintenance, atau Critical, lalu dashboard di-deploy. Minggu 16 disiapkan untuk laporan akhir dan demo.

Data → Preprocessing → GA → PSO → NN → Fuzzy → Streamlit

Hal yang perlu diperhatikan adalah sedikitnya kasus kegagalan dan kemungkinan model terlalu menyesuaikan data validation. Karena itu, jumlah percobaan akan dibatasi dan dicatat, GA/PSO dijalankan dengan beberapa seed, dan data test tetap disimpan untuk evaluasi akhir.

## Sumber

UCI Machine Learning Repository. (2020). AI4I 2020 Predictive Maintenance Dataset. https://doi.org/10.24432/C5HS5C.

Panduan Deliverables Tugas Besar Kecerdasan Buatan Minggu 12–16. (2026). Dokumen mata kuliah TE2514031, Gasal 2026/2027.

Tugas Besar Kecerdasan Buatan: 16 Kelompok UCI Streamlit. (2026). Dokumen mata kuliah TE2514031, Gasal 2026/2027.