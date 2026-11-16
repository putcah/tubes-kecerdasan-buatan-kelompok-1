"""Memindahkan isi PDF ke gaya dokumen Word contoh, tanpa merangkum isinya.

python tools/format_pdf_as_word.py --source-pdf sumber.pdf --template contoh.docx \
    --output hasil.docx --assets-dir work/aset
Keperluan tambahan: PyMuPDF, pdfplumber, python-docx, dan LibreOffice untuk PDF.
"""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import fitz
import pdfplumber
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm,Pt

def clean(text):
    return re.sub(r'\s+',' ',text).strip()

def extract(pdf_path,assets):
    events=[]
    pdf=fitz.open(pdf_path)
    with pdfplumber.open(pdf_path) as layout:
        for index,page in enumerate(pdf):
            tables=layout.pages[index].find_tables()
            for table in tables:
                rows=[]
                for row in table.rows:
                    rows.append([clean(page.get_textbox(fitz.Rect(cell))) if cell else '' for cell in row.cells])
                cells=table.rows[0].cells
                widths=[cell[2]-cell[0] for cell in cells]
                events.append({'page':index,'y':table.bbox[1],'type':'table','rows':rows,'widths':widths})
            for block in page.get_text('dict')['blocks']:
                if block['type']!=0:continue
                box=fitz.Rect(block['bbox'])
                if box.y0>page.rect.height-60:continue
                if index==0 and box.y0<140:continue
                if any(fitz.Rect(table.bbox).contains(fitz.Point((box.x0+box.x1)/2,(box.y0+box.y1)/2)) for table in tables):continue
                lines=[];spans=[]
                for line in block['lines']:
                    lines.append(''.join(span['text'] for span in line['spans']))
                    for span in line['spans']:
                        spans.append({'text':span['text'],'bold':'bold' in span['font'].lower()})
                    spans.append({'text':' ','bold':False})
                text=clean(' '.join(lines))
                maximum=max(span['size'] for line in block['lines'] for span in line['spans'])
                events.append({'page':index,'y':box.y0,'type':'heading' if maximum>=11.5 else 'paragraph',
                               'text':text,'small':maximum<8,'spans':spans,'lines':lines})
            for image in page.get_images(full=True):
                xref=image[0]
                content=pdf.extract_image(xref)
                destination=assets/f'figura_pagina_{index+1}_{xref}.{content["ext"]}'
                destination.write_bytes(content['image'])
                for box in page.get_image_rects(xref):
                    events.append({'page':index,'y':box.y0,'type':'image','path':str(destination)})
    return sorted(events,key=lambda value:(value['page'],value['y']))

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--source-pdf',type=Path,required=True)
    parser.add_argument('--template',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--assets-dir',type=Path,required=True)
    args=parser.parse_args()
    args.assets_dir.mkdir(parents=True,exist_ok=True)
    events=extract(args.source_pdf,args.assets_dir)
    (args.assets_dir/'content_manifest.json').write_text(json.dumps(events,ensure_ascii=False,indent=2),encoding='utf-8')
    doc=Document(args.template)
    # Pertahankan judul, identitas anggota, pengampu, gaya, margin, dan footer contoh.
    body=doc._element.body;cut=False
    for element in list(body):
        if element.tag==qn('w:sectPr'):continue
        if element.tag==qn('w:p') and ''.join(element.itertext()).startswith('1. Gambaran Tugas'):
            cut=True
        if cut:body.remove(element)
    if not cut:raise ValueError('Bagian isi awal pada template tidak ditemukan; tidak ada isi yang dihapus.')
    markdown=[]
    doc.core_properties.title='Proposal Progres Minggu 12 - Isi PDF dalam Format Word'
    doc.core_properties.subject='Intelligent Predictive Maintenance System - Kelompok 1 Kelas B'
    width=16.0
    table_no=0;image_no=0;reference_mode=False
    table_titles=['Rancangan arsitektur','Usulan pembagian peran','Variabel dan peran dalam model',
                  'Pembagian data','Perbandingan model pada validation','Rencana pengerjaan minggu 13–16']
    for event in events:
        kind=event['type']
        if kind=='heading':
            title=event['text'];heading=doc.add_paragraph(title,style='Heading 2');markdown.append('## '+title)
            if title.startswith('6. '):heading.paragraph_format.page_break_before=True
            reference_mode=title=='Sumber'
        elif kind=='paragraph':
            if reference_mode:
                entries=re.split(r'(?m)(?=^\d+\.\s)','\n'.join(event['lines']))
                for entry in entries:
                    if not clean(entry):continue
                    p=doc.add_paragraph(clean(entry));p.paragraph_format.line_spacing=1
                    p.alignment=WD_ALIGN_PARAGRAPH.LEFT
                    p.paragraph_format.space_after=Pt(3)
                    for run in p.runs:run.font.size=Pt(9.5)
                    markdown.append(clean(entry))
                continue
            p=doc.add_paragraph()
            for span in event['spans']:
                run=p.add_run(span['text']);run.bold=span['bold']
                if event['small']:run.font.size=Pt(10)
            if event['small']:p.paragraph_format.line_spacing=1
            markdown.append(event['text'])
        elif kind=='table':
            caption=doc.add_paragraph(table_titles[table_no],style='Caption')
            caption.paragraph_format.keep_with_next=True
            caption.paragraph_format.space_before=Pt(4);caption.paragraph_format.space_after=Pt(4)
            for run in caption.runs:run.font.size=Pt(10.5);run.bold=False
            rows=event['rows'];proportions=event['widths'];total=sum(proportions)
            widths=[width*value/total for value in proportions]
            table=doc.add_table(rows=1,cols=len(rows[0]));table.autofit=False;table.style='Table Grid'
            for column,w in zip(table.columns,widths):column.width=Cm(w)
            for i,row in enumerate(rows):
                cells=table.rows[0].cells if i==0 else table.add_row().cells
                for cell,text,w in zip(cells,row,widths):
                    cell.width=Cm(w);cell.text=text
                    for paragraph in cell.paragraphs:
                        f=paragraph.paragraph_format;f.first_line_indent=Cm(0);f.line_spacing=1
                        f.alignment=WD_ALIGN_PARAGRAPH.LEFT;f.space_before=Pt(2);f.space_after=Pt(2)
                        for run in paragraph.runs:run.font.size=Pt(10.5);run.bold=i==0
                props=table.rows[i]._tr.get_or_add_trPr();props.append(OxmlElement('w:cantSplit'))
                if i==0:props.append(OxmlElement('w:tblHeader'))
            table_no+=1
            markdown.append('| '+' | '.join(rows[0])+' |\n|'+'|'.join(['---']*len(rows[0]))+'|\n'+
                            '\n'.join('| '+' | '.join(row)+' |' for row in rows[1:]))
        elif kind=='image':
            image_no+=1
            p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.keep_with_next=True;p.paragraph_format.line_spacing=1
            p.add_run().add_picture(event['path'],width=Cm(16))
            title='Distribusi target dan proporsi failure menurut urutan UDI' if image_no==1 else 'Kurva loss dan confusion matrix baseline MLP'
            caption=doc.add_paragraph(f'Gambar {image_no}. '+title,style='Caption')
            caption.paragraph_format.space_after=Pt(5)
            for run in caption.runs:run.font.size=Pt(10.5);run.bold=False
            markdown.append(f'![{title}]({Path(event["path"]).name})')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    doc.save(args.output)
    (args.assets_dir/'isi_terformat.md').write_text('\n\n'.join(markdown),encoding='utf-8')
    print('Word:',args.output,'| tables:',table_no,'| figures:',image_no)
    office=shutil.which('soffice') or shutil.which('libreoffice')
    if office:
        with tempfile.TemporaryDirectory(prefix='proposal-pdf-') as temp:
            env=os.environ.copy();env.setdefault('XDG_CACHE_HOME',str(Path(temp)/'cache'))
            subprocess.run([office,'-env:UserInstallation='+(Path(temp)/'profile').as_uri(),'--headless',
                            '--convert-to','pdf','--outdir',str(args.output.parent),str(args.output)],check=True,env=env)
    else:print('Ekspor PDF melalui Word/LibreOffice setelah membuka dokumen hasil.')

if __name__=='__main__':main()
