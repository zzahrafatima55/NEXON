from dotenv import load_dotenv
import os
load_dotenv('.env')
print('GROQ:', os.getenv('GROQ_API_KEY')[:10] if os.getenv('GROQ_API_KEY') else 'MISSING')
print('TMDB:', os.getenv('TMDB_API_KEY')[:10] if os.getenv('TMDB_API_KEY') else 'MISSING')
print('GOOGLE_ID:', os.getenv('GOOGLE_CLIENT_ID')[:10] if os.getenv('GOOGLE_CLIENT_ID') else 'MISSING')
print('GOOGLE_SECRET:', os.getenv('GOOGLE_CLIENT_SECRET')[:10] if os.getenv('GOOGLE_CLIENT_SECRET') else 'MISSING')
print('SECRET_KEY:', os.getenv('SECRET_KEY')[:10] if os.getenv('SECRET_KEY') else 'MISSING')