from fastapi import FastAPI
import openai
from dotenv import load_dotenv
import requests
import os
import numpy as np
import random


load_dotenv()   #loading environment variables

openai_api_key = os.getenv("OPENAI_API_KEY")
tmdb_api_key = os.getenv("TMDB_API_KEY")

openai.api_key = openai_api_key
app = FastAPI()
client = openai.OpenAI()


def get_movie_recommendation(genre):
    url = f"https://api.themoviedb.org/3/discover/movie?api_key={tmdb_api_key}&with_genres={genre}&sort_by=popularity.desc&include_adult=false"
    response = requests.get(url)
    if response.status_code==200:
        data = response.json()
        all_movies = data.get("results", [])
        # selected_indices = np.random.randint(0, len(all_movies)+1, 5)
        # movies = [all_movies[i] for i in selected_indices]
        if len(all_movies) >= 5:
            movies = random.sample(all_movies, 5)
        else:
            movies  = all_movies
        #movies = data.get("results", [])[:5]
        return movies
    return []

def why_this_movie(mood, movie):
    why_prompt = f'''
                  Given the user's mood ({mood}) and the description of the movie ({movie['overview']}), explain in one or two sentences why/how this movie could help the user.
                  '''
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful AI assistant that can connect the links between movies and human emotions/mood."
            },
            {
                "role": "user",
                "content": why_prompt
            }
        ]
    )
    why = response.choices[0].message.content.strip()
    return why

from pydantic import BaseModel

class MoodRequest(BaseModel):
    mood: str


@app.post("/recommend/")
def recommend_movie(req: MoodRequest):
    mood = req.mood

    print(f"API Key Length: {len(openai.api_key)}")
    print(f"API Key Starts With: {openai.api_key[:5]}****")
    
    prompt = f'''
              Based on the user’s mood ({mood}), select the most suitable movie genre from: 
              Action, Adventure, Comedy, Drama, Horror, Science Fiction, Romance, Mystery. 
              Return the genre and why this genre would be helpful given the mood, separated by '|'.
              '''
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful AI movie recommendation assistant."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    
    genre = response.choices[0].message.content.strip().split('|')[0][:-1]
    genre_reason = response.choices[0].message.content.strip().split('|')[1][1:]

    genre_mapping = {
        "Action": 28,
        "Adventure": 12,
        "Comedy": 35,
        "Drama": 18,
        "Horror": 27,
        "Science Fiction": 878,
        "Romance": 10749,
        "Mystery": 9648
    }

    genre_id = genre_mapping.get(genre, 18)
    movies = get_movie_recommendation(genre_id)
    #why_this_movie = []
    for movie in movies:
        movie["why_this_movie"] = why_this_movie(mood, movie)

    return {"mood": mood, "suggested_genre": genre, "suggested_genre_reason": genre_reason, "movies": movies}
