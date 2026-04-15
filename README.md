# Note Quiz Generator

A Streamlit app that turns note images into:
- Structured study notes
- Auto-generated MCQ quizzes
- Text-to-speech audio summaries

The app uses Google Gemini for understanding image content and generating educational outputs.

## Features

- Upload up to 3 note images (JPG/JPEG/PNG)
- Automatic language detection (Bangla or English)
- Generates concise, structured markdown notes
- Generates 5 MCQ questions with difficulty control:
  - Easy
  - Medium
  - Hard
- Converts generated notes to audio (gTTS)
- Clean Streamlit UI with sidebar controls and sectioned outputs

## Tech Stack

- Python
- Streamlit
- Google Gemini API (`google-genai`)
- Pillow (image handling)
- gTTS (text-to-speech)
- python-dotenv (environment variables)

## Project Structure

```text
.
|-- app.py              # Streamlit UI and app flow
|-- api_calling.py      # Gemini + note/quiz/audio generation logic
|-- requirements.txt    # Python dependencies
|-- .env                # Local environment variables (not for commit)
```

## Prerequisites

- Python 3.10+ recommended
- A Google Gemini API key

## Installation

1. Clone the repository

```bash
git clone https://github.com/TasnimTaz/-Note-Quiz-Generator.git
cd -Note-Quiz-Generator
```

2. Create and activate a virtual environment

Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root

```env
GEMINI_API_KEY=your_api_key_here
```

## Run the App

```bash
streamlit run app.py
```

Then open the local URL shown in terminal (usually `http://localhost:8501`).

## How to Use

1. Upload 1-3 note images from the sidebar
2. Select quiz difficulty (`Easy`, `Medium`, `Hard`)
3. Click `Generate Notes & Quiz`
4. Review outputs in three sections:
   - Note Summary
   - Audio Transcription
   - Quiz

## Output Details

### 1) Note Summary
- Generated from image content
- Language follows detected note language
- Structured in markdown headings and bullets

### 2) Audio Transcription
- Generated from note text using gTTS
- Supports Bangla (`bn`) and English (`en`)

### 3) Quiz
- Exactly 5 MCQ questions
- Difficulty-aware question style
- Includes answer and short explanation for each question

## Environment Variables

- `GEMINI_API_KEY`: Required for Gemini model calls

## Troubleshooting

- API key error:
  - Ensure `.env` exists and has valid `GEMINI_API_KEY`
- Image open error:
  - Re-export images as valid PNG/JPG and try again
- Audio generation error:
  - Check internet connection and supported language text
- Streamlit not found:
  - Activate the correct virtual environment before running

## Notes

- Do not commit `.env` or API keys.
- Keep image count within the app limit (max 3).
- For best results, use clear and readable note photos.

## Future Improvements

- Answer reveal/hide interaction for quiz section
- Save/export generated notes as PDF/Markdown
- Download quiz as worksheet
- Multi-language expansion beyond Bangla/English

## License

This project is open-source. Add a license file (`LICENSE`) to define usage terms.
