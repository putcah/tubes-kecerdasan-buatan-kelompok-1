"""Dashboard W12: streamlit run app.py."""
import os
os.environ.setdefault('MPLCONFIGDIR', '/tmp/tubes-kb-mpl')
import json
import joblib
import pandas as pd
import streamlit as st
from src.common import ROOT, FEATURES, NUMERIC, TARGET, load_data, splits, validate_inputs

st.set_page_config(page_title='K01 | Predictive Maintenance', page_icon='⚙️', layout='wide')
st.markdown('''<style>.block-container{max-width:1200px;padding-top:2rem}
[data-testid="stMetric"]{background:white;border:1px solid #dce5ed;border-radius:12px;padding:16px}
h1,h2,h3{color:#142c42}</style>''', unsafe_allow_html=True)
st.caption('KECERDASAN BUATAN · KELOMPOK 01 · PROGRES MINGGU 12')
st.title('Intelligent Predictive Maintenance')
st.write('Eksplorasi kondisi mesin, evaluasi baseline MLP, dan simulasi risiko kegagalan.')

@st.cache_data
def data(): return load_data()

@st.cache_resource
def artifact(): return joblib.load(ROOT/'artifacts/baseline.joblib')

try:
    df=data();bundle=artifact()
except Exception as exc:
    st.error(f'Belum bisa memuat data/model: {exc}')
    st.code('python -m src.eda\npython -m src.train_baseline')
    st.stop()
cfg=json.loads((ROOT/'project.json').read_text())
meta=bundle['metadata'];val=meta['validation']
menu=['Overview','Dataset Explorer','Neural Network','Prediction / Simulation','GA Optimization','PSO Optimization','Fuzzy Inference','Model Comparison']
page=st.sidebar.radio('Halaman',menu)
st.sidebar.success('W12 · EDA dan baseline tersedia')
st.sidebar.caption('GA → W13 · PSO → W14 · Fuzzy & online → W15')
st.sidebar.caption(f"Kelas: {cfg['class']}")

if page=='Overview':
    cols=st.columns(4)
    for c,label,value in zip(cols,['Data','Fitur input','Kegagalan','Recall validasi'],[f'{len(df):,}','6',f'{df[TARGET].mean():.2%}',f"{val['recall']:.2%}"]): c.metric(label,value)
    st.subheader('Tujuan sistem')
    st.write('Mengklasifikasikan kegagalan mesin dari jenis produk dan lima variabel operasi; tahap akhir mengubah probabilitas model menjadi prioritas perawatan.')
    st.code('UCI → preprocessing → GA → PSO → MLP → Fuzzy → Streamlit',language=None)
    st.info('Saat ini: preprocessing + baseline MLP + dashboard. Komponen GA, PSO, dan Fuzzy masih rencana; keluaran simulasi adalah baseline.')
    st.subheader('Anggota dan usulan tanggung jawab')
    st.dataframe(pd.DataFrame(cfg['members']).rename(columns={'nim':'NIM','name':'Nama','proposed_role':'Usulan peran'}),hide_index=True,width='stretch')
    st.caption('Pembagian ini usulan untuk dikonfirmasi kelompok; bukan catatan kontribusi yang sudah terjadi.')
    st.link_button('Dataset resmi UCI 601','https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset')
    st.warning('Dataset sintetis. Prediksi status kegagalan pada satu pengamatan, bukan estimasi sisa umur mesin. Skor probabilitas belum dikalibrasi untuk penggunaan industri.')

elif page=='Dataset Explorer':
    st.subheader('Kualitas dan distribusi data')
    a,b,c=st.columns(3);a.metric('Baris',len(df));b.metric('Missing values',int(df.isna().sum().sum()));c.metric('Kolom total',len(df.columns))
    st.dataframe(df.head(30),hide_index=True,width='stretch')
    st.dataframe(df[NUMERIC].describe().T,width='stretch')
    for name in ['target_and_order.png','feature_distributions.png','correlation.png']:
        st.image(str(ROOT/'W12/eda'/name),width='stretch')
    st.dataframe(df.isna().sum().rename('Missing values'),width='stretch')
    st.caption('EDA seluruh data untuk audit deskriptif. Parameter scaler/imputer dan bobot kelas hanya dihitung dari train; test tidak dipakai memilih model.')
    st.subheader('Split tetap berdasarkan UDI')
    st.dataframe(pd.DataFrame([{'Split':n,'Baris':len(p),'Failure':int(p[TARGET].sum()),'UDI awal':int(p.UDI.min()),'UDI akhir':int(p.UDI.max())} for n,p in splits(df).items()]),hide_index=True)

elif page=='Neural Network':
    st.subheader('Baseline MLP · hasil validasi')
    st.code(f"6 variabel → 8 input hasil encoding → Dense 32 ReLU → Dense 16 ReLU → output biner\nAdam · lr 0.001 · batch 128 · L2 0.0001 · seed {meta['seed']}\nParameter: {meta['parameter_count']:,} · checkpoint epoch {meta['best_epoch']} · threshold 0.5",language=None)
    cols=st.columns(4)
    for c,key in zip(cols,['accuracy','precision','recall','f1']): c.metric(key.capitalize(),f'{val[key]:.4f}')
    st.image(str(ROOT/'W12/baseline/baseline_curves.png'),width='stretch')
    st.write(f"Average precision: {val['average_precision']:.4f} · ROC AUC: {val['roc_auc']:.4f}")
    st.write('Loss kurva ditampilkan tanpa bobot untuk membandingkan train/validation. Optimasi training menggunakan bobot kelas dari train.')
    st.info('Angka di atas berasal dari validation. Test disimpan untuk evaluasi akhir setelah pilihan model dikunci.')
    st.json(meta)

elif page=='Prediction / Simulation':
    st.subheader('Simulasi baseline')
    st.caption('Input harus berada dalam rentang dataset. Semua fitur dipakai pada baseline; sensor penting belum ditentukan GA.')
    mode=st.radio('Cara input',['Manual','Upload CSV'],horizontal=True)
    def infer(frame):
        clean=validate_inputs(frame,df)
        probability=bundle['pipeline'].predict_proba(clean)[:,1]
        return clean.assign(probability_failure=probability,predicted_failure=(probability>=bundle['threshold']).astype(int))
    if mode=='Manual':
        with st.form('manual'):
            values={'Type':st.selectbox('Type',['L','M','H'])}
            cols=st.columns(2)
            for i,col in enumerate(NUMERIC):
                values[col]=cols[i%2].number_input(col,min_value=float(df[col].min()),max_value=float(df[col].max()),value=float(df[col].median()),format='%.2f')
            submit=st.form_submit_button('Prediksi kondisi mesin',type='primary')
        if submit:
            out=infer(pd.DataFrame([values]));p=float(out.probability_failure.iloc[0])
            st.metric('Skor probabilitas kegagalan',f'{p:.2%}')
            st.write('Prediksi baseline: **'+('Failure' if p>=.5 else 'Non-failure')+'**')
            st.info('Prioritas maintenance berbasis Fuzzy belum tersedia pada W12.')
    else:
        st.download_button('Unduh template CSV',df[FEATURES].head(3).to_csv(index=False),'template_input.csv','text/csv')
        upload=st.file_uploader('CSV dengan enam kolom input',type='csv')
        if upload is not None:
            try:
                result=infer(pd.read_csv(upload))
                st.dataframe(result,hide_index=True,width='stretch')
                st.download_button('Unduh hasil',result.to_csv(index=False),'prediksi_baseline.csv','text/csv')
            except (ValueError,KeyError,TypeError) as exc: st.error(f'Periksa CSV: {exc}')

elif page=='GA Optimization':
    st.subheader('Rencana W13 · seleksi fitur')
    st.info('Belum dijalankan. Belum ada fitur terpilih atau kurva konvergensi GA.')
    st.write('Kromosom 6 bit merepresentasikan enam variabel asli; Type dipilih sebagai satu grup encoding. Tolak kromosom kosong. Fitness: F1 validation dikurangi penalti ukuran subset; test tidak digunakan.')
    st.write('Usulan awal: populasi 20, generasi 15, tournament 3, crossover 0,8, mutation 1/6, elitism 2, seed 11/22/33. Tetapkan bobot penalti dan budget sebelum eksperimen; laporkan best/mean/std.')

elif page=='PSO Optimization':
    st.subheader('Rencana W14 · optimasi MLP')
    st.info('Belum dijalankan. Tidak ada nilai global best atau hyperparameter hasil PSO.')
    st.dataframe(pd.DataFrame({'Hyperparameter':['learning rate','hidden units','dropout','batch size'],'Usulan ruang pencarian':['10^-4 sampai 10^-2 (log)','16 sampai 128 (integer)','0.0 sampai 0.5','32 / 64 / 128']}),hide_index=True)
    st.write('Baseline scikit-learn belum memakai dropout. W14: gunakan backend NN yang mendukung dropout untuk seluruh empat konfigurasi dan latih ulang baseline dengan split tetap. Definisikan pbest/gbest dan gunakan beberapa seed dengan budget sebanding.')

elif page=='Fuzzy Inference':
    st.subheader('Rencana W15 · prioritas perawatan')
    st.info('FIS belum diimplementasikan. Tidak ada keputusan Fuzzy yang dihitung pada W12.')
    st.write('Usulan input: probabilitas failure, tool wear dan torque. Output: Normal → Inspection → Maintenance → Critical. Mamdani, agregasi max dan centroid; membership/rules perlu diuji sebelum integrasi.')
    st.write('Contoh aturan rancangan: jika probabilitas tinggi dan tool wear tinggi maka Critical. Batas membership bukan hasil eksperimen W12.')

elif page=='Model Comparison':
    st.subheader('Status eksperimen pembanding')
    rows=[{'Model':'A · Baseline NN','Status':'Selesai W12','Fitur':6,**{k:round(val[k],4) for k in ['accuracy','precision','recall','f1']}}]
    rows += [{'Model':name,'Status':status,'Fitur':None,'accuracy':None,'precision':None,'recall':None,'f1':None} for name,status in [('B · GA+NN','Rencana W13'),('C · PSO+NN','Rencana W14'),('D · GA+PSO+NN','Rencana W14')]]
    st.dataframe(pd.DataFrame(rows),hide_index=True,width='stretch')
    st.write(f"Dummy selalu non-failure pada validation: accuracy {meta['dummy_validation']['accuracy']:.2%}, recall 0%, F1 0. Accuracy tinggi saja tidak menunjukkan kemampuan mendeteksi failure.")
    st.caption('Fuzzy menjadi lapisan keputusan sistem E; tidak diasumsikan meningkatkan akurasi prediksi NN.')
