"""Baseline MLP terukur. Test sengaja tidak dievaluasi pada W12."""
import os
os.environ.setdefault('MPLCONFIGDIR', '/tmp/tubes-kb-mpl')
import argparse
import copy
import time
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, log_loss, average_precision_score, roc_auc_score, balanced_accuracy_score)
from sklearn.pipeline import Pipeline
from threadpoolctl import threadpool_limits
from src.common import ROOT, FEATURES, TARGET, load_data, splits, make_preprocessor, write_json

def metrics(y, probability):
    pred = (probability >= .5).astype(int)
    return {'accuracy': accuracy_score(y,pred), 'precision':precision_score(y,pred,zero_division=0),
            'recall':recall_score(y,pred,zero_division=0), 'f1':f1_score(y,pred,zero_division=0),
            'balanced_accuracy': balanced_accuracy_score(y,pred),
            'average_precision':average_precision_score(y,probability), 'roc_auc':roc_auc_score(y,probability),
            'log_loss':log_loss(y,probability), 'confusion_matrix':confusion_matrix(y,pred,labels=[0,1]).tolist()}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--seed',type=int,default=42)
    args=parser.parse_args(); seed=args.seed
    parts=splits(load_data());train,val=parts['train'],parts['validation']
    pre=make_preprocessor();x=pre.fit_transform(train[FEATURES]);xv=pre.transform(val[FEATURES])
    y=train[TARGET].to_numpy();yv=val[TARGET].to_numpy()
    # Bobot kelas dihitung HANYA pada train; jumlah bobot = jumlah baris train.
    counts=np.bincount(y);weights=len(y)/(2*counts[y])
    model=MLPClassifier(hidden_layer_sizes=(32,16),activation='relu',solver='adam',alpha=1e-4,
                        batch_size=128,learning_rate_init=1e-3,random_state=seed,
                        shuffle=True,early_stopping=False)
    history=[];best_loss=float('inf');best=None;best_epoch=0;stale=0;start=time.perf_counter()
    with threadpool_limits(limits=1):
        for epoch in range(1,151):
            model.partial_fit(x,y,classes=np.array([0,1]),sample_weight=weights)
            pt=model.predict_proba(x)[:,1];pv=model.predict_proba(xv)[:,1]
            loss=log_loss(yv,pv)
            history.append({'epoch':epoch,'train_log_loss':log_loss(y,pt),'validation_log_loss':loss,
                            'validation_f1':f1_score(yv,pv>=.5,zero_division=0)})
            if loss < best_loss-1e-5:
                best_loss=loss;best=copy.deepcopy(model);best_epoch=epoch;stale=0
            else: stale+=1
            if stale>=20: break
    pipeline=Pipeline([('preprocess',pre),('nn',best)])
    prob=pipeline.predict_proba(val[FEATURES])[:,1]
    result={'model':'Baseline MLP (class-weighted)', 'seed':seed,'threshold':.5,
            'hidden_layers':[32,16],'input_dimension':int(x.shape[1]),
            'parameter_count':int(sum(w.size for w in best.coefs_)+sum(b.size for b in best.intercepts_)),
            'epochs_run':len(history),'best_epoch':best_epoch,'seconds':time.perf_counter()-start,
            'class_weights':{str(k):float(len(y)/(2*counts[k])) for k in [0,1]},
            'validation':metrics(yv,prob),
            'dummy_validation':{'accuracy':float((yv==0).mean()),'precision':0.,'recall':0.,'f1':0.,
                                'confusion_matrix':confusion_matrix(yv,np.zeros_like(yv),labels=[0,1]).tolist()},
            'test_status':'LOCKED: tidak dievaluasi pada W12; tidak dipakai training/checkpoint/tuning'}
    out=ROOT/'W12/baseline';out.mkdir(parents=True,exist_ok=True)
    artifacts=ROOT/'artifacts';artifacts.mkdir(exist_ok=True)
    joblib.dump({'pipeline':pipeline,'features':FEATURES,'threshold':.5,'metadata':result},artifacts/'baseline.joblib')
    write_json(out/'metrics.json',result)
    hist=pd.DataFrame(history);hist.to_csv(out/'training_history.csv',index=False)
    pd.DataFrame({'UDI':val.UDI,'actual':yv,'probability':prob,'predicted':(prob>=.5).astype(int)}).to_csv(out/'validation_predictions.csv',index=False)
    fig,axes=plt.subplots(1,2,figsize=(9,3.2))
    axes[0].plot(hist.epoch,hist.train_log_loss,label='Train (tanpa bobot)');axes[0].plot(hist.epoch,hist.validation_log_loss,label='Validation')
    axes[0].axvline(best_epoch,color='gray',linestyle='--');axes[0].set(xlabel='Epoch',ylabel='Binary log loss',title='Kurva baseline');axes[0].legend(fontsize=8)
    cm=np.array(result['validation']['confusion_matrix']);axes[1].imshow(cm,cmap='Blues')
    for i in range(2):
        for j in range(2): axes[1].text(j,i,str(cm[i,j]),ha='center',va='center',color='white' if cm[i,j]>cm.max()/2 else 'black')
    axes[1].set(xticks=[0,1],yticks=[0,1],xlabel='Prediksi',ylabel='Aktual',title='Validation confusion matrix')
    fig.tight_layout();fig.savefig(out/'baseline_curves.png',dpi=160);plt.close(fig)
    # Verifikasi artefak memuat preprocessing yang sama.
    loaded=joblib.load(artifacts/'baseline.joblib')
    np.testing.assert_allclose(prob,loaded['pipeline'].predict_proba(val[FEATURES])[:,1],rtol=0,atol=0)
    print(result)

if __name__=='__main__': main()
