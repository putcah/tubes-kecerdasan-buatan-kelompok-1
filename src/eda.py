"""Jalankan dari root project: python -m src.eda."""
import os
os.environ.setdefault('MPLCONFIGDIR', '/tmp/tubes-kb-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from src.common import ROOT, FEATURES, NUMERIC, TARGET, EXCLUDED, SHA256, SOURCE, load_data, splits, write_json

def main():
    df = load_data()
    folder = ROOT / 'W12/eda'
    folder.mkdir(parents=True, exist_ok=True)
    parts = splits(df)
    summary = {'rows': len(df), 'columns': len(df.columns), 'input_features': len(FEATURES),
               'class_counts': {str(k): int(v) for k, v in df[TARGET].value_counts().items()},
               'failure_rate': float(df[TARGET].mean()), 'missing_cells': int(df.isna().sum().sum()),
               'duplicated_full_rows': int(df.duplicated().sum()),
               'duplicated_feature_rows': int(df.duplicated(FEATURES).sum()),
               'excluded_features': EXCLUDED, 'source': SOURCE, 'sha256': SHA256,
               'split': {name: {'rows':len(p), 'failure':int(p[TARGET].sum()),
                                'UDI_min':int(p.UDI.min()), 'UDI_max':int(p.UDI.max())} for name,p in parts.items()}}
    write_json(folder / 'summary.json', summary)
    df.isna().sum().rename('missing').to_csv(folder / 'missing_values.csv')
    df[NUMERIC].describe().T.to_csv(folder / 'numeric_statistics.csv')
    df.groupby('Type')[TARGET].agg(['size','sum','mean']).to_csv(folder / 'failure_by_type.csv')
    pd.concat([p[['UDI', TARGET]].assign(split=name) for name,p in parts.items()]).to_csv(ROOT/'W12/split_manifest.csv', index=False)
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.1))
    df[TARGET].value_counts().sort_index().plot.bar(ax=axes[0], color=['#1b7f79','#e28838'], rot=0)
    axes[0].set(title='Distribusi target (semua data)', xlabel='Machine failure', ylabel='Jumlah baris')
    for container in axes[0].containers: axes[0].bar_label(container)
    rates = df.groupby((df.UDI-1)//500)[TARGET].mean()*100
    axes[1].plot((rates.index+1)*500, rates, marker='o', color='#1b7f79')
    axes[1].axvline(6000, color='#e28838', linestyle='--'); axes[1].axvline(8000, color='#e28838', linestyle='--')
    axes[1].set(title='Kegagalan per blok 500 UDI', xlabel='Akhir blok UDI', ylabel='Failure (%)')
    fig.tight_layout(); fig.savefig(folder/'target_and_order.png', dpi=160); plt.close(fig)
    corr = df[NUMERIC + [TARGET]].corr()
    corr.to_csv(folder/'correlation.csv')
    fig, ax = plt.subplots(figsize=(7,5))
    short = ['Air temp','Process temp','Speed','Torque','Tool wear','Failure']
    im=ax.imshow(corr, vmin=-1, vmax=1,cmap='RdBu_r')
    ax.set_xticks(range(6),short,rotation=35,ha='right');ax.set_yticks(range(6),short)
    for i in range(6):
        for j in range(6): ax.text(j,i,f'{corr.iloc[i,j]:.2f}',ha='center',va='center',fontsize=9)
    fig.colorbar(im,ax=ax);fig.tight_layout();fig.savefig(folder/'correlation.png',dpi=150);plt.close(fig)
    fig,axes=plt.subplots(2,3,figsize=(10,5.4))
    for ax,col in zip(axes.flat,NUMERIC):
        ax.hist(df[col],bins=35,color='#1b7f79');ax.set_title(col,fontsize=10)
    df.Type.value_counts().plot.bar(ax=axes.flat[-1],color='#e28838',rot=0);axes.flat[-1].set_title('Type')
    fig.tight_layout();fig.savefig(folder/'feature_distributions.png',dpi=140);plt.close(fig)
    print(summary)

if __name__ == '__main__': main()
