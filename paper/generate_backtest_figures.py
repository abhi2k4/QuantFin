"""Generate repo-grounded figures for the IEEE paper.

This script runs the backend's walk-forward backtest (the same logic used by
`/api/backtest/run`) and exports:
- CSV of strategy vs benchmark values
- Equity curve PNG (strategy vs benchmark)
- Drawdown PNG (strategy vs benchmark)

Run (from repo root):
  C:/Users/DELL/AppData/Local/Programs/Python/Python311/python.exe paper/generate_backtest_figures.py
"""

from __future__ import annotations

import asyncio
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
import sys

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


@dataclass
class BacktestConfig:
    strategy: str = "LINEAR"
    start_date: str = "2023-01-01"
    end_date: str = "2024-01-01"
    capital: float = 100000
    top_n: int = 10
    rebalance_frequency: str = "monthly"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _paper_dir() -> Path:
    return _repo_root() / "paper"


def _figures_dir() -> Path:
    return _paper_dir() / "figures"


def _ensure_paths() -> None:
    _figures_dir().mkdir(parents=True, exist_ok=True)


def _compute_drawdown(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    running_max = np.maximum.accumulate(values)
    dd = (values - running_max) / running_max
    return dd


async def run_backtest(config: BacktestConfig):
    repo_root = _repo_root()
    backend_dir = repo_root / "backend"

    sys.path.insert(0, str(backend_dir))

    from app.routers.backtest import BacktestRequest, run_backtest as run_backtest_endpoint

    request = BacktestRequest(
        strategy=config.strategy,
        start_date=config.start_date,
        end_date=config.end_date,
        capital=config.capital,
        top_n=config.top_n,
        rebalance_frequency=config.rebalance_frequency,
    )

    response = await run_backtest_endpoint(request)
    return response


def main() -> int:
    _ensure_paths()

    config = BacktestConfig()
    response = asyncio.run(run_backtest(config))

    dates = pd.to_datetime(pd.Series(response.dates))
    strat = np.array(response.portfolio_values, dtype=float)
    bench = np.array(response.benchmark_values, dtype=float)

    # Save series for LaTeX/verification.
    out_csv = _figures_dir() / "backtest_series_2023_2024_linear.csv"
    df = pd.DataFrame(
        {
            "date": dates.dt.strftime("%Y-%m-%d"),
            "strategy_value": strat,
            "benchmark_value": bench,
            "strategy_norm": strat / strat[0],
            "benchmark_norm": bench / bench[0],
            "strategy_drawdown": _compute_drawdown(strat),
            "benchmark_drawdown": _compute_drawdown(bench),
        }
    )
    df.to_csv(out_csv, index=False)

    # Equity curve (normalized).
    equity_path = _figures_dir() / "equity_curve_2023_2024_linear.png"
    plt.figure(figsize=(7.2, 3.6))
    plt.plot(dates, strat / strat[0], label=f"{config.strategy} strategy")
    plt.plot(dates, bench / bench[0], label="Benchmark (equal-weight)")
    plt.ylabel("Normalized value (V/V0)")
    plt.xlabel("Date")
    plt.grid(True, alpha=0.3)
    plt.legend(loc="upper left", fontsize=8)
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    plt.tight_layout()
    plt.savefig(equity_path, dpi=300, bbox_inches="tight")
    plt.close()

    # Drawdown.
    dd_path = _figures_dir() / "drawdown_2023_2024_linear.png"
    plt.figure(figsize=(7.2, 3.0))
    plt.plot(dates, 100.0 * _compute_drawdown(strat), label=f"{config.strategy} strategy")
    plt.plot(dates, 100.0 * _compute_drawdown(bench), label="Benchmark (equal-weight)")
    plt.ylabel("Drawdown (%)")
    plt.xlabel("Date")
    plt.grid(True, alpha=0.3)
    plt.legend(loc="lower left", fontsize=8)
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    plt.tight_layout()
    plt.savefig(dd_path, dpi=300, bbox_inches="tight")
    plt.close()

    # Save a small JSON summary to cross-check paper numbers.
    summary_path = _figures_dir() / "backtest_summary_2023_2024_linear.json"
    summary = {
        "config": asdict(config),
        "strategy": {
            "cagr": float(response.strategy_cagr),
            "sharpe": float(response.strategy_sharpe),
            "sortino": float(response.strategy_sortino),
            "max_drawdown": float(response.strategy_max_drawdown),
            "final_value": float(response.final_value),
        },
        "benchmark": {
            "cagr": float(response.benchmark_cagr),
            "sharpe": float(response.benchmark_sharpe),
            "sortino": float(response.benchmark_sortino),
            "max_drawdown": float(response.benchmark_max_drawdown),
            "final_value": float(response.benchmark_values[-1]),
        },
    }
    pd.Series(summary).to_json(summary_path, indent=2)

    print("Wrote:", out_csv)
    print("Wrote:", equity_path)
    print("Wrote:", dd_path)
    print("Wrote:", summary_path)
    print("Strategy CAGR:", response.strategy_cagr)
    print("Benchmark CAGR:", response.benchmark_cagr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
