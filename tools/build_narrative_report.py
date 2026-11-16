"""Membuat laporan W12 dari narasi yang dapat disunting di proposal_narasi.json."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE
from docx.shared import Cm,Pt

ROOT=Path(__file__).resolve().parents[1]

def plain(text):
    return text.replace(' · ', ', ').replace('·', ',').replace('—', ',').replace('–',' sampai ')

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--template',type=Path,default=ROOT/'W12/W12_Proposal_EDA.docx')
    parser.add_argument('--output',type=Path,default=ROOT/'W12/W12_Proposal_EDA.docx')
    args=parser.parse_args()
    data=json.loads(Path(__file__).with_name('proposal_narasi.json').read_text())
    config=json.loads((ROOT/'project.json').read_text())
    doc=Document(args.template)
    found=False
    for element in list(doc._element.body):
        if element.tag==qn('w:sectPr'):continue
        if element.tag==qn('w:p'):
            text=''.join(element.itertext())
            if re.match(r'^1\.\s',text):found=True
        if found:doc._element.body.remove(element)
    if not found:raise ValueError('Awal isi pada template tidak ditemukan.')
    used_images={element.get(qn('r:embed')) for element in doc._element.iter() if element.get(qn('r:embed'))}
    for rel_id,rel in list(doc.part.rels.items()):
        if rel.reltype==RELATIONSHIP_TYPE.IMAGE and rel_id not in used_images:doc.part.drop_rel(rel_id)
    for paragraph in doc.paragraphs:
        for run in paragraph.runs:run.text=plain(run.text)
        if paragraph.text.startswith('Pengampu:'):
            for run in paragraph.runs:
                if '\n' in run.text:run.text=run.text.replace('\n',' (')+')'
    doc.core_properties.title='Proposal Progres Minggu 12: Intelligent Predictive Maintenance System'
    doc.core_properties.author='Kelompok 1, Kelas B, Institut Teknologi Kalimantan'
    markdown=['# Proposal Progres Minggu 12',
              'Tugas Besar Kecerdasan Buatan: Intelligent Predictive Maintenance System',
              'Kelompok 1, Kelas B, Institut Teknologi Kalimantan']
    markdown.extend(f"{member['name']} (NIM {member['nim']})" for member in config['members'])
    markdown.extend(['Pengampu: Ir. Muhammad Ridho Dewanto, S.T., M.T.','TE2514031, Semester Gasal 2026/2027'])
    for section in data['sections']:
        heading=doc.add_paragraph(section['heading'],style='Heading 2')
        markdown.append('## '+section['heading'])
        for item in section['content']:
            kind=item['type']
            if kind in ['paragraph','note','reference']:
                p=doc.add_paragraph(item['text'])
                if kind!='paragraph':
                    p.paragraph_format.line_spacing=Pt(11 if kind=='reference' else 12)
                    for run in p.runs:run.font.size=Pt(9.5 if kind=='reference' else 10)
                if kind=='reference':
                    p.alignment=WD_ALIGN_PARAGRAPH.LEFT
                    p.paragraph_format.space_after=Pt(3)
                    if item.get('url'):
                        link=OxmlElement('w:hyperlink')
                        link.set(qn('r:id'),doc.part.relate_to(item['url'],RELATIONSHIP_TYPE.HYPERLINK,is_external=True))
                        for run in list(p.runs):
                            p._p.remove(run._r);link.append(run._r)
                        p._p.append(link)
                markdown.append(f'[{item["text"]}]({item["url"]})' if item.get('url') else item['text'])
            elif kind=='table':
                cap=doc.add_paragraph(item['title'],style='Caption')
                cap.paragraph_format.keep_with_next=True
                cap.paragraph_format.space_before=Pt(4);cap.paragraph_format.space_after=Pt(4)
                for run in cap.runs:run.font.size=Pt(10.5);run.bold=False
                rows=item['rows'];widths=item['widths']
                table=doc.add_table(rows=1,cols=len(rows[0]));table.style='Table Grid';table.autofit=False
                for col,width in zip(table.columns,widths):col.width=Cm(width)
                for i,row in enumerate(rows):
                    cells=table.rows[0].cells if i==0 else table.add_row().cells
                    for cell,text,width in zip(cells,row,widths):
                        cell.width=Cm(width);cell.text=text
                        for p in cell.paragraphs:
                            f=p.paragraph_format;f.first_line_indent=Cm(0);f.line_spacing=1
                            f.space_before=Pt(2);f.space_after=Pt(2);f.alignment=WD_ALIGN_PARAGRAPH.LEFT
                            for run in p.runs:run.font.size=Pt(10 if section['heading'].startswith('8.') else 10.5);run.bold=i==0
                    props=table.rows[i]._tr.get_or_add_trPr();props.append(OxmlElement('w:cantSplit'))
                    if i==0:props.append(OxmlElement('w:tblHeader'))
                markdown.append('| '+' | '.join(rows[0])+' |\n|'+'|'.join(['---']*len(rows[0]))+'|\n'+
                                '\n'.join('| '+' | '.join(row)+' |' for row in rows[1:]))
            elif kind=='image':
                p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.keep_with_next=True;p.paragraph_format.line_spacing=1
                p.add_run().add_picture(str(ROOT/item['path']),width=Cm(14.5))
                p=doc.add_paragraph(item['caption'],style='Caption');p.paragraph_format.space_after=Pt(5)
                for run in p.runs:run.font.size=Pt(10.5);run.bold=False
                markdown.append(f'![{item["caption"]}]({os.path.relpath(ROOT/item["path"],args.output.parent)})')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    doc.save(args.output)
    args.output.with_suffix('.md').write_text('\n\n'.join(markdown)+'\n',encoding='utf-8')
    print('Word:',args.output)
    office=shutil.which('soffice') or shutil.which('libreoffice')
    if office:
        with tempfile.TemporaryDirectory(prefix='narasi-w12-') as temp:
            env=os.environ.copy();env.setdefault('XDG_CACHE_HOME',str(Path(temp)/'cache'))
            subprocess.run([office,'-env:UserInstallation='+(Path(temp)/'profile').as_uri(),'--headless',
                            '--convert-to','pdf','--outdir',str(args.output.parent),str(args.output)],check=True,env=env)
    else:print('Ekspor berkas Word sebagai PDF melalui Microsoft Word atau LibreOffice.')

if __name__=='__main__':main()
