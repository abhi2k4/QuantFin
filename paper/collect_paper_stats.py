"""Collect repo-grounded stats for the paper.

Outputs:
- paper/figures/dataset_summary.json
- paper/figures/backtest_variants_summary.json

This script only uses repository data + the implemented backtest router.
"""

from __future__ import annotations

import asyncio
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
import sys

import pandas as pd


@dataclass(frozen=True)
class BacktestVariant:
    name: str
    strategy: str
    start_date: str
    end_date: str
    capital: float = 100000
    top_n: int = 10
    rebalance_frequency: str = "monthly"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def figures_dir() -> Path:
    return repo_root() / "paper" / "figures"


def backend_data_dir() -> Path:
    return repo_root() / "backend" / "data"


def summarize_dataset() -> dict:
    data_dir = backend_data_dir()

    csv_files = sorted(
        [p for p in data_dir.glob("*.csv") if p.stem not in {"portfolio", "nifty50"}]
    )
    symbols = [p.stem for p in csv_files]

    # Determine global date range across all available symbol CSVs.
    min_date = None
    max_date = None
    usable_symbols = 0

    for path in csv_files:
        try:
            df = pd.read_csv(path, skiprows=2)
            df.columns = ["Date", "Close", "High", "Low", "Open", "Volume"]
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
            df = df.dropna(subset=["Date"]).sort_values("Date")
            if df.empty:
                continue
            usable_symbols += 1
            s_min = df["Date"].iloc[0].to_pydatetime()
            s_max = df["Date"].iloc[-1].to_pydatetime()
            min_date = s_min if min_date is None else min(min_date, s_min)
            max_date = s_max if max_date is None else max(max_date, s_max)
        except Exception:
            continue

    return {
        "data_dir": str(data_dir),
        "num_symbol_csv": len(csv_files),
        "num_symbols_usable": usable_symbols,
        "symbols": symbols,
        "global_start_date": min_date.strftime("%Y-%m-%d") if min_date else None,
        "global_end_date": max_date.strftime("%Y-%m-%d") if max_date else None,
    }


async def run_backtest_variant(variant: BacktestVariant) -> dict:
    backend_dir = repo_root() / "backend"
    sys.path.insert(0, str(backend_dir))

    from app.routers.backtest import BacktestRequest, run_backtest as run_backtest_endpoint

    req = BacktestRequest(
        strategy=variant.strategy,
        start_date=variant.start_date,
        end_date=variant.end_date,
        capital=variant.capital,
        top_n=variant.top_n,
        rebalance_frequency=variant.rebalance_frequency,
    )
    resp = await run_backtest_endpoint(req)

    return {
        "variant": asdict(variant),
        "strategy": {
            "cagr": float(resp.strategy_cagr),
            "sharpe": float(resp.strategy_sharpe),
            "sortino": float(resp.strategy_sortino),
            "max_drawdown": float(resp.strategy_max_drawdown),
            "volatility": float(resp.strategy_volatility),
            "final_value": float(resp.final_value),
        },
        "benchmark": {
            "cagr": float(resp.benchmark_cagr),
            "sharpe": float(resp.benchmark_sharpe),
            "sortino": float(resp.benchmark_sortino),
            "max_drawdown": float(resp.benchmark_max_drawdown),
            "volatility": float(resp.benchmark_volatility),
            "final_value": float(resp.benchmark_values[-1]),
        },
        "num_rebalances": int(resp.num_rebalances),
        "num_points": len(resp.dates),
    }


def main() -> int:
    figures_dir().mkdir(parents=True, exist_ok=True)

    dataset_summary = summarize_dataset()
    (figures_dir() / "dataset_summary.json").write_text(
        json.dumps(dataset_summary, indent=2), encoding="utf-8"
    )

    variants = [
        BacktestVariant(
            name="Monthly (2023-01-01 to 2024-01-01)",
            strategy="LINEAR",
            start_date="2023-01-01",
            end_date="2024-01-01",
            rebalance_frequency="monthly",
        ),
        BacktestVariant(
            name="Quarterly (2023-01-01 to 2024-01-01)",
            strategy="LINEAR",
            start_date="2023-01-01",
            end_date="2024-01-01",
            rebalance_frequency="quarterly",
        ),
        BacktestVariant(
            name="Monthly (2022-01-01 to 2024-01-01)",
            strategy="LINEAR",
            start_date="2022-01-01",
            end_date="2024-01-01",
            rebalance_frequency="monthly",
        ),
    ]

    results = []
    for v in variants:
        results.append(asyncio.run(run_backtest_variant(v)))

    (figures_dir() / "backtest_variants_summary.json").write_text(
        json.dumps({"results": results}, indent=2), encoding="utf-8"
    )

    print("Wrote:", figures_dir() / "dataset_summary.json")
    print("Wrote:", figures_dir() / "backtest_variants_summary.json")
    for r in results:
        print("---", r["variant"]["name"])
        print("strategy_cagr", r["strategy"]["cagr"], "benchmark_cagr", r["benchmark"]["cagr"])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
