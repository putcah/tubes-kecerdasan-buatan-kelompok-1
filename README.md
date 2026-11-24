# Intelligent Predictive Maintenance System

Tugas Besar Kecerdasan Buatan, Kelompok 1 Kelas B, Institut Teknologi Kalimantan. Proyek ini menggunakan dataset AI4I 2020 untuk mengenali kegagalan mesin dari jenis produk dan lima variabel operasi.

| Progres | Berkas |
| --- | --- |
| Minggu 13: seleksi fitur dengan GA | [Laporan PDF](W13/W13_GA_Progress.pdf), [Word](W13/W13_GA_Progress.docx), [hasil eksperimen dan cara reproduksi](W13/README.md) |
| Minggu 12: eksplorasi data dan baseline | [Laporan yang dikumpulkan](W12/M12_Kelompok_1_B.pdf), [data dan artefak W12](W12/README.md) |

## Progres minggu 13

Genetic Algorithm (GA) memilih subset dari enam fitur. Model MLP dengan subset terpilih dibandingkan dengan baseline enam fitur menggunakan tiga seed yang sama. Data uji disimpan untuk evaluasi akhir. Lihat [kurva konvergensi](W13/hasil/convergence.png), [fitur terpilih](W13/hasil/selected_features.csv), dan [metrik validasi per seed](W13/hasil/comparison.csv).

Pada data validasi, rata-rata F1 naik dari 0,4285 menjadi 0,4549, sedangkan recall turun dari 76,30% menjadi 70,37%. GA memilih empat fitur pada satu seed dan mempertahankan seluruh fitur pada dua seed lainnya.

Dashboard lokal menampilkan hasil pada menu **GA Optimization** dan **Model Comparison**. Integrasi PSO, Fuzzy Logic, dan deployment publik direncanakan pada tahap berikutnya. [Panduan deployment](DEPLOYMENT.md)

## Menjalankan dashboard

Gunakan Python 3.12. Dari folder repository, jalankan:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Buka alamat lokal yang ditampilkan Streamlit. Dataset diunduh otomatis dari UCI saat pertama kali dibutuhkan. Dashboard membaca model dan hasil yang sudah tersedia di repository.

Untuk mengulang eksperimen GA, jalankan:

```bash
python -m src.ga_feature_selection --workers 3
```

Opsi `--workers 1` menjalankan ketiga percobaan secara berurutan. Rincian seed, fitness, dan berkas keluaran ada di [panduan W13](W13/README.md).

## Anggota

| Nama | NIM |
| --- | --- |
| Putri Cahaya Lestari | 04231072 |
| Hendra Firmansyah | 04231038 |
| Nur Rahmad | 04231070 |

Sumber data: [AI4I 2020 Predictive Maintenance Dataset (UCI 601)](https://doi.org/10.24432/C5HS5C).
