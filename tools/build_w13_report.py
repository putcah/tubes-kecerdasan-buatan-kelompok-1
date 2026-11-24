"""Membuat laporan Word W13 dari hasil percobaan yang tersimpan."""
import json
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
W13 = ROOT / 'W13'


def number(value, places=4):
    return f'{value:.{places}f}'.replace('.', ',')


def table(doc, rows, widths):
    layout = doc.add_table(rows=0, cols=len(widths))
    layout.style = 'Table Grid'
    layout.autofit = False
    for col, width in zip(layout.columns, widths):
        col.width = Cm(width)
    for index, row in enumerate(rows):
        item = layout.add_row()
        item._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
        for cell, value, width in zip(item.cells, row, widths):
            cell.width = Cm(width)
            cell.text = str(value)
            for para in cell.paragraphs:
                para.paragraph_format.line_spacing = 1
                para.paragraph_format.space_before = Pt(3)
                para.paragraph_format.space_after = Pt(3)
                for run in para.runs:
                    run.font.size = Pt(10.5)
                    run.bold = index == 0


def main():
    report = json.loads((W13 / 'hasil' / 'summary.json').read_text(encoding='utf-8'))
    project = json.loads((ROOT / 'project.json').read_text(encoding='utf-8'))
    best = report['selected']
    baseline, ga = (report['aggregate'][key] for key in ('Baseline NN', 'GA + NN'))
    reduced_run = next((run for run in report['runs'] if len(run['ga']['features']) < 6), None)
    group = Document()
    section = group.sections[0]
    section.page_width, section.page_height = Cm(21), Cm(29.7)
    section.left_margin = section.right_margin = section.top_margin = section.bottom_margin = Cm(2.5)
    section.footer_distance = Cm(1.5)
    for name, size in [('Normal', 12), ('Heading 1', 12), ('Caption', 10.5)]:
        style = group.styles[name]
        style.font.name = 'Times New Roman'
        style.font.size = Pt(size)
        style.font.color.rgb = RGBColor(0, 0, 0)
        fonts = style._element.get_or_add_rPr().find(qn('w:rFonts'))
        for attribute in ('asciiTheme', 'hAnsiTheme', 'eastAsiaTheme', 'cstheme'):
            fonts.attrib.pop(qn('w:' + attribute), None)
    normal = group.styles['Normal'].paragraph_format
    normal.line_spacing = 1.15
    normal.space_after = Pt(6)
    normal.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    page_number = OxmlElement('w:fldSimple')
    page_number.set(qn('w:instr'), 'PAGE')
    footer._p.append(page_number)

    def center(text, bold=False, size=12):
        paragraph = group.add_paragraph()
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = paragraph.add_run(text)
        run.bold = bold
        run.font.size = Pt(size)

    def heading(text):
        group.add_paragraph(text, 'Heading 1')

    def paragraph(text):
        group.add_paragraph(text)

    group.core_properties.title = 'Laporan Progres Minggu 13: Seleksi Fitur dengan Genetic Algorithm'
    group.core_properties.author = 'Kelompok 1, Kelas B, Institut Teknologi Kalimantan'
    center('Laporan Progres Minggu 13', bold=True, size=14)
    center('Intelligent Predictive Maintenance System', bold=True)
    center('Tugas Besar Kecerdasan Buatan')
    center('Kelompok 1, Kelas B, Institut Teknologi Kalimantan')
    table(group, [['Nama', 'NIM']] + [[m['name'], m['nim']] for m in project['members']], [10, 6])

    heading('1. Tujuan Pengerjaan')
    paragraph('Pada minggu ke-12, model awal MLP mengenali 25 dari 45 kegagalan pada data validasi. '
              'Pada minggu ini, kami menguji apakah pemilihan fitur dengan Genetic Algorithm (GA) '
              'dapat memperbaiki hasil deteksi atau mengurangi jumlah masukan yang diperlukan. '
              'Pengaruh seleksi fitur dinilai dengan membandingkan GA + NN dan baseline enam fitur.')
    heading('2. Cara Seleksi Fitur')
    paragraph('Kromosom terdiri atas enam bit. Urutannya adalah Type, suhu udara, suhu proses, kecepatan '
              'rotasi, torsi, dan keausan alat. Bit 1 berarti variabel dipakai dan bit 0 berarti dikeluarkan. '
              'Semua kolom indikator milik Type dipilih bersama. Jika mutasi menghasilkan kromosom kosong, '
              'satu bit diaktifkan secara acak.')
    paragraph('Setiap subset dinilai menggunakan F1 pada data validasi. Penalti yang ditetapkan sebelum '
              'percobaan memberi keuntungan pada subset kecil jika kemampuan deteksinya hampir sama.')
    center('Fitness = F1 validasi − 0,02 × (jumlah fitur terpilih / 6)')
    paragraph('Populasi awal berisi 20 subset unik yang diambil secara acak. Setiap induk dipilih dari '
              'turnamen tiga kandidat, kemudian dilakukan persilangan satu titik dengan peluang 0,8 '
              'dan mutasi setiap bit dengan peluang 1/6. Dua kandidat terbaik diteruskan ke generasi '
              'berikutnya. Pencarian berhenti setelah 15 generasi. Skor kromosom yang sudah dinilai '
              'dipakai kembali dalam percobaan yang sama.')

    group.add_page_break()
    heading('3. Kondisi Percobaan dan Konvergensi')
    paragraph('Pembagian data mengikuti W12, yakni 6.000 baris untuk pelatihan, 2.000 untuk validasi, '
              'dan 2.000 untuk pengujian akhir, seluruhnya berdasarkan urutan UDI. Pengolahan awal dan '
              'bobot kelas dihitung dari data pelatihan. Data validasi dipakai untuk memilih checkpoint '
              'dan menilai fitness. Data uji tetap disimpan untuk evaluasi akhir.')
    paragraph('Baseline dan GA + NN dilatih ulang pada seed 11, 22, dan 33. Untuk setiap pasangan, '
              'MLP memakai dua lapisan tersembunyi berukuran 32 dan 16, Adam, learning rate 0,001, '
              'batch size 128, L2 sebesar 0,0001, dan batas prediksi 0,5. Pelatihan berjalan hingga 150 epoch dengan '
              'penghentian jika log loss validasi tidak membaik selama 20 epoch.')
    picture = group.add_paragraph()
    picture.alignment = WD_ALIGN_PARAGRAPH.CENTER
    picture.add_run().add_picture(str(W13 / 'hasil' / 'convergence.png'), width=Cm(15.7))
    center('Gambar 1. Perubahan fitness terbaik pada setiap seed.', size=10.5)
    table(group, [['Seed', 'Kromosom akhir', 'F1 validasi', 'Fitness', 'Subset unik']] + [
        [run['seed'], run['ga']['chromosome'], number(run['ga']['validation']['f1']),
         number(run['ga']['fitness']), run['ga']['unique_evaluations']]
        for run in report['runs']
    ], [2, 3.4, 3.2, 3.2, 4.2])
    values = report['fitness']
    paragraph(f"Fitness terbaik dari tiga percobaan adalah {number(values['best'])}, "
              f"dengan rata-rata {number(values['mean'])} dan simpangan baku {number(values['std'])}. "
              'Jumlah subset unik menunjukkan berapa banyak kandidat yang benar-benar dilatih pada setiap seed.')

    group.add_page_break()
    heading('4. Fitur Terpilih dan Perbandingan Model')
    paragraph(f"Kandidat dengan fitness tertinggi diperoleh pada seed {best['seed']} dengan "
              f"kromosom {best['chromosome']}. Tabel berikut menunjukkan fitur yang dipakai pada kandidat "
              'tersebut. Angka rata-rata di tabel perbandingan dihitung dari subset terbaik masing-masing seed.')
    feature_rows = [['Variabel', 'Baseline', 'GA terbaik']]
    if reduced_run:
        feature_rows[0].append(f"GA seed {reduced_run['seed']}")
    for feature in report['chromosome_order']:
        row = [feature, 'Dipakai', 'Dipakai' if feature in best['features'] else 'Dikeluarkan']
        if reduced_run:
            row.append('Dipakai' if feature in reduced_run['ga']['features'] else 'Dikeluarkan')
        feature_rows.append(row)
    table(group, feature_rows, [6.4, 2.8, 3.4, 3.4] if reduced_run else [7.8, 3.2, 5])
    paragraph('')
    model_rows = [['Ukuran validasi', 'Baseline NN', 'GA + NN']]
    for key, title in [('accuracy', 'Accuracy'), ('precision', 'Precision'), ('recall', 'Recall'),
                       ('f1', 'F1-score'), ('feature_count', 'Jumlah fitur rata-rata'),
                       ('fit_seconds', 'Waktu latih satu model (detik)'),
                       ('search_seconds', 'Waktu pencarian GA (detik)')]:
        original = 'Tidak ada' if key == 'search_seconds' else number(
            baseline[key]['mean'], 2 if key.endswith('seconds') or key == 'feature_count' else 4
        )
        model_rows.append([title, original, number(
            ga[key]['mean'], 2 if key.endswith('seconds') or key == 'feature_count' else 4
        )])
    table(group, model_rows, [8, 4, 4])
    delta = ga['f1']['mean'] - baseline['f1']['mean']
    direction = 'meningkat' if delta > 0 else 'menurun' if delta < 0 else 'tetap'
    paragraph(f"Rata-rata F1 validasi {direction} dari {number(baseline['f1']['mean'])} menjadi "
              f"{number(ga['f1']['mean'])}. Simpangan bakunya adalah {number(baseline['f1']['std'])} "
              f"untuk baseline dan {number(ga['f1']['std'])} untuk GA + NN. Waktu latih menunjukkan "
              'durasi satu kali pelatihan, sedangkan waktu pencarian mencakup seluruh kandidat. '
              'Waktu diukur pada lingkungan yang sama dengan tiga seed dijalankan paralel.')

    group.add_page_break()
    heading('5. Pembahasan dan Tindak Lanjut')
    if reduced_run:
        reduced = reduced_run['ga']
        omitted = [feature for feature in report['chromosome_order'] if feature not in reduced['features']]
        reduced_metrics = reduced['validation']
        base_metrics = reduced_run['baseline']['validation']
        paragraph(f"Pada seed {reduced_run['seed']}, GA mengeluarkan {' dan '.join(omitted)}. "
                  f"F1 validasi naik dari {number(base_metrics['f1'])} menjadi {number(reduced_metrics['f1'])}, "
                  f"sementara recall turun dari {number(base_metrics['recall'])} menjadi {number(reduced_metrics['recall'])}. "
                  "Perubahan tersebut menunjukkan bahwa kenaikan F1 dapat disertai lebih banyak kegagalan yang terlewat. "
                  "Hasil per seed digunakan untuk melihat apakah pengurangan fitur terjadi secara konsisten.")
    tn, fp = best['validation']['confusion_matrix'][0]
    fn, tp = best['validation']['confusion_matrix'][1]
    paragraph(f"Pada kandidat GA terbaik, {tp} dari {tp + fn} kegagalan berhasil dikenali, sedangkan "
              f"{fn} lainnya terlewat. Model memunculkan {fp} alarm keliru dan mengenali {tn} kondisi "
              'tidak gagal dengan benar. Jumlah tersebut membantu membaca hasil F1 bersama konsekuensi '
              'dari kesalahan prediksi.')
    paragraph('Hasil minggu ini menunjukkan kinerja pada data validasi yang turut dipakai untuk memilih '
              'subset. Karena itu, model yang terpilih dapat terlihat lebih baik pada data tersebut. '
              'Pengujian akhir diperlukan setelah konfigurasi model ditetapkan agar kinerjanya dapat '
              'dinilai pada data yang belum dipakai selama pengembangan.')
    paragraph('Dashboard menampilkan kurva konvergensi, fitur terpilih, dan hasil tiga seed melalui '
              'menu GA Optimization. Menu Model Comparison merangkum baseline dan GA + NN. '
              'Tahap berikutnya akan menguji pengaturan Neural Network dengan PSO sebelum hasilnya '
              'dihubungkan dengan Fuzzy Logic.')
    heading('6. Berkas dan Reproduksi')
    paragraph('Jalankan python -m src.ga_feature_selection --workers 3 setelah memasang dependensi '
              'dari requirements.txt. Ringkasan, hasil per seed, daftar subset yang dilatih, serta model '
              'GA tersimpan pada folder W13/hasil. Gunakan python -m streamlit run app.py untuk membuka dashboard lokal.')
    paragraph(project['repository_url'])
    heading('Sumber')
    paragraph('UCI Machine Learning Repository. (2020). AI4I 2020 Predictive Maintenance Dataset. '
              'https://doi.org/10.24432/C5HS5C')
    paragraph('Kelompok 1 Kelas B. (2026). Proposal Progres Minggu 12. Institut Teknologi Kalimantan.')
    group.save(W13 / 'W13_GA_Progress.docx')


if __name__ == '__main__':
    main()
