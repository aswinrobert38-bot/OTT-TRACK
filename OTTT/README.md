# OTTTrack — Real TMDB Stage

This build removes the fake Stage 1 catalogue. Movie search, posters, details, trending, popular, now-playing and upcoming data are loaded from TMDB.

## 1. Create the environment

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Add your TMDB token

Create a file named `.env` in the project root:

```env
TMDB_API_KEY=YOUR_TMDB_API_READ_ACCESS_TOKEN
```

TMDB documents Bearer-token authentication and the movie search/details workflow in its official API documentation.

## 3. Start

```bat
streamlit run app.py
```

Open `http://localhost:8501`.

## What is real in this build?

- Movie search: TMDB
- Movie posters/backdrops: TMDB image CDN
- Ratings/vote counts: TMDB
- Cast/director/genres/runtime: TMDB
- Theatrical release date: TMDB
- India watch-provider availability: TMDB's watch-provider endpoint, powered by JustWatch
- No hard-coded fictional movies
- No invented OTT release dates

## Important OTT rule

TMDB's watch-provider endpoint gives current provider availability categories. It does **not** provide a trustworthy OTT release-date history for every title. Therefore this build shows the provider and keeps the OTT release date as `TBD` rather than guessing.

The next stage should add a separate source-verification service for official OTT/production announcements and only replace `TBD` when a verifiable release-date source is found.

## TMDB attribution

This product uses the TMDB API but is not endorsed or certified by TMDB.

TMDB API docs: https://developer.themoviedb.org/docs/getting-started
