import pandas as pd

def safe_float(x, default=0.0) -> float:
    try:
        if x is None:
            return default
        return float(x)
    except Exception:
        return default

def compute_correlation_matrix(rows):
    # Computes correlation matrix for key popularity and track features
    """
    rows: List[dict] from SQL
    returns: Pandas DataFrame correlation matrix
    """
    df = pd.DataFrame(rows)

    cols = [
        "track_popularity",
        "artist_popularity",
        "artist_followers",
        "track_duration_min",
    ]

    df = df[cols].dropna()

    return df.corr()
