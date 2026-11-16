"""Regenerasi PDF/Markdown dari metrik nyata dan project.json.
pip install -r requirements-report.txt; python tools/build_report.py
"""
import json
import sys
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether

ROOT=Path(__file__).resolve().parents[1]
cfg=json.loads((ROOT/'project.json').read_text())
eda=json.loads((ROOT/'W12/eda/summary.json').read_text())
result=json.loads((ROOT/'W12/baseline/metrics.json').read_text())
m=result['validation']
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='BodyID',fontName='Helvetica',fontSize=9,leading=12,spaceAfter=6,textColor=colors.HexColor('#243b50')))
styles.add(ParagraphStyle(name='SmallID',parent=styles['BodyID'],fontSize=7.6,leading=10,spaceAfter=4))
styles.add(ParagraphStyle(name='HeadID',fontName='Helvetica-Bold',fontSize=12,leading=15,spaceBefore=7,spaceAfter=6,textColor=colors.HexColor('#147d78')))
styles.add(ParagraphStyle(name='TitleID',fontName='Helvetica-Bold',fontSize=21,leading=25,spaceAfter=10,textColor=colors.HexColor('#142c42')))
story=[];md=[]
def p(text,small=False):
    story.append(Paragraph(text,styles['SmallID' if small else 'BodyID']));md.append(text.replace('<b>','**').replace('</b>','**'))
def h(text):
    story.append(Paragraph(text,styles['HeadID']));md.append('## '+text)
def table(rows,widths=None):
    cells=[[Paragraph(escape(str(cell)),styles['SmallID']) for cell in row] for row in rows]
    t=Table(cells,colWidths=widths,repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e4f1ef')),('VALIGN',(0,0),(-1,-1),'TOP'),('GRID',(0,0),(-1,-1),.4,colors.HexColor('#dce5ed')),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
    story.extend([t,Spacer(1,7)])
    md.append('\n'.join('| '+' | '.join(map(str,row))+' |' for row in rows[:1])+ '\n|'+ '|'.join(['---']*len(rows[0]))+'|\n'+'\n'.join('| '+' | '.join(map(str,row))+' |' for row in rows[1:]))
def image(relative,width,height):
    story.append(Image(str(ROOT/relative),width=width,height=height,hAlign='CENTER'));md.append(f'![Hasil eksperimen]({relative.replace("W12/", "", 1)})')
def page(): story.append(PageBreak());md.append('\n---\n')

p('TE2514031 | GASAL 2026/2027 | PROGRES MINGGU 12',True)
story.append(Paragraph('Intelligent Predictive<br/>Maintenance System',styles['TitleID']))
md.append('# Intelligent Predictive Maintenance System')
p(f"<b>Kelompok 01 · Kelas: {escape(cfg['class'])}</b><br/>Dataset AI4I 2020 (UCI ID 601) · Target: Machine failure (0/1)")
h('1. Masalah, tujuan, dan batas sistem')
p('Kondisi operasi mesin dapat digunakan untuk mengidentifikasi indikasi kegagalan dan membantu penentuan prioritas perawatan. Proyek ini membangun sistem hibrida yang memetakan jenis produk dan sensor operasi ke prediksi kegagalan, kemudian ke keputusan perawatan yang dapat dijelaskan.')
p('<b>Tujuan terukur:</b> menghasilkan baseline NN yang dapat diulang; pada tahap berikutnya membandingkan GA+NN, PSO+NN dan GA+PSO+NN memakai split tetap. Kualitas deteksi failure dinilai melalui precision, recall dan F1, disertai metrik lain. Fuzzy menjadi lapisan keputusan, bukan jaminan peningkatan akurasi.')
p('<b>Batasan:</b> klasifikasi kondisi pada satu pengamatan, bukan prediksi waktu menuju kegagalan atau remaining useful life. Dataset sintetis; skor baseline belum dikalibrasi untuk penerapan industri.')
h('2. Rancangan arsitektur')
table([['Tahap','Alur dan status'],['W12 · tersedia','UCI → validasi data → split → imputer/scaler/encoding → baseline MLP → prediksi Streamlit'],['W13–W15 · rencana','Preprocessing → GA seleksi fitur → PSO hyperparameter → NN → Fuzzy → dashboard online']],[95,420])
p('Input akhir dashboard: kondisi mesin manual/CSV. Keluaran akhir yang direncanakan: probabilitas failure, subset sensor hasil GA, serta prioritas Normal / Inspection / Maintenance / Critical. Saat W12, keluaran yang berfungsi baru prediksi baseline.')
h('3. Anggota dan usulan pembagian peran')
table([['NIM · Nama','Usulan tanggung jawab']]+[[a['nim']+' · '+a['name'],a['proposed_role']] for a in cfg['members']],[230,285])
p('Pembagian peran di atas merupakan usulan, perlu disepakati anggota; bukan bukti kontribusi yang telah dilakukan. Setiap anggota tetap perlu memahami seluruh pipeline saat demo.',True)

page()
h('4. Data dictionary dan kebijakan input')
p('Sumber: AI4I 2020 Predictive Maintenance Dataset, UCI 601. File resmi memuat 10.000 observasi dan 14 kolom; hanya enam variabel dipakai sebagai input. Type di-one-hot menjadi tiga kolom, sehingga NN menerima delapan input.')
table([['Variabel','Tipe / satuan','Peran'],['Type','Kategori H/L/M','Input kualitas produk'],['Air temperature [K]','Numerik / K','Input suhu udara'],['Process temperature [K]','Numerik / K','Input suhu proses'],['Rotational speed [rpm]','Numerik / rpm','Input kecepatan rotasi'],['Torque [Nm]','Numerik / Nm','Input torsi'],['Tool wear [min]','Numerik / menit','Input keausan alat'],['Machine failure','Biner 0/1','Target utama'],['UDI; Product ID','Identitas','Dikeluarkan; UDI hanya untuk split'],['TWF/HDF/PWF/OSF/RNF','Label jenis failure','Dikeluarkan untuk mencegah leakage']],[190,120,205])
h('5. Temuan EDA dan kualitas data')
p(f"Ditemukan <b>{eda['missing_cells']} sel kosong</b>, {eda['duplicated_full_rows']} duplikasi baris penuh dan {eda['duplicated_feature_rows']} duplikasi kombinasi enam fitur. Distribusi target: 9.661 non-failure (96,61%) dan 339 failure (3,39%). Imbalance perlu ditangani pada training; accuracy saja tidak cukup.")
image('W12/eda/target_and_order.png',505,174)
p('Grafik memperlihatkan proporsi kegagalan berbeda antarblok UDI. Karena suhu dibangkitkan dengan pola random walk dan urutan berpotensi berkorelasi, split tidak diacak. UDI bukan timestamp yang terverifikasi; evaluasi tetap tidak membuktikan generalisasi pada mesin atau periode nyata yang independen.',True)
p('Analisis lengkap tersedia pada W12/eda/: statistik numerik, missing values, korelasi, distribusi fitur, failure menurut Type, dan ringkasan JSON. Korelasi dipakai sebagai deskripsi, bukan dasar menyaring fitur dengan melihat test. Dataset bersifat sintetis sebagaimana keterangan UCI.',True)

page()
h('6. Split aman dan preprocessing')
table([['Split','Rentang UDI','Baris','Failure'],['Train','1–6000','6.000','255 (4,25%)'],['Validation','6001–8000','2.000','45 (2,25%)'],['Test terkunci','8001–10000','2.000','39 (1,95%)']],[110,160,90,155])
p('Imputer median/mode dan StandardScaler fit hanya pada train. Type memakai kategori kamus H/L/M. Walaupun tidak ada missing values, imputer disimpan bersama model agar pipeline konsisten. Bobot kelas dihitung dari train: w(c)=n_train/(2 n_c), yaitu 0,5222 untuk kelas 0 dan 11,7647 untuk kelas 1; validation/test tidak di-resample.')
p('Manifest split menyimpan UDI untuk audit. Validation dipakai memilih checkpoint; threshold tetap 0,5. Test belum dihitung metriknya dan tidak digunakan untuk preprocessing, fitness, tuning atau checkpoint. EDA semua data merupakan audit deskriptif; pemilihan model tidak menggunakan statistik test.')
h('7. Baseline Neural Network dan hasil validasi')
p(f"MLP: 8 input → 32 ReLU → 16 ReLU → 1 sigmoid; <b>{result['parameter_count']} parameter</b>. Adam, learning rate 0,001; batch 128; L2 0,0001; tanpa dropout; seed 42. Maksimum 150 epoch, patience 20 berdasarkan log loss validation; checkpoint terbaik epoch {result['best_epoch']}. Satu run awal; bukan hasil GA/PSO.")
table([['Model (validation)','Accuracy','Precision','Recall','F1'],['Dummy selalu non-failure','0,9775','0','0','0'],['MLP baseline']+[f'{m[k]:.4f}' for k in ['accuracy','precision','recall','f1']]],[175,85,85,85,85])
p(f"AP={m['average_precision']:.4f}; ROC AUC={m['roc_auc']:.4f}; balanced accuracy={m['balanced_accuracy']:.4f}. Confusion matrix: TN=1.897, FP=58, FN=20, TP=25. Model menemukan 25 dari 45 failure, tetapi masih melewatkan 20 failure dan menghasilkan 58 false alarm. Hasil ini menunjukkan ruang perbaikan; belum ada klaim keunggulan optimasi.",True)
image('W12/baseline/baseline_curves.png',490,174)
p('Kurva loss train/validation di atas dihitung tanpa bobot agar dapat dibandingkan; pembaruan bobot NN tetap memakai class weights. Artefak baseline.joblib menyimpan preprocessing dan model untuk inference; hasil setelah reload diverifikasi sama.',True)

page()
h('8. Rencana integrasi W13–W16')
table([['Minggu','Rencana teknis dan keluaran'],['13 · GA','Kromosom 6 bit; Type satu grup. Tolak subset kosong. Fitness F1 validation dengan penalti jumlah fitur. Usulan populasi 20/generasi 15, crossover 0,8, mutation 1/6, elitism 2; seed 11/22/33. Tetapkan bobot penalti sebelum run; simpan convergence dan best/mean/std.'],['14 · PSO + NN','Optimasi lr (10^-4–10^-2), hidden units (16–128), dropout (0–0,5), batch (32/64/128). Implementasi pbest/gbest dan update posisi-kecepatan. Bandingkan empat konfigurasi, split/budget setara dan beberapa seed.'],['15 · FIS + deploy','Rancang Mamdani + centroid. Input usulan probabilitas failure, wear dan torque; output empat prioritas. Validasi membership/rules dan skenario ekstrem. Integrasi end-to-end dan URL Streamlit publik.'],['16 · UAS','Laporan final, slide, demo langsung, video, source, artefak dan bukti kontribusi nyata. Siapkan demo lokal sebagai cadangan.']],[95,420])
p('<b>Catatan dropout:</b> MLPClassifier W12 tidak mendukung dropout. Pada W14 seluruh empat konfigurasi, termasuk baseline, akan dilatih ulang dengan backend NN yang mendukung dropout agar pembandingan konsisten. Search bounds di atas masih rancangan, bukan hasil pencarian.',True)
h('9. Risiko dan mitigasi')
p('<b>Leakage:</b> buang label jenis failure/ID, fit preprocessing hanya train, kunci test. <b>Imbalance:</b> class weights dari train dan evaluasi kelas positif. <b>Overfitting validation:</b> catat budget pencarian, beberapa seed dan evaluasi akhir sekali setelah model terkunci. <b>Data sintetis dan urutan:</b> jelaskan keterbatasan generalisasi. <b>False alarm/FN:</b> laporkan keduanya; threshold 0,5 belum dioptimalkan. <b>Deployment:</b> pin dependensi, simpan artefak dan uji URL publik tanpa login.')
h('10. Status pengumpulan dan reproduksi')
p('<b>Tersedia:</b> laporan 4 halaman; script EDA/preprocessing/baseline; statistik, grafik, manifest split, metrik validation, model tersimpan, README, requirements dan delapan area Streamlit. Prediksi manual/CSV memakai NN asli. GA/PSO/Fuzzy diberi status rencana.')
p(f"<b>Kelas:</b> {escape(cfg['class'])}. <b>Repository remote:</b> {escape(cfg['repository_url'])}. <b>Dashboard publik:</b> {escape(cfg['deployment_url'])}. URL repository sudah dicantumkan; deployment publik belum dilakukan. W12 mengizinkan bukti aplikasi awal lokal; URL skeleton dicantumkan bila tersedia.")
p('Reproduksi (Python 3.12): pip install -r requirements.txt; python -m src.eda; python -m src.train_baseline --seed 42; streamlit run app.py. Unggah PDF progres dan URL repo ke Moodle; tenggat resmi mengikuti Moodle/pengampu.',True)
h('Sumber')
p('1. Panduan Deliverables Tubes KB Minggu 12–16 (PDF dosen), hlm. 1–3.<br/>2. Tugas Besar KB 16 Kelompok UCI Streamlit (PDF dosen), hlm. 5 dan 9.<br/>3. UCI AI4I 2020, DOI: 10.24432/C5HS5C (CC BY 4.0). https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset<br/>4. Deployment resmi: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app',True)

def footer(canvas,doc):
    canvas.setStrokeColor(colors.HexColor('#147d78'));canvas.line(40,37,555,37)
    canvas.setFont('Helvetica',8);canvas.setFillColor(colors.HexColor('#536b7b'))
    canvas.drawString(40,24,'KELOMPOK 01 | W12 | PROPOSAL, EDA & BASELINE')
    canvas.drawRightString(555,24,f'{doc.page}')
out=ROOT/'W12/W12_Proposal_EDA.pdf'
doc=SimpleDocTemplate(str(out),pagesize=A4,rightMargin=40,leftMargin=40,topMargin=34,bottomMargin=46,title='W12 Proposal EDA - Kelompok 01',author='Kelompok 01')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
(ROOT/'W12/W12_Proposal_EDA.md').write_text('\n\n'.join(md),encoding='utf-8')
print(out)
