# Checklist pengumpulan W12

Tenggat sesuai Moodle/pengampu. Dokumen dosen meminta satu PDF progres dan satu URL repository; URL deployment disertakan bila sudah tersedia.

## Sudah disiapkan

- [x] Dataset AI4I 2020 resmi terbaca, checksum dan atribusi dicatat.
- [x] Target `Machine failure`, enam input, ID dan label jenis failure dibuang.
- [x] Missing-values analysis, statistik, distribusi target/fitur dan korelasi.
- [x] Split train/validation/test tetap dengan manifest; test tidak dipakai tuning.
- [x] Baseline NN benar-benar dilatih, metrik validation dan confusion matrix disimpan.
- [x] Pipeline/model tersimpan dan hasil reload diverifikasi identik.
- [x] Script modular, README dan requirements.
- [x] Kerangka Streamlit dengan prediksi manual/CSV yang berfungsi.
- [x] Laporan PDF 4 halaman; teks Markdown dan script pembuat laporan tersedia.
- [x] Proposal/progres format laporan mahasiswa (17 halaman) tersedia dalam Word dan PDF; gunakan versi 4 halaman jika batas 2–4 halaman pada panduan tetap diterapkan.
- [x] Usulan pembagian peran untuk disepakati anggota.

## Perlu diselesaikan sebelum submit

- [x] Kelas **B** sudah diisi di `project.json`.
- [ ] Sepakati pembagian peran; ubah jika perlu. Jangan mengaku sebagai bukti kontribusi yang sudah terjadi.
- [x] Repository kelompok: https://github.com/putcah/tubes-kecerdasan-buatan-kelompok-1 .
- [x] Kelas dan URL repo sudah dimasukkan dan PDF diregenerasi. Untuk memperbarui lagi: `pip install -r requirements-report.txt` dan `python tools/build_report.py`.
- [ ] Jalankan `python -m src.eda` dan `streamlit run app.py` pada laptop kelompok.
- [ ] Sertakan bukti dashboard awal dari `W12/bukti_dashboard/`; bila sudah deploy sertakan screenshot Incognito dan URL aktif.
- [ ] Unggah **W12/W12_Proposal_EDA.pdf** dan **URL repository** ke Moodle. Jika formulir mengizinkan, sertakan URL dashboard atau bukti lokal.

## Belum wajib diimplementasikan W12

GA pada W13; PSO dan empat eksperimen pada W14; Fuzzy dan deployment publik pada W15. Tidak ada angka hasil optimasi atau keputusan Fuzzy fiktif. Kebutuhan dashboard dan deploy final tetap wajib dipenuhi.

Jangan mengirim ZIP sebagai pengganti URL repository jika Moodle meminta tautan repo. Panduan `DEPLOYMENT.md` menjelaskan langkah dari file siap pakai menuju repo dan URL Streamlit publik.
