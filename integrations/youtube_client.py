import os
import requests
from typing import List, Dict, Any, Optional
from config.settings import settings
import streamlit as st

class YouTubeClient:
    def __init__(self):
        self.api_key = settings.YOUTUBE_API_KEY
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self.demo_mode = self.api_key == "demo_key" or not self.api_key

    def search_videos(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search for YouTube videos related to the query"""
        if self.demo_mode:
            return self._get_demo_videos(query, max_results)

        try:
            url = f"{self.base_url}/search"
            params = {
                'part': 'snippet',
                'q': query,
                'type': 'video',
                'maxResults': max_results,
                'key': self.api_key,
                'videoEmbeddable': 'true',
                'videoSyndicated': 'true',
                'safeSearch': 'strict'
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                videos = []
                
                for item in data.get('items', []):
                    video = {
                        'video_id': item['id']['videoId'],
                        'title': item['snippet']['title'],
                        'description': item['snippet']['description'],
                        'thumbnail': item['snippet']['thumbnails']['medium']['url'],
                        'channel': item['snippet']['channelTitle'],
                        'published_at': item['snippet']['publishedAt'],
                        'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}"
                    }
                    videos.append(video)
                
                return videos
            else:
                st.error(f"YouTube API error: {response.status_code}")
                return self._get_demo_videos(query, max_results)
                
        except Exception as e:
            st.error(f"Failed to search YouTube videos: {str(e)}")
            return self._get_demo_videos(query, max_results)

    def _get_demo_videos(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Get demo videos when API is not available"""
        demo_videos = [
            {
                'video_id': 'demo1',
                'title': f'Introduction to {query}',
                'description': f'A comprehensive introduction to {query} covering all the basics you need to know.',
                'thumbnail': 'https://via.placeholder.com/320x180?text=Demo+Video',
                'channel': 'Demo Learning Channel',
                'published_at': '2024-01-01T00:00:00Z',
                'url': f'https://www.youtube.com/results?search_query={query.replace(" ", "+")}'
            },
            {
                'video_id': 'demo2',
                'title': f'{query} Best Practices',
                'description': f'Learn the best practices and advanced techniques for {query}.',
                'thumbnail': 'https://via.placeholder.com/320x180?text=Demo+Video+2',
                'channel': 'Expert Learning Hub',
                'published_at': '2024-01-01T00:00:00Z',
                'url': f'https://www.youtube.com/results?search_query={query.replace(" ", "+")}+tutorial'
            },
            {
                'video_id': 'demo3',
                'title': f'Hands-on {query} Tutorial',
                'description': f'Step-by-step tutorial for practical {query} implementation.',
                'thumbnail': 'https://via.placeholder.com/320x180?text=Demo+Video+3',
                'channel': 'Practical Learning',
                'published_at': '2024-01-01T00:00:00Z',
                'url': f'https://www.youtube.com/results?search_query={query.replace(" ", "+")}+hands+on'
            }
        ]
        
        return demo_videos[:max_results]

    def get_video_details(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific video"""
        if self.demo_mode:
            return {
                'video_id': video_id,
                'title': 'Demo Video Title',
                'description': 'Demo video description',
                'duration': 'PT10M30S',
                'view_count': '1000000',
                'like_count': '50000',
                'channel': 'Demo Channel'
            }

        try:
            url = f"{self.base_url}/videos"
            params = {
                'part': 'snippet,contentDetails,statistics',
                'id': video_id,
                'key': self.api_key
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                items = data.get('items', [])
                
                if items:
                    item = items[0]
                    return {
                        'video_id': video_id,
                        'title': item['snippet']['title'],
                        'description': item['snippet']['description'],
                        'duration': item['contentDetails']['duration'],
                        'view_count': item['statistics'].get('viewCount', 0),
                        'like_count': item['statistics'].get('likeCount', 0),
                        'channel': item['snippet']['channelTitle']
                    }
            
            return None
            
        except Exception as e:
            st.error(f"Failed to get video details: {str(e)}")
            return None

    def find_learning_videos_for_daily_plan(self, daily_plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find relevant YouTube videos for a daily learning plan"""
        try:
            # Extract key topics from the daily plan
            title = daily_plan.get('title', '')
            objectives = daily_plan.get('objectives', [])
            key_concepts = daily_plan.get('key_concepts', [])
            
            # Create search queries
            search_queries = []
            
            # Use the main title
            if title:
                search_queries.append(title)
            
            # Use objectives
            for objective in objectives[:2]:  # Limit to first 2 objectives
                search_queries.append(objective)
            
            # Use key concepts
            for concept in key_concepts[:2]:  # Limit to first 2 concepts
                search_queries.append(concept)
            
            # Collect videos from all searches
            all_videos = []
            for query in search_queries[:3]:  # Limit to 3 searches
                videos = self.search_videos(query, max_results=2)
                all_videos.extend(videos)
            
            # Remove duplicates based on video_id
            unique_videos = []
            seen_ids = set()
            for video in all_videos:
                if video['video_id'] not in seen_ids:
                    unique_videos.append(video)
                    seen_ids.add(video['video_id'])
            
            return unique_videos[:5]  # Return top 5 unique videos
            
        except Exception as e:
            st.error(f"Failed to find learning videos: {str(e)}")
            return []

    def create_learning_playlist_data(self, learning_path: Dict[str, Any]) -> Dict[str, Any]:
        """Create playlist data for a learning path"""
        try:
            goal = learning_path.get('goal', 'Learning Path')
            daily_plans = learning_path.get('daily_plans', [])
            
            playlist_data = {
                'title': f"Learning Path: {goal}",
                'description': f"Curated videos for your {goal} learning journey",
                'videos': []
            }
            
            # Collect videos for each day
            for day_plan in daily_plans[:7]:  # Limit to first 7 days
                day_videos = self.find_learning_videos_for_daily_plan(day_plan)
                
                for video in day_videos[:2]:  # 2 videos per day
                    video['day'] = day_plan.get('day', 1)
                    video['day_title'] = day_plan.get('title', f"Day {day_plan.get('day', 1)}")
                    playlist_data['videos'].append(video)
            
            return playlist_data
            
        except Exception as e:
            st.error(f"Failed to create playlist data: {str(e)}")
            return {'title': 'Learning Playlist', 'description': 'Videos for learning', 'videos': []}

    def format_video_duration(self, duration_str: str) -> str:
        """Format YouTube duration string to readable format"""
        try:
            # Parse ISO 8601 duration (PT10M30S format)
            import re
            pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
            match = re.match(pattern, duration_str)
            
            if match:
                hours, minutes, seconds = match.groups()
                hours = int(hours) if hours else 0
                minutes = int(minutes) if minutes else 0
                seconds = int(seconds) if seconds else 0
                
                if hours > 0:
                    return f"{hours}h {minutes}m {seconds}s"
                elif minutes > 0:
                    return f"{minutes}m {seconds}s"
                else:
                    return f"{seconds}s"
            
            return "Unknown duration"
            
        except Exception:
            return "Unknown duration"

    def get_educational_channels(self, subject: str) -> List[Dict[str, Any]]:
        """Get recommended educational channels for a subject"""
        if self.demo_mode:
            return [
                {
                    'channel_id': 'demo_channel_1',
                    'title': f'{subject} Education Hub',
                    'description': f'The best channel for learning {subject}',
                    'subscriber_count': '1M',
                    'video_count': '500+'
                },
                {
                    'channel_id': 'demo_channel_2',
                    'title': f'Master {subject}',
                    'description': f'Professional {subject} tutorials and courses',
                    'subscriber_count': '500K',
                    'video_count': '300+'
                }
            ]

        try:
            # Search for channels related to the subject
            url = f"{self.base_url}/search"
            params = {
                'part': 'snippet',
                'q': f"{subject} tutorial education",
                'type': 'channel',
                'maxResults': 5,
                'key': self.api_key,
                'order': 'relevance'
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                channels = []
                
                for item in data.get('items', []):
                    channel = {
                        'channel_id': item['id']['channelId'],
                        'title': item['snippet']['title'],
                        'description': item['snippet']['description'],
                        'thumbnail': item['snippet']['thumbnails']['medium']['url'],
                        'published_at': item['snippet']['publishedAt']
                    }
                    channels.append(channel)
                
                return channels
            else:
                return self.get_educational_channels(subject)  # Fallback to demo
                
        except Exception as e:
            st.error(f"Failed to get educational channels: {str(e)}")
            return self.get_educational_channels(subject)  # Fallback to demo

youtube_client = YouTubeClient()
