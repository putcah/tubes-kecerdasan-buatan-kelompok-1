"""Dashboard progres proyek. Jalankan dengan streamlit run app.py."""
import os
os.environ.setdefault('MPLCONFIGDIR', '/tmp/tubes-kb-mpl')
import json
import joblib
import pandas as pd
import streamlit as st
from src.common import ROOT, FEATURES, NUMERIC, TARGET, load_data, splits, validate_inputs

st.set_page_config(page_title='K01 | Predictive Maintenance', page_icon='⚙️', layout='wide')
st.markdown('''<style>.block-container{max-width:1200px;padding-top:4rem}
[data-testid="stMetric"]{background:white;border:1px solid #dce5ed;border-radius:12px;padding:16px}
h1,h2,h3{color:#142c42}</style>''', unsafe_allow_html=True)
st.caption('Kecerdasan Buatan, Kelompok 1, Kelas B')
st.title('Intelligent Predictive Maintenance')
st.write('Eksplorasi kondisi mesin, evaluasi model, dan seleksi fitur dengan GA.')

@st.cache_data
def data(): return load_data()

@st.cache_resource
def artifact(): return joblib.load(ROOT/'artifacts/baseline.joblib')

GA_DIR = ROOT / 'W13' / 'hasil'


@st.cache_data
def ga_results():
    return json.loads((GA_DIR / 'summary.json').read_text(encoding='utf-8'))


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
st.sidebar.success('Progres minggu 13')
st.sidebar.caption('PSO direncanakan pada W14, Fuzzy dan deployment pada W15.')
st.sidebar.caption(f"Kelas: {cfg['class']}")

if page=='Overview':
    cols=st.columns(4)
    for c,label,value in zip(cols,['Data','Fitur input','Kegagalan','Recall validasi'],[f'{len(df):,}','6',f'{df[TARGET].mean():.2%}',f"{val['recall']:.2%}"]): c.metric(label,value)
    st.subheader('Tujuan sistem')
    st.write('Mengklasifikasikan kegagalan mesin dari jenis produk dan lima variabel operasi; tahap akhir mengubah probabilitas model menjadi prioritas perawatan.')
    st.code('UCI → preprocessing → GA → PSO → MLP → Fuzzy → Streamlit',language=None)
    st.info('Hasil seleksi fitur tersedia di GA Optimization. Model Comparison menampilkan perbandingan validasi dengan baseline pada tiga seed.')
    st.subheader('Anggota dan tanggung jawab')
    st.dataframe(pd.DataFrame(cfg['members']).rename(columns={'nim':'NIM','name':'Nama','proposed_role':'Tanggung jawab'}),hide_index=True,width='stretch')
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
    st.caption('Simulasi ini menggunakan baseline W12 dengan enam fitur. Hasil eksperimen subset tersedia di GA Optimization.')
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
            st.info('Prioritas perawatan berbasis Fuzzy direncanakan pada minggu 15.')
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
    st.subheader('Seleksi fitur dengan Genetic Algorithm')
    if not (GA_DIR / 'summary.json').exists():
        st.info('Jalankan eksperimen GA untuk menghasilkan ringkasan dan grafik.')
        st.code('python -m src.ga_feature_selection')
        st.stop()
    summary = ga_results()
    selected = summary['selected']
    st.write('Setiap bit mewakili satu variabel. Type dipilih sebagai satu kelompok, '
             'termasuk seluruh kolom hasil pengkodeannya. Fitness dihitung dari '
             'F1 validasi dikurangi penalti 0,02 × jumlah fitur / 6.')
    columns = st.columns(3)
    columns[0].metric('Kromosom terbaik', selected['chromosome'])
    columns[1].metric('Fitur terpilih', f"{len(selected['features'])} dari 6")
    columns[2].metric('Fitness terbaik', f"{selected['fitness']:.4f}")
    st.caption('Urutan bit: ' + ', '.join(summary['chromosome_order']))
    st.image(str(GA_DIR / 'convergence.png'), width='stretch')
    st.caption('Kurva menunjukkan kandidat terbaik pada setiap generasi. '
               'Nilai yang tetap menunjukkan bahwa belum ditemukan kandidat dengan fitness lebih tinggi.')
    st.dataframe(pd.DataFrame([
        {'Seed': run['seed'], 'Kromosom': run['ga']['chromosome'],
         'Fitness': run['ga']['fitness'], 'F1 validasi': run['ga']['validation']['f1'],
         'Jumlah fitur': len(run['ga']['features']),
         'Subset unik dievaluasi': run['ga']['unique_evaluations']}
        for run in summary['runs']
    ]), hide_index=True, width='stretch')
    stats = summary['fitness']
    st.write(f"Fitness terbaik {stats['best']:.4f}, rata-rata {stats['mean']:.4f}, "
             f"dan simpangan baku {stats['std']:.4f}.")
    st.subheader('Fitur sebelum dan sesudah seleksi')
    by_seed = {run['seed']: run['ga']['features'] for run in summary['runs']}
    chosen_seed = st.selectbox('Seed untuk melihat fitur', list(by_seed),
                               index=list(by_seed).index(selected['seed']))
    st.dataframe(pd.DataFrame([
        {'Fitur baseline': feature, 'Hasil GA': 'Terpilih' if feature in by_seed[chosen_seed] else 'Dikeluarkan'}
        for feature in summary['chromosome_order']
    ]), hide_index=True, width='stretch')
    with st.expander('Pengaturan eksperimen'):
        st.json(summary['config'])

elif page=='PSO Optimization':
    st.subheader('Rencana W14 · optimasi MLP')
    st.info('Belum dijalankan. Tidak ada nilai global best atau hyperparameter hasil PSO.')
    st.dataframe(pd.DataFrame({'Hyperparameter':['learning rate','hidden units','dropout','batch size'],'Usulan ruang pencarian':['10^-4 sampai 10^-2 (log)','16 sampai 128 (integer)','0.0 sampai 0.5','32 / 64 / 128']}),hide_index=True)
    st.write('Baseline scikit-learn belum memakai dropout. W14: gunakan backend NN yang mendukung dropout untuk seluruh empat konfigurasi dan latih ulang baseline dengan split tetap. Definisikan pbest/gbest dan gunakan beberapa seed dengan budget sebanding.')

elif page=='Fuzzy Inference':
    st.subheader('Rencana W15 · prioritas perawatan')
    st.info('FIS direncanakan pada minggu 15.')
    st.write('Usulan input: probabilitas failure, tool wear dan torque. Output: Normal → Inspection → Maintenance → Critical. Mamdani, agregasi max dan centroid; membership/rules perlu diuji sebelum integrasi.')
    st.write('Contoh aturan rancangan: jika probabilitas tinggi dan tool wear tinggi maka Critical. Batas membership bukan hasil eksperimen W12.')

elif page=='Model Comparison':
    st.subheader('Baseline NN dan GA + NN')
    if (GA_DIR / 'summary.json').exists():
        summary = ga_results()
        labels = {'accuracy': 'Accuracy', 'precision': 'Precision', 'recall': 'Recall',
                  'f1': 'F1', 'feature_count': 'Jumlah fitur',
                  'fit_seconds': 'Latih model (detik)', 'search_seconds': 'Pencarian GA (detik)'}
        st.dataframe(pd.DataFrame([
            {'Model': name, **{label: round(results[key]['mean'], 4) for key, label in labels.items()}}
            for name, results in summary['aggregate'].items()
        ]), hide_index=True, width='stretch')
        st.caption('Rata-rata pada seed 11, 22, dan 33. Waktu pencarian mencakup pelatihan kandidat. '
                   'Validasi digunakan dalam pemilihan subset; data uji disimpan untuk evaluasi akhir.')
        with st.expander('Hasil setiap seed'):
            st.dataframe(pd.read_csv(GA_DIR / 'comparison.csv'), hide_index=True, width='stretch')
    else:
        st.info('Jalankan eksperimen GA untuk melihat perbandingan.')
    st.caption('Model PSO + NN dan GA + PSO + NN direncanakan pada minggu 14.')
    st.caption('Evaluasi prioritas perawatan berbasis Fuzzy dilakukan tersendiri pada tahap integrasi.')
