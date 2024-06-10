import pickle
import streamlit as st
import requests
import importlib
import pandas as pd
from difflib import SequenceMatcher


st.header("Movies Recommendation System Using Machine Learning")
# with open('artificates/movie_list.pkl', 'rb') as file:
#     movies = pickle.load(file)
movies = pd.read_pickle("artificates/movie_list.pkl")
cosine_sim = pd.read_pickle("artificates/cosine_sim.pkl")
# with open('artificates/cosine_sim.pkl', 'rb') as file:
#     cosine_sim = pickle.load(file)

def title_similarity(title1, title2):
    return SequenceMatcher(None, title1, title2).ratio()

new_df = pd.read_csv('movies_with_id.csv')

def fetch_poster(movie_id):
    url = new_df[new_df['movie_id'] == movie_id].Movie_Link.values[0]
    data = requests.get(url) #Sửa code lấy poster


# Hàm để lấy gợi ý phim dựa trên sự kết hợp của cosine similarity và title similarity
def get_recommendations(movie, n_recommendations=10):
    movie = movie.lower()  # Chuyển đổi tên phim đầu vào thành chữ thường
    recommended_movies_name = []
    recommended_movies_poster = []
    if movie not in movies['Movie_Name'].values:
        return f"Phim '{movie}' không có trong cơ sở dữ liệu."
    
    # Tìm chỉ số của phim đầu vào
    idx = movies[movies['Movie_Name'] == movie].index[0]
    
    # Lấy điểm cosine similarity cho phim đầu vào
    sim_scores = list(enumerate(cosine_sim[idx]))
    
    # Tính toán mức độ tương đồng của tên phim
    movie_sim_scores = [(i, title_similarity(movie, movies.iloc[i]['Movie_Name'])) for i in range(len(movies))]
    
    # Kết hợp điểm cosine similarity và điểm tương đồng của tên phim
    combined_scores = [(i, 0.5 * sim_scores[i][1] + 0.5 * movie_sim_scores[i][1]) for i in range(len(movies))]
    
    # Sắp xếp các phim dựa trên điểm số kết hợp
    combined_scores = sorted(combined_scores, key=lambda x: x[1], reverse=True)
    
    # Lấy chỉ số của các phim được gợi ý
    movie_indices = [i[0] for i in combined_scores[1:n_recommendations+1]]
    for i in movie_indices:
        movie_id = movies.iloc[i].movie_id
        recommended_movies_poster.append(fetch_poster(movie_id))
        recommended_movies_name.append(movies.iloc[i].Movie_Name)

    return recommended_movies_name, recommended_movies_poster


movie_list = movies['Movie_Name'].values
selected_movie = st.selectbox(
    "Type or select a movie to get recommendations", 
    movie_list
)

if st.button("Show Recommendation"):
    recommended_movies_name, recommended_movies_poster = get_recommendations(selected_movie, cosine_sim, movies)