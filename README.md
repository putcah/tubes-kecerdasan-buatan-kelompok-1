# Kelompok 01 — Intelligent Predictive Maintenance (W12)

Paket progres Minggu 12 mata kuliah TE2514031, Gasal 2026/2027. Data: AI4I 2020, UCI ID 601. Dashboard memakai **Streamlit asli**, model baseline memakai MLPClassifier (Neural Network).

**Berkas pengumpulan:** [Proposal PDF W12 (2 halaman)](W12/W12_Proposal_EDA.pdf) · [Proposal Word](W12/W12_Proposal_EDA.docx) · [Checklist Moodle](PENGUMPULAN_W12.md) · [Cara deploy](DEPLOYMENT.md) · [Catatan presentasi](CATATAN_PRESENTASI.md)

## Proposal awal minggu 12

Proposal utama sudah disusun ulang menjadi **2 halaman**, sesuai batas 2–4 halaman pada panduan dosen. Identitas: Institut Teknologi Kalimantan, Kelompok 1, Kelas B.

- [Unduh proposal Word yang dapat diedit](W12/W12_Proposal_EDA.docx)
- [Buka proposal PDF untuk pengumpulan W12](W12/W12_Proposal_EDA.pdf)

Bagian isinya: Gambaran Tugas, Data yang Dipakai, Cara Pengerjaan, Hasil Sementara, Pembagian Tugas Awal, Rencana Selanjutnya, dan Sumber. Identitas kelompok langsung diletakkan di bagian atas. Bahasa dibuat lebih langsung seperti catatan proposal/progres mahasiswa; tidak memakai susunan BAB, kata pengantar, daftar isi, atau sampul terpisah. Tujuan, kamus data, arsitektur, split, preprocessing, metrik, risiko, dan pembagian peran tetap tercakup.

Format: A4, Times New Roman 12, spasi isi 1,15, dan margin 2,5 cm. Tabel, identitas, serta sumber memakai ukuran lebih kecil dan spasi tunggal. Halaman bernomor 1–2. Program studi dan fakultas tidak ditambahkan karena belum dikonfirmasi. Angka hasil awal berasal dari eksperimen yang tersimpan; GA, PSO, Fuzzy dan deployment publik masih dijelaskan sebagai rencana.

Teks yang bisa disalin tersedia pada [versi Markdown](W12/W12_Proposal_EDA.md). Untuk membuat ulang, pasang `requirements-report.txt` lalu jalankan `python tools/build_report.py`. Script membuat Word dan mengekspor PDF jika LibreOffice tersedia. Jika tidak, buka Word lalu gunakan Export/Save as PDF; periksa kembali jumlah halaman setelah mengedit.

<details>
<summary>Draf panjang sebelumnya — arsip</summary>

Draf 17 halaman disimpan sebagai arsip penulisan, bukan dokumen utama untuk pengumpulan progres W12:

- [Word draf panjang](W12/W12_Proposal_Progres_KelasB_Kelompok01.docx)
- [PDF draf panjang](W12/W12_Proposal_Progres_KelasB_Kelompok01.pdf)

</details>

## Jalankan cepat

Gunakan Python **3.12**. Dari folder yang berisi `app.py`:

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux (gunakan ini sebagai pengganti aktivasi Windows):
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m src.eda
streamlit run app.py
```

Pilih **satu** perintah aktivasi sesuai OS. Buka URL lokal yang dicetak Streamlit. Data akan diunduh dari UCI pada eksekusi EDA/kunjungan pertama; setelah terunduh, aplikasi bisa berjalan tanpa unduhan ulang. Model terlatih sudah disertakan dan tidak dilatih ulang saat dashboard dibuka.

Untuk mengulang eksperimen baseline (akan menimpa artefak W12):

```bash
python -m src.train_baseline --seed 42
```

`src/eda.py` dan `src/train_baseline.py` memenuhi opsi **script** pada panduan; notebook tidak diwajibkan bersamaan. Waktu training dan hasil numerik sangat kecil dapat bervariasi antar mesin. Versi dependensi langsung dikunci; `W12/environment_lock.txt` mencatat versi runtime yang digunakan.

## Isi paket

- `W12/W12_Proposal_EDA.pdf` dan `.docx`: proposal progres ringkas 2 halaman.
- `W12/W12_Proposal_EDA.md`: teks laporan yang dapat diedit.
- `src/common.py`: kontrak enam fitur, checksum, split, preprocessing dan validasi input.
- `src/eda.py`: unduh/checksum, ringkasan, statistik, missing values, grafik dan split manifest.
- `src/train_baseline.py`: baseline MLP, pembobotan kelas, kurva, metrik, prediksi validation dan artefak.
- `artifacts/baseline.joblib`: preprocessing + model + metadata; hanya muat artefak project ini.
- `app.py`: delapan area dashboard, termasuk prediksi manual/CSV yang berfungsi.
- `W12/eda/`, `W12/baseline/`: bukti hasil eksekusi, bukan angka simulasi.
- `DEPLOYMENT.md`, `PENGUMPULAN_W12.md`, `CATATAN_PRESENTASI.md`: panduan tindak lanjut.
- `project.json`: kelas, URL, anggota dan **usulan** pembagian peran.

## Keputusan metodologi

Target biner `Machine failure`, bukan remaining useful life. Input: `Type` dan lima variabel numerik. `UDI`/`Product ID` dibuang sebagai identitas; `TWF/HDF/PWF/OSF/RNF` adalah label jenis kegagalan dan **tidak** boleh masuk fitur. Setelah one-hot encoding Type ada 8 input NN. Data sintetis, 10.000 baris, 339 failure, tidak ada missing values.

Split tetap berdasarkan urutan UDI: train 1–6000, validation 6001–8000, test 8001–10000. UDI dipakai sebagai proxy urutan agar pola berdekatan tidak diacak ke semua split; tidak ada timestamp terverifikasi, sehingga ini **bukan bukti** evaluasi forecasting atau pemisahan antar mesin. Test tidak dipakai menghitung parameter preprocessing, bobot kelas, checkpoint atau fitness. EDA semua data bersifat audit deskriptif dan tidak dipakai memilih fitur/hiperparameter.

Imputer dan StandardScaler fit pada train saja; kategori H/L/M berasal dari kamus data. Bobot kelas train `n_train/(2*n_class)` mengatasi imbalance tanpa oversampling validation/test. Baseline tetap `(32,16)`, ReLU, Adam, lr 0.001, batch 128, L2 0.0001, seed 42; maksimum 150 epoch, patience 20 berdasarkan log loss validation, threshold 0.5 tetap. Metrik utama F1 dan recall kelas failure, disertai precision, accuracy, confusion matrix, balanced accuracy, average precision (AP), ROC AUC.

**Test belum dievaluasi** supaya dapat dipakai untuk pembandingan final yang telah dikunci. Jangan mencoba berkali-kali pada test untuk memilih konfigurasi. GA/PSO belum dikerjakan pada W12. Halamannya jelas berstatus rencana. Belum ada klaim peningkatan optimasi atau keputusan Fuzzy.

## Rencana W13–W16

W13 GA: enam bit, grup Type utuh; fitness F1 validation dengan penalti jumlah fitur; beberapa seed, convergence dan fitur terpilih. W14 PSO: learning rate, hidden units, dropout dan batch size; lakukan empat eksperimen dengan protokol yang setara. Karena MLPClassifier tidak mendukung dropout, rencana W14 adalah memigrasikan **seluruh** konfigurasi (termasuk baseline) ke backend NN yang mendukung dropout, lalu melatih ulang dan mencatat versinya. W15 Mamdani/centroid, uji rule dan integrasi, akses publik Streamlit. W16 laporan, slide, video dan bukti kontribusi.

## Sumber dan status

Ketentuan tugas: dua PDF dosen yang dilampirkan pengguna, khususnya Panduan Deliverables halaman 1–3 dan Pembagian Tugas halaman 5/9. Tenggat mengikuti Moodle; paket disiapkan untuk progres besok sesuai permintaan pengguna, bukan hasil verifikasi jadwal Moodle.

- [UCI AI4I 2020](https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset), DOI https://doi.org/10.24432/C5HS5C, CC BY 4.0. `data/SOURCE.md` mencatat checksum. Dataset kecil disertakan pada ZIP untuk demo lokal; `.gitignore` mencegah unggah CSV berulang ke GitHub.
- [Deploy Streamlit resmi](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app).
- Referensi video dari pengguna: https://www.youtube.com/watch?v=qTVpbdGzKY8. Konten video tidak berhasil diakses; tidak ada klaim mengikuti rincian tutorialnya. Panduan deployment berdasarkan dokumentasi resmi Streamlit dan ketentuan PDF.

Kelas **B**, Kelompok 01. Repository: https://github.com/putcah/tubes-kecerdasan-buatan-kelompok-1 . Deployment publik **belum dibuat**; ikuti DEPLOYMENT.md. URL aplikasi di project.json diisi setelah benar-benar aktif.
