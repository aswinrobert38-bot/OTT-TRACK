"""OTT availability service."""

from services.tmdb_service import (
    get_watch_providers,
    get_tv_watch_providers
)


def get_india_availability(
    content_id,
    content_type="movie"
):

    if content_type == "tv":

        data = get_tv_watch_providers(
            content_id
        )

    else:

        data = get_watch_providers(
            content_id
        )

    india = data.get(
        "results",
        {}
    ).get(
        "IN",
        {}
    )

    return {
        "link": india.get("link"),

        "flatrate": india.get(
            "flatrate",
            []
        ),

        "free": india.get(
            "free",
            []
        ),

        "ads": india.get(
            "ads",
            []
        ),

        "rent": india.get(
            "rent",
            []
        ),

        "buy": india.get(
            "buy",
            []
        )
    }
