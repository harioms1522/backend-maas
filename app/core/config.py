# env variables and other configuration settings for the app
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration settings
ENV = os.getenv("ENV", "DEVELOPMENT")

# database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")