"""Membuat proposal/progres dengan tata tulis laporan mahasiswa.

Jalankan dari root: python tools/build_proposal_mahasiswa.py
Konversi PDF: LibreOffice/Word. Nomor daftar isi dapat diperbarui memakai
--page-map work/proposal_page_map.json setelah PDF dikonversi.
"""
import argparse
import json
from pathlib import Path
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING
from docx.enum.section import WD_SECTION
from docx.shared import Cm, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'W12' / 'arsip'
OUT.mkdir(parents=True, exist_ok=True)
NAME = 'W12_Proposal_Progres_KelasB_Kelompok01'

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--page-map',type=Path,default=Path(__file__).with_name('proposal_page_map.json'))
    args=parser.parse_args()
    page_map=json.loads(args.page_map.read_text()) if args.page_map.exists() else {}
    config=json.loads((ROOT/'project.json').read_text())
    result=json.loads((OUT/'baseline/metrics.json').read_text())
    v=result['validation']
    d=Document();md=[];headings=[]
    sec=d.sections[0]
    def setup(section):
        section.page_width=Cm(21);section.page_height=Cm(29.7)
        section.left_margin=Cm(4);section.right_margin=Cm(3)
        section.top_margin=Cm(3);section.bottom_margin=Cm(3)
        section.footer_distance=Cm(1.5);section.header_distance=Cm(1.5)
    setup(sec)
    normal=d.styles['Normal'];normal.font.name='Times New Roman';normal.font.size=Pt(12)
    normal._element.rPr.rFonts.set(qn('w:eastAsia'),'Times New Roman')
    pf=normal.paragraph_format
    pf.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY;pf.first_line_indent=Cm(1.25)
    pf.line_spacing=1.5;pf.space_before=Pt(0);pf.space_after=Pt(0);pf.widow_control=True
    for name in ['Heading 1','Heading 2','Heading 3']:
        s=d.styles[name];s.font.name='Times New Roman';s.font.size=Pt(12);s.font.bold=True;s.font.color.rgb=RGBColor(0,0,0)
        s.paragraph_format.first_line_indent=Cm(0);s.paragraph_format.space_before=Pt(10);s.paragraph_format.space_after=Pt(6)
        s.paragraph_format.line_spacing=1.5;s.paragraph_format.keep_with_next=True
    d.styles['Heading 1'].paragraph_format.alignment=WD_ALIGN_PARAGRAPH.CENTER
    d.styles['Heading 1'].paragraph_format.space_before=Pt(0)
    d.styles['Heading 1'].paragraph_format.space_after=Pt(12)
    for name in ['Caption','Footer']:
        s=d.styles[name];s.font.name='Times New Roman';s.font.size=Pt(10 if name=='Caption' else 12)
        s.font.color.rgb=RGBColor(0,0,0);s.paragraph_format.first_line_indent=Cm(0)
        s.paragraph_format.alignment=WD_ALIGN_PARAGRAPH.CENTER;s.paragraph_format.line_spacing=1
    # Tema bawaan Word dapat mengalahkan nama font eksplisit saat dikonversi.
    for name in ['Normal','Heading 1','Heading 2','Heading 3','Caption','Footer']:
        fonts=d.styles[name]._element.get_or_add_rPr().find(qn('w:rFonts'))
        if fonts is None:
            fonts=OxmlElement('w:rFonts');d.styles[name]._element.get_or_add_rPr().append(fonts)
        for key in ['asciiTheme','hAnsiTheme','eastAsiaTheme','cstheme','csTheme']:
            fonts.attrib.pop(qn('w:'+key),None)
        for key in ['ascii','hAnsi','eastAsia','cs']:
            fonts.set(qn('w:'+key),'Times New Roman')
    d.core_properties.title='Proposal dan Laporan Progres Minggu 12 - Intelligent Predictive Maintenance System'
    d.core_properties.author='Kelompok 1 - Kelas B - Institut Teknologi Kalimantan'
    d.core_properties.subject='Tugas Besar Kecerdasan Buatan TE2514031'

    def p(text='',first=True):
        x=d.add_paragraph(text)
        if not first:x.paragraph_format.first_line_indent=Cm(0)
        md.append(text)
        return x
    def center(text,size=12,bold=False,after=0,before=0):
        x=d.add_paragraph();x.alignment=WD_ALIGN_PARAGRAPH.CENTER
        x.paragraph_format.first_line_indent=Cm(0);x.paragraph_format.line_spacing=1.25
        x.paragraph_format.space_after=Pt(after);x.paragraph_format.space_before=Pt(before)
        r=x.add_run(text);r.bold=bold;r.font.size=Pt(size)
        md.append(text);return x
    def h(text,level=2):
        d.add_paragraph(text,style='Heading '+str(level));headings.append((text,level));md.append('#'*level+' '+text)
    def chapter(roman,title,first=False):
        if not first:d.add_page_break()
        h('BAB '+roman+'\n'+title,1)
    def item(text,num):
        x=p(str(num)+'. '+text,False);x.paragraph_format.left_indent=Cm(.65);x.paragraph_format.first_line_indent=Cm(-.65)
    def caption(text):
        x=d.add_paragraph(text,style='Caption');x.paragraph_format.space_before=Pt(5);x.paragraph_format.space_after=Pt(7)
        md.append(text)
    def table(title,rows,widths):
        caption(title)
        t=d.add_table(rows=1,cols=len(rows[0]));t.autofit=False
        t.style='Table Grid'
        for col,w in zip(t.columns,widths):col.width=Cm(w)
        for i,row in enumerate(rows):
            cells=t.rows[0].cells if i==0 else t.add_row().cells
            for cell,text,w in zip(cells,row,widths):
                cell.width=Cm(w);cell.text=str(text)
                for par in cell.paragraphs:
                    par.paragraph_format.first_line_indent=Cm(0);par.paragraph_format.line_spacing=1
                    par.paragraph_format.space_after=Pt(4);par.paragraph_format.space_before=Pt(4)
                    par.alignment=WD_ALIGN_PARAGRAPH.LEFT
                    for run in par.runs:run.font.size=Pt(10.5);run.bold=i==0
                if i==0:
                    sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'EDEDED');cell._tc.get_or_add_tcPr().append(sh)
            pr=t.rows[i]._tr.get_or_add_trPr();pr.append(OxmlElement('w:cantSplit'))
            if i==0:
                repeat=OxmlElement('w:tblHeader');pr.append(repeat)
        d.add_paragraph().paragraph_format.space_after=Pt(0)
        md.append('\n'.join('| '+' | '.join(map(str,r))+' |' for r in rows[:1])+'\n|'+'|'.join(['---']*len(rows[0]))+'|\n'+'\n'.join('| '+' | '.join(map(str,r))+' |' for r in rows[1:]))
    def figure(relative,text,width=13.8):
        par=d.add_paragraph();par.paragraph_format.first_line_indent=Cm(0);par.alignment=WD_ALIGN_PARAGRAPH.CENTER
        par.paragraph_format.keep_with_next=True;par.paragraph_format.line_spacing=1
        par.add_run().add_picture(str(ROOT/relative),width=Cm(width))
        caption(text);md.append(f'![{text}]({relative.replace("W12/", "../", 1)})')
    def numbering(section,fmt,start=1):
        section.footer.is_linked_to_previous=False
        prop=section._sectPr
        old=prop.find(qn('w:pgNumType'))
        if old is not None:prop.remove(old)
        typ=OxmlElement('w:pgNumType');typ.set(qn('w:fmt'),fmt);typ.set(qn('w:start'),str(start));prop.append(typ)
        par=section.footer.paragraphs[0];par.style=d.styles['Footer']
        f=OxmlElement('w:fldSimple');f.set(qn('w:instr'),'PAGE');par._p.append(f)

    center('PROPOSAL DAN LAPORAN PROGRES\nTUGAS BESAR KECERDASAN BUATAN',14,True,after=20)
    center('INTELLIGENT PREDICTIVE MAINTENANCE SYSTEM\nBERBASIS GA, PSO, NEURAL NETWORK, DAN FUZZY LOGIC',14,True,after=12)
    center('Progres Minggu ke-12\nSemester Gasal Tahun Akademik 2026/2027',12,False,after=28)
    center('Disusun untuk memenuhi tugas mata kuliah\nKecerdasan Buatan (TE2514031)',12,False,after=16)
    center('Dosen Pengampu:\nIr. Muhammad Ridho Dewanto, S.T., M.T.',12,False,after=28)
    center('Disusun oleh:\nKelompok 1 — Kelas B',12,True,after=10)
    t=d.add_table(rows=0,cols=2);t.autofit=False
    for a in config['members']:
        cells=t.add_row().cells;cells[0].width=Cm(9);cells[1].width=Cm(5)
        cells[0].text=a['name'];cells[1].text=a['nim']
        for c in cells:
            for par in c.paragraphs:
                par.paragraph_format.first_line_indent=Cm(0);par.paragraph_format.line_spacing=1.25
                for run in par.runs:run.font.size=Pt(12)
        md.append(a['name']+' — '+a['nim'])
    center('INSTITUT TEKNOLOGI KALIMANTAN\n2026',14,True,before=45)

    front=d.add_section(WD_SECTION.NEW_PAGE);setup(front);numbering(front,'lowerRoman')
    center('KATA PENGANTAR',12,True,after=18)
    p('Proposal dan laporan progres ini disusun untuk memenuhi tahapan minggu ke-12 Tugas Besar mata kuliah Kecerdasan Buatan, Institut Teknologi Kalimantan, semester gasal tahun akademik 2026/2027. Topik yang dikembangkan oleh Kelompok 1 Kelas B adalah Intelligent Predictive Maintenance System dengan memanfaatkan AI4I 2020 Predictive Maintenance Dataset dari UCI Machine Learning Repository.')
    p('Dokumen ini memuat latar belakang, landasan teori, rancangan sistem, metodologi pengolahan data, serta hasil awal eksplorasi dan pelatihan baseline Neural Network. Pada tahap berikutnya, sistem direncanakan mengintegrasikan Genetic Algorithm, Particle Swarm Optimization, Fuzzy Logic, dan dashboard Streamlit yang dapat diakses melalui internet.')
    p('Penyusun mengucapkan terima kasih kepada dosen pengampu, Ir. Muhammad Ridho Dewanto, S.T., M.T., atas arahan pembelajaran dan ketentuan pelaksanaan tugas besar. Dokumen ini masih terbatas pada progres awal. Saran dan masukan diperlukan untuk memperbaiki rancangan, eksperimen, dan penyajian hasil pada tahap selanjutnya.')
    x=p('November 2026\n\nKelompok 1',False);x.alignment=WD_ALIGN_PARAGRAPH.RIGHT;x.paragraph_format.space_before=Pt(24)
    d.add_page_break()
    center('DAFTAR ISI',12,True,after=14)
    toc_paragraphs=[]
    def toc_entry(label,key,level=1,fixed=None):
        par=d.add_paragraph();par.paragraph_format.first_line_indent=Cm(0)
        par.paragraph_format.left_indent=Cm(0 if level==1 else .5)
        par.paragraph_format.line_spacing=1.08;par.paragraph_format.space_after=Pt(2)
        from docx.enum.text import WD_TAB_ALIGNMENT,WD_TAB_LEADER
        par.paragraph_format.tab_stops.add_tab_stop(Cm(13.9),WD_TAB_ALIGNMENT.RIGHT,WD_TAB_LEADER.DOTS)
        r=par.add_run(label+'\t'+str(fixed or page_map.get(key,'—')));r.font.size=Pt(11);r.bold=level==1
        toc_paragraphs.append(label)
    toc_entry('KATA PENGANTAR','',fixed='i');toc_entry('DAFTAR ISI','',fixed='ii')
    toc_index=len(d.paragraphs)
    # Entri bab/subbab ditambahkan ke daftar isi setelah seluruh isi dibangun.
    toc_anchor=d.paragraphs[-1]._p

    body=d.add_section(WD_SECTION.NEW_PAGE);setup(body);numbering(body,'decimal')
    chapter('I','PENDAHULUAN',True)
    h('1.1 Latar Belakang')
    p('Kegagalan mesin dapat mengganggu keberlangsungan proses operasi. Informasi kondisi mesin, seperti suhu, kecepatan putaran, torsi, dan keausan alat, dapat digunakan sebagai masukan untuk mengidentifikasi indikasi kegagalan. Pengolahan data tersebut menjadi prediksi dan rekomendasi perawatan merupakan dasar pengembangan sistem predictive maintenance dalam tugas besar ini.')
    p('AI4I 2020 menyediakan data sintetis yang menggambarkan karakteristik predictive maintenance untuk keperluan pengembangan metode (UCI Machine Learning Repository, 2020). Data ini memungkinkan eksperimen klasifikasi kegagalan secara terukur, tetapi tidak dapat langsung mewakili seluruh kondisi mesin industri nyata.')
    p('Sistem yang diusulkan memadukan GA untuk seleksi fitur, PSO untuk optimasi hyperparameter, Neural Network sebagai model prediksi, serta Fuzzy Logic untuk menentukan prioritas perawatan. Minggu ke-12 difokuskan pada pemahaman data, pencegahan kebocoran informasi, pelatihan baseline, dan pembuatan kerangka Streamlit sesuai panduan tugas besar.')
    h('1.2 Rumusan Masalah')
    for i,s in enumerate(['Bagaimana menyiapkan data AI4I 2020 dan membaginya untuk pengembangan model tanpa membocorkan informasi target?','Bagaimana kinerja awal MLP dalam mendeteksi kegagalan mesin pada data dengan kelas yang tidak seimbang?','Bagaimana merancang integrasi GA, PSO, NN, Fuzzy Logic, dan Streamlit untuk tahap pengembangan berikutnya?'],1):item(s,i)
    h('1.3 Tujuan')
    for i,s in enumerate(['Menghasilkan eksplorasi data, kamus variabel, dan pipeline preprocessing yang dapat dijalankan ulang.','Membangun baseline MLP dan mengukur kinerja deteksi kelas kegagalan pada data validasi.','Menyusun arsitektur sistem hibrida, kerangka dashboard, pembagian peran, dan rencana pengerjaan minggu ke-13 sampai ke-16.'],1):item(s,i)
    h('1.4 Batasan Masalah')
    p('Pengamatan dibatasi pada dataset AI4I 2020, target biner Machine failure, dan enam variabel masukan. Sistem belum mengestimasi sisa umur mesin atau waktu menuju kerusakan. Hasil minggu ke-12 adalah baseline tanpa GA, PSO, dan Fuzzy. Implementasi publik Streamlit serta pengujian sistem hibrida dilakukan pada tahapan berikutnya. Prediksi belum ditujukan sebagai dasar keputusan operasional industri.')
    h('1.5 Manfaat')
    p('Proyek diharapkan menjadi sarana penerapan optimasi, pembelajaran, dan pengambilan keputusan dalam satu pipeline yang dapat dijelaskan. Dashboard juga diharapkan memudahkan pengguna mengeksplorasi data dan memahami hubungan antara masukan mesin, prediksi model, dan prioritas perawatan.')

    chapter('II','TINJAUAN PUSTAKA')
    h('2.1 Predictive Maintenance dan Dataset AI4I 2020')
    p('Dalam proyek ini, predictive maintenance dioperasionalkan sebagai klasifikasi status kegagalan berdasarkan kondisi operasi pada satu pengamatan. Dataset AI4I 2020 merupakan data sintetis dari UCI yang mencakup jenis produk, lima variabel operasi, dan label kegagalan. Penggunaan data sintetis membantu penyusunan eksperimen awal, tetapi validasi pada data nyata masih diperlukan sebelum penerapan di lapangan (UCI Machine Learning Repository, 2020).')
    h('2.2 Neural Network dan Multilayer Perceptron')
    p('Neural Network mempelajari hubungan antara input dan keluaran melalui penyesuaian bobot. Backpropagation menghitung perubahan bobot berdasarkan galat keluaran (Rumelhart, Hinton, dan Williams, 1986). MLP dipilih karena masukan proyek berbentuk tabel per pengamatan. Implementasi baseline menggunakan MLPClassifier dengan lapisan tersembunyi beraktivasi ReLU dan output biner (scikit-learn developers, t.t.-a).')
    h('2.3 Genetic Algorithm')
    p('GA menggunakan populasi kandidat solusi serta operasi seleksi, crossover, dan mutasi untuk melakukan pencarian. Konsep adaptasi dan pencarian melalui mekanisme evolusi dijelaskan oleh Holland (1992). Pada proyek ini, GA direncanakan memilih subset variabel masukan. Setiap kromosom berupa enam bit, sedangkan semua kolom hasil encoding Type diperlakukan sebagai satu kelompok fitur.')
    h('2.4 Particle Swarm Optimization')
    p('PSO menggerakkan sekumpulan partikel dalam ruang pencarian dengan mempertimbangkan solusi terbaik masing-masing partikel dan solusi terbaik kelompok (Kennedy dan Eberhart, 1995). Perannya dalam proyek ini adalah mencari konfigurasi hyperparameter NN, meliputi learning rate, jumlah hidden units, dropout, dan batch size. Hasil terbaik tetap perlu dibuktikan melalui evaluasi dengan protokol yang konsisten.')
    h('2.5 Fuzzy Logic')
    p('Himpunan fuzzy menyatakan derajat keanggotaan suatu nilai, sehingga konsep linguistik dapat direpresentasikan secara bertahap (Zadeh, 1965). Fuzzy Logic direncanakan mengolah probabilitas kegagalan dan kondisi mesin menjadi empat prioritas perawatan, yaitu Normal, Inspection, Maintenance, dan Critical. Perancangan mencakup fungsi keanggotaan, aturan, inferensi, dan defuzzification.')
    h('2.6 Evaluasi dan Pencegahan Data Leakage')
    p('Pada klasifikasi yang tidak seimbang, accuracy perlu dibaca bersama precision, recall, F1-score, dan confusion matrix. Data leakage terjadi ketika informasi yang seharusnya belum tersedia ikut memengaruhi pelatihan atau pemilihan model. Pemisahan data dan penyimpanan preprocessing bersama model membantu menjaga konsistensi proses training dan inference (scikit-learn developers, t.t.-b).')
    h('2.7 Dashboard Streamlit')
    p('Streamlit digunakan sebagai antarmuka untuk menampilkan eksplorasi data, evaluasi model, dan prediksi interaktif. Dokumen tugas menetapkan bahwa aplikasi akhir harus dapat diakses melalui internet tanpa izin khusus. Deployment direncanakan menggunakan Streamlit Community Cloud dengan source, dependensi, dan artefak model yang tersimpan dalam repository (Streamlit, t.t.).')

    chapter('III','METODOLOGI DAN RANCANGAN SISTEM')
    h('3.1 Jenis dan Tahapan Pengerjaan')
    p('Pengerjaan menggunakan eksperimen komputasional pada data sekunder. Tahapannya meliputi pengumpulan data, pemeriksaan kualitas, pembagian data, preprocessing, pembangunan baseline, optimasi, penyusunan FIS, integrasi dashboard, dan evaluasi. Tahap optimasi dan FIS masih merupakan rancangan pada laporan progres ini.')
    table('Tabel 3.1 Rancangan alur sistem',[
        ['Tahap','Proses dan keluaran'],['Data dan preprocessing','Dataset UCI → audit → split → encoding dan standardisasi.'],['Baseline W12','Enam variabel → MLP → probabilitas kegagalan → evaluasi validation.'],['Optimasi W13–W14','GA memilih variabel; PSO mencari hyperparameter NN.'],['Integrasi W15','Prediksi NN → inferensi Fuzzy → prioritas perawatan → Streamlit online.']],[4,10])
    h('3.2 Sumber Data dan Definisi Variabel')
    p('Dataset bersumber dari UCI ID 601 dengan 10.000 baris dan 14 kolom. Target utama adalah Machine failure dengan nilai 0 untuk non-failure dan 1 untuk failure. Data diunduh dari sumber resmi, dan identitas versi berkas dicatat melalui checksum agar eksperimen dapat diulang.')
    table('Tabel 3.2 Kamus variabel dan kebijakan penggunaan',[
        ['Variabel','Satuan/tipe','Penggunaan'],['Type','Kategori H, L, M','Input; jenis/kualitas produk.'],['Air temperature','Kelvin','Input suhu udara.'],['Process temperature','Kelvin','Input suhu proses.'],['Rotational speed','rpm','Input kecepatan rotasi.'],['Torque','Nm','Input torsi.'],['Tool wear','Menit','Input keausan alat.'],['Machine failure','Biner','Target klasifikasi.'],['UDI; Product ID','Identitas','Tidak menjadi input NN.'],['TWF; HDF; PWF; OSF; RNF','Label failure','Dikeluarkan untuk mencegah leakage.']],[5.1,2.9,6])
    p('Label jenis kegagalan tidak digunakan sebagai prediktor Machine failure karena mengandung informasi keluaran yang hendak diprediksi. UDI dipakai untuk menentukan urutan pembagian data, sedangkan Product ID dikeluarkan sebagai pengenal produk.')
    h('3.3 Pembagian Data dan Preprocessing')
    table('Tabel 3.3 Pembagian data yang digunakan',[
        ['Bagian','UDI','Jumlah','Failure'],['Train','1–6000','6.000','255'],['Validation','6001–8000','2.000','45'],['Test','8001–10000','2.000','39']],[3.5,4.5,3,3])
    p('Pembagian dilakukan berurutan dengan proporsi 60%/20%/20%. Pendekatan ini mengurangi pencampuran pola antarbaris yang berdekatan. Namun, UDI hanya menjadi proxy urutan; tidak tersedia timestamp terverifikasi. Dengan demikian, pembagian tersebut tidak membuktikan evaluasi peramalan waktu maupun pemisahan mesin yang benar-benar independen.')
    p('Imputer numerik menggunakan median dan imputer kategori menggunakan modus, kemudian variabel numerik distandardisasi. Seluruh parameter tersebut dihitung dari train saja. Type diubah menjadi tiga kolom one-hot sehingga terdapat delapan masukan NN. Data validation dan test hanya ditransformasi memakai preprocessing hasil train.')
    p('Ketidakseimbangan kelas ditangani dengan bobot kelas w(c) = n_train / (2 × n_c). Bobot kelas 0 sebesar 0,5222 dan kelas 1 sebesar 11,7647. Tidak dilakukan oversampling pada validation atau test. EDA seluruh dataset dipakai untuk audit deskriptif, bukan untuk memilih fitur atau konfigurasi berdasarkan test.')
    h('3.4 Konfigurasi Baseline Neural Network')
    table('Tabel 3.4 Konfigurasi baseline MLP',[
        ['Komponen','Konfigurasi'],['Arsitektur','8 input → 32 ReLU → 16 ReLU → 1 output sigmoid.'],['Jumlah parameter','833 parameter.'],['Optimasi','Adam; learning rate 0,001; batch size 128.'],['Regularisasi','L2 sebesar 0,0001; tanpa dropout.'],['Training','Maksimum 150 epoch; seed 42; bobot kelas dari train.'],['Checkpoint','Log loss validation terendah; patience 20 epoch.'],['Threshold','0,5; ditetapkan sebelum evaluasi hasil baseline.']],[4.2,9.8])
    p('Model baseline dilatih melalui pembaruan per epoch, lalu checkpoint dipilih dari log loss validation. Model dan preprocessing disimpan dalam satu artefak agar inference menggunakan transformasi yang sama. Test belum dievaluasi dan tetap disimpan untuk penilaian akhir setelah konfigurasi dikunci.')
    h('3.5 Metrik Evaluasi')
    p('Metrik utama adalah recall dan F1 kelas failure, dengan precision untuk melihat konsekuensi false alarm. Accuracy dan confusion matrix tetap disajikan. Metrik tambahan meliputi balanced accuracy, average precision, dan ROC AUC. Definisi metrik utama ditunjukkan sebagai berikut.',False)
    for s in ['Accuracy = (TP + TN) / (TP + TN + FP + FN)','Precision = TP / (TP + FP)','Recall = TP / (TP + FN)','F1 = 2 × Precision × Recall / (Precision + Recall)']:
        x=p(s,False);x.paragraph_format.line_spacing=1.15;x.paragraph_format.space_after=Pt(4)
    p('TP menyatakan failure yang terdeteksi, TN menyatakan non-failure yang dikenali, FP merupakan false alarm, dan FN merupakan failure yang terlewat. Pengambilan kesimpulan tidak dilakukan dari accuracy saja karena kelas non-failure mendominasi data.')
    h('3.6 Rencana GA, PSO, dan Fuzzy Logic')
    p('GA direncanakan memakai kromosom enam bit dengan larangan subset kosong. Fitness menggabungkan F1 validation dan penalti jumlah fitur. Usulan awal adalah populasi 20, generasi 15, crossover 0,8, mutasi 1/6, elitism 2, dan seed 11/22/33. Besaran penalti ditetapkan sebelum eksperimen. Konvergensi dan statistik antar-run akan dilaporkan tanpa memakai test untuk seleksi.')
    p('Ruang pencarian PSO yang direncanakan adalah learning rate 0,0001–0,01, hidden units 16–128, dropout 0–0,5, serta batch size 32/64/128. Karena MLPClassifier baseline belum mendukung dropout, seluruh konfigurasi pembanding akan dilatih ulang dengan backend NN yang mendukungnya agar perbandingan tetap setara.')
    p('FIS direncanakan menggunakan inferensi Mamdani dan defuzzification centroid. Masukan usulan berupa probabilitas failure, tool wear, dan torque. Fungsi keanggotaan serta aturan perlu ditetapkan dan diuji pada skenario normal maupun ekstrem. Belum ada klaim bahwa Fuzzy meningkatkan akurasi NN; perannya adalah menghasilkan keputusan yang lebih mudah dijelaskan.')

    chapter('IV','PROGRES DAN HASIL AWAL')
    h('4.1 Hasil Eksplorasi Data')
    p('Pemeriksaan dataset menunjukkan 9.661 baris non-failure (96,61%) dan 339 baris failure (3,39%). Tidak ditemukan nilai kosong, duplikasi baris penuh, maupun duplikasi kombinasi enam variabel input. Ketidakseimbangan ini memperkuat kebutuhan evaluasi khusus pada kelas failure.')
    figure('W12/eda/target_and_order.png','Gambar 4.1 Distribusi target dan proporsi failure per blok UDI')
    p('Proporsi failure bervariasi antarblok UDI. Jumlah failure juga berbeda antara train, validation, dan test. Kondisi ini perlu dipertimbangkan ketika membaca hasil baseline dan menjadi alasan untuk tidak menyimpulkan kinerja hanya dari satu ukuran agregat. Statistik numerik, missing values, distribusi fitur, dan korelasi tersedia pada folder W12/eda di repository.')
    h('4.2 Hasil Baseline Neural Network')
    p(f"Pelatihan baseline mencapai {result['epochs_run']} epoch dan checkpoint terbaik berada pada epoch {result['best_epoch']}. Evaluasi awal dilakukan terhadap 2.000 data validation dengan 45 kasus failure. Tabel 4.1 menunjukkan hasil baseline dan pembanding sederhana yang selalu memprediksi non-failure.")
    def dec(x):return f'{x:.4f}'.replace('.',',')
    table('Tabel 4.1 Perbandingan kinerja pada data validation',[
        ['Model','Accuracy','Precision','Recall','F1'],['Dummy non-failure','0,9775','0,0000','0,0000','0,0000'],['Baseline MLP']+[dec(v[k]) for k in ['accuracy','precision','recall','f1']]],[4,2.5,2.5,2.5,2.5])
    table('Tabel 4.2 Confusion matrix baseline pada validation',[
        ['Kondisi aktual','Prediksi non-failure','Prediksi failure'],['Non-failure','1.897 (TN)','58 (FP)'],['Failure','20 (FN)','25 (TP)']],[4.4,4.8,4.8])
    figure('W12/baseline/baseline_curves.png','Gambar 4.2 Kurva loss dan confusion matrix baseline')
    p('Baseline mendeteksi 25 dari 45 failure, sehingga recall mencapai 55,56%. Namun, 20 failure masih terlewat dan 58 non-failure menghasilkan false alarm. Precision sebesar 30,12% menunjukkan bahwa banyak prediksi positif belum sesuai dengan label aktual. Oleh karena itu, baseline ini merupakan titik awal, bukan model akhir dengan kinerja yang sudah memadai.')
    p('Dummy memperoleh accuracy lebih tinggi karena selalu mengikuti kelas mayoritas, tetapi tidak mendeteksi satu pun failure. Perbandingan tersebut menunjukkan keterbatasan accuracy pada data yang timpang. Metrik tambahan baseline adalah average precision 0,4710, ROC AUC 0,9234, dan balanced accuracy 0,7629. Kurva loss ditampilkan tanpa bobot untuk membandingkan train dan validation, sedangkan pembaruan NN tetap memakai bobot kelas.')
    h('4.3 Progres Implementasi Dashboard dan Repository')
    p('Kerangka Streamlit telah menyediakan delapan area: Overview, Dataset Explorer, GA Optimization, PSO Optimization, Neural Network, Fuzzy Inference, Prediction/Simulation, dan Model Comparison. Prediksi manual dan unggah CSV sudah menggunakan baseline MLP yang tersimpan. Area GA, PSO, dan Fuzzy ditandai sebagai rencana karena implementasinya belum dilakukan pada minggu ke-12.')
    p('Pemeriksaan awal mencakup pemisahan split, parameter scaler dari train, kesamaan prediksi setelah model dimuat ulang, serta penolakan input yang tidak valid. Delapan halaman dan alur prediksi manual/CSV telah diperiksa. Bukti screenshot dan catatan verifikasi tersedia pada repository. Pemeriksaan ini belum merupakan validasi operasional pada mesin nyata.')
    p('Repository: https://github.com/putcah/tubes-kecerdasan-buatan-kelompok-1. Aplikasi telah dijalankan secara lokal, tetapi belum di-deploy publik. Panduan deployment sudah disiapkan; URL publik akan dicantumkan setelah aplikasi benar-benar aktif dan diuji tanpa login khusus.',False)
    h('4.4 Usulan Pembagian Peran')
    table('Tabel 4.3 Usulan tanggung jawab anggota',[
        ['Nama dan NIM','Usulan tanggung jawab']]+[[a['name']+'\n'+a['nim'],a['proposed_role']] for a in config['members']],[6.3,7.7])
    p('Pembagian tersebut merupakan usulan untuk disepakati kelompok, bukan bukti kontribusi yang telah dilakukan. Setiap anggota tetap perlu memahami seluruh pipeline dan mendokumentasikan kontribusinya pada tahap selanjutnya.')
    h('4.5 Jadwal Pengembangan Selanjutnya')
    table('Tabel 4.4 Rencana penyelesaian tugas besar',[
        ['Minggu','Target pekerjaan dan keluaran'],['12','EDA, preprocessing, split, baseline NN, proposal progres, dan kerangka Streamlit.'],['13','Implementasi GA, fitur terpilih, kurva convergence, dan Baseline vs GA+NN.'],['14','Implementasi PSO, training NN, artefak, dan empat konfigurasi pembanding.'],['15','FIS, integrasi end-to-end, dashboard publik, dan draft laporan akhir.'],['16','Laporan final, slide, video, demo langsung, dan bukti kontribusi.']],[2.4,11.6])
    h('4.6 Kendala dan Mitigasi')
    p('Kendala utama adalah jumlah failure yang kecil, perbedaan distribusi antarbagian data, serta banyaknya false alarm dan failure yang terlewat pada baseline. Mitigasinya meliputi evaluasi kelas positif, pencatatan budget pencarian, beberapa seed untuk GA/PSO, dan penyimpanan test untuk evaluasi akhir. Penggunaan validation secara berulang juga perlu dibatasi agar tidak menimbulkan optimisme hasil. Keterbatasan data sintetis dan belum adanya deployment publik tetap dicantumkan sebagai batas progres saat ini.')

    chapter('V','PENUTUP')
    h('5.1 Kesimpulan Progres')
    p('Tahap minggu ke-12 telah menghasilkan pemahaman dataset, kamus variabel, split train/validation/test, preprocessing, baseline MLP, serta kerangka Streamlit. Enam variabel digunakan sebagai input, sedangkan ID dan label jenis kegagalan dikeluarkan untuk mengurangi risiko data leakage. Model beserta preprocessing telah disimpan untuk inference.')
    p('Hasil validation menunjukkan accuracy 96,10%, precision 30,12%, recall 55,56%, dan F1 0,3906. Hasil tersebut belum cukup untuk menyimpulkan keberhasilan sistem akhir. Baseline masih menghasilkan false alarm dan melewatkan sebagian failure. Test belum dievaluasi, sedangkan hasil GA, PSO, dan Fuzzy belum tersedia pada tahap ini.')
    h('5.2 Rencana Tindak Lanjut')
    p('Pengerjaan berikutnya difokuskan pada implementasi GA dan evaluasi subset fitur. Setelah itu, PSO digunakan untuk optimasi NN dengan protokol perbandingan yang setara. Fuzzy Logic akan diintegrasikan sebagai lapisan keputusan, kemudian dashboard di-deploy agar dapat diakses publik. Evaluasi akhir, laporan, dan demo akan disusun berdasarkan hasil eksperimen yang dapat diverifikasi.')

    d.add_page_break();h('DAFTAR PUSTAKA',1)
    refs=[
        'Holland, J. H. (1992). Adaptation in natural and artificial systems: An introductory analysis with applications to biology, control, and artificial intelligence. The MIT Press.',
        'Kennedy, J., & Eberhart, R. (1995). Particle swarm optimization. Proceedings of ICNN ’95—International Conference on Neural Networks, 4, 1942–1948. https://doi.org/10.1109/ICNN.1995.488968',
        'Panduan Deliverables Tugas Besar Kecerdasan Buatan: Minggu 12–16. (2026). Dokumen penugasan mata kuliah TE2514031, semester gasal 2026/2027.',
        'Rumelhart, D. E., Hinton, G. E., & Williams, R. J. (1986). Learning representations by back-propagating errors. Nature, 323, 533–536. https://doi.org/10.1038/323533a0',
        'scikit-learn developers. (t.t.-a). MLPClassifier. Dokumentasi scikit-learn 1.8. https://scikit-learn.org/1.8/modules/generated/sklearn.neural_network.MLPClassifier.html',
        'scikit-learn developers. (t.t.-b). Common pitfalls and recommended practices. Dokumentasi scikit-learn 1.8. https://scikit-learn.org/1.8/common_pitfalls.html',
        'Streamlit. (t.t.). Prep and deploy your app on Community Cloud. Dokumentasi Streamlit. https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app',
        'Tugas Besar Kecerdasan Buatan: 16 Kelompok UCI Streamlit. (2026). Dokumen penugasan mata kuliah TE2514031, semester gasal 2026/2027.',
        'UCI Machine Learning Repository. (2020). AI4I 2020 predictive maintenance dataset [Dataset]. https://doi.org/10.24432/C5HS5C',
        'Zadeh, L. A. (1965). Fuzzy sets. Information and Control, 8(3), 338–353. https://doi.org/10.1016/S0019-9958(65)90241-X'
    ]
    for ref in refs:
        x=p(ref,False);x.paragraph_format.left_indent=Cm(1.25);x.paragraph_format.first_line_indent=Cm(-1.25)
        x.paragraph_format.line_spacing=1;x.paragraph_format.space_after=Pt(10)

    # Sisipkan entri daftar isi pada anchor front matter, tidak pada akhir dokumen.
    for text,level in headings:
        label=text.replace('\n',' ')
        par=d.add_paragraph();par.paragraph_format.first_line_indent=Cm(0)
        par.paragraph_format.left_indent=Cm(0 if level==1 else .5)
        par.paragraph_format.line_spacing=1.08;par.paragraph_format.space_after=Pt(2)
        from docx.enum.text import WD_TAB_ALIGNMENT,WD_TAB_LEADER
        par.paragraph_format.tab_stops.add_tab_stop(Cm(13.9),WD_TAB_ALIGNMENT.RIGHT,WD_TAB_LEADER.DOTS)
        r=par.add_run(label+'\t'+str(page_map.get(label,'—')));r.font.size=Pt(10.5);r.bold=level==1
        toc_anchor.addnext(par._p);toc_anchor=par._p
    # Daftar isi memakai nomor aktual hasil konversi PDF; heading tetap tersedia
    # di panel navigasi Word dan dapat dipakai membuat TOC otomatis jika diinginkan.
    d.save(OUT/(NAME+'.docx'))
    (OUT/(NAME+'.md')).write_text('\n\n'.join(md),encoding='utf-8')
    print(OUT/(NAME+'.docx'))

if __name__=='__main__':main()
