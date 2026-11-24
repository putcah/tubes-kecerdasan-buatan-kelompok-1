"""Jalankan eksperimen W13 dengan python -m src.ga_feature_selection."""
import argparse
from concurrent.futures import ProcessPoolExecutor
from itertools import product
from pathlib import Path
from time import perf_counter

import joblib
import numpy as np
import pandas as pd

from src.common import FEATURES, ROOT, SHA256, TARGET, load_data, splits, write_json
from src.train_baseline import fit_mlp, plt

CONFIG = {
    'seeds': [11, 22, 33],
    'population': 20,
    'generations': 15,
    'tournament': 3,
    'crossover_probability': 0.8,
    'mutation_probability': 1 / len(FEATURES),
    'elitism': 2,
    'feature_penalty': 0.02,
}
METRICS = ['accuracy', 'precision', 'recall', 'f1', 'average_precision', 'roc_auc']


def features_for(mask):
    return [feature for feature, bit in zip(FEATURES, mask) if bit]


def fitness(f1, count):
    return f1 - CONFIG['feature_penalty'] * count / len(FEATURES)


def rank(candidate):
    """Urutan tetap untuk seri: F1, jumlah fitur, lalu urutan kromosom."""
    mask, result = candidate
    return result['fitness'], result['validation']['f1'], -sum(mask), mask


def search(train, validation, seed):
    rng = np.random.default_rng(seed)
    options = [mask for mask in product((0, 1), repeat=len(FEATURES)) if any(mask)]
    population = [options[i] for i in rng.choice(len(options), CONFIG['population'], replace=False)]
    cache = {}
    convergence = []
    evaluations = []
    start = perf_counter()

    def evaluate(mask, generation):
        if mask not in cache:
            features = features_for(mask)
            pipeline, probabilities, _, model = fit_mlp(train, validation, features, seed)
            model.update(features=features, fitness=fitness(model['validation']['f1'], len(features)))
            cache[mask] = (pipeline, probabilities, model)
            evaluations.append({
                'seed': seed, 'generation': generation,
                'chromosome': ''.join(map(str, mask)), 'features': ' | '.join(features),
                'feature_count': len(features), 'fitness': model['fitness'],
                'fit_seconds': model['fit_seconds'],
                **{name: model['validation'][name] for name in METRICS},
            })
        return mask, cache[mask][2]

    def parent():
        contenders = rng.choice(len(population), CONFIG['tournament'], replace=False)
        return max((evaluate(population[i], generation) for i in contenders), key=rank)[0]

    for generation in range(1, CONFIG['generations'] + 1):
        ranked = sorted((evaluate(mask, generation) for mask in population), key=rank, reverse=True)
        best_mask, best_model = ranked[0]
        convergence.append({
            'seed': seed, 'generation': generation,
            'best_fitness': best_model['fitness'],
            'mean_fitness': float(np.mean([result['fitness'] for _, result in ranked])),
            'best_f1': best_model['validation']['f1'],
            'unique_evaluations': len(cache),
            'best_feature_count': sum(best_mask),
        })
        if generation == CONFIG['generations']:
            break

        next_population = [mask for mask, _ in ranked[:CONFIG['elitism']]]
        while len(next_population) < CONFIG['population']:
            left, right = parent(), parent()
            if rng.random() < CONFIG['crossover_probability']:
                pivot = int(rng.integers(1, len(FEATURES)))
                children = (left[:pivot] + right[pivot:], right[:pivot] + left[pivot:])
            else:
                children = left, right
            for mask in children:
                child = [bit ^ int(rng.random() < CONFIG['mutation_probability']) for bit in mask]
                if not any(child):
                    child[int(rng.integers(len(child)))] = 1
                next_population.append(tuple(child))
        population = next_population

    pipeline, probabilities, model = cache[best_mask]
    model.update(chromosome=''.join(map(str, best_mask)), search_seconds=perf_counter() - start,
                 unique_evaluations=len(cache))
    print(f"Seed {seed}: {len(cache)} subset, F1={model['validation']['f1']:.4f}", flush=True)
    return {'seed': seed, 'best': model, 'pipeline': pipeline, 'probabilities': probabilities,
            'convergence': convergence, 'evaluations': evaluations}


def run_seed(args):
    train, validation, seed = args
    _, _, _, baseline = fit_mlp(train, validation, FEATURES, seed)
    result = search(train, validation, seed)
    return {**result, 'baseline': baseline}


def aggregate(values):
    return {'best': float(np.max(values)), 'mean': float(np.mean(values)),
            'std': float(np.std(values, ddof=1))}


def save_results(runs, validation, output):
    output.mkdir(parents=True, exist_ok=True)
    selected = max(runs, key=lambda run: rank((
        tuple(map(int, run['best']['chromosome'])), run['best']
    )))
    comparisons = []
    for run in runs:
        for label, model in [('Baseline NN', run['baseline']), ('GA + NN', run['best'])]:
            comparisons.append({
                'seed': run['seed'], 'model': label,
                'feature_count': len(model.get('features', FEATURES)),
                'fit_seconds': model['fit_seconds'], 'search_seconds': model.get('search_seconds', 0),
                **{name: model['validation'][name] for name in METRICS},
            })

    summary = {
        'dataset_sha256': SHA256, 'config': CONFIG, 'chromosome_order': FEATURES,
        'split': {'train_udi': [1, 6000], 'validation_udi': [6001, 8000], 'test_udi': [8001, 10000]},
        'test_evaluated': False, 'threshold': 0.5,
        'runs': [{'seed': run['seed'], 'baseline': run['baseline'], 'ga': run['best']} for run in runs],
        'aggregate': {
            label: {name: aggregate([row[name] for row in comparisons if row['model'] == label])
                    for name in METRICS + ['feature_count', 'fit_seconds', 'search_seconds']}
            for label in ('Baseline NN', 'GA + NN')
        },
        'fitness': aggregate([run['best']['fitness'] for run in runs]),
        'selected': selected['best'],
    }
    write_json(output / 'summary.json', summary)
    pd.DataFrame(comparisons).to_csv(output / 'comparison.csv', index=False)
    pd.DataFrame([
        {'feature': feature, 'baseline': True, 'ga': feature in selected['best']['features']}
        for feature in FEATURES
    ]).to_csv(output / 'selected_features.csv', index=False)
    convergence = pd.DataFrame([row for run in runs for row in run['convergence']])
    convergence.to_csv(output / 'convergence.csv', index=False)
    pd.DataFrame([row for run in runs for row in run['evaluations']]).to_csv(
        output / 'evaluated_subsets.csv', index=False
    )
    pd.DataFrame({'UDI': validation['UDI'], 'actual': validation[TARGET],
                  'probability': selected['probabilities'],
                  'predicted': (selected['probabilities'] >= 0.5).astype(int)}).to_csv(
        output / 'validation_predictions.csv', index=False
    )
    joblib.dump({'pipeline': selected['pipeline'], 'features': selected['best']['features'],
                 'threshold': 0.5, 'metadata': selected['best']}, output / 'ga_mlp.joblib')
    figure, axis = plt.subplots(figsize=(7.5, 3.1), layout='constrained')
    for seed, series in convergence.groupby('seed'):
        axis.plot(series['generation'], series['best_fitness'], marker='o',
                  markersize=3, linewidth=1.6, label=f'Seed {seed}')
    axis.set(xlabel='Generasi', ylabel='Fitness terbaik', xticks=range(1, CONFIG['generations'] + 1))
    axis.grid(alpha=0.25)
    axis.legend(loc='lower right')
    figure.savefig(output / 'convergence.png', dpi=200)
    plt.close(figure)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=1, choices=range(1, 4))
    parser.add_argument('--output', type=Path, default=ROOT / 'W13' / 'hasil')
    args = parser.parse_args()
    parts = splits(load_data())
    train, validation = parts['train'], parts['validation']
    experiments = [(train, validation, seed) for seed in CONFIG['seeds']]
    if args.workers == 1:
        runs = [run_seed(experiment) for experiment in experiments]
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            runs = list(pool.map(run_seed, experiments))
    summary = save_results(runs, validation, args.output)
    print('Fitur terpilih:', ', '.join(summary['selected']['features']))
    print('Hasil:', args.output)


if __name__ == '__main__':
    main()
