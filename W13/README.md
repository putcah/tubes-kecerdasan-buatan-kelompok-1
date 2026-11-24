# Progres Minggu 13

## Berkas pengumpulan

- [Laporan progres PDF](W13_GA_Progress.pdf) dan [versi Word](W13_GA_Progress.docx)
- [Kode eksperimen GA](../src/ga_feature_selection.py)
- [Kurva konvergensi](hasil/convergence.png), [log generasi](hasil/convergence.csv), dan [seluruh subset yang dinilai](hasil/evaluated_subsets.csv)
- [Perbandingan per seed](hasil/comparison.csv), [fitur kandidat terbaik](hasil/selected_features.csv), dan [ringkasan lengkap](hasil/summary.json)
- [Bukti dashboard lokal](bukti_dashboard/)

## Hasil utama

Dari tiga percobaan, rata-rata F1 validasi berubah dari **0,4285** pada baseline menjadi **0,4549** pada GA + NN. Rata-rata recall turun dari **0,7630** menjadi **0,7037**. GA memilih empat fitur pada seed 11, dengan mengeluarkan Type dan kecepatan rotasi. Pada seed 22 dan 33, semua fitur tetap terpilih. Kandidat dengan fitness tertinggi adalah seed 22 dengan enam fitur.

Perbandingan ini menggunakan validasi yang juga dipakai untuk memilih subset. Data uji disimpan untuk evaluasi akhir setelah konfigurasi ditetapkan.

## Cara mengulang

Dari folder utama repository, jalankan:

```bash
python -m pip install -r requirements.txt
python -m src.ga_feature_selection --workers 3
python -m streamlit run app.py
```

Perintah eksperimen menulis ulang `W13/hasil`. Gunakan `--workers 1` untuk menjalankan percobaan berturut-turut atau `--output PATH` untuk menyimpan salinan hasil di folder lain. Angka waktu dipengaruhi perangkat dan mode eksekusi. Hasil yang dilaporkan diukur dengan tiga pekerja paralel.

GA menggunakan populasi 20, 15 generasi, turnamen 3, persilangan satu titik dengan peluang 0,8, mutasi 1/6 per bit, dan elitisme dua kandidat. Fitness dihitung dari F1 validasi dikurangi 0,02 kali proporsi fitur yang dipakai. Penyimpanan hasil per kromosom menghindari pelatihan berulang pada seed yang sama. Baseline dan GA + NN memakai seed berpasangan, yakni 11, 22, dan 33, serta rancangan MLP dan pembagian data yang sama.

Setelah eksperimen, buka **GA Optimization** dan **Model Comparison**. Untuk membuat ulang dokumen Word berdasarkan hasil yang tersimpan, pasang `requirements-report.txt`, lalu jalankan `python tools/build_w13_report.py`. Ekspor dokumen ke PDF melalui Word atau LibreOffice.
