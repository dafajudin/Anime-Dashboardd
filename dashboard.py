import streamlit as st
import pandas as pd
import plotly.express as px
import os 

# Page Configuration
st.set_page_config(page_title="Anime Dashboard", layout="wide")

# Load dataset
@st.cache_data
def load_data():
    return pd.read_csv('data/clean_anime.csv')

anime_data = load_data()

# Sidebar Filters
st.sidebar.header("Filters")

rating_filter = st.sidebar.selectbox(
    "Select Rating", 
    options=["All"] + list(anime_data['Rating'].unique()),
    index=0
)

type_filter = st.sidebar.selectbox(
    "Select Type", 
    options=["All"] + list(anime_data['Type'].unique()),
    index=0
)

status_filter = st.sidebar.selectbox(
    "Select Status", 
    options=["All"] + list(anime_data['Status'].unique()),
    index=0
)

demographic_filter = st.sidebar.selectbox(
    "Select Demographics", 
    options=["All"] + list(anime_data['Demographics'].unique()),
    index=0
)

# Apply filters
filtered_data = anime_data.copy()

if rating_filter != "All":
    filtered_data = filtered_data[filtered_data['Rating'] == rating_filter]

if type_filter != "All":
    filtered_data = filtered_data[filtered_data['Type'] == type_filter]

if status_filter != "All":
    filtered_data = filtered_data[filtered_data['Status'] == status_filter]

if demographic_filter != "All":
    filtered_data = filtered_data[filtered_data['Demographics'] == demographic_filter]

# Judul Besar di Paling Atas
st.markdown(
    """
    <h1 style='text-align: center; font-size: 60px; color: #FFA500; font-weight: bold; text-shadow: 2px 2px 4px #000000; margin-bottom: 50px;'>
        Anime That You Should Watch
    </h1>
    """,
    unsafe_allow_html=True
)

# ---- Top 10 Ranked Anime Section (Not Filtered) ----
st.markdown("<h1 style='text-align: left;'>Top 10 Ranked Anime of All Time</h1>", unsafe_allow_html=True)

top_10_anime = anime_data.sort_values(by='Ranked').head(10)

# Display top 10 anime with posters and ranking numbers
cols = st.columns(10)

for idx, (index, anime) in enumerate(top_10_anime.iterrows()):
    with cols[idx]:
        poster_path = f"Poster/{anime['Name']}.jpg"
        if os.path.exists(poster_path):
            st.image(poster_path, caption=anime['Name'])
        else:
            st.image('Poster/default.jpg', caption=anime['Name'])
        
        # CSS agar teks sejajar rata tengah
        st.markdown(
            f"""
            <div style='text-align: center;'>
                <p style='font-size: 16px; margin: 5px 0;'>
                    ⭐ {anime['Score']}/10
                </p>
                <div style='font-size: 24px; font-weight: bold; color: #f1c40f;'>
                    {idx+1}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )



# Genre Bubble Chart
st.markdown("<h1 style='text-align: left;'>Anime Genre Distribution</h1>", unsafe_allow_html=True)

genre_counts = filtered_data['Genres'].str.split(', ').explode().value_counts().reset_index()
genre_counts.columns = ['Genre', 'Count']

genre_colors = {
    'Action': '#1f77b4',
    'Comedy': '#ff7f0e',
    'Adventure': '#d62728',
    'Drama': '#2ca02c',
    'Fantasy': '#17becf',
    'SliceofLife': '#bcbd22',
    'Sci-Fi': '#7f7f7f',
    'Romance': '#aec7e8',
    'Mystery': '#1f77b4',
    'AwardWinning': '#e377c2',
    'Horror': '#d62728',
    'BoysLove': '#98df8a',
    'Supernatural': '#8c564b',
    'Ecchi': '#ffbb78',
    'Gourmet': '#ff9896',
    'Suspense': '#9467bd',
    'GirlsLove': '#c5b0d5',
    'Unknown-Genre': '#7f4f24'  # Ubah ke warna berbeda dari Comedy
}

genre_counts['Color'] = genre_counts['Genre'].map(genre_colors).fillna('#c7c7c7')

fig = px.scatter(
    genre_counts,
    x='Genre',
    y='Count',
    size='Count',
    text='Genre',
    color='Genre',
    title="Genres by Number of Anime",
    size_max=100,
    color_discrete_map=genre_colors
)

fig.update_traces(
    textposition='middle center'
)
fig.update_layout(
    xaxis=dict(visible=False),
    yaxis=dict(visible=False),
    showlegend=False,
    height=300,
    margin=dict(l=20, r=20, t=40, b=20)
)
st.plotly_chart(fig, use_container_width=True)

# Genre Selection for Filtering (via button)
st.markdown("**Click a genre below to filter the data:**")

if 'selected_genre' not in st.session_state:
    st.session_state.selected_genre = None

if st.button("All Genre"):
    st.session_state.selected_genre = None
    filtered_data = anime_data.copy()

cols = st.columns(6)
for idx, genre in enumerate(genre_counts['Genre']):
    if cols[idx % 6].button(genre):
        st.session_state.selected_genre = genre

if st.session_state.selected_genre:
    filtered_data = filtered_data[
        filtered_data['Genres'].str.contains(st.session_state.selected_genre)
    ]
    st.success(f"Filtered by Genre: {st.session_state.selected_genre}")
else:
    st.info("Showing all genres")

filtered_data['HoverText'] = (
    "Name: " + filtered_data['Name'] +
    "<br>Genres: " + filtered_data['Genres'] +
    "<br>Score: " + filtered_data['Score'].astype(str) +
    "<br>Popularity: " + filtered_data['Popularity'].astype(str) +
    "<br>Aired: " + filtered_data['Aired'] +
    "<br>Themes: " + filtered_data['Themes']
)

# Create Two Columns for Top 10 Charts
left_container, right_container = st.columns(2)

# Top 10 Favorite Anime Chart (Left)
with left_container:
    st.markdown("### 🎖️ Top 10 Favorite Anime (Filtered by Genre)")
    top_favorites = filtered_data.sort_values(by='Favorites', ascending=False).head(10)
    
    fig = px.bar(
        top_favorites,
        x='Favorites',
        y='Name',
        orientation='h',
        hover_data=['HoverText'],
        color='Genres',
        color_discrete_map=genre_colors
    )
    fig.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig, use_container_width=True)

# Top 10 Most Popular Anime Chart (Right)
with right_container:
    st.markdown("### 🔥 Top 10 Most Popular Anime (Filtered by Genre)")
    top_popular = filtered_data.sort_values(by='Popularity').head(10)
    
    fig = px.bar(
        top_popular,
        x='Members',
        y='Name',
        orientation='h',
        hover_data=['HoverText'],
        color='Genres',
        color_discrete_map=genre_colors
    )
    fig.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig, use_container_width=True)
