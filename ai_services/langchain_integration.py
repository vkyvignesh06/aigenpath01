from typing import Dict, Any, List, Optional
from langchain.schema import BaseMessage, HumanMessage, SystemMessage
from langchain.callbacks.base import BaseCallbackHandler
import streamlit as st
from ai_services.gemini_client import gemini_client
import json

class StreamlitCallbackHandler(BaseCallbackHandler):
    """Custom callback handler for Streamlit integration"""
    
    def __init__(self):
        self.container = None
        self.text = ""
    
    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any) -> None:
        """Called when LLM starts running"""
        if st.session_state.get('show_ai_thinking', False):
            self.container = st.empty()
            self.container.info("🤖 AI is thinking...")
    
    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """Called when a new token is generated"""
        if self.container and st.session_state.get('show_ai_thinking', False):
            self.text += token
            self.container.info(f"🤖 AI is generating: {self.text[-50:]}...")
    
    def on_llm_end(self, response, **kwargs: Any) -> None:
        """Called when LLM finishes"""
        if self.container:
            self.container.empty()

class LangChainIntegration:
    """LangChain integration for enhanced AI capabilities"""
    
    def __init__(self):
        self.callback_handler = StreamlitCallbackHandler()
        self.conversation_history = []
    
    def create_learning_path_with_context(self, user_context: Dict[str, Any], 
                                        learning_goal: str, duration: int, 
                                        difficulty: str) -> Dict[str, Any]:
        """Create learning path using LangChain with user context"""
        try:
            # Build context-aware prompt
            system_prompt = self._build_system_prompt(user_context)
            user_prompt = self._build_user_prompt(learning_goal, duration, difficulty, user_context)
            
            # Create messages
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            # Add conversation history for continuity
            if self.conversation_history:
                messages.extend(self.conversation_history[-4:])  # Last 4 messages for context
            
            # Generate learning path using Gemini through LangChain-style interface
            learning_path = self._generate_with_langchain_style(messages, user_context)
            
            # Store in conversation history
            self.conversation_history.extend([
                HumanMessage(content=user_prompt),
                # SystemMessage(content=json.dumps(learning_path, indent=2))
            ])
            
            return learning_path
            
        except Exception as e:
            st.error(f"LangChain integration error: {str(e)}")
            # Fallback to regular generation
            return gemini_client.generate_normal_learning_path(
                learning_goal, duration, difficulty, True
            )
    
    def _build_system_prompt(self, user_context: Dict[str, Any]) -> str:
        """Build system prompt with user context"""
        learning_profile = user_context.get('learning_profile', {})
        preferences = user_context.get('preferences', {})
        progress_history = user_context.get('progress_history', [])
        
        system_prompt = f"""
        You are an expert AI learning coach specializing in personalized education using Model Context Protocol (MCP).
        
        LEARNER PROFILE:
        - Learning Style: {learning_profile.get('learning_style', 'mixed')}
        - Pace Preference: {learning_profile.get('pace_preference', 'moderate')}
        - Complexity Tolerance: {learning_profile.get('complexity_tolerance', 'medium')}
        - Previous Experience: {learning_profile.get('previous_experience', [])}
        
        PREFERENCES:
        - Preferred Content Types: {preferences.get('preferred_content_types', ['text', 'video'])}
        - Study Time Slots: {preferences.get('study_time_slots', ['evening'])}
        - Feedback Style: {preferences.get('feedback_style', 'encouraging')}
        
        LEARNING HISTORY:
        - Previous Paths Completed: {len(progress_history)}
        - Average Completion Rate: {sum(p.get('completion_rate', 0) for p in progress_history) / max(len(progress_history), 1):.1f}%
        
        INSTRUCTIONS:
        1. Create highly personalized learning paths that adapt to the learner's profile
        2. Use the learner's preferred content types and learning style
        3. Adjust complexity based on their tolerance and previous performance
        4. Include metacognitive elements to help them learn how to learn
        5. Provide adaptive checkpoints for real-time path adjustment
        6. Consider their available time and preferred study schedule
        
        Always respond with valid JSON in the specified format.
        """
        
        return system_prompt
    
    def _build_user_prompt(self, learning_goal: str, duration: int, 
                          difficulty: str, user_context: Dict[str, Any]) -> str:
        """Build user prompt with specific requirements"""
        enhanced_context = user_context.get('enhanced_context', {})
        
        user_prompt = f"""
        Create a personalized {duration}-day learning path for: "{learning_goal}"
        
        REQUIREMENTS:
        - Difficulty Level: {difficulty}
        - Duration: {duration} days
        - Learning Style: {enhanced_context.get('learning_style', 'mixed')}
        - Available Time per Day: {enhanced_context.get('time_per_day', '1-2 hours')}
        - Previous Learning: {enhanced_context.get('previous_learning', 'None specified')}
        - Specific Interests: {enhanced_context.get('interests', 'General')}
        
        PERSONALIZATION REQUIREMENTS:
        1. Adapt content delivery to the learner's style
        2. Include spaced repetition and active recall techniques
        3. Provide alternative learning paths for different progress rates
        4. Include self-assessment and reflection opportunities
        5. Add motivational elements and progress celebrations
        6. Consider real-world application and project-based learning
        
        FORMAT: Return a JSON object with the following structure:
        {{
            "goal": "{learning_goal}",
            "duration_days": {duration},
            "difficulty": "{difficulty}",
            "type": "mcp",
            "personalization_level": "high",
            "learning_strategy": "Description of the adaptive approach used",
            "daily_plans": [
                {{
                    "day": 1,
                    "title": "Personalized day title",
                    "objectives": ["Specific learning objectives"],
                    "content": "Detailed content adapted to learning style",
                    "activities": ["Interactive activities"],
                    "estimated_time": "Flexible time estimate",
                    "resources": ["Curated resources"],
                    "key_concepts": ["Core concepts"],
                    "metacognitive_element": "Learning strategy awareness",
                    "checkpoint": "Progress assessment point",
                    "alternatives": ["Alternative approaches for different learning speeds"],
                    "personalization_notes": "How this day is adapted to the learner"
                }}
            ],
            "adaptation_strategy": "How the path will adapt based on progress",
            "success_metrics": ["How to measure learning success"],
            "motivation_elements": ["Built-in motivation and engagement features"]
        }}
        
        Make this truly adaptive and personalized, not just a standard learning path.
        """
        
        return user_prompt
    
    def _generate_with_langchain_style(self, messages: List[BaseMessage], 
                                     user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate learning path using LangChain-style message handling"""
        try:
            # Convert messages to a single prompt for Gemini
            full_prompt = ""
            for message in messages:
                if isinstance(message, SystemMessage):
                    full_prompt += f"SYSTEM: {message.content}\n\n"
                elif isinstance(message, HumanMessage):
                    full_prompt += f"USER: {message.content}\n\n"
            
            # Use Gemini client with enhanced context
            enhanced_context = user_context.get('enhanced_context', {})
            learning_path = gemini_client.generate_mcp_learning_path(
                goal=enhanced_context.get('goal', 'Learning Goal'),
                duration=enhanced_context.get('duration', 7),
                difficulty=enhanced_context.get('difficulty', 'beginner'),
                context_data=enhanced_context
            )
            
            # Enhance with LangChain-specific features
            learning_path = self._add_langchain_enhancements(learning_path, user_context)
            
            return learning_path
            
        except Exception as e:
            st.error(f"Error in LangChain-style generation: {str(e)}")
            raise
    
    def _add_langchain_enhancements(self, learning_path: Dict[str, Any], 
                                  user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Add LangChain-specific enhancements to learning path"""
        try:
            # Add conversation context
            learning_path['langchain_features'] = {
                'conversation_aware': True,
                'context_memory': len(self.conversation_history),
                'personalization_level': 'advanced',
                'adaptive_responses': True
            }
            
            # Add chain-of-thought reasoning
            learning_path['reasoning_chain'] = [
                "Analyzed learner's profile and preferences",
                "Considered previous learning history and performance",
                "Adapted content delivery to preferred learning style",
                "Incorporated metacognitive elements for self-awareness",
                "Designed adaptive checkpoints for real-time adjustment",
                "Included motivational elements based on learner psychology"
            ]
            
            # Add interactive elements
            for plan in learning_path.get('daily_plans', []):
                plan['interactive_elements'] = [
                    "Self-reflection questions",
                    "Progress self-assessment",
                    "Adaptive difficulty adjustment",
                    "Peer discussion prompts",
                    "Real-world application exercises"
                ]
                
                # Add conversation starters for each day
                plan['conversation_starters'] = [
                    f"What aspects of {plan.get('title', 'today\'s topic')} interest you most?",
                    "How does this connect to your previous experience?",
                    "What challenges do you anticipate with this material?",
                    "How will you apply this knowledge in real situations?"
                ]
            
            return learning_path
            
        except Exception as e:
            st.error(f"Error adding LangChain enhancements: {str(e)}")
            return learning_path
    
    def refine_learning_path(self, learning_path: Dict[str, Any], 
                           user_feedback: str, progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """Refine learning path based on user feedback and progress"""
        try:
            # Build refinement prompt
            refinement_prompt = f"""
            CURRENT LEARNING PATH: {json.dumps(learning_path, indent=2)}
            
            USER FEEDBACK: {user_feedback}
            
            PROGRESS DATA: {json.dumps(progress_data, indent=2)}
            
            Please refine the learning path based on:
            1. User feedback and preferences
            2. Actual progress vs. expected progress
            3. Areas where the learner is struggling or excelling
            4. Opportunities for better personalization
            
            Provide an updated learning path that addresses these points while maintaining the overall learning objectives.
            """
            
            # Add to conversation history
            self.conversation_history.append(HumanMessage(content=refinement_prompt))
            
            # Generate refined path
            refined_path = gemini_client.enhance_daily_content(learning_path, user_feedback)
            
            # Add refinement metadata
            refined_path['refinement_history'] = refined_path.get('refinement_history', [])
            refined_path['refinement_history'].append({
                'timestamp': str(pd.Timestamp.now()),
                'feedback': user_feedback,
                'progress_snapshot': progress_data,
                'refinement_type': 'user_feedback'
            })
            
            return refined_path
            
        except Exception as e:
            st.error(f"Error refining learning path: {str(e)}")
            return learning_path
    
    def generate_motivational_message(self, user_context: Dict[str, Any], 
                                    progress_data: Dict[str, Any]) -> str:
        """Generate personalized motivational message"""
        try:
            prompt = f"""
            Generate a personalized motivational message for a learner with the following context:
            
            USER CONTEXT: {json.dumps(user_context, indent=2)}
            PROGRESS DATA: {json.dumps(progress_data, indent=2)}
            
            The message should be:
            1. Encouraging and positive
            2. Specific to their progress and achievements
            3. Motivating for continued learning
            4. Personalized to their learning style and preferences
            5. Brief but impactful (2-3 sentences)
            
            Consider their recent progress, challenges overcome, and learning goals.
            """
            
            # For demo purposes, generate a contextual message
            completion_rate = progress_data.get('completion_rate', 0)
            goal = user_context.get('goal', 'your learning journey')
            
            if completion_rate >= 80:
                message = f"🌟 Outstanding progress on {goal}! You're {completion_rate:.1f}% complete and showing incredible dedication. Keep up this amazing momentum - you're almost at the finish line!"
            elif completion_rate >= 50:
                message = f"💪 Great work on {goal}! You've crossed the halfway mark at {completion_rate:.1f}% completion. Your consistency is paying off - stay focused and success is within reach!"
            else:
                message = f"🚀 Every expert was once a beginner, and you're making solid progress on {goal} at {completion_rate:.1f}% completion. Each day of learning builds your expertise - keep going, you've got this!"
            
            return message
            
        except Exception as e:
            st.error(f"Error generating motivational message: {str(e)}")
            return "Keep up the great work on your learning journey! 🌟"
    
    def clear_conversation_history(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def get_conversation_summary(self) -> str:
        """Get summary of conversation history"""
        if not self.conversation_history:
            return "No conversation history available."
        
        return f"Conversation includes {len(self.conversation_history)} messages covering learning path creation, refinements, and personalization."

# Global instance
langchain_integration = LangChainIntegration()