import logging
from pathlib import Path
import argparse

from data_loader import load_data_from_dir
from data_cleaner import clean_and_standardize, merge_dataframes
from data_analyzer import generate_statistics, scale_numeric_data
from data_visualizer import plot_quantity_by_chemical, plot_cost_vs_purity, plot_avg_cost_per_plant

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(levelname)s — %(message)s")

DEFAULT_OUTPUT = Path.cwd() / "output"


def run_pipeline(data_dir: Path, output_dir: Path):
    logger.info("Loading data from %s", data_dir)
    dfs = load_data_from_dir(data_dir)
    if not dfs:
        logger.error("No dataframes loaded. Exiting.")
        return

    logger.info("Cleaning individual dataframes")
    cleaned = [clean_and_standardize(df) for df in dfs]

    logger.info("Merging into master dataframe")
    master = merge_dataframes(cleaned)

    logger.info("Saving merged data")
    output_dir.mkdir(parents=True, exist_ok=True)
    master.to_csv(output_dir / "merged_data.csv", index=False)

    logger.info("Generating statistics")
    stats = generate_statistics(master)
    stats.to_csv(output_dir / "summary_statistics.csv")

    logger.info("Scaling numeric data (saved for downstream use)")
    scaled = scale_numeric_data(master)
    scaled.to_csv(output_dir / "merged_data_scaled.csv", index=False)

    logger.info("Generating visualizations")
    plot_quantity_by_chemical(master, output_dir)
    plot_cost_vs_purity(master, output_dir)
    plot_avg_cost_per_plant(master, output_dir)

    logger.info("Pipeline completed. Outputs written to %s", output_dir)


def cli():
    parser = argparse.ArgumentParser(description="Run chemical-data ETL and reports.")
    parser.add_argument("--data-dir", type=Path, default=Path.cwd() / "data", help="Directory with input CSV/XLSX files.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT, help="Where to write outputs.")
    args = parser.parse_args()
    run_pipeline(args.data_dir, args.output_dir)


if __name__ == "__main__":
    cli()