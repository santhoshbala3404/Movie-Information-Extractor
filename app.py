from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from pydantic import BaseModel
from typing import List, Optional
from langchain_core.output_parsers import PydanticOutputParser
from dotenv import load_dotenv
import streamlit as st
import os

# Load environment variables
load_dotenv()

# Initialize model
model = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.7,
    max_tokens=1024
)

# Pydantic Schema
class MovieInfo(BaseModel):
    title: str
    release_year: Optional[str] = "Unknown"
    genre: List[str]
    director: Optional[str] = "Unknown"
    main_cast: str
    setting_location: Optional[str] = "Unknown"
    plot: str
    themes: str
    rating: Optional[str] = "Unknown"
    notable_features: Optional[str] = "Unknown"
    short_summary: str

# Parser
parser = PydanticOutputParser(pydantic_object=MovieInfo)

# Prompt Template
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
Extract movie information from the paragraph.

{format_instructions}

Return only valid JSON.
"""
        ),
        ("human", "{paragraph}")
    ]
)

# Streamlit UI
st.set_page_config(page_title="Movie Information Extractor", page_icon="🎬")

st.title("🎬 Movie Information Extractor")
st.write("Paste a movie review and extract structured information.")

review = st.text_area(
    "Movie Review",
    height=250,
    placeholder="Paste your movie review here..."
)

if st.button("Extract Information"):

    if not review.strip():
        st.warning("Please enter a movie review.")
    else:
        try:
            with st.spinner("Analyzing review..."):

                final_prompt = prompt.invoke(
                    {
                        "paragraph": review,
                        "format_instructions": parser.get_format_instructions(),
                    }
                )

                response = model.invoke(final_prompt)

                movie_info = parser.parse(response.content)

            st.success("Extraction Complete!")

            st.subheader("Movie Details")

            st.write(f"**Title:** {movie_info.title}")
            st.write(f"**Release Year:** {movie_info.release_year}")
            st.write(f"**Genre:** {', '.join(movie_info.genre)}")
            st.write(f"**Director:** {movie_info.director}")
            st.write(f"**Main Cast:** {movie_info.main_cast}")
            st.write(f"**Setting Location:** {movie_info.setting_location}")
            st.write(f"**Rating:** {movie_info.rating}")

            st.subheader("Plot")
            st.write(movie_info.plot)

            st.subheader("Themes")
            st.write(movie_info.themes)

            st.subheader("Notable Features")
            st.write(movie_info.notable_features)

            st.subheader("Short Summary")
            st.write(movie_info.short_summary)

            # Optional JSON Output
            with st.expander("View Raw JSON"):
                st.json(movie_info.model_dump())

        except Exception as e:
            st.error(f"Error: {e}")