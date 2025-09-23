import os
from typing import Optional
from twilio.rest import Client
from config.settings import settings
import streamlit as st

class TwilioClient:
    def __init__(self):
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.phone_number = settings.TWILIO_PHONE_NUMBER
        self.whatsapp_number = settings.TWILIO_WHATSAPP_NUMBER
        
        self.demo_mode = (self.account_sid == "demo_sid" or 
                         not self.account_sid or 
                         not self.auth_token)
        
        if not self.demo_mode:
            try:
                self.client = Client(self.account_sid, self.auth_token)
            except Exception as e:
                st.error(f"Failed to initialize Twilio client: {str(e)}")
                self.demo_mode = True
                self.client = None
        else:
            self.client = None

    def send_sms(self, to_phone_number: str, message: str) -> bool:
        """Send SMS message"""
        if self.demo_mode:
            st.info(f"📱 Demo SMS to {to_phone_number}: {message[:50]}...")
            return True

        try:
            message_instance = self.client.messages.create(
                body=message,
                from_=self.phone_number,
                to=to_phone_number
            )
            
            st.success(f"SMS sent successfully. Message SID: {message_instance.sid}")
            return True
            
        except Exception as e:
            st.error(f"Failed to send SMS: {str(e)}")
            return False

    def send_whatsapp_message(self, to_phone_number: str, message: str) -> bool:
        """Send WhatsApp message"""
        if self.demo_mode:
            st.info(f"💬 Demo WhatsApp to {to_phone_number}: {message[:50]}...")
            return True

        try:
            # Format phone number for WhatsApp
            whatsapp_to = f"whatsapp:{to_phone_number}"
            
            message_instance = self.client.messages.create(
                body=message,
                from_=self.whatsapp_number,
                to=whatsapp_to
            )
            
            st.success(f"WhatsApp message sent successfully. Message SID: {message_instance.sid}")
            return True
            
        except Exception as e:
            st.error(f"Failed to send WhatsApp message: {str(e)}")
            return False

    def make_voice_call(self, to_phone_number: str, message: str) -> bool:
        """Make a voice call with text-to-speech message"""
        if self.demo_mode:
            st.info(f"📞 Demo voice call to {to_phone_number}: {message[:50]}...")
            return True

        try:
            # Create TwiML for the voice message
            twiml_url = self._create_twiml_for_message(message)
            
            call = self.client.calls.create(
                twiml=f'<Response><Say>{message}</Say></Response>',
                to=to_phone_number,
                from_=self.phone_number
            )
            
            st.success(f"Voice call initiated successfully. Call SID: {call.sid}")
            return True
            
        except Exception as e:
            st.error(f"Failed to make voice call: {str(e)}")
            return False

    def _create_twiml_for_message(self, message: str) -> str:
        """Create TwiML for voice message"""
        return f"""
        <Response>
            <Say voice="alice">
                {message}
            </Say>
        </Response>
        """

    def send_learning_reminder(self, to_phone_number: str, reminder_data: dict, 
                             method: str = "sms") -> bool:
        """Send learning reminder via specified method"""
        try:
            # Format the reminder message
            message = self._format_reminder_message(reminder_data)
            
            if method.lower() == "sms":
                return self.send_sms(to_phone_number, message)
            elif method.lower() == "whatsapp":
                return self.send_whatsapp_message(to_phone_number, message)
            elif method.lower() == "voice":
                return self.make_voice_call(to_phone_number, message)
            else:
                st.error(f"Unsupported notification method: {method}")
                return False
                
        except Exception as e:
            st.error(f"Failed to send learning reminder: {str(e)}")
            return False

    def _format_reminder_message(self, reminder_data: dict) -> str:
        """Format reminder message"""
        goal = reminder_data.get("goal", "your learning goal")
        day = reminder_data.get("day", 1)
        title = reminder_data.get("title", "Daily Learning")
        
        message = f"""
🎓 Learning Reminder: {goal}

📅 Day {day}: {title}

It's time for your daily learning session! 

🎯 Today's focus: {reminder_data.get('objectives', ['Continue your learning journey'])[0] if reminder_data.get('objectives') else 'Continue your learning journey'}

⏱️ Estimated time: {reminder_data.get('estimated_time', '30-60 minutes')}

Keep up the great work! Consistency is key to achieving your learning goals.

Happy learning! 🚀
        """.strip()
        
        return message

    def send_completion_congratulations(self, to_phone_number: str, 
                                      completion_data: dict, method: str = "sms") -> bool:
        """Send completion congratulations message"""
        try:
            message = self._format_completion_message(completion_data)
            
            if method.lower() == "sms":
                return self.send_sms(to_phone_number, message)
            elif method.lower() == "whatsapp":
                return self.send_whatsapp_message(to_phone_number, message)
            elif method.lower() == "voice":
                return self.make_voice_call(to_phone_number, message)
            else:
                st.error(f"Unsupported notification method: {method}")
                return False
                
        except Exception as e:
            st.error(f"Failed to send completion message: {str(e)}")
            return False

    def _format_completion_message(self, completion_data: dict) -> str:
        """Format completion congratulations message"""
        goal = completion_data.get("goal", "your learning goal")
        total_days = completion_data.get("total_days", 0)
        completion_rate = completion_data.get("completion_rate", 100)
        
        message = f"""
🎉 Congratulations! 🎉

You've completed your learning path: {goal}

📊 Your Achievement:
• Duration: {total_days} days
• Completion Rate: {completion_rate}%

🏆 You've shown amazing dedication and consistency in your learning journey!

🚀 Ready for your next challenge? Create a new learning path to continue growing!

Keep learning, keep growing! 💪
        """.strip()
        
        return message

    def send_motivation_message(self, to_phone_number: str, 
                              progress_data: dict, method: str = "sms") -> bool:
        """Send motivational message based on progress"""
        try:
            message = self._format_motivation_message(progress_data)
            
            if method.lower() == "sms":
                return self.send_sms(to_phone_number, message)
            elif method.lower() == "whatsapp":
                return self.send_whatsapp_message(to_phone_number, message)
            elif method.lower() == "voice":
                return self.make_voice_call(to_phone_number, message)
            else:
                st.error(f"Unsupported notification method: {method}")
                return False
                
        except Exception as e:
            st.error(f"Failed to send motivation message: {str(e)}")
            return False

    def _format_motivation_message(self, progress_data: dict) -> str:
        """Format motivational message"""
        completion_rate = progress_data.get("completion_rate", 0)
        streak_days = progress_data.get("streak_days", 0)
        goal = progress_data.get("goal", "your learning goal")
        
        if completion_rate >= 80:
            message = f"""
🌟 Outstanding Progress! 🌟

You're crushing your learning goal: {goal}

📈 Progress: {completion_rate}%
🔥 Streak: {streak_days} days

You're so close to the finish line! Keep up the incredible work!

Success is just around the corner! 💪🎯
            """.strip()
        elif completion_rate >= 50:
            message = f"""
💪 Great Progress! 💪

You're making solid progress on: {goal}

📈 Progress: {completion_rate}%
🔥 Streak: {streak_days} days

You're halfway there! Every day of learning brings you closer to your goal.

Keep going, you've got this! 🚀
            """.strip()
        else:
            message = f"""
🌱 Every Step Counts! 🌱

Your learning journey for {goal} is underway!

📈 Progress: {completion_rate}%
🔥 Streak: {streak_days} days

Remember, consistency beats perfection. Small daily steps lead to big achievements!

You're building something amazing! 🎯✨
            """.strip()
        
        return message

twilio_client = TwilioClient()
