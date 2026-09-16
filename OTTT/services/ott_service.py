"""OTT availability adapter.

For the current build, TMDB's watch-provider endpoint is used for India.
It is intentionally treated as availability data, not as proof of an OTT
release date. Dates remain TBD unless a verified date source is added later.
"""

from services.tmdb_service import build_watch_data


def get_india_availability(movie_id: int):
    return build_watch_data(movie_id)
