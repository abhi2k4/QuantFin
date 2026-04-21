import pickle
from pathlib import Path


def main() -> None:
    cache = Path(__file__).resolve().parent.parent / "model_cache"
    names = [
        "lstm_model.pkl",
        "svm_model.pkl",
        "linear_regression_model.pkl",
        "arima_model.pkl",
    ]

    print(f"Cache dir: {cache}")

    for name in names:
        p = cache / name
        print("\n" + name)
        if not p.exists():
            print("  MISSING")
            continue

        with open(p, "rb") as f:
            obj = pickle.load(f)

        print("  type:", type(obj))
        if isinstance(obj, dict):
            print("  keys:", list(obj.keys()))
            for k in [
                "model",
                "metrics",
                "scaler_X",
                "scaler_y",
                "scaler",
                "cached_at",
                "cache_expires",
            ]:
                if k in obj:
                    print(f"  has {k}:", type(obj[k]))


if __name__ == "__main__":
    main()
