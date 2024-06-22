import pickle
import streamlit as st
import requests
import importlib
import pandas as pd
from PIL import Image
from io import BytesIO
import os
import time
from difflib import SequenceMatcher

st.header("Movies Recommendation System Using Machine Learning")

with open('C:\\Users\\ADMIN\\OneDrive - Trường ĐH CNTT - University of Information Technology\\Máy tính\\Hệ khuyến nghị phim\\DoAn\\artificates\\movie_list.pkl', 'rb') as file:
    movies = pickle.load(file)

with open('C:\\Users\\ADMIN\\OneDrive - Trường ĐH CNTT - University of Information Technology\\Máy tính\\Hệ khuyến nghị phim\\DoAn\\artificates\\cosine_sim.pkl', 'rb') as file:
    cosine_sim = pickle.load(file)

def title_similarity(title1, title2):
    return SequenceMatcher(None, title1, title2).ratio()

new_df = pd.read_csv('C:\\Users\\ADMIN\\OneDrive - Trường ĐH CNTT - University of Information Technology\\Máy tính\\Hệ khuyến nghị phim\\DoAn\\movies_with_id.csv')


def fetch_poster(movie_id):
    # Get the poster path from the DataFrame
    poster_url = new_df[new_df['movie_id'] == movie_id]['poster_path'].values[0]

    try:
        # Check if the poster path is a valid URL
        if 'http' in poster_url:
            # Download the poster from the URL
            posters_folder='posters'
            response = requests.get(poster_url)
            if response.status_code == 200:
                try:
                    # Create the posters folder if it doesn't exist
                    if not os.path.exists(posters_folder):
                        os.makedirs(posters_folder)

                    # Generate a unique file name for the poster
                    file_name = f'{movie_id}.jpg'
                    poster_url = os.path.join(posters_folder, file_name)

                    # Save the poster to the file
                    with open(poster_url, 'wb') as f:
                        f.write(response.content)
                    print(f'Đã tải xuống và lưu trữ poster của phim có ID {movie_id}.')
                    return poster_url
                except (IOError, OSError):
                    print(f'Lỗi khi xử lý poster của phim có ID {movie_id}: Không thể xác định định dạng hình ảnh.')
                    return None
            elif response.status_code == 403:
                print(f'Lỗi khi tải xuống poster của phim có ID {movie_id}: {response.status_code} Forbidden')
                time.sleep(2)  # Chờ 2 giây trước khi thử lại
                return fetch_poster(movie_id, posters_folder)
            else:
                print(f'Lỗi khi tải xuống poster của phim có ID {movie_id}: {response.status_code}')
                return None
        else:
            # Lấy poster từ đường dẫn tương đối
            parts = poster_url.split('/')
            file_name = parts[-1]
            
            # Xác định thư mục chứa file
            if len(parts) > 1:
                sub_folder = parts[-2]
            else:
                sub_folder = ''
            
            # Ghép đường dẫn tương đối
            relative_poster_path = os.path.join('DoAn', 'data', sub_folder, file_name)
            print(relative_poster_path)
            if os.path.exists(relative_poster_path):
                print(f'Poster của phim có ID {movie_id} đã tồn tại.')
                return relative_poster_path
            else:
                print(f'Không tìm thấy poster của phim có ID {movie_id} tại đường dẫn {relative_poster_path}.')
                return None
    except requests.exceptions.RequestException as e:
        print(f'Lỗi khi tải xuống poster của phim có ID {movie_id}: {e}')
        return None
  


def get_recommendations(movie, n_recommendations=10):
    movie = movie.lower()  # Chuyển đổi tên phim đầu vào thành chữ thường
    recommended_movies_name = []
    recommended_movies_poster = []
    recommended_movies_description = []
    recommended_movies_category = []
    recommended_movies_actors = []
    recommended_movies_directors = []
    recommended_movies_released_year = []
    recommended_movies_ratings = []
    recommended_movies_duration = []
    recommended_movies_country = []
    recommended_movies_original_language = []
    recommended_movies_certificate = []
    recommended_movies_writting_credits = []

    if movie not in movies['Movie_Name'].values:
        return f"Phim '{movie}' không có trong cơ sở dữ liệu."
    
    # Tìm chỉ số của phim đầu vào
    idx = movies[movies['Movie_Name'] == movie].index_col.values[0]
    
    # Lấy điểm cosine similarity cho phim đầu vào
    sim_scores = list(enumerate(cosine_sim[idx]))
    
    # Tính toán mức độ tương đồng của tên phim
    movie_sim_scores = [(i, title_similarity(movie, movies.iloc[i]['Movie_Name'])) for i in range(len(movies))]
    
    # Kết hợp điểm cosine similarity và điểm tương đồng của tên phim
    combined_scores = [(i, 0.7 * sim_scores[i][1] + 0.3 * movie_sim_scores[i][1]) for i in range(len(movies))]
    
    # Sắp xếp các phim dựa trên điểm số kết hợp
    combined_scores = sorted(combined_scores, key=lambda x: x[1], reverse=True)
    
    # Lấy chỉ số của các phim được gợi ý
    movie_indices = [i[0] for i in combined_scores[1:n_recommendations+1]]
    for i in movie_indices:
        movie_id = movies.iloc[i].movie_id
        recommended_movies_poster.append(fetch_poster(movie_id))
        recommended_movies_name.append(movies.iloc[i].Movie_Name)
        recommended_movies_description.append(movies.iloc[i].Description)
        recommended_movies_category.append(movies.iloc[i].Movie_category)
        recommended_movies_actors.append(movies.iloc[i].Film_Actor)
        recommended_movies_directors.append(movies.iloc[i].Directors)
        recommended_movies_released_year.append(movies.iloc[i].Released_Year)
        recommended_movies_ratings.append(movies.iloc[i].Ratings)
        recommended_movies_duration.append(movies.iloc[i].Duration)
        recommended_movies_country.append(movies.iloc[i].Country)
        recommended_movies_original_language.append(movies.iloc[i].Original_Language)
        recommended_movies_certificate.append(movies.iloc[i]['Certificate (MPAA)'])
        recommended_movies_writting_credits.append(movies.iloc[i].Writing_Credits)

    return (recommended_movies_name, recommended_movies_poster, recommended_movies_description, recommended_movies_category,
            recommended_movies_actors, recommended_movies_directors, recommended_movies_released_year, recommended_movies_ratings,
            recommended_movies_duration, recommended_movies_country, recommended_movies_original_language,
            recommended_movies_certificate, recommended_movies_writting_credits)


movie_list = movies['Movie_Name'].values
selected_movie = st.selectbox(
    "Type or select a movie to get recommendations", 
    movie_list
)

if st.button("Show Recommendation"):
    print(movies.columns)
    recommended_movies_name, recommended_movies_poster, recommended_movies_description, recommended_movies_category, recommended_movies_actors, recommended_movies_directors, recommended_movies_released_year, recommended_movies_ratings, recommended_movies_duration, recommended_movies_country, recommended_movies_original_language, recommended_movies_certificate, recommended_movies_writting_credits = get_recommendations(selected_movie)

    # Hiển thị 3 phim trong một hàng
    num_movies = len(recommended_movies_name)
    for i in range(0, num_movies, 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < num_movies:
                with cols[j]:
                    st.write("") 
                    st.write("") 
                    st.image(recommended_movies_poster[i+j], width=200, use_column_width=False)
                    st.markdown(f"<h2><b>{recommended_movies_name[i+j].upper()}</b></h2>", unsafe_allow_html=True)
                    st.write(f"**Description:** {recommended_movies_description[i+j]}")
                    st.write(f"**Category:** {recommended_movies_category[i+j]}")
                    st.write(f"**Actors:** {recommended_movies_actors[i+j]}")
                    st.write(f"**Directors:** {recommended_movies_directors[i+j]}")
                    st.write(f"**Released Year:** {recommended_movies_released_year[i+j]}")
                    st.write(f"**Ratings:** {recommended_movies_ratings[i+j]}")
                    st.write(f"**Duration:** {recommended_movies_duration[i+j]} minutes")
                    st.write(f"**Country:** {recommended_movies_country[i+j]}")
                    st.write(f"**Original Language:** {recommended_movies_original_language[i+j]}")
                    st.write(f"**Certificate:** {recommended_movies_certificate[i+j]}")
                    st.write(f"**Writting Credits:** {recommended_movies_writting_credits[i+j]}")
        st.markdown("---")