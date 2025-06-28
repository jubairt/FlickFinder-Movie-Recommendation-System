import streamlit as st
import pickle as pkl
import pandas as pd
import requests

# Load Data
movie_dict = pkl.load(open('Artifacts/movies_dict.pkl', 'rb'))
movies = pd.DataFrame(movie_dict)
similarity = pkl.load(open('Artifacts/similsrity.pkl', 'rb'))

# TMDB API Key
TMDB_API_KEY = '5af237a75d2d1cb019386db2eb1da0fe'  # ⬅️ Replace this with your actual API key

# Streamlit Title
st.title('🎥 FlickFinder: Discover your next favorite movie')

# Movie Input
selected_movie_name = st.selectbox(
    "🎬 Pick a movie to get recommendations:",
    movies['title'].values,
    index=None,
    placeholder="Search or select a movie..."
)


# Recommendation Logic
def recommend(movie):
    movi_index = movies[movies['title'] == movie].index[0]
    distance = similarity[movi_index]
    movies_list = sorted(list(enumerate(distance)), reverse=True, key=lambda x: x[1])[1:6]
    recommend_movies = []
    for i in movies_list:
        recommend_movies.append(movies.iloc[i[0]].title)
    return recommend_movies

# Fetch Movie Details from TMDB
def get_movie_details(title):
    try:
        search_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={title}"
        res = requests.get(search_url).json()
        if res['results']:
            movie = res['results'][0]
            movie_id = movie['id']
            detail_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}"
            details = requests.get(detail_url).json()
            poster = f"https://image.tmdb.org/t/p/original{movie.get('poster_path', '')}"
            return {
                'title': movie.get('original_title', 'N/A'),
                'poster': poster,
                'overview': details.get('overview', 'N/A'),
                'rating': details.get('vote_average', 'N/A'),
                'genres': ", ".join([g['name'] for g in details.get('genres', [])]),
                'release_date': details.get('release_date', 'N/A'),
                'runtime': details.get('runtime', 0)
            }
    except Exception as e:
        return None

# Display Output
if st.button('Recommend'):
    # Show full details for the selected movie
    details = get_movie_details(selected_movie_name)
    if details:
        col1, col2 = st.columns([1, 2])
        col1.image(details['poster'], width=300)
        col2.markdown(f"### {details['title']}")
        col2.markdown(f"**Genres**: {details['genres']}")
        col2.markdown(f"**Rating**: {details['rating']} ⭐")
        col2.markdown(f"**Runtime**: {details['runtime']} min")
        col2.markdown(f"**Release Date**: {details['release_date']}")
        col2.markdown(f"**Overview**: {details['overview']}")
        st.markdown("---")

    # Show only titles of recommended movies
    recommendations = recommend(selected_movie_name)
    st.subheader("Top Picks You Might Enjoy:")
    for movie in recommendations:
        st.markdown(f"- {movie}")
