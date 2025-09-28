from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import streamlit as st
from ai_services.gemini_client import gemini_client
from pages.api_key_management import api_key_manager
import requests

class EnhancedMCPIntegration:
    """Enhanced Model Context Protocol integration with GitHub-style features"""
    
    def __init__(self):
        self.context_store = {}
        self.learning_analytics = {}
        self.github_repo_url = "https://github.com/revanthgopi-nw/mcp-learning-path-demo.git"

    def generate_enhanced_mcp_path(self, user_id: str, goal: str, duration: int, 
                                 difficulty: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate enhanced MCP learning path with GitHub-style features"""
        try:
            # Get user's API keys
            user_keys = api_key_manager.get_user_api_keys(user_id)
            
            # Enhanced context collection
            enhanced_context = self._collect_enhanced_context(user_id, user_context)
            
            # Generate base learning path
            learning_path = self._generate_contextual_path(
                goal, duration, difficulty, enhanced_context, user_keys
            )
            
            # Add MCP enhancements
            learning_path = self._add_mcp_enhancements(learning_path, enhanced_context)
            
            # Add GitHub-style features
            learning_path = self._add_github_features(learning_path, user_id)
            
            # Real-time adaptability setup
            learning_path = self._setup_real_time_adaptation(learning_path, user_id)
            
            return learning_path
            
        except Exception as e:
            st.error(f"Enhanced MCP generation failed: {str(e)}")
            # Fallback to regular MCP
            return gemini_client.generate_mcp_learning_path(goal, duration, difficulty, user_context)

    def _collect_enhanced_context(self, user_id: str, base_context: Dict[str, Any]) -> Dict[str, Any]:
        """Collect enhanced context for MCP"""
        enhanced_context = base_context.copy()
        
        # Add user API capabilities
        user_keys = api_key_manager.get_user_api_keys(user_id)
        enhanced_context['available_integrations'] = {
            'youtube': bool(user_keys.get('youtube')),
            'elevenlabs': bool(user_keys.get('elevenlabs')),
            'twilio': bool(user_keys.get('twilio_sid') and user_keys.get('twilio_token')),
            'notion': bool(user_keys.get('notion')),
            'google_drive': bool(user_keys.get('google_drive'))
        }
        
        # Add learning history analysis
        enhanced_context['learning_history'] = self._analyze_learning_history(user_id)
        
        # Add real-time preferences
        enhanced_context['real_time_preferences'] = self._get_real_time_preferences(user_id)
        
        # Add contextual learning patterns
        enhanced_context['learning_patterns'] = self._identify_learning_patterns(user_id)
        
        return enhanced_context

    def _generate_contextual_path(self, goal: str, duration: int, difficulty: str, 
                                context: Dict[str, Any], user_keys: Dict[str, str]) -> Dict[str, Any]:
        """Generate contextual learning path using available integrations"""
        
        # Use user's Gemini key if available
        gemini_key = user_keys.get('gemini', '')
        
        if gemini_key:
            # Initialize Gemini with user's key
            try:
                from google import genai
                client = genai.Client(api_key=gemini_key)
                
                # Enhanced prompt with full context
                prompt = self._build_enhanced_prompt(goal, duration, difficulty, context)
                
                response = client.models.generate_content(
                    model="gemini-2.5-pro",
                    contents=prompt,
                    config=genai.types.GenerateContentConfig(
                        response_mime_type="application/json"
                    )
                )
                
                if response.text:
                    learning_path = json.loads(response.text)
                    learning_path['generated_with_user_key'] = True
                    return learning_path
                    
            except Exception as e:
                st.warning(f"User Gemini key failed, using demo mode: {str(e)}")
        
        # Fallback to demo generation
        return self._generate_demo_enhanced_path(goal, duration, difficulty, context)

    def _build_enhanced_prompt(self, goal: str, duration: int, difficulty: str, 
                             context: Dict[str, Any]) -> str:
        """Build enhanced prompt for MCP generation"""
        
        integrations = context.get('available_integrations', {})
        learning_history = context.get('learning_history', {})
        preferences = context.get('real_time_preferences', {})
        
        prompt = f"""
        Create an ENHANCED MCP learning path for: "{goal}"
        Duration: {duration} days | Difficulty: {difficulty}
        
        AVAILABLE INTEGRATIONS:
        - YouTube: {integrations.get('youtube', False)}
        - Audio (ElevenLabs): {integrations.get('elevenlabs', False)}
        - Reminders (Twilio): {integrations.get('twilio', False)}
        - Notion: {integrations.get('notion', False)}
        - Google Drive: {integrations.get('google_drive', False)}
        
        LEARNER CONTEXT:
        - Learning History: {learning_history}
        - Preferences: {preferences}
        - Learning Style: {context.get('learning_style', 'mixed')}
        - Available Time: {context.get('time_per_day', '1-2 hours')}
        
        ENHANCED MCP REQUIREMENTS:
        1. **GitHub-Style Features**: Include version control concepts, collaborative learning
        2. **Real-time Adaptation**: Build in checkpoints that adapt based on progress
        3. **Multi-platform Integration**: Leverage available integrations for rich experience
        4. **Contextual Learning**: Adapt content based on learner's history and preferences
        5. **Progressive Complexity**: Gradually increase difficulty with safety nets
        
        JSON STRUCTURE:
        {{
            "goal": "{goal}",
            "duration_days": {duration},
            "difficulty": "{difficulty}",
            "type": "enhanced_mcp",
            "mcp_version": "2.0",
            "github_inspired_features": {{
                "version_control": "Track learning progress like code commits",
                "branching": "Alternative learning paths based on interests",
                "pull_requests": "Peer review and feedback mechanisms",
                "issues": "Track learning challenges and solutions"
            }},
            "real_time_adaptation": {{
                "adaptive_checkpoints": ["Day 3: Assess and adjust", "Day 7: Mid-course correction"],
                "difficulty_scaling": "Dynamic based on performance",
                "content_personalization": "Real-time content adjustment"
            }},
            "daily_plans": [
                {{
                    "day": 1,
                    "title": "Enhanced day title with MCP context",
                    "objectives": ["Context-aware objectives"],
                    "content": "Rich, adaptive content",
                    "activities": ["Interactive, personalized activities"],
                    "mcp_features": {{
                        "adaptation_trigger": "Performance threshold for next day adjustment",
                        "integration_points": ["YouTube videos", "Audio generation", "Notion notes"],
                        "github_analogy": "This day is like creating your first repository",
                        "real_time_feedback": "Continuous assessment and adjustment"
                    }},
                    "estimated_time": "Flexible based on learner pace",
                    "resources": ["Curated, personalized resources"],
                    "checkpoint": "Adaptive assessment point"
                }}
            ],
            "integration_strategy": "How to leverage available user integrations",
            "success_metrics": ["Adaptive success measurement"],
            "personalization_level": "maximum"
        }}
        
        Make this truly next-generation adaptive learning with MCP intelligence.
        """
        
        return prompt

    def _add_mcp_enhancements(self, learning_path: Dict[str, Any], 
                            context: Dict[str, Any]) -> Dict[str, Any]:
        """Add MCP-specific enhancements"""
        
        learning_path['mcp_enhancements'] = {
            'context_awareness_level': 'maximum',
            'real_time_adaptation': True,
            'multi_platform_integration': True,
            'personalization_engine': 'active',
            'learning_analytics': 'comprehensive'
        }
        
        # Add adaptive learning features
        learning_path['adaptive_features'] = {
            'difficulty_auto_adjustment': True,
            'content_personalization': True,
            'pacing_optimization': True,
            'interest_based_branching': True,
            'performance_prediction': True
        }
        
        # Add integration-specific enhancements
        integrations = context.get('available_integrations', {})
        
        for plan in learning_path.get('daily_plans', []):
            plan['mcp_enhancements'] = {
                'adaptive_content': True,
                'real_time_feedback': True,
                'personalized_resources': True,
                'integration_ready': True
            }
            
            # Add integration-specific features
            if integrations.get('youtube'):
                plan['youtube_integration'] = {
                    'curated_videos': True,
                    'playlist_generation': True,
                    'progress_tracking': True
                }
            
            if integrations.get('elevenlabs'):
                plan['audio_integration'] = {
                    'text_to_speech': True,
                    'personalized_voice': True,
                    'audio_summaries': True
                }
            
            if integrations.get('notion'):
                plan['notion_integration'] = {
                    'note_templates': True,
                    'progress_tracking': True,
                    'knowledge_base': True
                }
        
        return learning_path

    def _add_github_features(self, learning_path: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Add GitHub-inspired features to learning path"""
        
        learning_path['github_features'] = {
            'repository_url': self.github_repo_url,
            'version_control': {
                'commits': 'Track daily learning progress',
                'branches': 'Alternative learning paths',
                'merges': 'Integrate different learning approaches',
                'tags': 'Mark learning milestones'
            },
            'collaboration': {
                'pull_requests': 'Peer review of learning progress',
                'issues': 'Track learning challenges',
                'discussions': 'Community learning support',
                'wiki': 'Collaborative knowledge base'
            },
            'project_management': {
                'milestones': 'Learning goal checkpoints',
                'projects': 'Organize learning tasks',
                'actions': 'Automated learning workflows',
                'insights': 'Learning analytics and progress'
            }
        }
        
        # Add GitHub-style progress tracking
        for i, plan in enumerate(learning_path.get('daily_plans', []), 1):
            plan['github_analogy'] = self._get_github_analogy(i, plan.get('title', ''))
            plan['commit_message'] = f"Day {i}: {plan.get('title', 'Learning progress')}"
            plan['branch_options'] = self._generate_branch_options(plan)
        
        return learning_path

    def _get_github_analogy(self, day: int, title: str) -> str:
        """Get GitHub analogy for learning day"""
        analogies = {
            1: "🎯 Initialize repository - Setting up your learning foundation",
            2: "📝 First commit - Adding core knowledge",
            3: "🔀 Create branch - Exploring specialized topics",
            4: "🔧 Refactor code - Improving understanding",
            5: "🚀 Deploy feature - Applying knowledge practically",
            6: "🐛 Fix bugs - Addressing knowledge gaps",
            7: "📊 Release version - Milestone achievement"
        }
        
        if day <= 7:
            return analogies.get(day, f"📈 Continuous integration - Day {day} progress")
        else:
            cycle = ((day - 1) % 7) + 1
            return analogies.get(cycle, f"🔄 Iterative development - Day {day} advancement")

    def _generate_branch_options(self, plan: Dict[str, Any]) -> List[str]:
        """Generate branch options for learning paths"""
        return [
            f"feature/{plan.get('title', 'learning').lower().replace(' ', '-')}",
            f"practice/{plan.get('title', 'exercises').lower().replace(' ', '-')}",
            f"advanced/{plan.get('title', 'deep-dive').lower().replace(' ', '-')}"
        ]

    def _setup_real_time_adaptation(self, learning_path: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Setup real-time adaptation features"""
        
        learning_path['real_time_features'] = {
            'adaptive_engine': 'active',
            'performance_monitoring': 'continuous',
            'content_adjustment': 'dynamic',
            'difficulty_scaling': 'automatic',
            'personalization_updates': 'real-time'
        }
        
        # Add adaptation triggers
        adaptation_points = []
        total_days = learning_path.get('duration_days', 7)
        
        for day in range(3, total_days + 1, 3):  # Every 3 days
            adaptation_points.append({
                'day': day,
                'type': 'performance_checkpoint',
                'actions': [
                    'Assess learning progress',
                    'Adjust difficulty if needed',
                    'Personalize upcoming content',
                    'Update resource recommendations'
                ]
            })
        
        learning_path['adaptation_points'] = adaptation_points
        
        return learning_path

    def _analyze_learning_history(self, user_id: str) -> Dict[str, Any]:
        """Analyze user's learning history for context"""
        # This would analyze past learning paths, completion rates, etc.
        return {
            'completed_paths': 0,
            'average_completion_rate': 0,
            'preferred_difficulty': 'beginner',
            'learning_velocity': 'moderate',
            'strong_areas': [],
            'improvement_areas': []
        }

    def _get_real_time_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get real-time learning preferences"""
        return {
            'preferred_time_slots': ['morning', 'evening'],
            'content_types': ['video', 'text', 'audio'],
            'interaction_style': 'guided',
            'feedback_frequency': 'daily'
        }

    def _identify_learning_patterns(self, user_id: str) -> Dict[str, Any]:
        """Identify user's learning patterns"""
        return {
            'peak_learning_times': ['09:00-11:00', '19:00-21:00'],
            'optimal_session_length': '45-60 minutes',
            'break_frequency': 'every 25 minutes',
            'retention_strategy': 'spaced_repetition'
        }

    def _generate_demo_enhanced_path(self, goal: str, duration: int, 
                                   difficulty: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate demo enhanced MCP path"""
        
        daily_plans = []
        for day in range(1, duration + 1):
            plan = {
                "day": day,
                "title": f"Day {day}: Enhanced {goal} Learning",
                "objectives": [
                    f"Master {goal} concepts with MCP adaptation",
                    f"Apply GitHub-style learning methodology",
                    "Engage with multi-platform integrations"
                ],
                "content": f"Enhanced MCP content for {goal} on day {day}, adapted to your learning style and integrated with available platforms.",
                "activities": [
                    f"Interactive {goal} exercises",
                    "GitHub-style progress tracking",
                    "Multi-platform content consumption",
                    "Real-time adaptation assessment"
                ],
                "mcp_features": {
                    "adaptation_trigger": f"Day {day} performance assessment",
                    "integration_points": ["YouTube", "Audio", "Notion"],
                    "github_analogy": self._get_github_analogy(day, f"{goal} learning"),
                    "real_time_feedback": "Continuous progress monitoring"
                },
                "estimated_time": "Flexible 1-3 hours based on adaptation",
                "resources": [
                    f"Curated {goal} resources",
                    "GitHub-style learning materials",
                    "Multi-platform content"
                ],
                "checkpoint": f"Day {day} adaptive assessment"
            }
            daily_plans.append(plan)
        
        return {
            "goal": goal,
            "duration_days": duration,
            "difficulty": difficulty,
            "type": "enhanced_mcp",
            "mcp_version": "2.0",
            "description": f"Enhanced MCP learning path for {goal} with GitHub-style features and real-time adaptation",
            "github_features": {
                "repository_url": self.github_repo_url,
                "version_control": "Track progress like code commits",
                "collaboration": "Peer learning and review",
                "project_management": "Organized learning workflow"
            },
            "real_time_adaptation": {
                "adaptive_checkpoints": [f"Day {i}: Progress assessment" for i in range(3, duration, 3)],
                "difficulty_scaling": "Dynamic based on performance",
                "content_personalization": "Real-time adjustment"
            },
            "daily_plans": daily_plans,
            "created_with_ai": False,
            "enhanced_mcp": True
        }

# Global instance
enhanced_mcp_integration = EnhancedMCPIntegration()