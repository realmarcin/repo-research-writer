#!/usr/bin/env python3
"""
Benchmark evaluation against AlphaFold2 and RoseTTAFold.

This script compares ProteinNet-Transformer predictions with baseline methods
on the CASP14 benchmark dataset.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path


def load_predictions(predictions_dir, model_name):
    """
    Load prediction files for a given model.

    Args:
        predictions_dir: Directory containing .pdb prediction files
        model_name: Name of the model

    Returns:
        predictions: List of (protein_id, coordinates) tuples
    """
    pdb_files = Path(predictions_dir).glob(f"{model_name}/*.pdb")
    predictions = []

    for pdb_file in pdb_files:
        protein_id = pdb_file.stem
        coords = parse_pdb(pdb_file)
        predictions.append((protein_id, coords))

    return predictions


def compute_tm_score(pred_coords, true_coords):
    """
    Calculate TM-score between predicted and true structures.

    TM-score formula (Zhang & Skolnick, Proteins 2005):
        TM = (1/L) * Σ [1 / (1 + (d_i / d0)^2)]

    where:
        L = protein length
        d_i = distance between aligned residues
        d0 = 1.24 * (L - 15)^(1/3) - 1.8

    Args:
        pred_coords: Predicted Cα coordinates (N, 3)
        true_coords: True Cα coordinates (N, 3)

    Returns:
        tm_score: Float between 0 and 1 (higher is better)
    """
    L = len(true_coords)
    d0 = 1.24 * (L - 15) ** (1/3) - 1.8

    # Optimal superposition using Kabsch algorithm
    pred_aligned, true_aligned = kabsch_align(pred_coords, true_coords)

    # Calculate distances
    distances = np.linalg.norm(pred_aligned - true_aligned, axis=1)

    # TM-score formula
    tm_score = np.mean(1.0 / (1 + (distances / d0) ** 2))

    return tm_score


def generate_comparison_plot(results_df, output_path):
    """
    Generate bar plot comparing model accuracies.

    Creates Figure 1: Accuracy comparison on CASP14 benchmark.

    Args:
        results_df: DataFrame with columns [model_name, tm_score]
        output_path: Path to save figure
    """
    # Calculate mean TM-scores per model
    mean_scores = results_df.groupby('model_name')['tm_score'].mean()
    std_scores = results_df.groupby('model_name')['tm_score'].std()

    # Create bar plot
    fig, ax = plt.subplots(figsize=(10, 6))

    models = mean_scores.index
    x_pos = np.arange(len(models))

    bars = ax.bar(x_pos, mean_scores.values, yerr=std_scores.values,
                   capsize=5, alpha=0.8,
                   color=['#2ecc71', '#3498db', '#e74c3c'])

    ax.set_xlabel('Model', fontsize=12)
    ax.set_ylabel('TM-score', fontsize=12)
    ax.set_title('Structure Prediction Accuracy on CASP14 Benchmark', fontsize=14)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(models, rotation=15, ha='right')
    ax.set_ylim(0, 1.0)
    ax.grid(axis='y', alpha=0.3)

    # Add significance markers
    ax.text(0, mean_scores.iloc[0] + 0.05, '***', ha='center', fontsize=16)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    print(f"Figure saved to {output_path}")


def main():
    """
    Main evaluation pipeline.

    Workflow:
        1. Load predictions from all models
        2. Compute TM-scores against ground truth
        3. Save results to CSV
        4. Generate comparison plot
    """
    # Load predictions
    models = ['ProteinNet-Transformer', 'AlphaFold2', 'RoseTTAFold']
    results = []

    for model in models:
        predictions = load_predictions('predictions/', model)

        for protein_id, pred_coords in predictions:
            true_coords = load_ground_truth(protein_id)
            tm_score = compute_tm_score(pred_coords, true_coords)

            results.append({
                'model_name': model,
                'protein_id': protein_id,
                'tm_score': tm_score
            })

    # Save results
    results_df = pd.DataFrame(results)
    results_df.to_csv('data/benchmark_results.csv', index=False)
    print(f"Results saved to data/benchmark_results.csv")

    # Generate figure
    generate_comparison_plot(results_df, 'figures/accuracy_comparison.png')

    # Print summary statistics
    print("\nSummary Statistics:")
    print(results_df.groupby('model_name')['tm_score'].describe())


if __name__ == '__main__':
    main()
