import json
import os
from datetime import datetime
from typing import Optional, Dict, Any, List
from config.firebase_config import firebase_config
import streamlit as st

class FirestoreClient:
    def __init__(self):
        self.demo_data_file = "demo_data.json"
        self.ensure_demo_data_file()

    def ensure_demo_data_file(self):
        """Ensure demo data file exists"""
        if not os.path.exists(self.demo_data_file):
            demo_data = {
                "users": {},
                "learning_paths": {},
                "progress": {},
                "notifications": {}
            }
            with open(self.demo_data_file, 'w') as f:
                json.dump(demo_data, f, indent=2)

    def load_demo_data(self) -> Dict[str, Any]:
        """Load demo data from file"""
        try:
            with open(self.demo_data_file, 'r') as f:
                return json.load(f)
        except:
            self.ensure_demo_data_file()
            return self.load_demo_data()

    def save_demo_data(self, data: Dict[str, Any]):
        """Save demo data to file"""
        with open(self.demo_data_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)

    def create_user_profile(self, user_id: str, user_data: Dict[str, Any]) -> bool:
        """Create user profile"""
        try:
            if firebase_config.is_initialized:
                doc_ref = firebase_config.db.collection('users').document(user_id)
                doc_ref.set(user_data)
                return True
            else:
                # Demo mode
                data = self.load_demo_data()
                data['users'][user_id] = user_data
                self.save_demo_data(data)
                return True
        except Exception as e:
            st.error(f"Failed to create user profile: {str(e)}")
            return False

    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile"""
        try:
            if firebase_config.is_initialized:
                doc_ref = firebase_config.db.collection('users').document(user_id)
                doc = doc_ref.get()
                return doc.to_dict() if doc.exists else None
            else:
                # Demo mode
                data = self.load_demo_data()
                return data['users'].get(user_id)
        except Exception as e:
            st.error(f"Failed to get user profile: {str(e)}")
            return None

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        try:
            if firebase_config.is_initialized:
                users_ref = firebase_config.db.collection('users')
                query = users_ref.where('email', '==', email).limit(1)
                docs = query.stream()
                for doc in docs:
                    user_data = doc.to_dict()
                    user_data['user_id'] = doc.id
                    return user_data
                return None
            else:
                # Demo mode
                data = self.load_demo_data()
                for user_id, user_data in data['users'].items():
                    if user_data.get('email') == email:
                        user_data['user_id'] = user_id
                        return user_data
                return None
        except Exception as e:
            st.error(f"Failed to get user by email: {str(e)}")
            return None

    def save_learning_path(self, user_id: str, learning_path: Dict[str, Any]) -> str:
        """Save learning path"""
        try:
            path_id = f"path_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            learning_path['id'] = path_id
            learning_path['user_id'] = user_id
            learning_path['created_at'] = datetime.now()

            if firebase_config.is_initialized:
                doc_ref = firebase_config.db.collection('learning_paths').document(path_id)
                doc_ref.set(learning_path)
            else:
                # Demo mode
                data = self.load_demo_data()
                data['learning_paths'][path_id] = learning_path
                self.save_demo_data(data)

            return path_id
        except Exception as e:
            st.error(f"Failed to save learning path: {str(e)}")
            return ""

    def get_user_learning_paths(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's learning paths"""
        try:
            if firebase_config.is_initialized:
                paths_ref = firebase_config.db.collection('learning_paths')
                query = paths_ref.where('user_id', '==', user_id)
                docs = query.stream()
                return [doc.to_dict() for doc in docs]
            else:
                # Demo mode
                data = self.load_demo_data()
                user_paths = []
                for path_id, path_data in data['learning_paths'].items():
                    if path_data.get('user_id') == user_id:
                        user_paths.append(path_data)
                return user_paths
        except Exception as e:
            st.error(f"Failed to get learning paths: {str(e)}")
            return []

    def update_learning_progress(self, user_id: str, path_id: str, day: int, completed: bool) -> bool:
        """Update learning progress"""
        try:
            progress_key = f"{user_id}_{path_id}"
            
            if firebase_config.is_initialized:
                doc_ref = firebase_config.db.collection('progress').document(progress_key)
                doc = doc_ref.get()
                
                if doc.exists:
                    progress_data = doc.to_dict()
                else:
                    progress_data = {'completed_days': {}}
                
                progress_data['completed_days'][str(day)] = completed
                progress_data['last_updated'] = datetime.now().isoformat()
                doc_ref.set(progress_data)
            else:
                # Demo mode
                data = self.load_demo_data()
                if progress_key not in data['progress']:
                    data['progress'][progress_key] = {'completed_days': {}}
                
                data['progress'][progress_key]['completed_days'][str(day)] = completed
                data['progress'][progress_key]['last_updated'] = datetime.now().isoformat()
                self.save_demo_data(data)

            return True
        except Exception as e:
            st.error(f"Failed to update progress: {str(e)}")
            return False

    def get_learning_progress(self, user_id: str, path_id: str) -> Dict[str, Any]:
        """Get learning progress"""
        try:
            progress_key = f"{user_id}_{path_id}"
            
            if firebase_config.is_initialized:
                doc_ref = firebase_config.db.collection('progress').document(progress_key)
                doc = doc_ref.get()
                return doc.to_dict() if doc.exists else {'completed_days': {}}
            else:
                # Demo mode
                data = self.load_demo_data()
                return data['progress'].get(progress_key, {'completed_days': {}})
        except Exception as e:
            st.error(f"Failed to get progress: {str(e)}")
            return {'completed_days': {}}

    def save_notification_settings(self, user_id: str, settings: Dict[str, Any]) -> bool:
        """Save notification settings"""
        try:
            if firebase_config.is_initialized:
                doc_ref = firebase_config.db.collection('users').document(user_id)
                doc_ref.update({'notification_settings': settings})
            else:
                # Demo mode
                data = self.load_demo_data()
                if user_id in data['users']:
                    data['users'][user_id]['notification_settings'] = settings
                    self.save_demo_data(data)
            return True
        except Exception as e:
            st.error(f"Failed to save notification settings: {str(e)}")
            return False

firestore_client = FirestoreClient()
