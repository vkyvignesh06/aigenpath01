from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import streamlit as st
from ai_services.gemini_client import gemini_client
from ai_services.mcp_integration import mcp_integration
from database.firestore_client import firestore_client
from integrations.youtube_client import youtube_client
from integrations.drive_client import drive_client
from integrations.elevenlabs_client import elevenlabs_client

class LearningService:
    def __init__(self):
        pass

    def create_learning_path(self, user_id: str, path_data: Dict[str, Any]) -> Optional[str]:
        """Create a new learning path"""
        try:
            goal = path_data.get('goal', '')
            duration = path_data.get('duration', 7)
            difficulty = path_data.get('difficulty', 'beginner')
            path_type = path_data.get('type', 'normal')
            include_practice = path_data.get('include_practice', True)
            
            # Validate input
            if not goal or duration < 1 or duration > 90:
                st.error("Invalid learning path parameters")
                return None
            
            # Generate learning path based on type
            if path_type == 'mcp':
                # Get user context for MCP
                user_context = mcp_integration.collect_user_context(user_id)
                learning_path = mcp_integration.generate_adaptive_path(
                    goal=goal,
                    duration=duration,
                    difficulty=difficulty,
                    user_context=user_context
                )
            else:
                # Generate normal learning path
                learning_path = gemini_client.generate_normal_learning_path(
                    goal=goal,
                    duration=duration,
                    difficulty=difficulty,
                    include_practice=include_practice
                )
            
            if not learning_path:
                st.error("Failed to generate learning path")
                return None
            
            # Enhance with multimedia content
            learning_path = self._enhance_with_multimedia(learning_path)
            
            # Save to database
            path_id = firestore_client.save_learning_path(user_id, learning_path)
            
            if path_id:
                # Create Google Drive document
                self._create_drive_document(learning_path)
                
                # Initialize progress tracking
                self._initialize_progress_tracking(user_id, path_id, duration)
                
                st.success(f"Learning path created successfully! Path ID: {path_id}")
                return path_id
            else:
                st.error("Failed to save learning path")
                return None
                
        except Exception as e:
            st.error(f"Failed to create learning path: {str(e)}")
            return None

    def _enhance_with_multimedia(self, learning_path: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance learning path with multimedia content"""
        try:
            daily_plans = learning_path.get('daily_plans', [])
            
            for plan in daily_plans:
                # Find relevant YouTube videos
                videos = youtube_client.find_learning_videos_for_daily_plan(plan)
                plan['recommended_videos'] = videos
                
                # Generate audio content
                audio_data = elevenlabs_client.create_audio_for_daily_plan(plan)
                if audio_data:
                    plan['audio_available'] = True
                    plan['audio_duration'] = self._estimate_audio_duration(plan)
                else:
                    plan['audio_available'] = False
            
            # Create YouTube playlist data
            playlist_data = youtube_client.create_learning_playlist_data(learning_path)
            learning_path['youtube_playlist'] = playlist_data
            
            return learning_path
            
        except Exception as e:
            st.error(f"Failed to enhance with multimedia: {str(e)}")
            return learning_path

    def _estimate_audio_duration(self, daily_plan: Dict[str, Any]) -> str:
        """Estimate audio duration based on content length"""
        try:
            content = daily_plan.get('content', '')
            word_count = len(content.split())
            # Assume 150 words per minute speaking rate
            duration_minutes = max(1, word_count // 150)
            return f"{duration_minutes}m"
        except:
            return "5m"

    def _create_drive_document(self, learning_path: Dict[str, Any]):
        """Create Google Drive document for learning path"""
        try:
            document_url = drive_client.create_learning_path_document(learning_path)
            if document_url:
                learning_path['drive_document_url'] = document_url
                st.info(f"📄 Learning path document created: {document_url}")
        except Exception as e:
            st.error(f"Failed to create Drive document: {str(e)}")

    def _initialize_progress_tracking(self, user_id: str, path_id: str, duration: int):
        """Initialize progress tracking for the learning path"""
        try:
            # Initialize empty progress
            for day in range(1, duration + 1):
                firestore_client.update_learning_progress(user_id, path_id, day, False)
        except Exception as e:
            st.error(f"Failed to initialize progress tracking: {str(e)}")

    def get_user_learning_paths(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all learning paths for a user"""
        try:
            learning_paths = firestore_client.get_user_learning_paths(user_id)
            
            # Enhance with progress data
            for path in learning_paths:
                path_id = path.get('id', '')
                if path_id:
                    progress = firestore_client.get_learning_progress(user_id, path_id)
                    path['progress'] = progress
                    path['completion_percentage'] = self._calculate_completion_percentage(
                        progress, path.get('duration_days', 0)
                    )
            
            return learning_paths
            
        except Exception as e:
            st.error(f"Failed to get learning paths: {str(e)}")
            return []

    def _calculate_completion_percentage(self, progress: Dict[str, Any], total_days: int) -> float:
        """Calculate completion percentage"""
        try:
            completed_days = progress.get('completed_days', {})
            completed_count = sum(1 for completed in completed_days.values() if completed)
            return (completed_count / total_days * 100) if total_days > 0 else 0
        except:
            return 0

    def update_daily_progress(self, user_id: str, path_id: str, day: int, completed: bool) -> bool:
        """Update progress for a specific day"""
        try:
            success = firestore_client.update_learning_progress(user_id, path_id, day, completed)
            
            if success and completed:
                # Track analytics for MCP paths
                self._track_mcp_progress(user_id, path_id, day)
                
            return success
            
        except Exception as e:
            st.error(f"Failed to update progress: {str(e)}")
            return False

    def _track_mcp_progress(self, user_id: str, path_id: str, day: int):
        """Track progress for MCP analytics"""
        try:
            daily_progress = {
                'day': day,
                'completed': True,
                'time_spent': 60,  # Default estimate
                'difficulty_rating': 3,  # Default rating
                'satisfaction': 4,  # Default satisfaction
                'timestamp': datetime.now()
            }
            
            mcp_integration.track_learning_progress(user_id, path_id, daily_progress)
            
        except Exception as e:
            st.error(f"Failed to track MCP progress: {str(e)}")

    def get_learning_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get learning analytics for user"""
        try:
            learning_paths = self.get_user_learning_paths(user_id)
            
            analytics = {
                'total_paths': len(learning_paths),
                'completed_paths': 0,
                'active_paths': 0,
                'total_days_studied': 0,
                'average_completion_rate': 0,
                'longest_streak': 0,
                'current_streak': 0
            }
            
            total_completion = 0
            
            for path in learning_paths:
                completion_rate = path.get('completion_percentage', 0)
                total_completion += completion_rate
                
                if completion_rate >= 100:
                    analytics['completed_paths'] += 1
                elif completion_rate > 0:
                    analytics['active_paths'] += 1
                
                # Count completed days
                progress = path.get('progress', {})
                completed_days = progress.get('completed_days', {})
                analytics['total_days_studied'] += sum(
                    1 for completed in completed_days.values() if completed
                )
            
            # Calculate average completion rate
            if analytics['total_paths'] > 0:
                analytics['average_completion_rate'] = total_completion / analytics['total_paths']
            
            return analytics
            
        except Exception as e:
            st.error(f"Failed to get learning analytics: {str(e)}")
            return {}

    def get_learning_recommendations(self, user_id: str) -> List[Dict[str, Any]]:
        """Get learning recommendations for user"""
        try:
            # Get user's learning history
            learning_paths = self.get_user_learning_paths(user_id)
            
            recommendations = []
            
            # Analyze completed paths to suggest next steps
            completed_goals = []
            difficulty_levels = []
            
            for path in learning_paths:
                if path.get('completion_percentage', 0) >= 80:
                    completed_goals.append(path.get('goal', ''))
                    difficulty_levels.append(path.get('difficulty', 'beginner'))
            
            # Generate recommendations based on history
            if 'python' in str(completed_goals).lower():
                recommendations.append({
                    'title': 'Advanced Python Development',
                    'description': 'Take your Python skills to the next level with advanced concepts',
                    'difficulty': 'advanced',
                    'estimated_duration': 21,
                    'type': 'mcp'
                })
            
            if 'javascript' in str(completed_goals).lower():
                recommendations.append({
                    'title': 'React.js Framework',
                    'description': 'Learn modern JavaScript framework for building user interfaces',
                    'difficulty': 'intermediate',
                    'estimated_duration': 14,
                    'type': 'normal'
                })
            
            # Add general recommendations
            recommendations.extend([
                {
                    'title': 'Data Science Fundamentals',
                    'description': 'Introduction to data analysis and machine learning',
                    'difficulty': 'beginner',
                    'estimated_duration': 15,
                    'type': 'mcp'
                },
                {
                    'title': 'Digital Marketing',
                    'description': 'Learn modern digital marketing strategies and tools',
                    'difficulty': 'beginner',
                    'estimated_duration': 10,
                    'type': 'normal'
                }
            ])
            
            return recommendations[:5]  # Return top 5 recommendations
            
        except Exception as e:
            st.error(f"Failed to get recommendations: {str(e)}")
            return []

    def export_learning_path(self, user_id: str, path_id: str, format_type: str = 'pdf') -> Optional[bytes]:
        """Export learning path in specified format"""
        try:
            # Get learning path data
            learning_paths = self.get_user_learning_paths(user_id)
            learning_path = None
            
            for path in learning_paths:
                if path.get('id') == path_id:
                    learning_path = path
                    break
            
            if not learning_path:
                st.error("Learning path not found")
                return None
            
            if format_type.lower() == 'pdf':
                return drive_client.export_learning_path_as_pdf(learning_path)
            elif format_type.lower() == 'json':
                import json
                return json.dumps(learning_path, indent=2, default=str).encode('utf-8')
            else:
                st.error(f"Unsupported export format: {format_type}")
                return None
                
        except Exception as e:
            st.error(f"Failed to export learning path: {str(e)}")
            return None

    def duplicate_learning_path(self, user_id: str, path_id: str) -> Optional[str]:
        """Duplicate an existing learning path"""
        try:
            # Get original learning path
            learning_paths = self.get_user_learning_paths(user_id)
            original_path = None
            
            for path in learning_paths:
                if path.get('id') == path_id:
                    original_path = path
                    break
            
            if not original_path:
                st.error("Original learning path not found")
                return None
            
            # Create duplicate with modified title
            duplicated_path = original_path.copy()
            duplicated_path['goal'] = f"{original_path.get('goal', 'Learning Path')} (Copy)"
            duplicated_path['created_at'] = datetime.now()
            
            # Remove old IDs and progress
            if 'id' in duplicated_path:
                del duplicated_path['id']
            if 'progress' in duplicated_path:
                del duplicated_path['progress']
            
            # Save new path
            new_path_id = firestore_client.save_learning_path(user_id, duplicated_path)
            
            if new_path_id:
                # Initialize progress tracking
                duration = duplicated_path.get('duration_days', 7)
                self._initialize_progress_tracking(user_id, new_path_id, duration)
                st.success("Learning path duplicated successfully!")
                return new_path_id
            else:
                st.error("Failed to save duplicated learning path")
                return None
                
        except Exception as e:
            st.error(f"Failed to duplicate learning path: {str(e)}")
            return None

learning_service = LearningService()
