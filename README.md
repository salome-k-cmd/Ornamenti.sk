🎨 Ornamenti - Georgian Art Gallery
Final project for TBC x GeoLab Back-end Python course.

Ornamenti is a web platform dedicated to showcasing Georgian art and heritage. It features an AI-driven assistant and interactive community tools.

Tech Stack & Implementation
Backend: Python / Flask
Database: SQLite & SQLAlchemy (Models for Users, Artworks, and Comments)
AI Integration: Groq API (Configured with a specific System Prompt to act as a specialized Gallery Assistant)
Frontend: Bootstrap 5 (Dark Theme) & Vanilla JavaScript
UX Enhancement: AJAX for "Like" buttons to provide a seamless experience without page refreshes.
Admin Features: Secure Dashboard with full CRUD functionality (Create, Read, Update, Delete) for managing the collection.

Security & Deployment
Hosting: Deployed on Render.
Environment Variables: API keys and Secret Keys are managed via environment variables (not hardcoded) for security.

Installation
Clone the repo.
Install dependencies: pip install -r requirements.txt.
Set up your .env file with GROQ_API_KEY.
Run python app.py
