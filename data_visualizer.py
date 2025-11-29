from typing import Optional
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import logging

logger = logging.getLogger(__name__)


def ensure_output_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def save_matplotlib(fig, path: Path):
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def plot_quantity_by_chemical(df: pd.DataFrame, output_dir: Path):
    """Bar chart of total quantity per chemical; works with different column names."""
    output_dir = Path(output_dir)
    ensure_output_dir(output_dir)
    qty_col = next((c for c in df.columns if 'quantity' in c or 'qty' in c), None)
    chem_col = next((c for c in df.columns if 'chemical' in c or 'chem' in c or 'product_code' in c), None)
    if qty_col is None or chem_col is None:
        logger.warning("plot_quantity_by_chemical: required columns not found.")
        return

    summary = df.groupby(chem_col)[qty_col].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(10, 6))
    summary.plot(kind='bar', ax=ax)
    ax.set_title("Total Quantity by Chemical")
    ax.set_xlabel(chem_col)
    ax.set_ylabel(qty_col)
    ax.tick_params(axis='x', rotation=45)
    save_matplotlib(fig, output_dir / "quantity_by_chemical.png")


def plot_cost_vs_purity(df: pd.DataFrame, output_dir: Path):
    output_dir = Path(output_dir)
    ensure_output_dir(output_dir)
    purity = next((c for c in df.columns if 'purity' in c), None)
    cost = next((c for c in df.columns if 'cost' in c), None)
    if purity is None or cost is None:
        logger.warning("plot_cost_vs_purity: required columns not found.")
        return
    fig = px.scatter(df, x=purity, y=cost, hover_data=df.columns, title="Cost vs Purity")
    try:
        # Preferred: save static PNG via Kaleido
        fig.write_image(str(output_dir / "cost_vs_purity.png"))
    except Exception as e:
        logger.warning("Failed to write static image with Kaleido: %s. Falling back to HTML output.", e)
        # fallback: interactive HTML that requires no extra engine
        fig.write_html(str(output_dir / "cost_vs_purity.html"))


def plot_avg_cost_per_plant(df: pd.DataFrame, output_dir: Path):
    output_dir = Path(output_dir)
    ensure_output_dir(output_dir)
    plant = next((c for c in df.columns if 'plant' in c), None)
    cost = next((c for c in df.columns if 'cost' in c), None)
    if plant is None or cost is None:
        logger.warning("plot_avg_cost_per_plant: required columns not found.")
        return
    avg = df.groupby(plant)[cost].mean().sort_values()
    fig, ax = plt.subplots(figsize=(8, 6))
    avg.plot(kind='barh', ax=ax)
    ax.set_title("Average Cost per Plant")
    ax.set_xlabel(cost)
    save_matplotlib(fig, output_dir / "avg_cost_per_plant.png")