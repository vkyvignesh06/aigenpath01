from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import streamlit as st
from ai_services.gemini_client import gemini_client
from ai_services.langchain_integration import langchain_integration

class MCPIntegration:
    """Model Context Protocol integration for adaptive learning"""
    
    def __init__(self):
        self.context_store = {}
        self.learning_analytics = {}

    def collect_user_context(self, user_id: str) -> Dict[str, Any]:
        """Collect comprehensive user context for MCP"""
        context = {
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'learning_profile': self._get_learning_profile(user_id),
            'progress_history': self._get_progress_history(user_id),
            'preferences': self._get_user_preferences(user_id),
            'performance_metrics': self._get_performance_metrics(user_id)
        }
        
        self.context_store[user_id] = context
        return context

    def _get_learning_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user's learning profile"""
        # In a real implementation, this would fetch from database
        return {
            'learning_style': 'visual',  # visual, auditory, kinesthetic, mixed
            'pace_preference': 'moderate',  # slow, moderate, fast
            'complexity_tolerance': 'medium',  # low, medium, high
            'previous_experience': [],
            'strengths': [],
            'areas_for_improvement': []
        }

    def _get_progress_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's learning progress history"""
        # This would fetch from actual database
        return [
            {
                'path_id': 'previous_path_1',
                'completion_rate': 85,
                'average_time_per_day': 120,  # minutes
                'difficulty_rating': 'medium',
                'satisfaction_score': 4.2
            }
        ]

    def _get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user preferences"""
        return {
            'preferred_content_types': ['video', 'text', 'interactive'],
            'study_time_slots': ['morning', 'evening'],
            'notification_frequency': 'daily',
            'feedback_style': 'encouraging'
        }

    def _get_performance_metrics(self, user_id: str) -> Dict[str, Any]:
        """Get user performance metrics"""
        return {
            'average_completion_rate': 78.5,
            'consistency_score': 85,
            'learning_velocity': 'moderate',
            'retention_rate': 82,
            'engagement_level': 'high'
        }

    def generate_adaptive_path(self, goal: str, duration: int, difficulty: str, 
                             user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate adaptive learning path using MCP"""
        try:
            # Enhance the goal with context-aware information
            enhanced_context = self._enhance_context_for_mcp(user_context)
            enhanced_context.update({
                'goal': goal,
                'duration': duration,
                'difficulty': difficulty
            })
            
            # Use LangChain integration for enhanced context awareness
            learning_path = langchain_integration.create_learning_path_with_context(
                user_context={'enhanced_context': enhanced_context},
                learning_goal=goal,
                duration=duration,
                difficulty=difficulty
            )
            
            # Add MCP-specific enhancements
            learning_path = self._add_mcp_features(learning_path, user_context)
            
            return learning_path
            
        except Exception as e:
            st.error(f"Failed to generate adaptive path: {str(e)}")
            # Fallback to regular MCP generation
            return gemini_client.generate_mcp_learning_path(
                goal=goal,
                duration=duration,
                difficulty=difficulty,
                context_data=enhanced_context
            )

    def _enhance_context_for_mcp(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance context with MCP-specific data"""
        learning_profile = user_context.get('learning_profile', {})
        preferences = user_context.get('preferences', {})
        metrics = user_context.get('performance_metrics', {})
        
        return {
            'learning_style': learning_profile.get('learning_style', 'mixed'),
            'pace_preference': learning_profile.get('pace_preference', 'moderate'),
            'previous_learning': [p.get('path_id', '') for p in user_context.get('progress_history', [])],
            'time_per_day': self._estimate_available_time(preferences),
            'interests': preferences.get('preferred_content_types', []),
            'current_level': self._assess_current_level(metrics),
            'learning_velocity': metrics.get('learning_velocity', 'moderate'),
            'retention_rate': metrics.get('retention_rate', 80)
        }

    def _estimate_available_time(self, preferences: Dict[str, Any]) -> str:
        """Estimate user's available study time"""
        time_slots = preferences.get('study_time_slots', ['evening'])
        if len(time_slots) >= 2:
            return "2-3 hours"
        elif 'morning' in time_slots:
            return "1-2 hours"
        else:
            return "1 hour"

    def _assess_current_level(self, metrics: Dict[str, Any]) -> str:
        """Assess user's current skill level"""
        completion_rate = metrics.get('average_completion_rate', 50)
        if completion_rate >= 90:
            return "Advanced"
        elif completion_rate >= 70:
            return "Intermediate"
        else:
            return "Beginner"

    def _add_mcp_features(self, learning_path: Dict[str, Any], 
                         user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Add MCP-specific features to learning path"""
        # Add adaptive checkpoints
        learning_path['mcp_features'] = {
            'adaptive_checkpoints': self._generate_checkpoints(learning_path['duration_days']),
            'personalization_level': 'high',
            'context_awareness': True,
            'real_time_adaptation': True,
            'learning_analytics': True
        }
        
        # Add user-specific adaptations
        learning_path['user_adaptations'] = {
            'content_type_preference': user_context.get('preferences', {}).get('preferred_content_types', []),
            'difficulty_adjustments': self._calculate_difficulty_adjustments(user_context),
            'pacing_recommendations': self._generate_pacing_recommendations(user_context),
            'learning_style_adaptations': self._get_learning_style_adaptations(user_context)
        }
        
        return learning_path

    def _generate_checkpoints(self, duration: int) -> List[Dict[str, Any]]:
        """Generate adaptive checkpoints"""
        checkpoints = []
        checkpoint_days = [i for i in range(3, duration + 1, 3)]
        
        for day in checkpoint_days:
            checkpoint = {
                'day': day,
                'type': 'adaptive_assessment',
                'description': f'Progress evaluation and path adjustment',
                'adaptive_actions': [
                    'Assess learning progress',
                    'Adjust difficulty if needed',
                    'Modify pacing based on performance',
                    'Update content recommendations'
                ]
            }
            checkpoints.append(checkpoint)
        
        return checkpoints

    def _calculate_difficulty_adjustments(self, user_context: Dict[str, Any]) -> Dict[str, str]:
        """Calculate difficulty adjustments based on user context"""
        metrics = user_context.get('performance_metrics', {})
        completion_rate = metrics.get('average_completion_rate', 70)
        
        if completion_rate >= 90:
            return {'recommendation': 'increase', 'reason': 'High performance indicates readiness for more challenge'}
        elif completion_rate < 60:
            return {'recommendation': 'decrease', 'reason': 'Lower completion rate suggests need for easier content'}
        else:
            return {'recommendation': 'maintain', 'reason': 'Current difficulty level appears appropriate'}

    def _generate_pacing_recommendations(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate pacing recommendations"""
        profile = user_context.get('learning_profile', {})
        pace_preference = profile.get('pace_preference', 'moderate')
        
        pacing_map = {
            'slow': {'daily_time': '30-45 minutes', 'break_frequency': 'every 15 minutes'},
            'moderate': {'daily_time': '45-90 minutes', 'break_frequency': 'every 20 minutes'},
            'fast': {'daily_time': '90-120 minutes', 'break_frequency': 'every 25 minutes'}
        }
        
        return pacing_map.get(pace_preference, pacing_map['moderate'])

    def _get_learning_style_adaptations(self, user_context: Dict[str, Any]) -> List[str]:
        """Get learning style adaptations"""
        learning_style = user_context.get('learning_profile', {}).get('learning_style', 'mixed')
        
        adaptations = {
            'visual': [
                'Include diagrams and flowcharts',
                'Use color-coded information',
                'Provide visual summaries',
                'Add infographics and charts'
            ],
            'auditory': [
                'Include audio explanations',
                'Add discussion points',
                'Provide verbal repetition',
                'Include music or sound cues'
            ],
            'kinesthetic': [
                'Include hands-on activities',
                'Add physical movement breaks',
                'Provide interactive exercises',
                'Include real-world applications'
            ],
            'mixed': [
                'Combine multiple learning modalities',
                'Provide content variety',
                'Include choice in learning methods',
                'Adapt based on progress'
            ]
        }
        
        return adaptations.get(learning_style, adaptations['mixed'])

    def _fallback_adaptive_path(self, goal: str, duration: int, difficulty: str) -> Dict[str, Any]:
        """Fallback adaptive path when MCP fails"""
        return {
            'goal': goal,
            'duration_days': duration,
            'difficulty': difficulty,
            'type': 'mcp',
            'description': f'Adaptive learning path for {goal} (fallback mode)',
            'daily_plans': [
                {
                    'day': i,
                    'title': f'Day {i}: Adaptive Learning',
                    'content': f'Adaptive content for day {i}',
                    'mcp_features': ['basic_adaptation', 'progress_tracking']
                }
                for i in range(1, duration + 1)
            ],
            'mcp_features': {
                'adaptive_checkpoints': [],
                'personalization_level': 'basic',
                'context_awareness': False
            }
        }

    def track_learning_progress(self, user_id: str, path_id: str, 
                              daily_progress: Dict[str, Any]) -> Dict[str, Any]:
        """Track learning progress for adaptive adjustments"""
        if user_id not in self.learning_analytics:
            self.learning_analytics[user_id] = {}
        
        if path_id not in self.learning_analytics[user_id]:
            self.learning_analytics[user_id][path_id] = {
                'daily_progress': {},
                'performance_trends': [],
                'adaptation_history': []
            }
        
        # Store daily progress
        day = daily_progress.get('day', 1)
        self.learning_analytics[user_id][path_id]['daily_progress'][str(day)] = {
            'completed': daily_progress.get('completed', False),
            'time_spent': daily_progress.get('time_spent', 0),
            'difficulty_rating': daily_progress.get('difficulty_rating', 3),
            'satisfaction': daily_progress.get('satisfaction', 3),
            'timestamp': datetime.now().isoformat()
        }
        
        # Calculate performance trends
        self._update_performance_trends(user_id, path_id)
        
        return self.learning_analytics[user_id][path_id]

    def _update_performance_trends(self, user_id: str, path_id: str):
        """Update performance trends based on recent progress"""
        analytics = self.learning_analytics[user_id][path_id]
        daily_progress = analytics['daily_progress']
        
        # Calculate recent performance metrics
        recent_days = list(daily_progress.keys())[-7:]  # Last 7 days
        if recent_days:
            completion_rate = sum(
                daily_progress[day]['completed'] for day in recent_days
            ) / len(recent_days) * 100
            
            avg_time = sum(
                daily_progress[day]['time_spent'] for day in recent_days
            ) / len(recent_days)
            
            avg_difficulty = sum(
                daily_progress[day]['difficulty_rating'] for day in recent_days
            ) / len(recent_days)
            
            # Add to trends
            trend = {
                'date': datetime.now().isoformat(),
                'completion_rate': completion_rate,
                'avg_time_spent': avg_time,
                'avg_difficulty_rating': avg_difficulty,
                'days_analyzed': len(recent_days)
            }
            
            analytics['performance_trends'].append(trend)
            
            # Keep only last 30 trends
            analytics['performance_trends'] = analytics['performance_trends'][-30:]

    def suggest_adaptations(self, user_id: str, path_id: str) -> List[Dict[str, Any]]:
        """Suggest adaptations based on learning analytics"""
        if (user_id not in self.learning_analytics or 
            path_id not in self.learning_analytics[user_id]):
            return []
        
        analytics = self.learning_analytics[user_id][path_id]
        trends = analytics.get('performance_trends', [])
        
        if not trends:
            return []
        
        latest_trend = trends[-1]
        suggestions = []
        
        # Analyze completion rate
        completion_rate = latest_trend['completion_rate']
        if completion_rate < 50:
            suggestions.append({
                'type': 'difficulty_reduction',
                'priority': 'high',
                'description': 'Consider reducing content difficulty',
                'action': 'Simplify concepts and add more examples'
            })
        elif completion_rate > 90:
            suggestions.append({
                'type': 'difficulty_increase',
                'priority': 'medium',
                'description': 'Consider adding more challenging content',
                'action': 'Introduce advanced concepts and complex exercises'
            })
        
        # Analyze time spent
        avg_time = latest_trend['avg_time_spent']
        if avg_time > 120:  # More than 2 hours
            suggestions.append({
                'type': 'content_reduction',
                'priority': 'medium',
                'description': 'Daily content might be too much',
                'action': 'Break content into smaller chunks'
            })
        elif avg_time < 30:  # Less than 30 minutes
            suggestions.append({
                'type': 'content_expansion',
                'priority': 'low',
                'description': 'Could add more comprehensive content',
                'action': 'Include additional exercises and examples'
            })
        
        return suggestions

mcp_integration = MCPIntegration()
