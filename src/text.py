INTRO = """
# Spotify Track Popularity Dashboard

In this dashboard, I explore a Spotify track dataset to understand which factors are associated with higher song popularity.
The analysis mirrors my notebook, but is presented interactively using SQL queries and visualizations.
"""

POPULARITY_DIST = """
### Distribution of Track Popularity

The distribution of track popularity is clearly uneven. A very noticeable spike appears at popularity values close to 0, indicating that a substantial number of tracks receive little to no engagement. This suggests that many songs in the dataset are either very new, obscure, or have not accumulated enough listens to register a meaningful popularity score.

Beyond this initial spike, popularity increases steadily and peaks around the 60-75 range. This shows that a large portion of tracks in the dataset achieve moderate to high popularity rather than being evenly spread across the full scale. The long tail toward very high popularity values (above 80) indicates that truly top-performing tracks are relatively rare.

Overall, this distribution confirms that track popularity is highly skewed: most tracks either perform very poorly or cluster in the mid-to-high popularity range, while only a small fraction achieve extreme popularity.

"""

CORR_MATRIX = """
### Correlation Between Numerical Features

When focusing on relationships involving track popularity, artist popularity shows the clearest positive association, with a moderate correlation. This suggests that songs released by more well-known artists tend to achieve higher popularity on average, although the relationship is far from deterministic and there is substantial variation across individual tracks. In contrast, track duration exhibits only a very weak relationship with popularity, indicating that song length plays little role in determining how well a track performs.

Artist popularity is more strongly related to artist follower count, reflecting that both variables capture an artist's overall reach and audience size. However, this stronger relationship exists primarily between artist-level measures and does not directly translate into consistent success at the individual track level. Overall, the correlation patterns highlight that while artist visibility matters, track popularity remains influenced by additional factors beyond the numerical features considered here.
"""

POPULARITY_OVER_TIME = """
### Track Popularity Over Time

The line plot of average track popularity shows substantial volatility in earlier years, with sharp rises and drops from one year to the next. This suggests that early periods are represented by relatively few tracks in the dataset, making yearly averages highly sensitive to individual songs. As a result, fluctuations in these years are more likely driven by small sample sizes rather than true shifts in overall popularity.

From the late 1990s onward, the average popularity curve becomes noticeably smoother and more stable. This indicates that the dataset becomes denser in more recent years, with enough tracks per year for averages to be more reliable. In these later periods, average popularity generally stabilizes around the 50 rather than showing a clear upward or downward trend.
"""

EXPLICIT_COMPARISON = """
### Explicit vs Non-Explicit Tracks

From the boxplot, I observe that explicit tracks have a slightly higher median popularity compared to non-explicit tracks. This suggests that, in this dataset, explicit tracks tend to perform somewhat better on average.

However, the two distributions overlap substantially, and both explicit and non-explicit tracks span a wide range of popularity values, from very low to very high. This indicates that explicit content alone does not determine a track's success. While explicit tracks may be more common among higher-popularity songs, many non-explicit tracks achieve similar popularity levels, and many explicit tracks still perform poorly.
"""

TOP_GENRES_AVG = """
### Genres by Average Popularity

I noticed that several relatively niche genres such as Brazilian Funk, Reggaeton Chileno, and Corrido appear at the top. These genres show very high average popularity values, often above 75.

However, this does not necessarily mean these genres consistently outperform more mainstream genres. Average popularity can be strongly influenced by small sample sizes. A genre with only a few highly successful tracks can rank very high even if it is not widely represented in the dataset.

This chart is therefore most useful for identifying genres that contain high-performing tracks, rather than genres that are broadly popular across many releases. To fully understand genre importance, this needs to be considered together with genre frequency.
"""

GENRE_FREQUENCY = """
### Genre Frequency

This chart reveals the composition of the dataset rather than performance. Genres such as Soundtrack, Pop, Rap, and Country appear most frequently, indicating that these genres are heavily represented in the data.

Comparing this chart with the “Top Genres by Average Popularity” highlights an important distinction: genres that dominate in frequency are not necessarily the ones with the highest average popularity. This reinforces why both frequency and average metrics need to be considered together.

High-frequency genres provide more stable and reliable averages, while low-frequency genres can appear artificially strong due to a small number of successful tracks.
"""

ARTIST_VS_TRACK = """
### Artist Popularity vs Track Popularity

I observe a clear upward trend: as artist popularity increases, track popularity generally tends to increase as well. Tracks by very low-popularity artists rarely achieve high popularity scores, while tracks by highly popular artists span a much wider range of outcomes.

That said, the relationship is far from perfect. Even among artists with very high popularity, there are many tracks with low or even zero popularity. This vertical spread shows that artist popularity helps increase the potential for a track to perform well, but it does not guarantee success.

Overall, this suggests that artist popularity is an important contributing factor to track popularity, but other elements such as promotion, timing, and listener reception clearly play a major role.
"""

FOLLOWERS_VS_TRACK = """
### Artist Followers vs Track Popularity

Using a log scale reveals patterns that would otherwise be hidden due to the extremely wide range of follower counts. I can see that higher follower counts are generally associated with higher track popularity, but the relationship is much noisier than with artist popularity.

Many artists with millions of followers still have tracks with very low popularity, and some artists with relatively modest follower counts manage to achieve moderate popularity. This suggests that follower count reflects potential audience size, but it does not directly translate into engagement for every release.

Compared to artist popularity, follower count appears to be a weaker and less reliable indicator of individual track performance.
"""

DURATION_VS_POP = """
### Track Duration vs Popularity

This scatter plot shows the relationship between track duration (in minutes) and track popularity. Unlike artist popularity or follower count, track duration does not exhibit a strong or clear association with popularity.

Most tracks cluster between roughly 2 to 5 minutes, which reflects common industry norms for song length. Within this range, tracks span almost the entire popularity scale, from very low to very high popularity. This indicates that songs of typical length can either succeed or fail, depending on other factors.

Longer tracks (above 6-7 minutes) appear much less frequently in the dataset and do not show systematically higher popularity. While a few longer tracks achieve moderate to high popularity, they remain exceptions rather than the norm. Similarly, very short tracks are not consistently more or less popular than average.
"""

ALBUM_TYPE = """
### Popularity by Album Type

The boxplot shows that tracks released as part of albums tend to have the highest median popularity, followed by singles, while compilation tracks generally have the lowest typical popularity. Album tracks also display the widest spread, ranging from very low to very high popularity values, indicating greater variability in performance.

Singles occupy an intermediate position, with a moderate median popularity and a broad distribution, while compilation tracks cluster more tightly at lower popularity levels, with fewer extreme high-performing cases. However, the substantial overlap between all three distributions suggests that album type alone does not determine track success. Instead, album type is associated with differences in typical performance, while individual track popularity remains highly variable.
"""

TABLE_BUCKET_DESC = """
Tracks are grouped into Low (<=30), Medium (31-60), and High (>60) popularity buckets.
This categorization simplifies interpretation by replacing raw popularity scores
with meaningful, interpretable labels.
"""

TABLE_HIT_DESC = """
A simple rule-based classifier flags a track as a potential hit if both track
popularity (>=70) and artist popularity (>=75) exceed predefined thresholds.
This approach demonstrates how domain assumptions can be translated into
executable logic.
"""

TABLE_SIMILARITY_DESC = """
This table shows tracks most similar to a reference profile based on artist
popularity, follower count, and track duration. Similarity is computed after
log-scaling and normalization to ensure balanced comparison across features.
"""

FINAL_INTERPRETATION_TITLE = """
## Final Interpretation and Research Findings
"""

FINAL_INTERPRETATION_INTRO = """
This section brings together what the exploratory analysis shows about how popularity works on Spotify. The goal is not to predict hit songs, but to understand the patterns behind why some tracks perform better than others.
"""

RQ1_TITLE = """
### 1. Is track popularity evenly distributed, or concentrated among a small number of songs?
"""

RQ1_TEXT = """
Track popularity is clearly uneven. A large share of tracks sit at a popularity score of zero, meaning they attract little to no engagement at all. These tracks likely represent obscure releases, very new songs, or tracks that never managed to break through to a wider audience.

Once tracks move beyond zero, most of them cluster in a broad middle range rather than being evenly spread across the scale. This suggests that many songs achieve some level of visibility, but not enough to become standout successes. Only a small number of tracks reach very high popularity values near the top of the scale.

Overall, this shows that popularity on Spotify is highly concentrated. Many tracks fail to gain traction, a sizeable group achieves moderate success, and only a few become major hits. Reaching the very top appears to be the exception rather than the norm.
"""

RQ2_TITLE = """
### 2. How are artist popularity and follower count related to track popularity?
"""

RQ2_TEXT = """
Artist-level visibility has a clear connection to track popularity. As artist popularity and follower count increase, tracks generally tend to perform better, which is visible in the upward patterns in the scatter plots.

Artists with large audiences benefit from immediate exposure when releasing new music. Their tracks are more likely to appear in playlists, recommendations, and searches, giving them a strong starting advantage. This helps explain why tracks by popular artists often achieve higher popularity.

At the same time, the relationship is not guaranteed. Even very popular artists release tracks that perform poorly, and some less well-known artists manage to achieve high popularity. Artist visibility increases the chance of success, but it does not fully determine it.
"""

RQ3_TITLE = """
### 3. Do explicit tracks differ in popularity compared to non-explicit tracks?
"""

RQ3_TEXT = """
There is no strong or consistent difference between explicit and non-explicit tracks in terms of popularity. While explicit tracks sometimes show a slightly higher median, the overall distributions overlap heavily.

Both groups include tracks that perform very poorly as well as tracks that become highly popular. This suggests that explicit content by itself does not drive success on Spotify.

Instead, explicitness appears to be more of a stylistic or genre-related choice. Its impact on popularity seems minor compared to factors like artist visibility and competition.
"""

RQ4_TITLE = """
### 4. Are certain genres, album types, or release periods associated with higher popularity?
"""

RQ4_TEXT = """
The genre analysis highlights an important distinction between visibility and success. Some niche genres rank highly in average popularity, often because they include a small number of very successful tracks. Meanwhile, more mainstream genres dominate the dataset in terms of frequency but do not always achieve the highest averages.

This points to the role of competition. In highly saturated genres, it may be harder for individual tracks to stand out, while less crowded genres can appear strong on average due to a few standout releases. Album type shows some differences in typical popularity, but no format consistently guarantees success.

Over time, popularity patterns become more stable in later years. Earlier periods show more volatility, likely because fewer tracks are available. Overall, genre choice, album type, and timing matter, but they interact closely with competition and artist visibility.
"""

RQ5_TITLE = """
### 5. Can simple rule-based logic be used to identify potential hit songs?
"""

RQ5_TEXT = """
Simple rule-based logic can identify some potential hits, but only to a limited extent. When a hit is defined as a track in the top 30 percent of popularity, rules based on artist popularity and follower count manage to capture many genuinely popular tracks.

However, many tracks flagged as hits by the rule do not actually end up in the top tier. This leads to reasonable recall but relatively low precision. Artist-level visibility is clearly a useful signal, but it does not explain everything.

Overall, rule-based approaches work well as transparent and interpretable tools for exploration. They help illustrate general tendencies, but they cannot capture the full complexity of musical success, which depends on many factors beyond what is directly measured in the data.
"""

CONCLUSION_TITLE = """
## Overall Conclusion
"""

CONCLUSION_TEXT = """
Taken together, the analysis shows that Spotify popularity is shaped primarily by artist-level visibility and competitive dynamics. Most tracks struggle to gain attention, while a small number capture a disproportionate share of engagement.

Track-specific features such as duration or explicit content play a much smaller role. Popularity is less about individual song characteristics and more about who releases the track and how visible they already are.

While clear patterns emerge, predicting hit songs with a simple rule-based logic remains difficult. Success appears to depend on a mix of measurable factors and external influences that are not fully captured in the data.
"""

TABLE_QUANTILES_DESC = """
    Summarizes the distribution of track popularity using SQL-derived quantiles, highlighting how popularity is concentrated among a small number of tracks.
"""

TABLE_EXPLICIT_DESC = """
    Compares popularity metrics between explicit and non-explicit tracks to assess whether lyrical explicitness is associated with higher popularity.
"""

TABLE_GENRE_DESC = """
    Examines genre performance from two perspectives: average popularity and frequency, allowing comparison between genre success and genre saturation.
"""

TABLE_YEARLY_DESC = """
    Aggregates popularity metrics by release year to identify temporal trends and assess the stability of popularity over time.
"""

RULES_INTRO = """
This section demonstrates how simple, interpretable rules can be applied
to categorize tracks and identify potential hit songs. The goal is not
prediction accuracy, but transparency and interpretability.
"""

RULES_BUCKETS_INTRO = """
Tracks are grouped into **Low**, **Medium**, and **High** popularity categories
based on their popularity score. This simplifies reasoning about trends by
using interpretable labels instead of raw values.
"""

RULES_BUCKETS_INTERPRETATION = """
Based on these proportions, I observed that the largest share of tracks falls into 
the High popularity category (about 43%). Medium-popularity tracks make up a little 
over one-third of the dataset (around 40%), while Low-popularity tracks account for 
less than one-fifth (about 17%).

This distribution indicates that the dataset is skewed toward more popular tracks 
rather than being evenly balanced across popularity levels. As a result, the analysis 
reflects patterns among relatively successful songs more strongly than among 
low-engagement tracks.
"""

RULES_HIT_DESCRIPTION = """
A **true hit** is defined as a track whose popularity lies in the **top 30%**
of the dataset.

A track is **predicted as a hit** if:
- Artist popularity ≥ 75  
- Artist followers ≥ 1,000,000
"""

RULES_HIT_INTERPRETATION = """
The rule achieves **moderate accuracy and recall**, indicating that artist-level
popularity is a strong signal for identifying highly popular tracks. However,
precision remains limited, meaning that many tracks predicted as hits do not
actually fall into the top popularity tier.

This confirms that **simple rule-based logic can partially identify hit songs**,
but it cannot fully capture the complexity of musical success.
"""

RULES_SIMILARITY_INTRO = """
Tracks are compared using artist popularity, artist follower count (log-scaled),
and track duration. All features are normalized to ensure balanced similarity.
"""

RULES_SIMILARITY_INTERPRETATION = """
When examining the ranked similarity results, the reference track Golden by HUNTR/X appears at the top with a similarity score of zero, as expected. The closest matches are dominated by songs from the same artist or from artists with very similar audience scale and market position. These tracks cluster closely in normalized feature space because they share comparable artist popularity, follower counts, and track duration.

As the similarity score increases, the results gradually shift toward tracks by different but still similarly positioned artists such as sombr and Alex Warren. None of the variables decrease smoothly across the ranking. Instead, artist popularity and follower count show an overall downward trend with noticeable fluctuations, reflecting meaningful differences even among similarly sized artists.

Track popularity also declines in an overall sense, but it is far more volatile, exhibiting large jumps and drops between neighboring ranks. This indicates that while less similar tracks tend to be less popular on average, individual song performance varies dramatically, even among artists with comparable reach.

Overall, this pattern suggests that after logarithmic transformation and normalization, the similarity metric is driven primarily by stable artist-level characteristics and basic track attributes such as duration, while track-level popularity contributes noisier, less predictable variation.
"""

TOP_ARTISTS_TITLE = """
### Top Artists
"""

TOP_ARTISTS_INTRO = """
As a starting point, I wanted to see which artists stand out the most in this dataset.
Instead of looking at just one metric, I combine a few artist-level signals to get a
broader view of popularity.
"""

TOP_ARTISTS_INTERPRETATION = """
The results are not too surprising. Artists like Taylor Swift, The Weeknd, and Drake show
up at the top because they are everywhere: they have huge audiences, strong visibility on
Spotify, and a lot of tracks in the dataset. Some artists score high mainly because they
are extremely popular, even if they do not release as much, while others benefit from
having a larger catalog.
"""
