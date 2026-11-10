import os
import base64
import pandas as pd
import plotly.express as px
import streamlit as st

# ---------------------------------------------------------
# 1. Page Configuration & Custom CSS
# ---------------------------------------------------------
st.set_page_config(
    page_title="Anime That You Should Watch",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(
    """
    <style>
    /* Dark Theme Setup */
    .stApp {
        background-color: #121212;
        color: #FFFFFF;
    }
    
    [data-testid="block-container"] {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 3rem;
        padding-right: 3rem;
    }

    /* Main Big Title (Orange) */
    .main-title {
        text-align: center;
        font-size: 52px;
        color: #FFA500;
        font-weight: 800;
        margin-top: -10px;
        margin-bottom: 35px;
        letter-spacing: 1px;
    }

    /* Section Title */
    .section-title {
        font-size: 26px;
        font-weight: 700;
        color: #FFFFFF;
        margin-top: 20px;
        margin-bottom: 15px;
    }

    /* Top 10 Poster Cards Fixed Ratio & Alignment */
    .poster-box {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: space-between;
        height: 250px;
    }

    .poster-img {
        width: 100%;
        height: 150px;
        object-fit: cover;
        border-radius: 6px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.5);
    }

    .poster-name {
        font-size: 11px;
        color: #D1D5DB;
        text-align: center;
        margin-top: 6px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        width: 100%;
    }

    .poster-score {
        font-size: 11px;
        color: #FBBF24;
        font-weight: 600;
        margin-top: 2px;
    }

    .poster-rank {
        font-size: 18px;
        font-weight: 800;
        color: #FFA500;
        margin-top: 2px;
    }

    /* Styling Genre Filter Buttons */
    div.stButton > button {
        background-color: #1F2937;
        color: #E5E7EB;
        border: 1px solid #374151;
        border-radius: 6px;
        padding: 4px 10px;
        font-size: 12px;
        width: 100%;
    }
    div.stButton > button:hover {
        border-color: #FFA500;
        color: #FFA500;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# 2. Helper Functions & Data Loading
# ---------------------------------------------------------
def get_image_base64(path):
    """Mengonversi file gambar lokal ke Base64 agar dapat dibaca tag HTML browser."""
    if os.path.exists(path):
        with open(path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode()
            return f"data:image/jpeg;base64,{encoded}"
    return "https://via.placeholder.com/150x225?text=No+Image"

@st.cache_data
def load_data():
    file_path = "data/clean_anime.csv"
    if not os.path.exists(file_path):
        file_path = "data/top_animes_after_cleaning.csv"
    
    df = pd.read_csv(file_path)
    
    # Penyesuaian nama kolom
    if "Name" not in df.columns and "title" in df.columns:
        df.rename(columns={"title": "Name"}, inplace=True)
    if "Genres" not in df.columns and "Themes" in df.columns:
        df["Genres"] = df["Themes"]
        
    return df

anime_data = load_data()

# ---------------------------------------------------------
# 3. Sidebar Filters
# ---------------------------------------------------------
st.sidebar.header("Filters")

rating_opts = ["All"] + list(anime_data['Rating'].dropna().unique()) if 'Rating' in anime_data.columns else ["All"]
type_opts = ["All"] + list(anime_data['Type'].dropna().unique()) if 'Type' in anime_data.columns else ["All"]
status_opts = ["All"] + list(anime_data['Status'].dropna().unique()) if 'Status' in anime_data.columns else ["All"]
demo_opts = ["All"] + list(anime_data['Demographics'].dropna().unique()) if 'Demographics' in anime_data.columns else ["All"]

rating_filter = st.sidebar.selectbox("Select Rating", options=rating_opts, index=0)
type_filter = st.sidebar.selectbox("Select Type", options=type_opts, index=0)
status_filter = st.sidebar.selectbox("Select Status", options=status_opts, index=0)
demographics_filter = st.sidebar.selectbox("Select Demographics", options=demo_opts, index=0)

# Filter Logic
filtered_data = anime_data.copy()

if rating_filter != "All" and 'Rating' in filtered_data.columns:
    filtered_data = filtered_data[filtered_data['Rating'] == rating_filter]
if type_filter != "All" and 'Type' in filtered_data.columns:
    filtered_data = filtered_data[filtered_data['Type'] == type_filter]
if status_filter != "All" and 'Status' in filtered_data.columns:
    filtered_data = filtered_data[filtered_data['Status'] == status_filter]
if demographics_filter != "All" and 'Demographics' in filtered_data.columns:
    filtered_data = filtered_data[filtered_data['Demographics'].str.contains(demographics_filter, na=False)]

# ---------------------------------------------------------
# 4. Header Title
# ---------------------------------------------------------
st.markdown('<h1 class="main-title">Anime That You Should Watch</h1>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 5. Top 10 Ranked Anime Section (Menggunakan Base64)
# ---------------------------------------------------------
st.markdown('<div class="section-title">Top 10 Ranked Anime of All Time</div>', unsafe_allow_html=True)

top_10_anime = anime_data.sort_values(by='Ranked' if 'Ranked' in anime_data.columns else 'Score', ascending=True).head(10)

cols = st.columns(10)
for idx, (_, anime) in enumerate(top_10_anime.iterrows()):
    with cols[idx]:
        poster_path = f"Poster/{anime['Name']}.jpg"
        img_src = get_image_base64(poster_path)
        score_val = anime['Score'] if 'Score' in anime and pd.notnull(anime['Score']) else "N/A"
        
        st.markdown(
            f"""
            <div class="poster-box">
                <img src="{img_src}" class="poster-img"/>
                <div class="poster-name" title="{anime['Name']}">{anime['Name']}</div>
                <div class="poster-score">⭐ {score_val}</div>
                <div class="poster-rank">{idx+1}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

st.markdown("<br><br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 6. Anime Genre Distribution (Bubble Chart)
# ---------------------------------------------------------
st.markdown('<div class="section-title">Anime Genre Distribution</div>', unsafe_allow_html=True)

if 'Genres' in filtered_data.columns:
    genre_counts = filtered_data['Genres'].dropna().str.split(', ').explode().value_counts().reset_index()
    genre_counts.columns = ['Genre', 'Count']

    genre_colors = {
        'Action': '#1f77b4', 'Comedy': '#ff7f0e', 'Adventure': '#d62728', 'Drama': '#2ca02c',
        'Fantasy': '#17becf', 'SliceofLife': '#bcbd22', 'Sci-Fi': '#7f7f7f', 'Romance': '#aec7e8',
        'Mystery': '#1f77b4', 'AwardWinning': '#e377c2', 'Horror': '#d62728', 'BoysLove': '#98df8a',
        'Supernatural': '#8c564b', 'Ecchi': '#ffbb78', 'Gourmet': '#ff9896', 'Suspense': '#9467bd',
        'GirlsLove': '#c5b0d5', 'Unknown-Genre': '#7f4f24'
    }
    genre_counts['Color'] = genre_counts['Genre'].map(genre_colors).fillna('#c7c7c7')

    fig_bubble = px.scatter(
        genre_counts,
        x='Genre',
        y='Count',
        size='Count',
        text='Genre',
        color='Genre',
        title="Genres by Number of Anime",
        size_max=80,
        color_discrete_map=genre_colors
    )
    fig_bubble.update_traces(textposition='middle center')
    fig_bubble.update_layout(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        showlegend=False,
        height=280,
        margin=dict(l=10, r=10, t=30, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig_bubble, use_container_width=True)

# ---------------------------------------------------------
# 7. Interactive Genre Filter Buttons
# ---------------------------------------------------------
st.markdown("**Click a genre below to filter the data:**")

if 'selected_genre' not in st.session_state:
    st.session_state.selected_genre = None

if st.button("All Genre"):
    st.session_state.selected_genre = None

if 'Genres' in filtered_data.columns:
    unique_genres = genre_counts['Genre'].tolist() if 'genre_counts' in locals() else []
    btn_cols = st.columns(6)
    for idx, genre in enumerate(unique_genres):
        if btn_cols[idx % 6].button(genre, key=f"btn_{genre}"):
            st.session_state.selected_genre = genre

# Apply interactive genre selection
if st.session_state.selected_genre:
    chart_data = filtered_data[filtered_data['Genres'].str.contains(st.session_state.selected_genre, na=False)]
    st.info(f"Filtered by Genre: **{st.session_state.selected_genre}**")
else:
    chart_data = filtered_data.copy()
    st.info("Showing all genres")

# Hover details setup
chart_data['HoverText'] = (
    "Name: " + chart_data['Name'].astype(str) +
    "<br>Genres: " + chart_data['Genres'].astype(str) +
    "<br>Score: " + chart_data['Score'].astype(str)
)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 8. Dual Top 10 Horizontal Bar Charts
# ---------------------------------------------------------
left_col, right_col = st.columns(2)

with left_col:
    st.markdown("### 🏅 Top 10 Favorite Anime (Filtered by Genre)")
    if 'Favorites' in chart_data.columns and not chart_data.empty:
        top_fav = chart_data.sort_values(by='Favorites', ascending=False).head(10)
        fig_fav = px.bar(
            top_fav,
            x='Favorites',
            y='Name',
            orientation='h',
            hover_data=['HoverText'],
            color='Genres' if 'Genres' in top_fav.columns else None,
            color_discrete_map=genre_colors if 'genre_colors' in locals() else {}
        )
        fig_fav.update_layout(
            yaxis=dict(autorange="reversed", title=""),
            height=400,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_fav, use_container_width=True)

with right_col:
    st.markdown("### 🔥 Top 10 Most Popular Anime (Filtered by Genre)")
    pop_col = 'Members' if 'Members' in chart_data.columns else ('Popularity' if 'Popularity' in chart_data.columns else None)
    if pop_col and not chart_data.empty:
        top_pop = chart_data.sort_values(by=pop_col, ascending=(pop_col == 'Popularity')).head(10)
        fig_pop = px.bar(
            top_pop,
            x=pop_col,
            y='Name',
            orientation='h',
            hover_data=['HoverText'],
            color='Genres' if 'Genres' in top_pop.columns else None,
            color_discrete_map=genre_colors if 'genre_colors' in locals() else {}
        )
        fig_pop.update_layout(
            yaxis=dict(autorange="reversed", title=""),
            height=400,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_pop, use_container_width=True)