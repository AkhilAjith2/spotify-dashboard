# Spotify Track Popularity Dashboard

**Student:** Akhil Ambalapurath Ajith (487806)

## Project Description

This project explores the factors associated with Spotify track popularity using exploratory data analysis and SQL-based aggregation. The goal is not to predict popularity, but to understand structural patterns that characterize successful songs on the platform.

The analysis focuses on:

- How popularity is distributed across tracks
- How artist-level characteristics (popularity and follower count) relate to track success
- Whether explicit content influences popularity
- How genre, album type, and release period are associated with performance
- Whether simple rule-based logic can identify potential hit songs

The results are presented through an interactive Streamlit dashboard that mirrors the insights obtained in the accompanying Jupyter notebook. SQL is used extensively to compute summary statistics and aggregations, while visualizations are built using Plotly to maintain a clean, Spotify-inspired design.

## Dataset

**Original dataset source:**  
[Spotify Global Music Dataset (2009–2025)](https://www.kaggle.com/datasets/wardabilal/spotify-global-music-dataset-20092025?select=track_data_final.csv)

> **Note:** Dataset file names were kept consistent with the original download. The raw dataset is processed and transformed within the notebook before being stored in a SQLite database.

## How to Run

### 1. Create a Virtual Environment

First, create and activate a virtual environment to isolate your project dependencies:

```bash
python -m venv venv
```

Then activate it:

**On Windows:**

```bash
venv\Scripts\activate
```

**On macOS/Linux:**

```bash
source venv/bin/activate
```

### 2. Install Requirements

Make sure you have Python 3.13 or newer installed, then install all required dependencies:

```bash
pip install -r requirements.txt
```

### 3. Run the Notebook (Data Preparation)

1. Download `track_data_final.csv` from Kaggle and place it inside the `data/` folder
2. Open the Jupyter notebook: `Final Project Notebook.ipynb`
3. **Important:** Select the kernel version to match your Python installation. If you're using Python 3.13.7, select that kernel version from the notebook's kernel selector (top-right corner)
4. Run all cells in the notebook

This notebook:

- Cleans and preprocesses the raw Spotify dataset
- Performs exploratory data analysis
- Creates and populates the SQLite database (`spotify_database.db`) used by the dashboard

> **Important:** This step must be completed before running the Streamlit app.

### 4. Run the Dashboard

After the database has been created, start the Streamlit application:

```bash
streamlit run app.py
```

The interactive dashboard will open in your browser and allow you to explore the analysis using filters, charts, tables, and a final interpretation section.
