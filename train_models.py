"""Train the EduAdapt ML models.

  python train_models.py                                  # synthetic data (works out of the box)
  python train_models.py --assistments data/skill_builder_data.csv   # real knowledge-tracing data
  python train_models.py --dropout-csv data/my_students.csv          # real dropout data (FEATURES + at_risk)
"""
import argparse

from modules import training

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--students", type=int, default=1500, help="number of synthetic students")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--assistments", help="path to the ASSISTments skill-builder CSV")
    ap.add_argument("--dropout-csv", help="CSV with the dropout features and an at_risk column")
    ap.add_argument("--no-plots", action="store_true")
    a = ap.parse_args()
    training.train_all(a.students, a.seed, a.assistments, a.dropout_csv, plots=not a.no_plots)
