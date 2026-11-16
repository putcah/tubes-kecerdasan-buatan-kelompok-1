# Menyediakan repository dan URL dashboard

Status paket ini: dashboard lokal dan model siap dijalankan, **belum ada deployment publik**. W12 meminta URL repository; URL skeleton dicantumkan jika tersedia. Deployment publik wajib pada W15/final.

## 1. Repository GitHub

Buat repository milik kelompok, misalnya `TUBES_KB_2026_Kelompok01`; tambahkan nama kelas setelah dikonfirmasi. Folder lokal sudah diinisialisasi Git. Jangan menambahkan `.venv`, `.env`, token, atau password.

Jika memakai antarmuka website GitHub, unggah semua isi folder project **termasuk `artifacts`, `W12`, `src`, dan folder tersembunyi `.streamlit`**. Jangan unggah `.git`, `.venv`, atau ZIP project ke dalam repo. Cara Git dari folder project:

```bash
git status
git add .
git commit -m "Lengkapi identitas dan progres W12"
git branch -M main
git remote add origin https://github.com/USERNAME/NAMA_REPOSITORY.git
git push -u origin main
git tag -a W12 -m "Progres Minggu 12"
git push origin W12
```

Ganti USERNAME/NAMA_REPOSITORY dengan milik kelompok. Jika `git commit` menyebut tidak ada perubahan, lanjutkan perintah berikutnya. Jika folder ZIP tidak mengandung `.git`, jalankan `git init -b main` sebelum `git add`; atur nama/email Git dengan identitas sendiri jika diminta. Tautan repository pada Moodle harus URL repo sebenarnya, bukan path lokal atau nama ZIP.

## 2. Deploy ke Streamlit Community Cloud

1. Masuk ke https://share.streamlit.io/ memakai akun sendiri dan hubungkan GitHub.
2. Pilih **Create app**; pilih repository, branch `main`, dan entrypoint **`app.py`** (di root).
3. Di pengaturan lanjutan pilih **Python 3.12**, sesuai artefak dan requirements.
4. Deploy; tunggu pemasangan dependensi dan unduhan dataset pertama dari UCI. Tidak perlu secret/API key.
5. Di pengaturan sharing, izinkan akses publik. Salin URL `https://...streamlit.app` yang benar-benar diberikan layanan.
6. Buka URL lewat Incognito tanpa login. Uji Overview, Dataset Explorer, Neural Network, prediksi manual, dan unggahan `examples/input_sample.csv`.
7. Simpan screenshot akses publik, isi URL di `project.json`, README, dan Moodle. Screenshot lokal bukan bukti akses internet publik.

File `.gitignore` mengecualikan dataset CSV; aplikasi mengunduh versi UCI dengan checksum saat belum tersedia. Jika unduhan UCI gagal saat deploy, unggah satu salinan kecil CSV resmi ke `data/raw/ai4i2020.csv` disertai atribusi (hapus pengecualiannya secara sengaja) atau coba ulang saat UCI pulih. Jangan mengganti data dengan dataset lain.

## 3. Jika terjadi masalah

- `ModuleNotFoundError`: pastikan requirements.txt berada di root dan entrypoint `app.py`.
- Artefak tidak ditemukan: pastikan `artifacts/baseline.joblib` ikut di-push.
- Peringatan versi model: gunakan Python 3.12 dan versi scikit-learn/numpy sesuai requirements; jangan mengabaikan ketidakcocokan.
- Hasil GA/PSO kosong: memang belum diimplementasikan pada W12; jangan mengisi angka palsu.
- Data belum tersedia: jalankan `python -m src.eda` saat punya internet; setelah itu demo lokal dapat berjalan offline.

Panduan resmi: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app
