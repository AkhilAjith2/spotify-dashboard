#### Kaggle link: https://www.kaggle.com/datasets/wardabilal/spotify-global-music-dataset-20092025?select=track_data_final.csv

import streamlit as st

from src.data_loader import (
    get_connection,
    get_filter_options,
    fetch_dashboard_data,
    sql_popularity_buckets,
     sql_rule_based_hit_evaluation,
    sql_similarity_reference,
)
from src.preprocessing import compute_correlation_matrix
from src import plots
from src import text
import pandas as pd
import numpy as np
from numpy.linalg import norm

# -----------------------------
# Page configuration
# -----------------------------

st.set_page_config(
    page_title="Spotify Track Popularity Dashboard",
    page_icon="assets/spotify_icon.png",
    layout="wide",
)

# -----------------------------
# Theme
# -----------------------------

st.markdown(
    """
    <style>
    .stApp {
        background-color: #121212;
        color: #FFFFFF;
    }

    .block-container {
        padding-top: 2rem;
    }

    [data-testid="stSidebar"] {
        background-color: #0E0E0E;
    }

    .stMarkdown h1,
    .stMarkdown h2,
    .stMarkdown h3,
    .stMarkdown h4,
    .stMarkdown h5,
    .stMarkdown h6 {
        color: #1DB954 !important;
    }

    .spotify-note {
        background-color: rgba(29, 185, 84, 0.1);
        border-left: 4px solid #1DB954;
        padding: 12px 16px;
        margin: 16px 0;
        border-radius: 6px;
        color: #FFFFFF;
        font-size: 15px;
        line-height: 1.5;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Intro
# -----------------------------

st.markdown(text.INTRO)
st.markdown(
    """
    <div class="spotify-note">
        All filters apply to every chart and table.
        The written interpretations are based on the full dataset with no filters applied.
        Clear the filters to see the results in their original context.
    </div>
    """,
    unsafe_allow_html=True,
)


# -----------------------------
# Load filter options
# -----------------------------

with get_connection() as conn:
    opts = get_filter_options(conn)

# -----------------------------
# Sidebar filters
# -----------------------------

st.sidebar.header("Filters")

year_min, year_max = st.sidebar.slider(
    "Release year",
    min_value=opts["min_year"],
    max_value=opts["max_year"],
    value=(opts["min_year"], opts["max_year"]),
)

pop_min, pop_max = st.sidebar.slider(
    "Track popularity",
    min_value=0,
    max_value=100,
    value=(0, 100),
)

selected_album_types = st.sidebar.multiselect(
    "Album type(s)",
    opts["album_types"],
)

selected_genres = st.sidebar.multiselect(
    "Genre(s)",
    opts["genres"],
)

explicit_choice = st.sidebar.selectbox(
    "Explicit filter",
    ["All", "Explicit only", "Non-explicit only"],
    index=0,
)

exclude_unknown_genre = st.sidebar.checkbox(
    "Exclude 'Unknown' genre in genre charts",
    value=True,
)

# -----------------------------
# Query database
# -----------------------------

with get_connection() as conn:

    data = fetch_dashboard_data(
        conn,
        selected_genres,
        selected_album_types,
        year_min,
        year_max,
        pop_min,
        pop_max,
        explicit_choice,
        exclude_unknown_genre,
    )

    where_sql = data["where_sql"]
    params = data["params"]

    sim_rows = sql_similarity_reference(conn, where_sql, params)
    hit_rows = sql_rule_based_hit_evaluation(conn, where_sql, params)
    popularity_buckets = sql_popularity_buckets(conn, where_sql, params)

hit_df = pd.DataFrame(hit_rows)

metrics = data["metrics"]
median_popularity = data["median_popularity"]
rows_for_hist = data["rows_full"]
sample_rows = data["rows_sample"]
quantiles = data["quantiles"]
yearly_agg = data["yearly_agg"]
top_avg_genres = data["top_avg_genres"]
genre_freq = data["genre_freq"]
explicit_summary = data["explicit_summary"]
pop_over_time = data["popularity_over_time"]

if not sample_rows:
    st.warning(
        "No tracks match the selected filters. "
        "Try expanding the release year range or choosing a different album type."
    )
    st.stop()


# -----------------------------
# Overview metrics
# -----------------------------

st.markdown(
    "<h2 style='color:#1DB954;'>Overview</h2>",
    unsafe_allow_html=True,
)

def spotify_metric(label, value):
    st.markdown(
        f"""
        <div style="margin-bottom:20px;">
            <div style="color:#1DB954; font-size:14px; font-weight:600;">
                {label}
            </div>
            <div style="color:white; font-size:32px; font-weight:700;">
                {value}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


c1, c2, c3, c4 = st.columns(4)

with c1:
    spotify_metric("Tracks", f"{metrics['tracks']:,}")

with c2:
    spotify_metric("Unique Artists", f"{metrics['unique_artists']:,}")

with c3:
    spotify_metric("Avg Popularity", f"{metrics['avg_popularity']:.2f}")

with c4:
    spotify_metric(
        "Median Popularity",
        f"{median_popularity:.2f}" if median_popularity is not None else "N/A",
    )

# -----------------------------
# Tabs
# -----------------------------

tab_eda, tab_rules, tab_tables, tab_final = st.tabs(
    ["EDA Visuals", "Rule-Based Analysis", "Summary Tables", "Final Interpretation"]
)

# -----------------------------
# EDA VISUALS
# -----------------------------

with tab_eda:

    # 1) Top 10 artists by popularity index

    artist_agg = (
        pd.DataFrame(sample_rows)
        .groupby("artist_name")
        .agg(
            avg_artist_popularity=("artist_popularity", "mean"),
            avg_artist_followers=("artist_followers", "mean"),
            track_count=("track_name", "count"),
        )
        .reset_index()
    )

    # Log-transform followers to handle wide range and normalize all features
    artist_agg["followers_log"] = np.log10(artist_agg["avg_artist_followers"] + 1)

    features = ["avg_artist_popularity", "followers_log", "track_count"]
    for col in features:
        min_val = artist_agg[col].min()
        max_val = artist_agg[col].max()

        if max_val > min_val:
            artist_agg[col + "_norm"] = (artist_agg[col] - min_val) / (max_val - min_val)
        else:
            artist_agg[col + "_norm"] = 0.5

    # Weighted index: 50% artist popularity, 30% followers, 20% track count
    artist_agg["artist_popularity_index"] = (
        0.5 * artist_agg["avg_artist_popularity_norm"]
        + 0.3 * artist_agg["followers_log_norm"]
        + 0.2 * artist_agg["track_count_norm"]
    )

    top_artists = artist_agg.sort_values(
        "artist_popularity_index", ascending=False
    ).head(10)

    st.markdown(text.TOP_ARTISTS_TITLE)
    st.markdown(text.TOP_ARTISTS_INTRO)

    fig = plots.fig_top_artists_index(
        top_artists.sort_values("artist_popularity_index", ascending=True)
    )

    if artist_agg.shape[0] < 3:
        st.info("Not enough artists in this filter to compute a meaningful popularity ranking.")
    else:
        st.plotly_chart(fig, width="stretch")

    st.markdown(text.TOP_ARTISTS_INTERPRETATION)
    st.divider()

    # 2) Popularity distribution
    col_plot, col_text = st.columns([2, 1])
    with col_plot:
        st.plotly_chart(
            plots.fig_hist_popularity(rows_for_hist),
            width='stretch',
            key="pop_dist",
        )
    with col_text:
        st.markdown(text.POPULARITY_DIST)

    # 3) Correlation matrix
    col_text, col_plot = st.columns([1, 2])
    with col_plot:
        corr = compute_correlation_matrix(rows_for_hist)
        st.plotly_chart(
            plots.fig_corr_heatmap(corr),
            width='stretch',
            key="corr_matrix",
        )
    with col_text:
        st.markdown(text.CORR_MATRIX)

    # 4) Popularity over time
    col_plot, col_text = st.columns([2, 1])
    with col_plot:
        st.plotly_chart(
            plots.fig_line_popularity_over_time(pop_over_time),
            width='stretch',
            key="pop_time_line",
        )
    with col_text:
        st.markdown(text.POPULARITY_OVER_TIME)

    # 5) Explicit vs non-explicit
    col_text, col_plot = st.columns([1, 2])
    with col_plot:
        st.plotly_chart(
            plots.fig_box_explicit(sample_rows),
            width='stretch',
            key="explicit_box",
        )
    with col_text:
        st.markdown(text.EXPLICIT_COMPARISON)

    # 6) Avg popularity by genre
    col_plot, col_text = st.columns([2, 1])
    with col_plot:
        st.plotly_chart(
            plots.fig_bar_top_avg_genres(top_avg_genres),
            width='stretch',
            key="genre_avg",
        )
    with col_text:
        st.markdown(text.TOP_GENRES_AVG)

    # 7) Genre frequency
    col_text, col_plot = st.columns([1, 2])
    with col_plot:
        st.plotly_chart(
            plots.fig_bar_genre_frequency(genre_freq),
            width='stretch',
            key="genre_freq",
        )
    with col_text:
        st.markdown(text.GENRE_FREQUENCY)

    # 8) Artist popularity vs track popularity
    col_plot, col_text = st.columns([2, 1])
    with col_plot:
        st.plotly_chart(
            plots.fig_scatter_artist_vs_track(sample_rows),
            width='stretch',
            key="artist_vs_track",
        )
    with col_text:
        st.markdown(text.ARTIST_VS_TRACK)

    # 9) Followers vs track popularity
    col_text, col_plot = st.columns([1, 2])
    with col_plot:
        st.plotly_chart(
            plots.fig_scatter_followers_vs_track(sample_rows),
            width='stretch',
            key="followers_vs_track",
        )
    with col_text:
        st.markdown(text.FOLLOWERS_VS_TRACK)

    # 10) Duration vs popularity
    col_plot, col_text = st.columns([2, 1])
    with col_plot:
        st.plotly_chart(
            plots.fig_scatter_duration_vs_pop(sample_rows),
            width='stretch',
            key="duration_vs_pop",
        )
    with col_text:
        st.markdown(text.DURATION_VS_POP)

    # 11) Album type
    col_text, col_plot = st.columns([1, 2])
    with col_plot:
        st.plotly_chart(
            plots.fig_box_album_type(sample_rows),
            width='stretch',
            key="album_type",
        )
    with col_text:
        st.markdown(text.ALBUM_TYPE)

# -----------------------------
# Summary Tables
# -----------------------------

with tab_tables:

    st.markdown("### Popularity Distribution (SQL Quantiles)")
    st.markdown(text.TABLE_QUANTILES_DESC)

    if quantiles:
        q_df = (
            pd.DataFrame(quantiles)
            .assign(
                percentile=lambda d: (d["quantile"] * 100).astype(int).astype(str) + "%"
            )
            .rename(columns={"value": "Popularity"})
            [["percentile", "Popularity"]]
        )
        st.dataframe(q_df, width="stretch", hide_index=True)
    else:
        st.warning("No data available for the selected filters.")

    st.divider()
    
    st.markdown("### Explicit vs Non-Explicit Tracks")
    st.markdown(text.TABLE_EXPLICIT_DESC)
    st.dataframe(explicit_summary, width="stretch", hide_index=True)

    st.divider()

    st.markdown("### Genre-Level Summary")
    st.markdown(text.TABLE_GENRE_DESC)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<h5 style='color:#1DB954;'>Top Genres by Average Popularity</h5>", unsafe_allow_html=True)
        st.dataframe(top_avg_genres, width="stretch", hide_index=True)

    with col2:
        st.markdown("<h5 style='color:#1DB954;'>Most Frequent Genres</h5>", unsafe_allow_html=True)
        st.dataframe(genre_freq, width="stretch", hide_index=True)

    st.divider()

    st.markdown("### Yearly Aggregation")
    st.markdown(text.TABLE_YEARLY_DESC)
    st.dataframe(yearly_agg, width="stretch", hide_index=True)

# -----------------------------
# Rule-Based Analysis
# -----------------------------

with tab_rules:

    st.markdown("## Rule-Based Classification & Similarity Analysis")

    st.markdown(text.RULES_INTRO)

    st.divider()

    # -----------------------------
    # Popularity Buckets
    # -----------------------------

    st.markdown("### Popularity Buckets")

    st.markdown(text.RULES_BUCKETS_INTRO)
    
    bucket_df = pd.DataFrame(popularity_buckets)
    st.dataframe(bucket_df, width="stretch", hide_index=True)

    st.markdown(text.RULES_BUCKETS_INTERPRETATION)

    st.divider()

    # -----------------------------
    # Rule-Based Hit Identification 
    # -----------------------------

    st.markdown("### Rule-Based Hit Identification")

    df_eval = pd.DataFrame(sample_rows)

    # Define a hit as top 30% by popularity; predict hits based on artist metrics
    HIT_PERCENTILE = 0.70
    hit_cutoff = df_eval["track_popularity"].quantile(HIT_PERCENTILE)

    df_eval["true_hit"] = (df_eval["track_popularity"] >= hit_cutoff).astype(int)

    # Rule: artists with popularity >= 75 and followers >= 1M are likely to produce hits
    df_eval["predicted_hit"] = (
        (df_eval["artist_popularity"] >= 75) &
        (df_eval["artist_followers"] >= 1_000_000)
    ).astype(int)

    st.markdown(text.RULES_HIT_DESCRIPTION)

    tp = ((df_eval["predicted_hit"] == 1) & (df_eval["true_hit"] == 1)).sum()
    fp = ((df_eval["predicted_hit"] == 1) & (df_eval["true_hit"] == 0)).sum()
    tn = ((df_eval["predicted_hit"] == 0) & (df_eval["true_hit"] == 0)).sum()
    fn = ((df_eval["predicted_hit"] == 0) & (df_eval["true_hit"] == 1)).sum()

    confusion_df = pd.DataFrame(
        {
            "Predicted Hit": [tp, fp],
            "Predicted Non-Hit": [fn, tn],
        },
        index=["Actual Hit", "Actual Non-Hit"],
    )

    st.markdown("#### Confusion Matrix")
    st.dataframe(confusion_df, width="stretch")

    accuracy = (tp + tn) / (tp + tn + fp + fn)
    precision = tp / (tp + fp) if (tp + fp) else 0
    recall = tp / (tp + fn) if (tp + fn) else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("Accuracy", f"{accuracy:.2f}")
    c2.metric("Precision", f"{precision:.2f}")
    c3.metric("Recall", f"{recall:.2f}")

    st.markdown(text.RULES_HIT_INTERPRETATION)

    st.divider()

    # -----------------------------
    # Normalized Similarity Comparison
    # -----------------------------

    st.markdown("### Normalized Similarity Comparison")
    st.markdown(text.RULES_SIMILARITY_INTRO)


    sim_df = pd.DataFrame(sim_rows)

    sim_df["artist_followers_log"] = np.log10(sim_df["artist_followers"] + 1)

    POPULARITY_THRESHOLD = sim_df["track_popularity"].quantile(0.99)

    # Select reference track from top 1% most popular tracks with artist popularity >= 80
    very_popular_tracks = sim_df[
        (sim_df["track_popularity"] >= POPULARITY_THRESHOLD) &
        (sim_df["artist_popularity"] >= 80)
    ].sort_values("track_popularity", ascending=False)

    if very_popular_tracks.empty:
        st.warning("No suitable reference track found for similarity comparison.")
        st.stop()

    reference_track = very_popular_tracks.iloc[0]

    st.markdown("#### Reference Track (Anchor for Similarity)")

    st.dataframe(
        reference_track[
            [
                "track_name",
                "artist_name",
                "track_popularity",
                "artist_popularity",
                "artist_followers",
                "track_duration_min",
            ]
        ].to_frame().T,
        hide_index=True,
        width="stretch",
    )

    features = [
        "artist_popularity",
        "artist_followers_log",
        "track_duration_min",
    ]

    df_norm = sim_df.copy()

    for col in features:
        min_val = df_norm[col].min()
        max_val = df_norm[col].max()
        df_norm[col] = (df_norm[col] - min_val) / (max_val - min_val)

    reference_track_norm = df_norm.loc[reference_track.name]

    def normalized_similarity_score(row, reference):
        return norm(row[features].values - reference[features].values)

    sim_df["similarity_to_popular_song"] = df_norm.apply(
        normalized_similarity_score,
        axis=1,
        reference=reference_track_norm
    )

    st.dataframe(
        sim_df[
            [
                "track_name",
                "artist_name",
                "track_popularity",
                "artist_popularity",
                "artist_followers",
                "track_duration_min",
                "similarity_to_popular_song",
            ]
        ].sort_values("similarity_to_popular_song"),
        width="stretch",
        hide_index=True,
    )

    st.markdown(text.RULES_SIMILARITY_INTERPRETATION)

# -----------------------------
# Final Interpretation
#-----------------------------

with tab_final:

    st.markdown(text.FINAL_INTERPRETATION_TITLE, unsafe_allow_html=True)
    st.markdown(text.FINAL_INTERPRETATION_INTRO)

    st.divider()

    st.markdown(text.RQ1_TITLE, unsafe_allow_html=True)
    st.markdown(text.RQ1_TEXT)

    st.divider()

    st.markdown(text.RQ2_TITLE, unsafe_allow_html=True)
    st.markdown(text.RQ2_TEXT)

    st.divider()

    st.markdown(text.RQ3_TITLE, unsafe_allow_html=True)
    st.markdown(text.RQ3_TEXT)

    st.divider()

    st.markdown(text.RQ4_TITLE, unsafe_allow_html=True)
    st.markdown(text.RQ4_TEXT)

    st.divider()

    st.markdown(text.RQ5_TITLE, unsafe_allow_html=True)
    st.markdown(text.RQ5_TEXT)

    st.divider()

    st.markdown(text.CONCLUSION_TITLE, unsafe_allow_html=True)
    st.markdown(text.CONCLUSION_TEXT)
