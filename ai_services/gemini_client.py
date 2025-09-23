import os
import json
import logging
from typing import Dict, Any, List
from google import genai
from google.genai import types
from pydantic import BaseModel
from config.settings import settings
import streamlit as st

class LearningPathStructure(BaseModel):
    goal: str
    duration_days: int
    difficulty: str
    daily_plans: List[Dict[str, Any]]

class GeminiClient:
    def __init__(self):
        self.client = None
        self.initialize_client()

    def initialize_client(self):
        """Initialize Gemini client"""
        try:
            if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "demo_key":
                self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
                return True
            else:
                st.info("Gemini API not configured. Using demo mode.")
                return False
        except Exception as e:
            st.error(f"Failed to initialize Gemini client: {str(e)}")
            return False

    def generate_normal_learning_path(self, goal: str, duration: int, difficulty: str, 
                                    include_practice: bool = True) -> Dict[str, Any]:
        """Generate a normal learning path"""
        if not self.client:
            return self._generate_demo_learning_path(goal, duration, difficulty, include_practice)

        try:
            practice_text = "with hands-on practice exercises" if include_practice else "focused on theory and concepts"
            
            prompt = f"""
            Create a comprehensive {duration}-day learning path for: "{goal}"
            Difficulty level: {difficulty}
            Learning approach: {practice_text}

            IMPORTANT: Focus ONLY on {goal}-related concepts and practical skills. 
            - Avoid generic HTML content or unrelated information
            - Make content highly specific to {goal} with real examples and hands-on projects  
            - Include actual code examples, specific frameworks, and practical exercises
            - NO generic placeholder content or HTML markup in the response

            Please structure the response as a JSON object with the following format:
            {{
                "goal": "{goal}",
                "duration_days": {duration},
                "difficulty": "{difficulty}",
                "description": "Brief description of what the learner will achieve in {goal}",
                "daily_plans": [
                    {{
                        "day": 1,
                        "title": "Day title focused on {goal}",
                        "objectives": ["Specific {goal} objective 1", "Specific {goal} objective 2"],
                        "content": "Detailed {goal}-specific content for the day - NO generic HTML or markup",
                        "activities": ["Hands-on {goal} activity 1", "Practical {goal} exercise 2"],
                        "estimated_time": "2-3 hours",
                        "resources": ["Specific {goal} resource 1", "Relevant {goal} documentation"],
                        "key_concepts": ["{goal} concept 1", "{goal} concept 2"]
                    }}
                ]
            }}

            Make sure each day builds upon previous days with SPECIFIC {goal} topics and practical projects.
            Include only {goal}-related content, code examples, and hands-on exercises.
            """

            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )

            if response.text:
                learning_path = json.loads(response.text)
                learning_path['type'] = 'normal'
                learning_path['created_with_ai'] = True
                return learning_path
            else:
                return self._generate_demo_learning_path(goal, duration, difficulty, include_practice)

        except Exception as e:
            st.error(f"Failed to generate learning path: {str(e)}")
            return self._generate_demo_learning_path(goal, duration, difficulty, include_practice)

    def generate_mcp_learning_path(self, goal: str, duration: int, difficulty: str,
                                 context_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate an MCP-based learning path with enhanced context"""
        if not self.client:
            return self._generate_demo_mcp_learning_path(goal, duration, difficulty, context_data)

        try:
            context_info = ""
            if context_data:
                context_info = f"""
                Additional Context (Model Context Protocol):
                - Previous learning: {context_data.get('previous_learning', 'None specified')}
                - Learning style: {context_data.get('learning_style', 'Mixed')}
                - Available time per day: {context_data.get('time_per_day', '1-2 hours')}
                - Specific interests: {context_data.get('interests', 'General')}
                - Current skill level: {context_data.get('current_level', 'Beginner')}
                """

            prompt = f"""
            Using Model Context Protocol (MCP) approach, create an adaptive {duration}-day learning path for: "{goal}"
            Difficulty level: {difficulty}
            
            {context_info}

            MCP Enhancement Guidelines:
            1. Adapt content based on provided context
            2. Include checkpoints for adaptive learning
            3. Provide alternative paths based on progress
            4. Include metacognitive elements (learning how to learn)
            5. Integrate spaced repetition and active recall
            6. Consider individual learning preferences

            Structure the response as JSON:
            {{
                "goal": "{goal}",
                "duration_days": {duration},
                "difficulty": "{difficulty}",
                "type": "mcp",
                "context_aware": true,
                "description": "Adaptive learning path description",
                "learning_strategy": "Description of MCP approach used",
                "adaptation_points": ["Day 3: Assessment checkpoint", "Day 7: Path adjustment"],
                "daily_plans": [
                    {{
                        "day": 1,
                        "title": "Day title",
                        "objectives": ["Adaptive objective 1", "Objective 2"],
                        "content": "Context-aware content",
                        "activities": ["Activity with alternatives"],
                        "estimated_time": "Flexible 1-3 hours",
                        "resources": ["Adaptive resources"],
                        "key_concepts": ["Core concepts"],
                        "checkpoint": "Assessment or reflection point",
                        "alternatives": ["Alternative approach if struggling", "Advanced option if progressing quickly"],
                        "metacognitive_element": "What you'll learn about learning itself"
                    }}
                ]
            }}

            Make the path truly adaptive and context-aware, not just a regular learning path labeled as MCP.
            """

            response = self.client.models.generate_content(
                model="gemini-2.5-pro",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )

            if response.text:
                learning_path = json.loads(response.text)
                learning_path['type'] = 'mcp'
                learning_path['created_with_ai'] = True
                return learning_path
            else:
                return self._generate_demo_mcp_learning_path(goal, duration, difficulty, context_data)

        except Exception as e:
            st.error(f"Failed to generate MCP learning path: {str(e)}")
            return self._generate_demo_mcp_learning_path(goal, duration, difficulty, context_data)

    def _generate_demo_learning_path(self, goal: str, duration: int, difficulty: str, 
                                   include_practice: bool) -> Dict[str, Any]:
        """Generate demo learning path when AI is not available"""
        daily_plans = []
        
        for day in range(1, duration + 1):
            daily_plan = {
                "day": day,
                "title": f"Day {day}: Introduction to {goal}" if day == 1 else f"Day {day}: Advanced {goal} Concepts",
                "objectives": [
                    f"Understand key concepts of {goal}",
                    f"Apply {difficulty} level techniques",
                    "Complete practical exercises" if include_practice else "Review theoretical concepts"
                ],
                "content": f"This is day {day} of your {goal} learning journey. Focus on building foundational knowledge and applying concepts through practice.",
                "activities": [
                    f"Read about {goal} fundamentals",
                    f"Watch educational videos on {goal}",
                    "Complete hands-on exercises" if include_practice else "Review key concepts"
                ],
                "estimated_time": "2-3 hours",
                "resources": [
                    f"Introduction to {goal} - Online Tutorial",
                    f"{goal} Best Practices Guide",
                    f"Practice exercises for {goal}"
                ],
                "key_concepts": [
                    f"{goal} fundamentals",
                    f"{difficulty} level applications",
                    "Real-world examples"
                ]
            }
            daily_plans.append(daily_plan)

        return {
            "goal": goal,
            "duration_days": duration,
            "difficulty": difficulty,
            "type": "normal",
            "description": f"A comprehensive {duration}-day journey to master {goal} at {difficulty} level",
            "created_with_ai": False,
            "daily_plans": daily_plans
        }

    def _generate_demo_mcp_learning_path(self, goal: str, duration: int, difficulty: str,
                                       context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate demo MCP learning path when AI is not available"""
        daily_plans = []
        
        for day in range(1, duration + 1):
            daily_plan = {
                "day": day,
                "title": f"Day {day}: Adaptive {goal} Learning",
                "objectives": [
                    f"Context-aware learning of {goal}",
                    f"Metacognitive reflection on {goal}",
                    "Adaptive skill development"
                ],
                "content": f"Day {day} focuses on adaptive learning strategies for {goal}, adjusting to your learning style and progress.",
                "activities": [
                    f"Adaptive exercises in {goal}",
                    "Self-assessment and reflection",
                    "Progress-based activity selection"
                ],
                "estimated_time": "Flexible 1-3 hours",
                "resources": [
                    f"Adaptive {goal} Resources",
                    "Metacognitive Learning Guide",
                    "Progress Tracking Tools"
                ],
                "key_concepts": [
                    f"Adaptive {goal} concepts",
                    "Learning strategy awareness",
                    "Progress self-monitoring"
                ],
                "checkpoint": f"Day {day} progress assessment",
                "alternatives": [
                    f"Alternative approach for {goal}",
                    f"Advanced {goal} path option"
                ],
                "metacognitive_element": "Reflection on your learning process and strategy adjustment"
            }
            daily_plans.append(daily_plan)

        return {
            "goal": goal,
            "duration_days": duration,
            "difficulty": difficulty,
            "type": "mcp",
            "context_aware": True,
            "description": f"An adaptive, context-aware {duration}-day learning path for {goal}",
            "learning_strategy": "Model Context Protocol approach with adaptive content delivery",
            "adaptation_points": [f"Day {i}: Progress checkpoint" for i in range(3, duration, 3)],
            "created_with_ai": False,
            "daily_plans": daily_plans
        }

    def enhance_daily_content(self, daily_plan: Dict[str, Any], user_feedback: str = None) -> Dict[str, Any]:
        """Enhance daily content based on user feedback"""
        if not self.client or not user_feedback:
            return daily_plan

        try:
            prompt = f"""
            Enhance this daily learning plan based on user feedback:
            
            Original Plan: {json.dumps(daily_plan, indent=2)}
            User Feedback: {user_feedback}
            
            Please provide an enhanced version that addresses the feedback while maintaining the learning objectives.
            Return the enhanced plan in the same JSON format.
            """

            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )

            if response.text:
                return json.loads(response.text)
            
        except Exception as e:
            st.error(f"Failed to enhance content: {str(e)}")
        
        return daily_plan

gemini_client = GeminiClient()
