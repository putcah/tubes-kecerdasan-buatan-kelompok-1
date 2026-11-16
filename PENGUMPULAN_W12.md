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
- [x] Proposal awal minggu 12 sebanyak 4 halaman termasuk sampul, dalam format laporan mahasiswa; PDF, Word, Markdown, dan script tersedia.
- [x] Draf panjang sebelumnya dipisahkan sebagai arsip; dokumen pengumpulan utama adalah W12_Proposal_EDA.pdf.
- [x] Usulan pembagian peran untuk disepakati anggota.

## Perlu diselesaikan sebelum submit

- [x] Kelas **B** sudah diisi di `project.json`.
- [ ] Sepakati pembagian peran; ubah jika perlu. Jangan mengaku sebagai bukti kontribusi yang sudah terjadi.
- [x] Repository kelompok: https://github.com/putcah/tubes-kecerdasan-buatan-kelompok-1 .
- [x] Kelas dan URL repo sudah dimasukkan dan PDF diregenerasi. Untuk memperbarui lagi: `pip install -r requirements-report.txt` dan `python tools/build_report.py`. Ekspor PDF otomatis memerlukan LibreOffice; jika tidak tersedia, ekspor berkas Word melalui Microsoft Word.
- [ ] Jalankan `python -m src.eda` dan `streamlit run app.py` pada laptop kelompok.
- [ ] Sertakan bukti dashboard awal dari `W12/bukti_dashboard/`; bila sudah deploy sertakan screenshot Incognito dan URL aktif.
- [ ] Unggah **W12/W12_Proposal_EDA.pdf** dan **URL repository** ke Moodle. Jika formulir mengizinkan, sertakan URL dashboard atau bukti lokal.

## Belum wajib diimplementasikan W12

GA pada W13; PSO dan empat eksperimen pada W14; Fuzzy dan deployment publik pada W15. Tidak ada angka hasil optimasi atau keputusan Fuzzy fiktif. Kebutuhan dashboard dan deploy final tetap wajib dipenuhi.

Jangan mengirim ZIP sebagai pengganti URL repository jika Moodle meminta tautan repo. Panduan `DEPLOYMENT.md` menjelaskan langkah dari file siap pakai menuju repo dan URL Streamlit publik.
