# Fake-Profile-Detector

Detect potentially fake social media profiles using multiple input modes:

- CSV upload
- Manual entry
- Username/Link (via RapidAPI)
- Screenshot OCR (Tesseract)

## Prerequisites

- Python 3.9+
- Tesseract OCR (for the Screenshot mode)
  - Linux (Debian/Ubuntu): `sudo apt-get update && sudo apt-get install -y tesseract-ocr`
  - macOS (Homebrew): `brew install tesseract`
  - Windows: Install from https://github.com/UB-Mannheim/tesseract/wiki

## Setup

1) Create and activate a virtual environment
```
python -m venv .venv
source .venv/bin/activate
```

2) Install dependencies
```
pip install -r requirements.txt
```

3) Configure environment variables

- Copy `.env.example` to `.env` and fill in values:
```
cp .env.example .env
```

Required keys for Username/Link mode (RapidAPI):

- `RAPIDAPI_KEY`
- `RAPIDAPI_HOST` (e.g. the host provided by the specific Instagram API on RapidAPI)

Optional key for Tesseract path if not on PATH:

- `TESSERACT_CMD` (e.g. `/usr/bin/tesseract`, `/opt/homebrew/bin/tesseract`, or `C:\\Program Files\\Tesseract-OCR\\tesseract.exe`)

## Running the app

```
streamlit run app.py
```

Open the provided URL in your browser and choose a mode from the sidebar.

## Notes

- If RapidAPI credentials are missing, the Username/Link mode will show a helpful warning instead of failing.
- If Tesseract is not installed or not found, the Screenshot mode will prompt you to install or configure it.
- Scoring is rule-based and meant for demonstration. Tune the rules in `score_profile()` in `app.py` to fit your needs.