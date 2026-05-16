import os
from groq import Groq
from dotenv import load_dotenv

# explicitly point to .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def _ask(prompt):
    res = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800
    )
    return res.choices[0].message.content

def get_recommendation(mood, history):
    history_str = ", ".join(history) if history else "none yet"
    return _ask(
        f"Recommend 5 movies for someone feeling {mood}. "
        f"Already watched: {history_str}. Don't repeat watched movies. "
        f"Format each as: 🎬 Title (Year)\nWhy: one sentence."
    )

def get_similar(title):
    return _ask(
        f"Recommend 5 movies similar to '{title}'. "
        f"Format each as: 🎬 Title (Year)\nWhy: one sentence."
    )