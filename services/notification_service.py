from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import streamlit as st
import schedule
import time
import threading
from integrations.twilio_client import twilio_client
from database.firestore_client import firestore_client

class NotificationService:
    def __init__(self):
        self.scheduled_notifications = {}
        self.notification_thread = None
        self.running = False

    def schedule_learning_reminder(self, user_id: str, path_id: str, 
                                 reminder_settings: Dict[str, Any]) -> bool:
        """Schedule learning reminders for a user"""
        try:
            # Extract settings
            phone_number = reminder_settings.get('phone_number', '')
            notification_method = reminder_settings.get('method', 'sms')  # sms, whatsapp, voice
            reminder_time = reminder_settings.get('time', '09:00')  # HH:MM format
            days_to_remind = reminder_settings.get('days', [1, 2, 3, 4, 5])  # Mon-Fri
            
            if not phone_number:
                st.error("Phone number is required for notifications")
                return False
            
            # Get learning path details
            learning_paths = firestore_client.get_user_learning_paths(user_id)
            learning_path = None
            
            for path in learning_paths:
                if path.get('id') == path_id:
                    learning_path = path
                    break
            
            if not learning_path:
                st.error("Learning path not found")
                return False
            
            # Schedule reminders
            notification_key = f"{user_id}_{path_id}"
            
            # Store notification settings
            notification_data = {
                'user_id': user_id,
                'path_id': path_id,
                'phone_number': phone_number,
                'method': notification_method,
                'reminder_time': reminder_time,
                'days_to_remind': days_to_remind,
                'learning_path': learning_path,
                'created_at': datetime.now(),
                'active': True
            }
            
            self.scheduled_notifications[notification_key] = notification_data
            
            # Save to database
            firestore_client.save_notification_settings(user_id, {
                'path_id': path_id,
                'settings': reminder_settings,
                'active': True
            })
            
            st.success(f"Learning reminders scheduled for {reminder_time} daily!")
            return True
            
        except Exception as e:
            st.error(f"Failed to schedule reminders: {str(e)}")
            return False

    def send_immediate_reminder(self, user_id: str, path_id: str, 
                              phone_number: str, method: str = 'sms') -> bool:
        """Send an immediate learning reminder"""
        try:
            # Get learning path details
            learning_paths = firestore_client.get_user_learning_paths(user_id)
            learning_path = None
            
            for path in learning_paths:
                if path.get('id') == path_id:
                    learning_path = path
                    break
            
            if not learning_path:
                st.error("Learning path not found")
                return False
            
            # Get current progress
            progress = firestore_client.get_learning_progress(user_id, path_id)
            current_day = self._get_current_learning_day(progress, learning_path)
            
            # Get today's plan
            daily_plans = learning_path.get('daily_plans', [])
            today_plan = None
            
            for plan in daily_plans:
                if plan.get('day') == current_day:
                    today_plan = plan
                    break
            
            if not today_plan:
                st.error("No learning plan found for today")
                return False
            
            # Create reminder data
            reminder_data = {
                'goal': learning_path.get('goal', 'Learning Goal'),
                'day': current_day,
                'title': today_plan.get('title', 'Daily Learning'),
                'objectives': today_plan.get('objectives', []),
                'estimated_time': today_plan.get('estimated_time', '30-60 minutes')
            }
            
            # Send reminder
            success = twilio_client.send_learning_reminder(
                phone_number, reminder_data, method
            )
            
            if success:
                # Log the notification
                self._log_notification_sent(user_id, path_id, 'reminder', method)
                st.success(f"Reminder sent successfully via {method}!")
                return True
            else:
                st.error("Failed to send reminder")
                return False
                
        except Exception as e:
            st.error(f"Failed to send immediate reminder: {str(e)}")
            return False

    def _get_current_learning_day(self, progress: Dict[str, Any], 
                                learning_path: Dict[str, Any]) -> int:
        """Determine current learning day based on progress"""
        try:
            completed_days = progress.get('completed_days', {})
            total_days = learning_path.get('duration_days', 7)
            
            # Find the next incomplete day
            for day in range(1, total_days + 1):
                if not completed_days.get(str(day), False):
                    return day
            
            # If all days are complete, return the last day
            return total_days
            
        except:
            return 1

    def send_completion_celebration(self, user_id: str, path_id: str, 
                                  phone_number: str, method: str = 'sms') -> bool:
        """Send completion celebration message"""
        try:
            # Get learning path details
            learning_paths = firestore_client.get_user_learning_paths(user_id)
            learning_path = None
            
            for path in learning_paths:
                if path.get('id') == path_id:
                    learning_path = path
                    break
            
            if not learning_path:
                return False
            
            # Get progress data
            progress = firestore_client.get_learning_progress(user_id, path_id)
            completed_days = progress.get('completed_days', {})
            total_days = learning_path.get('duration_days', 0)
            
            completion_rate = (sum(1 for completed in completed_days.values() if completed) 
                             / total_days * 100) if total_days > 0 else 0
            
            # Create completion data
            completion_data = {
                'goal': learning_path.get('goal', 'Learning Goal'),
                'total_days': total_days,
                'completion_rate': completion_rate
            }
            
            # Send congratulations
            success = twilio_client.send_completion_congratulations(
                phone_number, completion_data, method
            )
            
            if success:
                self._log_notification_sent(user_id, path_id, 'completion', method)
                return True
            
            return False
            
        except Exception as e:
            st.error(f"Failed to send completion message: {str(e)}")
            return False

    def send_motivation_message(self, user_id: str, path_id: str, 
                              phone_number: str, method: str = 'sms') -> bool:
        """Send motivational message based on progress"""
        try:
            # Get learning path and progress
            learning_paths = firestore_client.get_user_learning_paths(user_id)
            learning_path = None
            
            for path in learning_paths:
                if path.get('id') == path_id:
                    learning_path = path
                    break
            
            if not learning_path:
                return False
            
            progress = firestore_client.get_learning_progress(user_id, path_id)
            completed_days = progress.get('completed_days', {})
            total_days = learning_path.get('duration_days', 0)
            
            completion_rate = (sum(1 for completed in completed_days.values() if completed) 
                             / total_days * 100) if total_days > 0 else 0
            
            # Calculate streak
            streak_days = self._calculate_streak(completed_days)
            
            # Create progress data
            progress_data = {
                'goal': learning_path.get('goal', 'Learning Goal'),
                'completion_rate': completion_rate,
                'streak_days': streak_days,
                'total_days': total_days
            }
            
            # Send motivation message
            success = twilio_client.send_motivation_message(
                phone_number, progress_data, method
            )
            
            if success:
                self._log_notification_sent(user_id, path_id, 'motivation', method)
                return True
            
            return False
            
        except Exception as e:
            st.error(f"Failed to send motivation message: {str(e)}")
            return False

    def _calculate_streak(self, completed_days: Dict[str, bool]) -> int:
        """Calculate current learning streak"""
        try:
            # Convert to sorted list of day numbers
            days = sorted([int(day) for day in completed_days.keys()])
            
            if not days:
                return 0
            
            # Calculate streak from the end
            streak = 0
            for i in range(len(days) - 1, -1, -1):
                day = days[i]
                if completed_days.get(str(day), False):
                    streak += 1
                else:
                    break
            
            return streak
            
        except:
            return 0

    def _log_notification_sent(self, user_id: str, path_id: str, 
                             notification_type: str, method: str):
        """Log sent notification"""
        try:
            log_entry = {
                'user_id': user_id,
                'path_id': path_id,
                'type': notification_type,
                'method': method,
                'sent_at': datetime.now(),
                'status': 'sent'
            }
            
            # In a real implementation, you'd save this to database
            # For now, just log to console
            print(f"Notification logged: {log_entry}")
            
        except Exception as e:
            print(f"Failed to log notification: {str(e)}")

    def get_notification_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Get notification history for user"""
        try:
            # In a real implementation, this would fetch from database
            # For demo, return sample data
            return [
                {
                    'type': 'reminder',
                    'method': 'sms',
                    'sent_at': datetime.now() - timedelta(days=1),
                    'status': 'delivered',
                    'path_goal': 'Python Programming'
                },
                {
                    'type': 'motivation',
                    'method': 'whatsapp',
                    'sent_at': datetime.now() - timedelta(days=3),
                    'status': 'delivered',
                    'path_goal': 'Data Science'
                }
            ]
            
        except Exception as e:
            st.error(f"Failed to get notification history: {str(e)}")
            return []

    def cancel_scheduled_reminders(self, user_id: str, path_id: str) -> bool:
        """Cancel scheduled reminders for a learning path"""
        try:
            notification_key = f"{user_id}_{path_id}"
            
            if notification_key in self.scheduled_notifications:
                self.scheduled_notifications[notification_key]['active'] = False
                
                # Update database
                firestore_client.save_notification_settings(user_id, {
                    'path_id': path_id,
                    'active': False,
                    'cancelled_at': datetime.now()
                })
                
                st.success("Scheduled reminders cancelled successfully!")
                return True
            else:
                st.warning("No scheduled reminders found for this learning path")
                return False
                
        except Exception as e:
            st.error(f"Failed to cancel reminders: {str(e)}")
            return False

    def update_notification_settings(self, user_id: str, path_id: str, 
                                   new_settings: Dict[str, Any]) -> bool:
        """Update notification settings for a learning path"""
        try:
            notification_key = f"{user_id}_{path_id}"
            
            if notification_key in self.scheduled_notifications:
                # Update existing settings
                self.scheduled_notifications[notification_key].update(new_settings)
                
                # Save to database
                firestore_client.save_notification_settings(user_id, {
                    'path_id': path_id,
                    'settings': new_settings,
                    'updated_at': datetime.now(),
                    'active': True
                })
                
                st.success("Notification settings updated successfully!")
                return True
            else:
                st.error("No notification settings found for this learning path")
                return False
                
        except Exception as e:
            st.error(f"Failed to update notification settings: {str(e)}")
            return False

    def test_notification(self, phone_number: str, method: str = 'sms') -> bool:
        """Send a test notification"""
        try:
            test_message = """
🧪 Test Notification from AI Learning Path Generator

This is a test message to verify your notification settings are working correctly.

If you received this message, your notifications are configured properly! 🎉

Ready to start your learning journey? 🚀
            """.strip()
            
            if method.lower() == 'sms':
                return twilio_client.send_sms(phone_number, test_message)
            elif method.lower() == 'whatsapp':
                return twilio_client.send_whatsapp_message(phone_number, test_message)
            elif method.lower() == 'voice':
                return twilio_client.make_voice_call(phone_number, 
                    "This is a test call from AI Learning Path Generator. Your voice notifications are working correctly!")
            else:
                st.error(f"Unsupported notification method: {method}")
                return False
                
        except Exception as e:
            st.error(f"Failed to send test notification: {str(e)}")
            return False

notification_service = NotificationService()
