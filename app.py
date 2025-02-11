import streamlit as st
import requests

API_URL = "https://movie-recommender-api-1jsv.onrender.com/recommend"  # Your FastAPI server

st.set_page_config(page_title="AI Movie Recommender", layout="centered")

st.title("how are you feeling today?")

st.write("Describe your mood, and I'll find the perfect movie for you!🎥")

# User Input
mood = st.text_area("", placeholder="I'm feeling adventurous...")

if st.button("Get Recommendation"):
    if mood.strip():
        with st.spinner("Finding the perfect movie..."):
            response = requests.post(API_URL, json={"mood": mood})
            if response.status_code == 200:
                data = response.json()
                st.subheader(f"Suggested Genre: {data['suggested_genre']}")
                st.text(f"Why this genre: {data["suggested_genre_reason"]}")
                
                movies = data["movies"]
                if movies:
                    for movie in movies:
                        #st.write(movie)
                        st.write(f"🎥 **{movie['title']}** ({movie['release_date'][:4]})")
                        st.image(f"https://image.tmdb.org/t/p/w500{movie['poster_path']}", width=150)
                        st.write(f"⭐ Rating: {movie['vote_average']}/10")
                        st.write(movie["overview"])
                        with st.expander("Why this movie?"):
                            st.write(movie['why_this_movie'])
                        st.write("---")
                else:
                    st.error("No movies found for this genre.")
            else:
                st.error("Something went wrong! Try again.")
                st.write(response.status_code)
                st.write(response.text)
    else:
        st.warning("Please enter a mood.")