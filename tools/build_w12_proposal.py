"""Proposal awal W12: empat halaman, termasuk sampul.

python tools/build_w12_proposal.py
Word dibuat dengan python-docx. PDF diekspor melalui LibreOffice jika tersedia.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'W12'

def main():
    cfg=json.loads((ROOT/'project.json').read_text())
    metric=json.loads((OUT/'baseline/metrics.json').read_text())
    eda=json.loads((OUT/'eda/summary.json').read_text())
    d=Document();md=[]
    def margins(section):
        section.page_width=Cm(21);section.page_height=Cm(29.7)
        section.left_margin=Cm(4);section.right_margin=Cm(3)
        section.top_margin=Cm(3);section.bottom_margin=Cm(3)
        section.footer_distance=Cm(1.5)
    margins(d.sections[0])
    for name in ['Normal','Heading 1','Heading 2','Caption','Footer']:
        s=d.styles[name];s.font.name='Times New Roman';s.font.size=Pt(12);s.font.color.rgb=RGBColor(0,0,0)
        fonts=s._element.get_or_add_rPr().find(qn('w:rFonts'))
        if fonts is None:
            fonts=OxmlElement('w:rFonts');s._element.get_or_add_rPr().append(fonts)
        for key in ['asciiTheme','hAnsiTheme','eastAsiaTheme','cstheme','csTheme']:
            fonts.attrib.pop(qn('w:'+key),None)
        for key in ['ascii','hAnsi','eastAsia','cs']:fonts.set(qn('w:'+key),'Times New Roman')
    norm=d.styles['Normal'].paragraph_format
    norm.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY;norm.first_line_indent=Cm(1.25)
    norm.line_spacing=1.5;norm.space_after=Pt(0);norm.space_before=Pt(0);norm.widow_control=True
    for name in ['Heading 1','Heading 2']:
        s=d.styles[name];s.font.bold=True
        f=s.paragraph_format;f.first_line_indent=Cm(0);f.keep_with_next=True
        f.space_before=Pt(6);f.space_after=Pt(3);f.line_spacing=1.15
    d.styles['Heading 1'].paragraph_format.alignment=WD_ALIGN_PARAGRAPH.CENTER
    d.styles['Heading 1'].paragraph_format.space_before=Pt(0)
    d.styles['Heading 1'].paragraph_format.space_after=Pt(10)
    for name in ['Caption','Footer']:
        f=d.styles[name].paragraph_format;f.first_line_indent=Cm(0);f.line_spacing=1
        f.alignment=WD_ALIGN_PARAGRAPH.CENTER
    d.core_properties.title='Proposal Awal Minggu 12 - Intelligent Predictive Maintenance System'
    d.core_properties.author='Kelompok 1, Kelas B, Institut Teknologi Kalimantan'
    d.core_properties.subject='Tugas Besar Kecerdasan Buatan TE2514031'
    def p(text,indent=True,size=None):
        x=d.add_paragraph(text)
        if not indent:x.paragraph_format.first_line_indent=Cm(0)
        if size:
            x.paragraph_format.line_spacing=1
            for r in x.runs:r.font.size=Pt(size)
        md.append(text);return x
    def center(text,size=12,bold=False,after=0,before=0):
        x=d.add_paragraph();x.alignment=WD_ALIGN_PARAGRAPH.CENTER
        f=x.paragraph_format;f.first_line_indent=Cm(0);f.line_spacing=1.25;f.space_after=Pt(after);f.space_before=Pt(before)
        r=x.add_run(text);r.font.size=Pt(size);r.bold=bold
        md.append(text);return x
    def h(text,level=2):
        d.add_paragraph(text,style='Heading '+str(level));md.append('#'*level+' '+text)
    def chapter(roman,title):h('BAB '+roman+'\n'+title,1)
    def table(title,rows,widths):
        x=d.add_paragraph(title,style='Caption');x.paragraph_format.keep_with_next=True
        x.paragraph_format.space_before=Pt(4);x.paragraph_format.space_after=Pt(4)
        for r in x.runs:r.font.size=Pt(10.5);r.bold=False
        t=d.add_table(rows=1,cols=len(rows[0]));t.autofit=False;t.style='Table Grid'
        for c,w in zip(t.columns,widths):c.width=Cm(w)
        for i,row in enumerate(rows):
            cells=t.rows[0].cells if i==0 else t.add_row().cells
            for cell,value,w in zip(cells,row,widths):
                cell.width=Cm(w);cell.text=str(value)
                for par in cell.paragraphs:
                    f=par.paragraph_format;f.first_line_indent=Cm(0);f.line_spacing=1
                    f.space_before=Pt(2);f.space_after=Pt(2);f.alignment=WD_ALIGN_PARAGRAPH.LEFT
                    for r in par.runs:r.font.size=Pt(10.5);r.bold=i==0
            pr=t.rows[i]._tr.get_or_add_trPr();pr.append(OxmlElement('w:cantSplit'))
            if i==0:pr.append(OxmlElement('w:tblHeader'))
        md.append(title+'\n\n'+'\n'.join('| '+' | '.join(map(str,row))+' |' for row in rows[:1])+'\n|'+'|'.join(['---']*len(rows[0]))+'|\n'+'\n'.join('| '+' | '.join(map(str,row))+' |' for row in rows[1:]))

    # Halaman 1: sampul.
    center('PROPOSAL AWAL TUGAS BESAR\nKECERDASAN BUATAN',14,True,after=26)
    center('INTELLIGENT PREDICTIVE MAINTENANCE SYSTEM',14,True,after=12)
    center('Progres Minggu ke-12\nSemester Gasal 2026/2027',12,after=36)
    center('Disusun untuk memenuhi tugas mata kuliah\nKecerdasan Buatan (TE2514031)',12,after=22)
    center('Dosen Pengampu:\nIr. Muhammad Ridho Dewanto, S.T., M.T.',12,after=32)
    center('Disusun oleh:\nKelompok 1 — Kelas B',12,True,after=12)
    t=d.add_table(rows=0,cols=2);t.autofit=False
    t.columns[0].width=Cm(9);t.columns[1].width=Cm(5)
    for person in cfg['members']:
        cells=t.add_row().cells;cells[0].text=person['name'];cells[1].text=person['nim']
        cells[0].width=Cm(9);cells[1].width=Cm(5)
        for cell in cells:
            for par in cell.paragraphs:
                par.paragraph_format.first_line_indent=Cm(0);par.paragraph_format.line_spacing=1.25
        md.append(person['name']+' — '+person['nim'])
    center('INSTITUT TEKNOLOGI KALIMANTAN\n2026',14,True,before=48)

    sec=d.add_section(WD_SECTION.NEW_PAGE);margins(sec)
    sec.footer.is_linked_to_previous=False
    num=OxmlElement('w:pgNumType');num.set(qn('w:fmt'),'decimal');num.set(qn('w:start'),'1');sec._sectPr.append(num)
    footer=sec.footer.paragraphs[0];footer.style=d.styles['Footer']
    field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');footer._p.append(field)

    # Halaman 2: alasan, masalah, dan tujuan yang spesifik pada topik kelompok.
    chapter('I','PENDAHULUAN')
    h('1.1 Latar Belakang')
    p('Kondisi mesin dapat dilihat dari beberapa variabel operasi, seperti suhu, kecepatan putaran, torsi, dan keausan alat. Data tersebut dapat digunakan untuk mengenali kondisi yang berkaitan dengan kegagalan mesin. Pada tugas besar ini, kelompok kami mengerjakan Intelligent Predictive Maintenance System untuk memprediksi status kegagalan dan, pada tahap akhir, memberikan prioritas perawatan.')
    p('Data yang digunakan adalah AI4I 2020 Predictive Maintenance Dataset dari UCI. Dataset ini berisi 10.000 pengamatan sintetis, dengan 339 kasus kegagalan (UCI Machine Learning Repository, 2020). Karena jumlah kegagalan jauh lebih sedikit daripada kondisi normal, model yang sering menjawab “tidak gagal” dapat memperoleh akurasi tinggi. Oleh sebab itu, kemampuan model mendeteksi kegagalan juga perlu dilihat dari precision, recall, dan F1-score.')
    h('1.2 Rumusan Masalah')
    p('Bagaimana menyiapkan data agar label kegagalan tidak ikut menjadi masukan model, dan bagaimana hasil awal Neural Network dalam mengenali kegagalan pada data yang tidak seimbang?',False)
    h('1.3 Tujuan Pengerjaan')
    p('Pada minggu ke-12, pengerjaan ditujukan untuk memahami isi dataset, menetapkan fitur dan target, menyiapkan pembagian data, serta melatih baseline Neural Network. Selain itu, disiapkan kerangka dashboard Streamlit dan rencana integrasi GA, PSO, serta Fuzzy Logic untuk minggu berikutnya.')
    h('1.4 Batasan Masalah')
    p('Target yang dipakai adalah Machine failure dengan dua kelas, yaitu gagal dan tidak gagal. Model memprediksi status pada satu pengamatan, bukan waktu menuju kerusakan atau sisa umur mesin. Data bersifat sintetis sehingga hasilnya belum dapat langsung diterapkan pada mesin nyata. Progres minggu ke-12 dibatasi pada data, baseline MLP, dan dashboard awal; GA, PSO, Fuzzy, serta deployment publik masih menjadi pekerjaan selanjutnya.')

    # Halaman 3: metode yang benar-benar dipakai dan rancangan integrasi.
    d.add_page_break();chapter('II','METODE PENGERJAAN')
    h('2.1 Data dan Variabel yang Digunakan')
    p('Dari 14 kolom dataset, enam variabel dipakai sebagai masukan dan satu kolom sebagai target. Rinciannya disajikan pada Tabel 1.')
    table('Tabel 1. Variabel masukan dan target',[
        ['Variabel','Jenis data/satuan','Keterangan'],
        ['Type','Kategori H, L, M','Jenis/kualitas produk'],
        ['Air temperature','Numerik, K','Suhu udara'],
        ['Process temperature','Numerik, K','Suhu proses'],
        ['Rotational speed','Numerik, rpm','Kecepatan rotasi'],
        ['Torque','Numerik, Nm','Torsi'],
        ['Tool wear','Numerik, menit','Keausan alat'],
        ['Machine failure','Biner, 0 atau 1','Target kegagalan']],[5.1,4.1,4.8])
    p('UDI dan Product ID tidak digunakan sebagai fitur. Kolom TWF, HDF, PWF, OSF, dan RNF juga dikeluarkan karena merupakan label jenis kegagalan yang dapat membocorkan informasi target.')
    h('2.2 Pembagian Data dan Preprocessing')
    p('Data dibagi berdasarkan urutan UDI: 6.000 baris untuk train, 2.000 untuk validation, dan 2.000 untuk test. UDI hanya menjadi acuan urutan, bukan timestamp yang terverifikasi. Imputer dan StandardScaler dihitung dari train saja. Type diubah menjadi tiga kolom one-hot, sehingga NN menerima delapan input. Ketidakseimbangan kelas ditangani dengan bobot kelas dari train. Test disimpan untuk evaluasi akhir.')
    h('2.3 Model Awal dan Rancangan Sistem')
    p('Baseline menggunakan MLP dengan susunan 8–32–16–1, aktivasi ReLU pada hidden layer, dan output sigmoid. Pelatihan memakai Adam, learning rate 0,001, batch size 128, maksimum 150 epoch, dan seed 42. Checkpoint dipilih dari log loss validation; batas klasifikasi ditetapkan 0,5.')
    p('Pada sistem akhir, GA akan memilih fitur, PSO mengoptimalkan hyperparameter NN, dan Fuzzy mengubah hasil prediksi menjadi prioritas Normal, Inspection, Maintenance, atau Critical. Alur yang direncanakan adalah:')
    center('Data → Preprocessing → GA → PSO → NN → Fuzzy → Streamlit',10.5,False,before=3)

    # Halaman 4: bukti progres, pembagian peran, dan tindak lanjut.
    d.add_page_break();chapter('III','PROGRES AWAL DAN RENCANA KERJA')
    h('3.1 Hasil Sementara Minggu ke-12')
    p(f"Pemeriksaan data menunjukkan {eda['class_counts']['0']:,} non-failure dan {eda['class_counts']['1']} failure, tanpa nilai kosong maupun duplikasi baris. Hasil baseline pada data validation ditunjukkan pada Tabel 2.".replace('9,661','9.661'))
    def percent(value):return f'{value*100:.2f}%'.replace('.',',')
    v=metric['validation'];cm=v['confusion_matrix']
    table('Tabel 2. Evaluasi baseline MLP pada validation',[
        ['Accuracy','Precision','Recall','F1-score'],
        [percent(v['accuracy']),percent(v['precision']),percent(v['recall']),f"{v['f1']:.4f}".replace('.',',')]
    ],[3.5,3.5,3.5,3.5])
    p(f"Confusion matrix berisi TN={cm[0][0]:,}, FP={cm[0][1]}, FN={cm[1][0]}, dan TP={cm[1][1]}. Sebanyak 25 dari 45 kegagalan terdeteksi, tetapi masih ada 58 false alarm. Deteksi kegagalan masih perlu diperbaiki.".replace('1,897','1.897'))
    p('Script, model, dan bukti dashboard tersedia di repository. Prediksi manual/CSV berjalan lokal; aplikasi belum di-deploy publik.')
    h('3.2 Pembagian Tugas')
    table('Tabel 3. Usulan pembagian kerja kelompok',[
        ['Anggota','Tanggung jawab'],
        ['Putri Cahaya Lestari','Pengolahan data, EDA, dan laporan'],
        ['Hendra Firmansyah','GA dan seleksi fitur'],
        ['Nur Rahmad','Baseline NN, PSO, dan evaluasi'],
        ['Ricky Alfian Ronaldo','Fuzzy, dashboard, dan deployment']],[6.3,7.7])
    p('Pembagian kerja ini masih perlu disepakati bersama.',False,size=10)
    h('3.3 Rencana Selanjutnya dan Risiko')
    p('Pengerjaan dilanjutkan dengan GA pada minggu ke-13, PSO pada minggu ke-14, Fuzzy dan deployment pada minggu ke-15, serta laporan dan demo pada minggu ke-16. Risiko jumlah failure yang sedikit dan overfitting validation ditangani melalui pembatasan percobaan, beberapa seed GA/PSO, dan test yang tetap terpisah.')
    h('DAFTAR PUSTAKA')
    for ref in [
        'UCI Machine Learning Repository. (2020). AI4I 2020 Predictive Maintenance Dataset. https://doi.org/10.24432/C5HS5C.',
        'Panduan Deliverables Tugas Besar Kecerdasan Buatan Minggu 12–16. (2026). Dokumen mata kuliah TE2514031, Gasal 2026/2027.',
        'Tugas Besar Kecerdasan Buatan: 16 Kelompok UCI Streamlit. (2026). Dokumen mata kuliah TE2514031, Gasal 2026/2027.'
    ]:
        x=p(ref,False,size=9.5);x.paragraph_format.space_after=Pt(3)
    path=OUT/'W12_Proposal_EDA.docx';d.save(path)
    (OUT/'W12_Proposal_EDA.md').write_text('\n\n'.join(md),encoding='utf-8')
    print('Word:',path)
    office=shutil.which('soffice') or shutil.which('libreoffice')
    if office:
        with tempfile.TemporaryDirectory(prefix='w12-office-') as temp:
            profile=(Path(temp)/'profile').as_uri()
            env=os.environ.copy();env.setdefault('XDG_CACHE_HOME',str(Path(temp)/'cache'))
            subprocess.run([office,'-env:UserInstallation='+profile,'--headless','--convert-to','pdf','--outdir',str(OUT),str(path)],check=True,env=env)
        print('PDF:',OUT/'W12_Proposal_EDA.pdf')
    else:
        print('LibreOffice tidak tersedia. Buka Word yang baru dibuat, lalu ekspor sebagai PDF.')

if __name__=='__main__':main()
