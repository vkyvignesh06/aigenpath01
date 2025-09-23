import os
import requests
from typing import Optional
import streamlit as st
from config.settings import settings

class ElevenLabsClient:
    def __init__(self):
        self.api_key = settings.ELEVENLABS_API_KEY
        self.base_url = "https://api.elevenlabs.io/v1"
        self.demo_mode = self.api_key == "demo_key" or not self.api_key

    def text_to_speech(self, text: str, voice_id: str = "21m00Tcm4TlvDq8ikWAM") -> Optional[bytes]:
        """Convert text to speech using ElevenLabs API"""
        if self.demo_mode:
            st.info("ElevenLabs API not configured. Audio synthesis in demo mode.")
            return self._generate_demo_audio(text)

        try:
            url = f"{self.base_url}/text-to-speech/{voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.api_key
            }
            
            data = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5
                }
            }
            
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                return response.content
            else:
                st.error(f"ElevenLabs API error: {response.status_code}")
                return None
                
        except Exception as e:
            st.error(f"Failed to generate audio: {str(e)}")
            return None

    def _generate_demo_audio(self, text: str) -> bytes:
        """Generate demo audio placeholder"""
        # Return a minimal WAV file header for demo purposes
        # In a real implementation, you might want to use a local TTS library
        demo_message = f"Demo audio for: {text[:50]}..."
        st.info(f"🔊 {demo_message}")
        return b""  # Empty bytes for demo

    def get_available_voices(self) -> list:
        """Get list of available voices"""
        if self.demo_mode:
            return [
                {"voice_id": "demo1", "name": "Demo Voice 1", "category": "narration"},
                {"voice_id": "demo2", "name": "Demo Voice 2", "category": "conversational"}
            ]

        try:
            url = f"{self.base_url}/voices"
            headers = {"xi-api-key": self.api_key}
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                voices_data = response.json()
                return voices_data.get("voices", [])
            else:
                st.error(f"Failed to fetch voices: {response.status_code}")
                return []
                
        except Exception as e:
            st.error(f"Failed to get voices: {str(e)}")
            return []

    def create_audio_for_daily_plan(self, daily_plan: dict) -> Optional[bytes]:
        """Create audio for a daily learning plan"""
        try:
            # Format the daily plan content for audio
            audio_content = self._format_daily_plan_for_audio(daily_plan)
            
            # Generate audio
            audio_data = self.text_to_speech(audio_content)
            
            return audio_data
            
        except Exception as e:
            st.error(f"Failed to create daily plan audio: {str(e)}")
            return None

    def _format_daily_plan_for_audio(self, daily_plan: dict) -> str:
        """Format daily plan content for audio narration"""
        title = daily_plan.get("title", "Daily Learning Plan")
        content = daily_plan.get("content", "")
        objectives = daily_plan.get("objectives", [])
        activities = daily_plan.get("activities", [])
        
        audio_script = f"""
        Welcome to {title}.
        
        Today's learning objectives are:
        {', '.join(objectives)}
        
        Here's what you'll be learning:
        {content}
        
        Your activities for today include:
        {', '.join(activities)}
        
        Take your time with each activity and remember to practice what you learn.
        Good luck with your learning journey today!
        """
        
        return audio_script.strip()

    def generate_lesson_summary_audio(self, lesson_summary: str) -> Optional[bytes]:
        """Generate audio for lesson summary"""
        if not lesson_summary:
            return None
            
        formatted_summary = f"""
        Here's your lesson summary:
        
        {lesson_summary}
        
        Great job completing today's lesson! 
        Remember to review the key concepts and practice what you've learned.
        See you tomorrow for the next part of your learning journey!
        """
        
        return self.text_to_speech(formatted_summary)

elevenlabs_client = ElevenLabsClient()
