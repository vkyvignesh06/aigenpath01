import streamlit as st
import hashlib
import secrets
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from firebase_admin import auth as firebase_auth_admin
from config.firebase_config import firebase_config
from database.firestore_client import firestore_client

class FirebaseAuth:
    def __init__(self):
        self.demo_users_file = "demo_users.json"
        self.ensure_demo_users_file()

    def ensure_demo_users_file(self):
        """Ensure demo users file exists"""
        if not os.path.exists(self.demo_users_file):
            demo_users = {
                "demo@example.com": {
                    "password_hash": self.hash_password("demo123"),
                    "name": "Demo User",
                    "role": "student",
                    "created_at": datetime.now().isoformat(),
                    "user_id": "demo_user_123"
                }
            }
            with open(self.demo_users_file, 'w') as f:
                json.dump(demo_users, f, indent=2)

    def hash_password(self, password: str) -> str:
        """Hash password with salt"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{password_hash}"

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        try:
            salt, password_hash = hashed.split(':')
            return hashlib.sha256((password + salt).encode()).hexdigest() == password_hash
        except ValueError:
            return False

    def create_user_with_email_password(self, email: str, password: str, name: str) -> Optional[Dict[str, Any]]:
        """Create user with email and password"""
        try:
            if firebase_config.is_initialized:
                # Firebase mode
                user_record = firebase_auth_admin.create_user(
                    email=email,
                    password=password,
                    display_name=name
                )
                
                # Store additional user data in Firestore
                user_data = {
                    'email': email,
                    'name': name,
                    'role': 'student',
                    'created_at': datetime.now(),
                    'learning_paths': [],
                    'preferences': {
                        'notifications': True,
                        'voice_enabled': True,
                        'reminder_time': '09:00'
                    }
                }
                
                firestore_client.create_user_profile(user_record.uid, user_data)
                
                return {
                    'user_id': user_record.uid,
                    'email': email,
                    'name': name,
                    'role': 'student'
                }
            else:
                # Demo mode - local storage
                with open(self.demo_users_file, 'r') as f:
                    users = json.load(f)
                
                if email in users:
                    return None  # User already exists
                
                user_id = f"demo_user_{secrets.token_hex(8)}"
                users[email] = {
                    "password_hash": self.hash_password(password),
                    "name": name,
                    "role": "student",
                    "created_at": datetime.now().isoformat(),
                    "user_id": user_id
                }
                
                with open(self.demo_users_file, 'w') as f:
                    json.dump(users, f, indent=2)
                
                return {
                    'user_id': user_id,
                    'email': email,
                    'name': name,
                    'role': 'student'
                }
                
        except Exception as e:
            st.error(f"Failed to create user: {str(e)}")
            return None

    def sign_in_with_email_password(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Sign in user with email and password"""
        try:
            if firebase_config.is_initialized:
                # In a real Firebase setup, you'd verify credentials through Firebase Auth
                # For now, we'll check against Firestore
                user_data = firestore_client.get_user_by_email(email)
                if user_data and self.verify_password(password, user_data.get('password_hash', '')):
                    return {
                        'user_id': user_data['user_id'],
                        'email': email,
                        'name': user_data.get('name', 'User'),
                        'role': user_data.get('role', 'student')
                    }
                return None
            else:
                # Demo mode
                with open(self.demo_users_file, 'r') as f:
                    users = json.load(f)
                
                if email in users:
                    user = users[email]
                    if self.verify_password(password, user['password_hash']):
                        return {
                            'user_id': user['user_id'],
                            'email': email,
                            'name': user['name'],
                            'role': user['role']
                        }
                return None
                
        except Exception as e:
            st.error(f"Sign in failed: {str(e)}")
            return None

    def sign_in_with_google(self) -> Optional[Dict[str, Any]]:
        """Sign in with Google (placeholder for demo)"""
        st.info("Google Sign-in would be implemented here with proper OAuth flow")
        # For demo purposes, return a mock Google user
        return {
            'user_id': 'google_demo_user',
            'email': 'google.user@gmail.com',
            'name': 'Google Demo User',
            'role': 'student'
        }

    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get current authenticated user"""
        if 'user' in st.session_state:
            return st.session_state.user
        return None

    def sign_out(self):
        """Sign out current user"""
        if 'user' in st.session_state:
            del st.session_state.user
        if 'authenticated' in st.session_state:
            del st.session_state.authenticated

    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return 'authenticated' in st.session_state and st.session_state.authenticated

    def require_auth(self):
        """Decorator to require authentication"""
        if not self.is_authenticated():
            st.error("Please log in to access this feature")
            st.stop()

firebase_auth = FirebaseAuth()
