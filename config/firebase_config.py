import firebase_admin
from firebase_admin import credentials, auth, firestore
from config.settings import settings
import streamlit as st

class FirebaseConfig:
    _instance = None
    _app = None
    _db = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseConfig, cls).__new__(cls)
        return cls._instance

    def initialize_firebase(self):
        """Initialize Firebase app and services"""
        try:
            if not firebase_admin._apps:
                # Check if we have valid Firebase configuration
                if all(value for value in settings.FIREBASE_CONFIG.values()):
                    cred = credentials.Certificate(settings.FIREBASE_CONFIG)
                    self._app = firebase_admin.initialize_app(cred)
                    self._db = firestore.client()
                    return True
                else:
                    # Demo mode - Firebase not configured
                    st.warning("Firebase not configured. Running in demo mode.")
                    return False
            else:
                self._app = firebase_admin.get_app()
                self._db = firestore.client()
                return True
        except Exception as e:
            st.error(f"Firebase initialization failed: {str(e)}")
            return False

    @property
    def db(self):
        """Get Firestore database instance"""
        if self._db is None:
            self.initialize_firebase()
        return self._db

    @property
    def is_initialized(self) -> bool:
        """Check if Firebase is properly initialized"""
        return self._app is not None and self._db is not None

firebase_config = FirebaseConfig()
