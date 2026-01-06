import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

SPOTIFY_GREEN = "#1DB954"
BG_COLOR = "#121212"
TEXT_COLOR = "#FFFFFF"
SPOTIFY_COLORSCALE = [
        [0.0, "#013F00"],
        [0.5, "#027500"],
        [1.0, "#00FF59"],
    ]


def _base_layout(fig):
    fig.update_layout(
        plot_bgcolor=BG_COLOR,
        paper_bgcolor=BG_COLOR,

        xaxis=dict(
            title_font=dict(size=16),
            tickfont=dict(size=16),
        ),
        yaxis=dict(
            title_font=dict(size=16),
            tickfont=dict(size=16),
        ),

        height=500,
        margin=dict(l=80, r=40, t=80, b=60),
    )

    return fig


def fig_hist_popularity(rows):
    df = pd.DataFrame(rows)

    fig = px.histogram(
        df,
        x="track_popularity",
        nbins=20,
        marginal="box",
        color_discrete_sequence=[SPOTIFY_GREEN],
    )
    fig.update_traces(
        marker_line_color="#000000",
        marker_line_width=2
    )
    return _base_layout(fig)

def fig_corr_heatmap(corr_df):
    # Displays correlation matrix with custom Spotify color gradient
    spotify_colorscale = [
        [0.0, "#000000"],
        [0.25, "#151d24"],
        [0.5, "#141010"],
        [0.75, "#127535"],
        [1.0, "#2cff7a"],
    ]

    fig = go.Figure(
        data=go.Heatmap(
            z=corr_df.values,
            x=corr_df.columns,
            y=corr_df.index,
            colorscale=spotify_colorscale,
            zmid=0,
            text=corr_df.round(2).values,
            texttemplate="%{text}",
            textfont=dict(size=20),
        )
    )

    fig.update_layout(
        template="plotly_dark",
        height=500,
        font=dict(size=16),
        xaxis=dict(
            side="top",
            tickfont=dict(size=16),
            title_font=dict(size=16),
        ),
        yaxis=dict(
            autorange="reversed",
            tickfont=dict(size=16),
            title_font=dict(size=16),
        ),
        margin=dict(l=80, r=40, t=80, b=60),
    )

    return fig

def fig_line_popularity_over_time(rows):
    df = pd.DataFrame(rows)
    fig = px.line(
        df,
        x="release_year",
        y="avg_popularity",
        markers=True,
    )
    fig.update_traces(line_color=SPOTIFY_GREEN)
    return _base_layout(fig)


def fig_box_popularity_over_time(rows):
    df = pd.DataFrame(rows)
    fig = px.box(
        df,
        x="release_year",
        y="track_popularity",
    )
    return _base_layout(fig)


def fig_box_explicit(rows):
    df = pd.DataFrame(rows)
    fig = px.box(
        df,
        x="explicit",
        y="track_popularity",
        color_discrete_sequence=[SPOTIFY_GREEN],
    )
    return _base_layout(fig)


def fig_bar_top_avg_genres(rows):
    # Ranks genres by average track popularity using color intensity
    df = pd.DataFrame(rows)
    df = df.sort_values("avg_popularity", ascending=True)

    fig = px.bar(
        df,
        x="avg_popularity",
        y="primary_genre",
        orientation="h",
        color="avg_popularity",
        color_continuous_scale=SPOTIFY_COLORSCALE,
    )

    fig.update_layout(coloraxis_showscale=False)

    return _base_layout(fig)

def fig_bar_genre_frequency(rows):
    # Identifies most common genres in filtered dataset
    df = pd.DataFrame(rows)
    df = df.sort_values("num_tracks", ascending=True)

    fig = px.bar(
        df,
        x="num_tracks",
        y="primary_genre",
        orientation="h",
        color="num_tracks",
        color_continuous_scale=SPOTIFY_COLORSCALE,
    )

    fig.update_layout(coloraxis_showscale=False)


    return _base_layout(fig)

def fig_scatter_artist_vs_track(rows):
    df = pd.DataFrame(rows)
    fig = px.scatter(
        df,
        x="artist_popularity",
        y="track_popularity",
        opacity=0.6,
        color_discrete_sequence=[SPOTIFY_GREEN],
    )
    return _base_layout(fig)


def fig_scatter_followers_vs_track(rows):
    df = pd.DataFrame(rows)
    fig = px.scatter(
        df,
        x="artist_followers",
        y="track_popularity",
        opacity=0.6,
        color_discrete_sequence=[SPOTIFY_GREEN],
    )
    fig.update_xaxes(type="log")
    return _base_layout(fig)


def fig_scatter_duration_vs_pop(rows):
    df = pd.DataFrame(rows)
    fig = px.scatter(
        df,
        x="track_duration_min",
        y="track_popularity",
        opacity=0.6,
        color_discrete_sequence=[SPOTIFY_GREEN],
    )
    return _base_layout(fig)


def fig_box_album_type(rows):
    df = pd.DataFrame(rows)
    fig = px.box(
        df,
        x="album_type",
        y="track_popularity",
        color_discrete_sequence=[SPOTIFY_GREEN],
    )
    return _base_layout(fig)


def fig_top_artists_index(df):
    # Visualizes normalized artist popularity index using rank-based coloring
    df = df.sort_values("artist_popularity_index", ascending=True)
    df["rank_color"] = range(len(df))

    fig = px.bar(
        df,
        x="artist_popularity_index",
        y="artist_name",
        orientation="h",
        color="rank_color",
        color_continuous_scale=SPOTIFY_COLORSCALE,
    )

    fig.update_layout(coloraxis_showscale=False)

    return _base_layout(fig)

