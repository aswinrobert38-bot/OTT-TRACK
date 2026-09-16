import os
import requests


# =========================================================
# TMDB CONFIG
# =========================================================

TMDB_BASE_URL = "https://api.themoviedb.org/3"


# =========================================================
# GET TMDB TOKEN
# =========================================================

def get_token():

    token = os.getenv("TMDB_TOKEN")

    if not token:
        raise ValueError("TMDB_TOKEN is missing")

    return token.strip()


# =========================================================
# TMDB HEADERS
# =========================================================

def get_headers():

    return {
        "Authorization": "Bearer " + get_token(),
        "Content-Type": "application/json"
    }


# =========================================================
# SEARCH MOVIES
# =========================================================

def search_movies(query, page=1):

    url = TMDB_BASE_URL + "/search/movie"

    params = {
        "query": query,
        "page": page,
        "include_adult": False
    }

    response = requests.get(
        url,
        headers=get_headers(),
        params=params,
        timeout=15
    )

    response.raise_for_status()

    return response.json()


# =========================================================
# MOVIE DETAILS
# =========================================================

def get_movie_details(movie_id):

    url = TMDB_BASE_URL + "/movie/" + str(movie_id)

    params = {
        "append_to_response": "credits,videos"
    }

    response = requests.get(
        url,
        headers=get_headers(),
        params=params,
        timeout=15
    )

    response.raise_for_status()

    return response.json()


# =========================================================
# UPCOMING MOVIES
# =========================================================

def get_upcoming_movies(page=1):

    url = TMDB_BASE_URL + "/movie/upcoming"

    params = {
        "page": page
    }

    response = requests.get(
        url,
        headers=get_headers(),
        params=params,
        timeout=15
    )

    response.raise_for_status()

    return response.json()


# =========================================================
# NOW PLAYING MOVIES
# =========================================================

def get_now_playing_movies(page=1):

    url = TMDB_BASE_URL + "/movie/now_playing"

    params = {
        "page": page
    }

    response = requests.get(
        url,
        headers=get_headers(),
        params=params,
        timeout=15
    )

    response.raise_for_status()

    return response.json()
