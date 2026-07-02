# 📚 AI-Powered Study Buddy

Students often struggle to understand complex concepts while studying. Searching
online gives long or irrelevant results, and teachers aren't always available.
**Study Buddy** is an AI-powered app that:

- 🧠 **Explains topics** in simple terms, at whatever level you need (5-year-old → expert)
- 📝 **Summarizes study notes** (pasted text or uploaded `.txt` / `.pdf` files)
- ❓ **Generates quizzes** (multiple choice, with instant scoring & explanations)
- 🗂️ **Generates flashcards** with a flip-card review interface

Built as a single-file [Streamlit](https://streamlit.io/) app powered by the
[OpenAI API](https://platform.openai.com/).

## Demo

![Study Buddy screenshot placeholder](docs/screenshot.png)

## Features

| Tab | What it does |
|---|---|
| Explain a Concept | Type any topic/question, pick a difficulty level, get a structured, easy-to-follow explanation with an analogy and real-world example. |
| Summarize Notes | Paste notes or upload a `.txt`/`.pdf`, choose a summary style (bullets, outline, paragraph). |
| Generate Quiz | Auto-generate multiple-choice questions from a topic or your notes, take the quiz in-app, and get an instant score with explanations. |
| Flashcards | Auto-generate flashcards from a topic or your notes, with a flip-card viewer to study front/back. |

## Tech Stack

- **Frontend + Backend:** [Streamlit](https://streamlit.io/) (Python)
- **AI:** [OpenAI API](https://platform.openai.com/docs/api-reference) (`gpt-4o-mini` by default, configurable)
- **PDF parsing:** [pypdf](https://pypi.org/project/pypdf/)

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/<your-username>/ai-study-buddy.git
cd ai-study-buddy
```

### 2. Create a virtual environment & install dependencies

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Add your OpenAI API key

Copy `.env.example` to `.env` and add your key:

```bash
cp .env.example .env
```

```
OPENAI_API_KEY=sk-your-key-here
```

Alternatively, you can paste your API key directly into the sidebar when the
app is running (useful for quick demos without a `.env` file).

### 4. Run the app

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`.

## Deploying

This app is ready to deploy for free on [Streamlit Community Cloud](https://streamlit.io/cloud):

1. Push this repo to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) and connect your repo.
3. Set `app.py` as the entry point.
4. Add `OPENAI_API_KEY` under **App settings → Secrets**:
   ```toml
   OPENAI_API_KEY = "sk-your-key-here"
   ```
5. Deploy 🎉

## Project Structure

```
ai-study-buddy/
├── app.py              # Main Streamlit app (all features)
├── requirements.txt    # Python dependencies
├── .env.example         # Example environment file
├── .gitignore
└── README.md
```

## Roadmap Ideas

- [ ] Export flashcards/quizzes to PDF or Anki format
- [ ] Save quiz history & track progress over time
- [ ] Support for images/diagrams in explanations
- [ ] Multi-language support

## License

MIT — feel free to use this project for learning, portfolios, or as a starting
point for your own study tools.
