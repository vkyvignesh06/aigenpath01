import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    # Firebase Configuration
    FIREBASE_CONFIG = {
        "type": os.getenv("FIREBASE_TYPE"),
        "project_id": os.getenv("FIREBASE_PROJECT_ID"),
        "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
        "private_key": os.getenv("FIREBASE_PRIVATE_KEY", "").replace('\\n', '\n'),
        "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
        "client_id": os.getenv("FIREBASE_CLIENT_ID"),
        "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
        "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
        "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL"),
        "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL")
    }

    # API Keys
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "demo_key")
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "demo_key")
    ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "demo_key")
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "demo_client_id")

    # Twilio Configuration
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "demo_sid")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "demo_token")
    TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "+1234567890")
    TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")

    # Application Settings
    SESSION_SECRET = os.getenv("SESSION_SECRET", "default-secret-key")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

    @property
    def is_demo_mode(self) -> bool:
        """Check if running in demo mode (without real API keys)"""
        return (self.GEMINI_API_KEY == "demo_key" or 
                self.YOUTUBE_API_KEY == "demo_key" or
                not self.GEMINI_API_KEY or
                not self.YOUTUBE_API_KEY)

settings = Settings()
