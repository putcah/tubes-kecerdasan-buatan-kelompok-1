"""Proposal progres W12 ringkas tanpa BAB dan sampul terpisah.

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
        section.left_margin=Cm(2.5);section.right_margin=Cm(2.5)
        section.top_margin=Cm(2.5);section.bottom_margin=Cm(2.5)
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
    norm.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY;norm.first_line_indent=Cm(0)
    norm.line_spacing=1.15;norm.space_after=Pt(5);norm.space_before=Pt(0);norm.widow_control=True
    for name in ['Heading 1','Heading 2']:
        s=d.styles[name];s.font.bold=True
        f=s.paragraph_format;f.first_line_indent=Cm(0);f.keep_with_next=True
        f.space_before=Pt(8);f.space_after=Pt(4);f.line_spacing=1.15
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

    center('Proposal Progres Minggu 12',14,True,after=3)
    center('Tugas Besar Kecerdasan Buatan\nIntelligent Predictive Maintenance System',12,True,after=4)
    center('Kelompok 1 · Kelas B · Institut Teknologi Kalimantan',11,after=4)
    t=d.add_table(rows=0,cols=2);t.autofit=False
    t.columns[0].width=Cm(10);t.columns[1].width=Cm(6)
    for person in cfg['members']:
        cells=t.add_row().cells;cells[0].text=person['name'];cells[1].text=person['nim']
        cells[0].width=Cm(10);cells[1].width=Cm(6)
        for cell in cells:
            for par in cell.paragraphs:
                par.paragraph_format.first_line_indent=Cm(0);par.paragraph_format.line_spacing=1
                par.paragraph_format.space_after=Pt(1)
                for run in par.runs:run.font.size=Pt(10.5)
        md.append(person['name']+' — '+person['nim'])
    center('Pengampu: Ir. Muhammad Ridho Dewanto, S.T., M.T.\nTE2514031 · Semester Gasal 2026/2027',10,after=3,before=3)

    sec=d.sections[0]
    num=OxmlElement('w:pgNumType');num.set(qn('w:fmt'),'decimal');num.set(qn('w:start'),'1');sec._sectPr.append(num)
    footer=sec.footer.paragraphs[0];footer.style=d.styles['Footer']
    field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');footer._p.append(field)

    h('1. Gambaran Tugas')
    p('Kelompok kami mengerjakan prediksi kegagalan mesin menggunakan data suhu, putaran, torsi, dan keausan alat. Hasil prediksi nantinya ditampilkan di dashboard Streamlit dan digunakan untuk membantu menentukan prioritas perawatan. Untuk progres minggu 12, fokus kami masih pada memahami data, menyiapkan pengolahan data, dan membuat model Neural Network (NN) awal sebagai pembanding untuk percobaan berikutnya.')
    h('2. Data yang Dipakai')
    p('Kami menggunakan AI4I 2020 Predictive Maintenance Dataset dari UCI. Data ini berisi 10.000 baris dan 14 kolom. Enam variabel menjadi masukan model, sedangkan Machine failure menjadi target: 0 untuk tidak gagal dan 1 untuk gagal.')
    table('Variabel yang digunakan',[
        ['Variabel','Jenis data/satuan','Keterangan'],
        ['Type','Kategori H, L, M','Jenis/kualitas produk'],
        ['Air temperature','Numerik, K','Suhu udara'],
        ['Process temperature','Numerik, K','Suhu proses'],
        ['Rotational speed','Numerik, rpm','Kecepatan rotasi'],
        ['Torque','Numerik, Nm','Torsi'],
        ['Tool wear','Numerik, menit','Keausan alat'],
        ['Machine failure','Biner, 0 atau 1','Target kegagalan']],[5.8,4.5,5.7])
    p('UDI dan Product ID tidak dijadikan input. TWF, HDF, PWF, OSF, dan RNF juga tidak dipakai karena sudah menunjukkan jenis kegagalan dan bisa membocorkan jawaban yang ingin diprediksi model. Data ini bersifat sintetis, sehingga hasilnya belum mewakili semua kondisi mesin nyata.')
    h('3. Cara Pengerjaan')
    p('Kami membagi data sesuai urutan UDI: 6.000 baris untuk train, 2.000 untuk validation, dan 2.000 untuk test. UDI hanya dipakai sebagai acuan urutan, bukan waktu pengukuran yang pasti. Imputer dan StandardScaler dihitung dari train saja. Type diubah menjadi tiga kolom one-hot, sehingga total input NN menjadi delapan. Bobot kelas juga dihitung dari train untuk membantu model memperhatikan kasus kegagalan.')
    p('Model awal memakai MLP 8–32–16–1 dengan ReLU dan output sigmoid. Pengaturannya adalah Adam, learning rate 0,001, batch size 128, maksimum 150 epoch, serta seed 42. Model terbaik dipilih dari log loss validation, dengan batas prediksi 0,5. Data test belum digunakan untuk memilih atau menilai model.')

    h('4. Hasil Sementara')
    p(f"Dari pemeriksaan awal, ada {eda['class_counts']['0']:,} baris tidak gagal dan {eda['class_counts']['1']} baris gagal. Tidak ditemukan nilai kosong atau baris duplikat. Berikut hasil model awal pada data validation.".replace('9,661','9.661'))
    def percent(value):return f'{value*100:.2f}%'.replace('.',',')
    v=metric['validation'];cm=v['confusion_matrix']
    table('Hasil baseline MLP',[
        ['Accuracy','Precision','Recall','F1-score'],
        [percent(v['accuracy']),percent(v['precision']),percent(v['recall']),f"{v['f1']:.4f}".replace('.',',')]
    ],[4,4,4,4])
    p(f"Confusion matrix-nya adalah TN={cm[0][0]:,}, FP={cm[0][1]}, FN={cm[1][0]}, dan TP={cm[1][1]}. Artinya, 25 dari 45 kasus kegagalan berhasil dikenali, tetapi 20 kasus masih terlewat dan ada 58 false alarm. Jadi, meskipun akurasinya tinggi, hasil deteksi kegagalannya masih perlu diperbaiki.".replace('1,897','1.897'))
    p('Script pengolahan data, model tersimpan, dan dashboard awal sudah tersedia di repository. Input manual dan unggah CSV sudah bisa menghasilkan prediksi secara lokal. Aplikasi belum di-deploy publik. Model ini memprediksi status kegagalan pada satu pengamatan, bukan sisa umur mesin.')
    h('5. Pembagian Tugas Awal')
    table('Usulan pembagian kerja',[
        ['Anggota','Tanggung jawab'],
        ['Putri Cahaya Lestari','Pengolahan data, EDA, dan laporan'],
        ['Hendra Firmansyah','GA dan seleksi fitur'],
        ['Nur Rahmad','Baseline NN, PSO, dan evaluasi'],
        ['Ricky Alfian Ronaldo','Fuzzy, dashboard, dan deployment']],[7,9])
    p('Pembagian kerja ini masih perlu disepakati bersama.',False,size=10)
    h('6. Rencana Selanjutnya')
    p('Minggu 13 akan difokuskan pada GA untuk memilih fitur. Minggu 14 dilanjutkan dengan PSO untuk mencari pengaturan NN dan membandingkan hasil model. Pada minggu 15, Fuzzy akan dipakai untuk menentukan prioritas Normal, Inspection, Maintenance, atau Critical, lalu dashboard di-deploy. Minggu 16 disiapkan untuk laporan akhir dan demo.')
    center('Data → Preprocessing → GA → PSO → NN → Fuzzy → Streamlit',10.5,False,before=2,after=3)
    p('Hal yang perlu diperhatikan adalah sedikitnya kasus kegagalan dan kemungkinan model terlalu menyesuaikan data validation. Karena itu, jumlah percobaan akan dibatasi dan dicatat, GA/PSO dijalankan dengan beberapa seed, dan data test tetap disimpan untuk evaluasi akhir.')
    h('Sumber')
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
