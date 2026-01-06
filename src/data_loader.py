import sqlite3
from typing import Any, Dict, List, Optional, Sequence, Tuple
import pandas as pd
import numpy as np

DB_PATH = "data/spotify_database.db"

def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def fetch_all(conn: sqlite3.Connection, query: str, params: Sequence[Any] = ()) -> List[Dict[str, Any]]:
    cur = conn.cursor()
    cur.execute(query, params)
    return [dict(r) for r in cur.fetchall()]

def fetch_one(conn: sqlite3.Connection, query: str, params: Sequence[Any] = ()) -> Optional[Dict[str, Any]]:
    cur = conn.cursor()
    cur.execute(query, params)
    row = cur.fetchone()
    return dict(row) if row else None

def get_filter_options(conn: sqlite3.Connection) -> Dict[str, Any]:
    years = fetch_one(
        conn,
        "SELECT MIN(release_year) AS min_year, MAX(release_year) AS max_year FROM tracks WHERE release_year IS NOT NULL",
    )

    genres = fetch_all(
        conn,
        "SELECT DISTINCT primary_genre FROM artists WHERE primary_genre IS NOT NULL ORDER BY primary_genre",
    )

    album_types = fetch_all(
        conn,
        "SELECT DISTINCT album_type FROM tracks WHERE album_type IS NOT NULL ORDER BY album_type",
    )

    return {
        "min_year": int(years["min_year"]) if years and years["min_year"] else 1950,
        "max_year": int(years["max_year"]) if years and years["max_year"] else 2025,
        "genres": [g["primary_genre"] for g in genres],
        "album_types": [a["album_type"] for a in album_types],
    }


def build_where_clause(
    selected_genres: List[str],
    selected_album_types: List[str],
    year_min: int,
    year_max: int,
    pop_min: int,
    pop_max: int,
    explicit_choice: str,
) -> Tuple[str, List[Any]]:

    clauses = []
    params: List[Any] = []

    if selected_genres:
        placeholders = ",".join("?" * len(selected_genres))
        clauses.append(f"a.primary_genre IN ({placeholders})")
        params.extend(selected_genres)

    if selected_album_types:
        placeholders = ",".join("?" * len(selected_album_types))
        clauses.append(f"t.album_type IN ({placeholders})")
        params.extend(selected_album_types)

    clauses.append("t.track_popularity BETWEEN ? AND ?")
    params.extend([pop_min, pop_max])

    clauses.append("t.release_year BETWEEN ? AND ?")
    params.extend([year_min, year_max])

    if explicit_choice == "Explicit only":
        clauses.append("t.explicit = 1")
    elif explicit_choice == "Non-explicit only":
        clauses.append("t.explicit = 0")

    where_sql = "WHERE " + " AND ".join(clauses) if clauses else ""
    return where_sql, params


def get_joined_rows(
    conn: sqlite3.Connection,
    selected_genres: List[str],
    selected_album_types: List[str],
    year_min: int,
    year_max: int,
    pop_min: int,
    pop_max: int,
    explicit_choice: str,
    limit: Optional[int] = None,
) -> List[Dict[str, Any]]:

    where_sql, params = build_where_clause(
        selected_genres,
        selected_album_types,
        year_min,
        year_max,
        pop_min,
        pop_max,
        explicit_choice,
    )

    limit_sql = f"LIMIT {limit}" if limit else ""

    query = f"""
    SELECT
        t.track_name,
        t.track_popularity,
        t.track_duration_min,
        t.explicit,
        t.release_year,
        t.album_type,
        a.artist_name,
        a.primary_genre,
        a.artist_popularity,
        a.artist_followers
    FROM tracks t
    JOIN artists a ON t.artist_id = a.artist_id
    {where_sql}
    {limit_sql}
    """

    return fetch_all(conn, query, params)


def get_overview_metrics(
    conn: sqlite3.Connection,
    where_sql: str,
    params: Sequence[Any],
) -> Dict[str, Any]:

    query = f"""
    SELECT
        COUNT(*) AS tracks,
        COUNT(DISTINCT a.artist_name) AS unique_artists,
        AVG(t.track_popularity) AS avg_popularity,
        SUM(CASE WHEN t.track_popularity = 0 THEN 1 ELSE 0 END) AS zero_popularity_count
    FROM tracks t
    JOIN artists a ON t.artist_id = a.artist_id
    {where_sql}
    """
    row = fetch_one(conn, query, params)

    return {
        "tracks": int(row["tracks"] or 0),
        "unique_artists": int(row["unique_artists"] or 0),
        "avg_popularity": float(row["avg_popularity"] or 0.0),
        "zero_popularity_count": int(row["zero_popularity_count"] or 0),
    }


def sql_quantiles_track_popularity(
    conn: sqlite3.Connection,
    where_sql: str,
    params: Sequence[Any],
) -> List[Dict[str, Any]]:

    quantiles = [0.10, 0.25, 0.50, 0.75, 0.90]
    results = []

    count_row = fetch_one(
        conn,
        f"""
        SELECT COUNT(*) AS n
        FROM tracks t
        JOIN artists a ON t.artist_id = a.artist_id
        {where_sql}
        """,
        params,
    )

    n = int(count_row["n"]) if count_row and count_row["n"] else 0
    if n == 0:
        return []

    for q in quantiles:
        offset = int((n - 1) * q)
        row = fetch_one(
            conn,
            f"""
            SELECT t.track_popularity AS value
            FROM tracks t
            JOIN artists a ON t.artist_id = a.artist_id
            {where_sql}
            ORDER BY t.track_popularity
            LIMIT 1 OFFSET {offset}
            """,
            params,
        )
        results.append({"quantile": q, "value": row["value"] if row else None})

    return results


def sql_yearly_agg(conn, where_sql, params):
    query = f"""
    SELECT
        t.release_year,
        AVG(t.track_popularity) AS mean,
        COUNT(*) AS count
    FROM tracks t
    JOIN artists a ON t.artist_id = a.artist_id
    {where_sql}
      AND t.release_year IS NOT NULL
    GROUP BY t.release_year
    ORDER BY t.release_year
    """
    return fetch_all(conn, query, params)


def sql_top_avg_genres(conn, where_sql, params, exclude_unknown=True):
    extra = "AND a.primary_genre != 'Unknown'" if exclude_unknown else ""
    query = f"""
    SELECT
        a.primary_genre,
        AVG(t.track_popularity) AS avg_popularity,
        COUNT(*) AS num_tracks
    FROM tracks t
    JOIN artists a ON t.artist_id = a.artist_id
    {where_sql}
      {extra}
    GROUP BY a.primary_genre
    ORDER BY avg_popularity DESC
    LIMIT 10
    """
    return fetch_all(conn, query, params)


def sql_genre_frequency(conn, where_sql, params, exclude_unknown=True):
    extra = "AND a.primary_genre != 'Unknown'" if exclude_unknown else ""
    query = f"""
    SELECT
        a.primary_genre,
        COUNT(*) AS num_tracks
    FROM tracks t
    JOIN artists a ON t.artist_id = a.artist_id
    {where_sql}
      {extra}
    GROUP BY a.primary_genre
    ORDER BY num_tracks DESC
    LIMIT 10
    """
    return fetch_all(conn, query, params)


def sql_explicit_summary(conn, where_sql, params):
    query = f"""
    SELECT
        t.explicit,
        AVG(t.track_popularity) AS avg_popularity,
        COUNT(*) AS num_tracks
    FROM tracks t
    JOIN artists a ON t.artist_id = a.artist_id
    {where_sql}
    GROUP BY t.explicit
    """
    return fetch_all(conn, query, params)


def sql_popularity_over_time(conn, where_sql, params):
    query = f"""
    SELECT
        t.release_year,
        AVG(t.track_popularity) AS avg_popularity,
        COUNT(*) AS num_tracks
    FROM tracks t
    JOIN artists a ON t.artist_id = a.artist_id
    {where_sql}
      AND t.release_year IS NOT NULL
    GROUP BY t.release_year
    ORDER BY t.release_year
    """
    return fetch_all(conn, query, params)

def sql_median_track_popularity(conn, where_sql: str, params):
    count_row = fetch_one(
        conn,
        f"""
        SELECT COUNT(*) AS n
        FROM tracks t
        JOIN artists a ON t.artist_id = a.artist_id
        {where_sql}
        """,
        params,
    )

    n = int(count_row["n"] or 0)
    if n == 0:
        return None

    offset = (n - 1) // 2

    row = fetch_one(
        conn,
        f"""
        SELECT t.track_popularity
        FROM tracks t
        JOIN artists a ON t.artist_id = a.artist_id
        {where_sql}
        ORDER BY t.track_popularity
        LIMIT 1 OFFSET {offset}
        """,
        params,
    )

    return float(row["track_popularity"]) if row else None

def fetch_dashboard_data(
    conn,
    selected_genres,
    selected_album_types,
    year_min,
    year_max,
    pop_min,
    pop_max,
    explicit_choice,
    exclude_unknown_genre,
):
    where_sql, params = build_where_clause(
        selected_genres,
        selected_album_types,
        year_min,
        year_max,
        pop_min,
        pop_max,
        explicit_choice,
    )

    return {
        "where_sql": where_sql,
        "params": params,
        "metrics": get_overview_metrics(conn, where_sql, params),
        "median_popularity": sql_median_track_popularity(conn, where_sql, params),
        "rows_full": get_joined_rows(
            conn,
            selected_genres,
            selected_album_types,
            year_min,
            year_max,
            pop_min,
            pop_max,
            explicit_choice,
            limit=None,
        ),
        "rows_sample": get_joined_rows(
            conn,
            selected_genres,
            selected_album_types,
            year_min,
            year_max,
            pop_min,
            pop_max,
            explicit_choice,
        ),
        "quantiles": sql_quantiles_track_popularity(conn, where_sql, params),
        "yearly_agg": sql_yearly_agg(conn, where_sql, params),
        "top_avg_genres": sql_top_avg_genres(
            conn, where_sql, params, exclude_unknown=exclude_unknown_genre
        ),
        "genre_freq": sql_genre_frequency(
            conn, where_sql, params, exclude_unknown=exclude_unknown_genre
        ),
        "explicit_summary": sql_explicit_summary(conn, where_sql, params),
        "popularity_over_time": sql_popularity_over_time(conn, where_sql, params),
    }

def sql_popularity_buckets(conn, where_sql, params):
    query = f"""
    SELECT
        CASE
            WHEN t.track_popularity <= 30 THEN 'Low'
            WHEN t.track_popularity <= 60 THEN 'Medium'
            ELSE 'High'
        END AS popularity_bucket,
        COUNT(*) AS num_tracks
    FROM tracks t
    JOIN artists a ON t.artist_id = a.artist_id
    {where_sql}
    GROUP BY popularity_bucket
    ORDER BY num_tracks DESC
    """
    return fetch_all(conn, query, params)

def sql_rule_based_hit_evaluation(conn, where_sql, params):
    """
    Returns raw data needed for rule-based hit evaluation.
    Percentile cutoff is computed in Python (not SQL).
    """

    query = f"""
    SELECT
        t.track_name,
        t.track_popularity,
        a.artist_popularity,
        a.artist_followers
    FROM tracks t
    JOIN artists a ON t.artist_id = a.artist_id
    {where_sql}
    """

    rows = fetch_all(conn, query, params)
    return rows

def sql_similarity_reference(conn, where_sql, params):
    """
    Returns rows needed for normalized similarity comparison.
    """
    query = f"""
    SELECT
        t.track_name,
        t.track_popularity,
        t.track_duration_min,
        a.artist_name,
        a.artist_popularity,
        a.artist_followers
    FROM tracks t
    JOIN artists a ON t.artist_id = a.artist_id
    {where_sql}
    """
    return fetch_all(conn, query, params)

def sql_global_reference_track(conn):
    """
    Returns a single globally popular reference track
    (independent of filters).
    """
    query = """
    SELECT
        t.track_name,
        t.track_popularity,
        t.track_duration_min,
        a.artist_name,
        a.artist_popularity,
        a.artist_followers
    FROM tracks t
    JOIN artists a ON t.artist_id = a.artist_id
    WHERE t.track_popularity IS NOT NULL
      AND a.artist_popularity IS NOT NULL
      AND a.artist_followers IS NOT NULL
    ORDER BY
        t.track_popularity DESC,
        a.artist_popularity DESC,
        a.artist_followers DESC
    LIMIT 1
    """
    return fetch_one(conn, query)
