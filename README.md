# 🎬 Movie Information Extractor

A Streamlit app that turns a free-text **movie review** into clean, **structured data** (title, genre, director, cast, plot, themes and more). It uses **Llama 3.3 70B** on **Groq**, with **LangChain** and **Pydantic** to enforce a strict output schema.

---

## Table of Contents
1. [Features](#features)
2. [Key concepts](#key-concepts)
3. [Tech stack](#tech-stack)
4. [Project structure](#project-structure)
5. [Setup](#setup)
6. [Usage](#usage)
7. [Extracted fields](#extracted-fields)
8. [How it works](#how-it-works)
9. [Customization](#customization)
10. [Design decisions](#design-decisions)
11. [Limitations](#limitations)
12. [Troubleshooting](#troubleshooting)
13. [Future improvements](#future-improvements)

---

## Features
- Paste any movie review and extract 11 structured fields
- Output validated against a Pydantic schema, not loosely formatted text
- Sensible defaults ("Unknown") when the review doesn't mention a detail
- Results shown in readable sections, plus an expandable raw-JSON view
- Friendly error handling for empty input and malformed model output

---

## Key concepts

**Structured output.** Raw LLM text is hard for software to use. Asking the model for JSON that matches a defined schema turns unstructured prose into data you can store, search, or feed into other programs.

**Pydantic validation.** A Pydantic model defines each field's name and type. After the LLM replies, Pydantic checks the result. If a required field is missing or the wrong type, it raises an error rather than letting bad data through.

**Format instructions.** LangChain's `PydanticOutputParser` converts the schema into plain-English and JSON-schema instructions that are placed into the prompt, so the model knows exactly what shape to return.

---

## Tech stack

| Component | Technology | Role |
|-----------|-----------|------|
| Language | Python 3.9+ | Core language |
| LLM framework | LangChain (`langchain-core`) | Prompt templates and output parser |
| LLM provider | Groq API | Fast inference |
| Model | Llama 3.3 70B Versatile | Information extraction |
| Validation | Pydantic | Schema definition and validation |
| Web UI | Streamlit | Interface |
| Config | python-dotenv | Loads the API key from `.env` |

---

## Project structure

```
movie-extractor/
├── app.py              # Streamlit app (schema, prompt, UI)
├── requirements.txt    # Dependencies
├── .env.example        # Template for your API key
├── .gitignore          # Keeps secrets out of Git
└── README.md
```

---

## Setup

### 1. Clone the repo
```bash
git clone <your-repo-url>
cd movie-extractor
```

### 2. (Recommended) Create a virtual environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Add your Groq API key
Get a free key at [console.groq.com](https://console.groq.com), then:
```bash
cp .env.example .env        # Windows: copy .env.example .env
```
Edit `.env`:
```
GROQ_API_KEY=your_real_key_here
```
> ⚠️ Never commit `.env`. It is already listed in `.gitignore`.

---

## Usage

```bash
streamlit run app.py
```
1. Open the URL shown in the terminal (usually http://localhost:8501).
2. Paste a movie review into the text box.
3. Click **Extract Information**.
4. Read the structured details, or expand **View Raw JSON** to copy the data.

**Example input**
> "Inception (2010), directed by Christopher Nolan, stars Leonardo DiCaprio as a thief who steals secrets through dreams. A mind-bending sci-fi thriller about memory and guilt, with stunning visuals and a haunting score."

---

## Extracted fields

| Field | Type | Notes |
|-------|------|-------|
| `title` | str | Required |
| `release_year` | str | Defaults to "Unknown" |
| `genre` | list[str] | One or more genres |
| `director` | str | Defaults to "Unknown" |
| `main_cast` | str | Required |
| `setting_location` | str | Defaults to "Unknown" |
| `plot` | str | Required |
| `themes` | str | Required |
| `rating` | str | Defaults to "Unknown" |
| `notable_features` | str | Defaults to "Unknown" |
| `short_summary` | str | Required |

---

## How it works

```
Review text ─► Prompt (system rules + schema instructions + review)
                         │
                Groq Llama 3.3 70B ─► JSON text
                         │
          PydanticOutputParser validates ─► MovieInfo object
                         │
              Displayed in the UI + raw JSON view
```

1. **Schema:** the `MovieInfo` Pydantic class defines every field and which ones are optional.
2. **Parser:** `PydanticOutputParser` generates format instructions from that schema.
3. **Prompt:** a `ChatPromptTemplate` combines the system instruction ("extract movie information, return only valid JSON"), the format instructions and the pasted paragraph.
4. **Model call:** the filled prompt is sent to the Groq model.
5. **Parsing:** `parser.parse()` converts the reply into a validated `MovieInfo` object. Missing optional fields get their defaults.
6. **Display:** fields appear in sections (details, plot, themes, features, summary) and as JSON in an expander.
7. **Errors:** empty input triggers a warning, and any model or parsing failure is shown as an error message instead of crashing the app.

---

## Customization

**Add or remove fields:** edit the `MovieInfo` class, then add a matching `st.write(...)` line in the display section. The parser picks up the change automatically.
```python
class MovieInfo(BaseModel):
    ...
    box_office: Optional[str] = "Unknown"
```
**Improve consistency:** lower `temperature` (currently 0.7) to around 0 to 0.2 for more reliable JSON.
**Reuse for other content:** swap the schema (for example, product reviews, job postings, recipes) and the same pipeline works.
**Change the model:** edit the `model=` value to any Groq-hosted chat model.

---

## Design decisions

- **Pydantic schema as the single source of truth:** one class defines the data shape, the prompt instructions and the validation.
- **Optional fields with defaults:** reviews rarely mention everything, so missing details become "Unknown" rather than causing failures.
- **Parse after generation:** validating the output means downstream code can trust the types.
- **Streamlit UI:** gives a usable interface with no frontend code.

---

## Limitations

- **Only extracts what's in the text.** The model can't verify facts, and unmentioned details become "Unknown". Depending on the model, it may occasionally guess.
- **Occasional malformed JSON.** LLMs sometimes add extra text around the JSON; the app shows an error rather than retrying.
- **Single review at a time.** There is no batch processing or file upload.
- **Some fields are plain strings.** For example, `main_cast` is one string, not a list.
- **No saved history.** Results disappear when the page is refreshed.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Authentication / missing key error | Create `.env` (not just `.env.example`) containing your key. |
| Parsing error shown | Click **Extract** again, shorten the review, or lower `temperature`. |
| Many fields show "Unknown" | The review probably doesn't mention them; try a more detailed paragraph. |
| `streamlit: command not found` | Activate your virtual environment and re-run `pip install -r requirements.txt`. |
| Rate-limit errors | Wait a moment; the Groq free tier has usage limits. |

---

## Future improvements

- [ ] Automatic retry when JSON parsing fails
- [ ] Batch extraction from multiple reviews or an uploaded file
- [ ] Download results as JSON or CSV
- [ ] Make `main_cast` a list of names
- [ ] Add sentiment analysis of the review
- [ ] Deploy on Streamlit Community Cloud (store the key in Streamlit secrets)

