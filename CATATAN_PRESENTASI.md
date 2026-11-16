# Narasi progres 3–5 menit

## 1. Topik dan target

“Kelompok 1 membuat Intelligent Predictive Maintenance memakai AI4I 2020 dari UCI. Pada minggu 12 kami menyiapkan pipeline data, baseline MLP dan dashboard awal. Targetnya Machine failure biner, bukan waktu menuju kerusakan.”

## 2. Data dan leakage

“Data sintetis terdiri dari 10.000 baris, hanya 339 failure. Kami menggunakan Type dan lima variabel operasi. ID dan lima label jenis failure tidak menjadi input karena label tersebut membocorkan informasi keluaran. Tidak ada missing values pada versi data ini.”

## 3. Split dan baseline

“Urutan UDI dipakai sebagai proxy urutan, dengan train 60%, validation 20% dan test 20%; tidak ada timestamp yang dapat membuktikan evaluasi waktu nyata. Scaler dan imputer hanya di-fit pada train. Bobot kelas dari train membantu NN memperhatikan kelas failure. Arsitekturnya delapan input hasil encoding, 32 dan 16 unit hidden ReLU, satu output biner, 833 parameter.”

## 4. Hasil yang perlu dipahami

“Pada validation, precision 30,12%, recall 55,56%, F1 0,3906 dan accuracy 96,10%. Ada 25 true positive, 20 false negative dan 58 false positive. Ini baseline awal; masih banyak ruang perbaikan. Dummy yang selalu menjawab tidak failure bahkan mendapat accuracy 97,75% tetapi recall nol, sehingga accuracy tidak cukup untuk menilai.”

## 5. Demo dan rencana

Jalankan `streamlit run app.py`. Tunjukkan Overview → Dataset Explorer → Neural Network → Prediction / Simulation. Isi kondisi mesin atau unggah `examples/input_sample.csv`; jelaskan bahwa keluaran masih baseline, belum Fuzzy. Tunjukkan bahwa halaman GA/PSO/Fuzzy transparan berstatus rencana.

“Minggu berikutnya kami mengerjakan GA untuk seleksi fitur, lalu PSO untuk NN. Karena baseline ini belum mendukung dropout, pada eksperimen W14 seluruh konfigurasi akan dilatih ulang memakai backend yang mendukung dropout. Fuzzy kemudian menghasilkan empat prioritas perawatan. Dashboard final wajib online dan dapat diakses tanpa login khusus.”

## Jawaban singkat untuk pertanyaan dosen

- Kenapa MLP? Data tabular per pengamatan, tidak ada struktur spasial yang memerlukan CNN.
- Mengapa test belum ada hasil? Disimpan untuk evaluasi akhir setelah konfigurasi dikunci; validation dipakai checkpoint dan optimasi.
- Apakah skor 90% berarti 90% peluang industri nyata? Belum; data sintetis dan probabilitas belum dikalibrasi.
- Apakah GA sudah menentukan sensor penting? Belum pada W12; seluruh enam variabel digunakan baseline.
- Mengapa Fuzzy tidak menaikkan accuracy? Fuzzy mengubah prediksi menjadi keputusan yang dapat dijelaskan; kualitas aturan dievaluasi tersendiri.
- Apakah URL publik sudah ada? Belum dalam paket awal; isi status yang benar setelah deployment, jangan menyebut localhost sebagai URL publik.
