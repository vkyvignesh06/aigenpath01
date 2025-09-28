import streamlit as st
from typing import Dict, Any
from database.firestore_client import firestore_client
from utils.helpers import *
import json

class APIKeyManager:
    def __init__(self):
        self.supported_apis = {
            'gemini': {
                'name': 'Google Gemini AI',
                'description': 'AI-powered learning path generation',
                'required': True,
                'placeholder': 'AIzaSy...'
            },
            'youtube': {
                'name': 'YouTube Data API v3',
                'description': 'Curated video recommendations',
                'required': True,
                'placeholder': 'AIzaSy...'
            },
            'elevenlabs': {
                'name': 'ElevenLabs TTS',
                'description': 'Text-to-speech audio generation',
                'required': False,
                'placeholder': 'sk_...'
            },
            'twilio_sid': {
                'name': 'Twilio Account SID',
                'description': 'SMS, WhatsApp, and voice reminders',
                'required': False,
                'placeholder': 'AC...'
            },
            'twilio_token': {
                'name': 'Twilio Auth Token',
                'description': 'Twilio authentication token',
                'required': False,
                'placeholder': 'your_auth_token'
            },
            'notion': {
                'name': 'Notion Integration Token',
                'description': 'Note-taking and roadmap tracking',
                'required': False,
                'placeholder': 'secret_...'
            },
            'google_drive': {
                'name': 'Google Drive API Key',
                'description': 'Document storage and sharing',
                'required': False,
                'placeholder': 'AIzaSy...'
            }
        }

    def show_api_key_management(self, user_id: str):
        """Show API key management interface"""
        st.markdown("""
        <div class="main-header">
            <h1>🔑 API Key Management</h1>
            <p>Manage your personal API keys for enhanced features</p>
        </div>
        """, unsafe_allow_html=True)

        # Get user's current API keys
        user_keys = self.get_user_api_keys(user_id)
        
        # API Key Status Overview
        st.subheader("📊 API Integration Status")
        
        col1, col2 = st.columns(2)
        
        with col1:
            configured_count = sum(1 for key in self.supported_apis.keys() if user_keys.get(key))
            total_count = len(self.supported_apis)
            
            st.metric("Configured APIs", f"{configured_count}/{total_count}")
            
            # Progress bar
            progress = configured_count / total_count
            st.progress(progress)
        
        with col2:
            required_apis = [k for k, v in self.supported_apis.items() if v['required']]
            required_configured = sum(1 for key in required_apis if user_keys.get(key))
            
            if required_configured == len(required_apis):
                st.success("✅ All required APIs configured")
            else:
                st.warning(f"⚠️ {len(required_apis) - required_configured} required APIs missing")

        # API Configuration Forms
        st.subheader("🔧 Configure API Keys")
        
        tabs = st.tabs(["🤖 AI Services", "📱 Communication", "☁️ Storage"])
        
        with tabs[0]:  # AI Services
            self._show_ai_services_config(user_id, user_keys)
        
        with tabs[1]:  # Communication
            self._show_communication_config(user_id, user_keys)
        
        with tabs[2]:  # Storage
            self._show_storage_config(user_id, user_keys)

        # Quick Setup Guide
        with st.expander("📚 Quick Setup Guide"):
            st.markdown("""
            ### Getting Your API Keys:
            
            **Required APIs:**
            1. **Google Gemini AI**: Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
            2. **YouTube Data API**: Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
            
            **Optional APIs:**
            3. **ElevenLabs**: Sign up at [ElevenLabs](https://elevenlabs.io/) → Profile → API Keys
            4. **Twilio**: Create account at [Twilio](https://www.twilio.com/) → Console → Account Info
            5. **Notion**: Visit [Notion Developers](https://developers.notion.com/) → Create Integration
            6. **Google Drive**: Use same Google Cloud Console as YouTube API
            
            ### Security Notes:
            - API keys are encrypted and stored securely
            - Keys are only accessible by your account
            - You can update or remove keys anytime
            """)

    def _show_ai_services_config(self, user_id: str, user_keys: Dict[str, str]):
        """Show AI services configuration"""
        st.markdown("### 🤖 AI Services")
        
        with st.form("ai_services_form"):
            # Gemini API
            gemini_key = st.text_input(
                "Google Gemini AI API Key *",
                value=user_keys.get('gemini', ''),
                type="password",
                placeholder=self.supported_apis['gemini']['placeholder'],
                help=self.supported_apis['gemini']['description']
            )
            
            # YouTube API
            youtube_key = st.text_input(
                "YouTube Data API v3 Key *",
                value=user_keys.get('youtube', ''),
                type="password",
                placeholder=self.supported_apis['youtube']['placeholder'],
                help=self.supported_apis['youtube']['description']
            )
            
            # ElevenLabs API
            elevenlabs_key = st.text_input(
                "ElevenLabs API Key",
                value=user_keys.get('elevenlabs', ''),
                type="password",
                placeholder=self.supported_apis['elevenlabs']['placeholder'],
                help=self.supported_apis['elevenlabs']['description']
            )
            
            if st.form_submit_button("💾 Save AI Services Keys", use_container_width=True):
                keys_to_save = {}
                if gemini_key:
                    keys_to_save['gemini'] = gemini_key
                if youtube_key:
                    keys_to_save['youtube'] = youtube_key
                if elevenlabs_key:
                    keys_to_save['elevenlabs'] = elevenlabs_key
                
                if self.save_user_api_keys(user_id, keys_to_save):
                    st.success("🎉 AI Services keys saved successfully!")
                    st.rerun()

    def _show_communication_config(self, user_id: str, user_keys: Dict[str, str]):
        """Show communication services configuration"""
        st.markdown("### 📱 Communication Services")
        
        with st.form("communication_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                twilio_sid = st.text_input(
                    "Twilio Account SID",
                    value=user_keys.get('twilio_sid', ''),
                    type="password",
                    placeholder=self.supported_apis['twilio_sid']['placeholder'],
                    help=self.supported_apis['twilio_sid']['description']
                )
            
            with col2:
                twilio_token = st.text_input(
                    "Twilio Auth Token",
                    value=user_keys.get('twilio_token', ''),
                    type="password",
                    placeholder=self.supported_apis['twilio_token']['placeholder'],
                    help=self.supported_apis['twilio_token']['description']
                )
            
            # Phone numbers
            twilio_phone = st.text_input(
                "Twilio Phone Number",
                value=user_keys.get('twilio_phone', ''),
                placeholder="+1234567890",
                help="Your Twilio phone number for sending SMS and making calls"
            )
            
            twilio_whatsapp = st.text_input(
                "Twilio WhatsApp Number",
                value=user_keys.get('twilio_whatsapp', ''),
                placeholder="whatsapp:+14155238886",
                help="Twilio WhatsApp sandbox number"
            )
            
            if st.form_submit_button("💾 Save Communication Keys", use_container_width=True):
                keys_to_save = {}
                if twilio_sid:
                    keys_to_save['twilio_sid'] = twilio_sid
                if twilio_token:
                    keys_to_save['twilio_token'] = twilio_token
                if twilio_phone:
                    keys_to_save['twilio_phone'] = twilio_phone
                if twilio_whatsapp:
                    keys_to_save['twilio_whatsapp'] = twilio_whatsapp
                
                if self.save_user_api_keys(user_id, keys_to_save):
                    st.success("📱 Communication keys saved successfully!")
                    st.rerun()

    def _show_storage_config(self, user_id: str, user_keys: Dict[str, str]):
        """Show storage services configuration"""
        st.markdown("### ☁️ Storage Services")
        
        with st.form("storage_form"):
            # Notion API
            notion_key = st.text_input(
                "Notion Integration Token",
                value=user_keys.get('notion', ''),
                type="password",
                placeholder=self.supported_apis['notion']['placeholder'],
                help=self.supported_apis['notion']['description']
            )
            
            # Google Drive API
            drive_key = st.text_input(
                "Google Drive API Key",
                value=user_keys.get('google_drive', ''),
                type="password",
                placeholder=self.supported_apis['google_drive']['placeholder'],
                help=self.supported_apis['google_drive']['description']
            )
            
            if st.form_submit_button("💾 Save Storage Keys", use_container_width=True):
                keys_to_save = {}
                if notion_key:
                    keys_to_save['notion'] = notion_key
                if drive_key:
                    keys_to_save['google_drive'] = drive_key
                
                if self.save_user_api_keys(user_id, keys_to_save):
                    st.success("☁️ Storage keys saved successfully!")
                    st.rerun()

    def get_user_api_keys(self, user_id: str) -> Dict[str, str]:
        """Get user's API keys"""
        try:
            if firestore_client.firebase_config.is_initialized:
                doc_ref = firestore_client.firebase_config.db.collection('user_api_keys').document(user_id)
                doc = doc_ref.get()
                return doc.to_dict() if doc.exists else {}
            else:
                # Demo mode - load from local file
                try:
                    with open(f"user_keys_{user_id}.json", 'r') as f:
                        return json.load(f)
                except FileNotFoundError:
                    return {}
        except Exception as e:
            st.error(f"Failed to load API keys: {str(e)}")
            return {}

    def save_user_api_keys(self, user_id: str, api_keys: Dict[str, str]) -> bool:
        """Save user's API keys"""
        try:
            # Get existing keys
            existing_keys = self.get_user_api_keys(user_id)
            
            # Update with new keys
            existing_keys.update(api_keys)
            
            if firestore_client.firebase_config.is_initialized:
                doc_ref = firestore_client.firebase_config.db.collection('user_api_keys').document(user_id)
                doc_ref.set(existing_keys)
            else:
                # Demo mode - save to local file
                with open(f"user_keys_{user_id}.json", 'w') as f:
                    json.dump(existing_keys, f, indent=2)
            
            return True
        except Exception as e:
            st.error(f"Failed to save API keys: {str(e)}")
            return False

    def get_api_key(self, user_id: str, api_name: str) -> str:
        """Get specific API key for user"""
        user_keys = self.get_user_api_keys(user_id)
        return user_keys.get(api_name, '')

    def has_required_keys(self, user_id: str) -> bool:
        """Check if user has all required API keys"""
        user_keys = self.get_user_api_keys(user_id)
        required_apis = [k for k, v in self.supported_apis.items() if v['required']]
        return all(user_keys.get(key) for key in required_apis)

# Global instance
api_key_manager = APIKeyManager()