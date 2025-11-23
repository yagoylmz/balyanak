import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    PREFIX = os.getenv("PREFIX", "!")

    @staticmethod
    def validate():
        if not Config.DISCORD_TOKEN or Config.DISCORD_TOKEN == "your_token_here":
            raise ValueError("DISCORD_TOKEN is not set in .env file.")
