import os
import requests


TMDB_BASE_URL = "https://api.themoviedb.org/3"


# =========================================================
# TMDB ERROR
# =========================================================

class TMDBError(Exception):
    pass


# =========================================================
# TOKEN
# =========================================================

def get_token():

    token = os.getenv("TMDB_TOKEN")

    if not token:
        raise TMDBError("TMDB_TOKEN is missing")

    return token.strip()


# =========================================================
# HEADERS
# =========================================================

def get_headers():

    return {
        "Authorization": "Bearer " + get_token(),
        "Content-Type": "application/json"
    }


# =========================================================
# REQUEST
# =========================================================

def _request(endpoint, params=None):

    try:

        response = requests.get(
            TMDB_BASE_URL + endpoint,
            headers=get_headers(),
            params=params,
            timeout=20
        )

    except requests.RequestException as error:

        raise TMDBError(
            "Unable to connect to TMDB: " + str(error)
        )

    if response.status_code != 200:

        try:
            data = response.json()
            message = data.get(
                "status_message",
                "TMDB request failed"
            )
        except Exception:
            message = "TMDB request failed"

        raise TMDBError(message)

    return response.json()


# =========================================================
# NORMALIZE MOVIE
# =========================================================

def normalize_movie(movie):

    poster_path = movie.get("poster_path")

    if poster_path:
        poster_url = (
            "https://image.tmdb.org/t/p/w500"
            + poster_path
        )
    else:
        poster_url = None

    return {
        "id": movie.get("id"),
        "title": movie.get("title", "Unknown"),
        "overview": movie.get("overview", ""),
        "poster_path": poster_path,
        "poster_url": poster_url,
        "backdrop_path": movie.get("backdrop_path"),
        "release_date": movie.get("release_date", ""),
        "vote_average": movie.get("vote_average", 0),
        "vote_count": movie.get("vote_count", 0),
        "popularity": movie.get("popularity", 0),
        "original_language": movie.get(
            "original_language",
            ""
        ),
        "genre_ids": movie.get(
            "genre_ids",
            []
        )
    }


# =========================================================
# SEARCH
# =========================================================

def search_movies(query, page=1):

    data = _request(
        "/search/movie",
        {
            "query": query,
            "page": page,
            "include_adult": False
        }
    )

    data["results"] = [
        normalize_movie(movie)
        for movie in data.get("results", [])
    ]

    return data


# =========================================================
# NOW PLAYING
# =========================================================

def get_now_playing(page=1):

    data = _request(
        "/movie/now_playing",
        {
            "page": page
        }
    )

    data["results"] = [
        normalize_movie(movie)
        for movie in data.get("results", [])
    ]

    return data


# =========================================================
# POPULAR
# =========================================================

def get_popular(page=1):

    data = _request(
        "/movie/popular",
        {
            "page": page
        }
    )

    data["results"] = [
        normalize_movie(movie)
        for movie in data.get("results", [])
    ]

    return data


# =========================================================
# TRENDING
# =========================================================

def get_trending(
    media_type="movie",
    time_window="week"
):

    data = _request(
        "/trending/"
        + media_type
        + "/"
        + time_window
    )

    data["results"] = [
        normalize_movie(movie)
        for movie in data.get("results", [])
    ]

    return data


# =========================================================
# UPCOMING
# =========================================================

def get_upcoming(page=1):

    data = _request(
        "/movie/upcoming",
        {
            "page": page
        }
    )

    data["results"] = [
        normalize_movie(movie)
        for movie in data.get("results", [])
    ]

    return data


# =========================================================
# MOVIE DETAILS
# =========================================================

def get_movie_details(movie_id):

    return _request(
        "/movie/" + str(movie_id),
        {
            "append_to_response":
                "credits,videos,watch/providers"
        }
    )
