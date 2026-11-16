"""Kontrak data yang dipakai EDA, training, dan dashboard."""
from pathlib import Path
import hashlib
import io
import json
import urllib.request
import zipfile
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[1]
NUMERIC = ['Air temperature [K]', 'Process temperature [K]', 'Rotational speed [rpm]', 'Torque [Nm]', 'Tool wear [min]']
FEATURES = ['Type'] + NUMERIC
TARGET = 'Machine failure'
EXCLUDED = ['UDI', 'Product ID', 'TWF', 'HDF', 'PWF', 'OSF', 'RNF']
SOURCE = 'https://archive.ics.uci.edu/static/public/601/ai4i+2020+predictive+maintenance+dataset.zip'
SHA256 = 'dc6630cd9b1f0f853922fad78a1b6436570d3f1ec863f1dd5c4340ac56bc8a8e'

def load_data(download=True):
    path = ROOT / 'data/raw/ai4i2020.csv'
    if not path.exists():
        if not download:
            raise FileNotFoundError('Jalankan python -m src.eda untuk mengunduh data.')
        with urllib.request.urlopen(SOURCE, timeout=60) as response:
            archive = zipfile.ZipFile(io.BytesIO(response.read()))
        data = archive.read('ai4i2020.csv')
        if hashlib.sha256(data).hexdigest() != SHA256:
            raise ValueError('Checksum dataset berubah; periksa sumber sebelum melanjutkan.')
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    if hashlib.sha256(path.read_bytes()).hexdigest() != SHA256:
        raise ValueError('Dataset lokal berbeda dari versi eksperimen.')
    df = pd.read_csv(path).sort_values('UDI').reset_index(drop=True)
    assert len(df) == 10000 and df['UDI'].is_unique
    assert set(FEATURES + [TARGET] + EXCLUDED).issubset(df.columns)
    return df

def splits(df):
    """UDI sebagai proxy urutan, bukan bukti timestamp/mesin independen."""
    return {'train': df.iloc[:6000].copy(), 'validation': df.iloc[6000:8000].copy(), 'test': df.iloc[8000:].copy()}

def make_preprocessor():
    return ColumnTransformer([
        ('numeric', Pipeline([('imputer', SimpleImputer(strategy='median')), ('scaler', StandardScaler())]), NUMERIC),
        ('type', Pipeline([('imputer', SimpleImputer(strategy='most_frequent')),
                           ('encoder', OneHotEncoder(categories=[['H', 'L', 'M']], handle_unknown='error', sparse_output=False))]), ['Type'])
    ], remainder='drop')

def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding='utf-8')

def validate_inputs(frame, reference):
    if frame.empty:
        raise ValueError('CSV tidak memiliki baris data.')
    if len(frame) > 10000:
        raise ValueError('Maksimal 10.000 baris per unggahan.')
    missing = [c for c in FEATURES if c not in frame.columns]
    if missing:
        raise ValueError('Kolom wajib belum ada: ' + ', '.join(missing))
    result = frame[FEATURES].copy()
    if not result['Type'].isin(['H', 'L', 'M']).all():
        raise ValueError('Type harus H, L, atau M; tidak boleh kosong.')
    for col in NUMERIC:
        result[col] = pd.to_numeric(result[col], errors='raise')
        if not np.isfinite(result[col]).all():
            raise ValueError(f'{col}: angka harus terisi dan bernilai finite.')
        lo, hi = float(reference[col].min()), float(reference[col].max())
        if not result[col].between(lo, hi).all():
            raise ValueError(f'{col}: gunakan rentang data {lo:g} sampai {hi:g}.')
    return result
