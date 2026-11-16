"""Pemeriksaan W12 tanpa membuka test untuk evaluasi model."""
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, f1_score
from src.common import ROOT, FEATURES, TARGET, EXCLUDED, NUMERIC, load_data, splits, validate_inputs, write_json
from streamlit.testing.v1 import AppTest

def main():
    checks=[]
    df=load_data();parts=splits(df)
    identifiers=[set(p.UDI) for p in parts.values()]
    assert not identifiers[0]&identifiers[1] and not identifiers[0]&identifiers[2] and not identifiers[1]&identifiers[2]
    assert set.union(*identifiers)==set(df.UDI)
    assert not set(FEATURES)&set(EXCLUDED+[TARGET])
    checks.append('Split saling terpisah, lengkap, dan tidak ada label/ID sebagai fitur')
    bundle=joblib.load(ROOT/'artifacts/baseline.joblib')
    scaler=bundle['pipeline']['preprocess'].named_transformers_['numeric']['scaler']
    np.testing.assert_allclose(scaler.mean_,parts['train'][NUMERIC].mean().to_numpy())
    checks.append('Rata-rata scaler identik dengan train, bukan seluruh dataset')
    expected=pd.read_csv(ROOT/'W12/baseline/validation_predictions.csv')
    prob=bundle['pipeline'].predict_proba(parts['validation'][FEATURES])[:,1]
    np.testing.assert_allclose(prob,expected.probability,rtol=1e-12,atol=1e-15)
    metrics=bundle['metadata']['validation'];y=parts['validation'][TARGET]
    assert confusion_matrix(y,prob>=.5).tolist()==metrics['confusion_matrix']
    assert np.isclose(f1_score(y,prob>=.5),metrics['f1'])
    checks.append('Prediksi artefak dan metrik validation cocok dengan hasil tersimpan')
    for bad in [pd.DataFrame(),pd.DataFrame([{**df[FEATURES].iloc[0].to_dict(),'Type':'X'}]),pd.DataFrame([{**df[FEATURES].iloc[0].to_dict(),'Torque [Nm]':np.inf}])]:
        try: validate_inputs(bad,df)
        except ValueError: continue
        raise AssertionError('Input tidak valid diterima')
    checks.append('Input kosong, kategori salah dan angka infinite ditolak')
    app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=30).run()
    assert len(app.exception)==0
    pages=['Overview','Dataset Explorer','Neural Network','Prediction / Simulation','GA Optimization','PSO Optimization','Fuzzy Inference','Model Comparison']
    for name in pages:
        app.sidebar.radio[0].set_value(name).run()
        assert len(app.exception)==0,(name,[e.message for e in app.exception])
        if name=='Prediction / Simulation':
            app.button[0].click().run()
            assert len(app.exception)==0 and any(m.label=='Skor probabilitas kegagalan' for m in app.metric)
    checks.append('Delapan halaman Streamlit dan prediksi manual lolos AppTest')
    result={'status':'PASS','checks':checks,'test_model_evaluation':'NOT RUN; test tetap terkunci'}
    write_json(ROOT/'W12/verification.json',result)
    print(json.dumps(result,indent=2,ensure_ascii=False))

if __name__=='__main__': main()
