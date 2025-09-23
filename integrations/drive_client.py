import os
import json
from typing import Optional, Dict, Any
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import streamlit as st
from config.settings import settings

class DriveClient:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/drive.file']
        self.service = None
        self.demo_mode = True  # Start in demo mode
        self.initialize_service()

    def initialize_service(self):
        """Initialize Google Drive service"""
        try:
            # For demo purposes, we'll simulate Drive functionality
            # In production, you'd implement proper OAuth2 flow
            if settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_ID != "demo_client_id":
                # Real implementation would go here
                st.info("Google Drive integration requires OAuth2 setup. Running in demo mode.")
            else:
                st.info("Google Drive not configured. Running in demo mode.")
            
        except Exception as e:
            st.error(f"Failed to initialize Google Drive: {str(e)}")
            self.demo_mode = True

    def create_learning_path_document(self, learning_path: Dict[str, Any]) -> Optional[str]:
        """Create a Google Docs document for the learning path"""
        if self.demo_mode:
            return self._create_demo_document(learning_path)

        try:
            # Create the document content
            document_content = self._format_learning_path_content(learning_path)
            
            # In a real implementation, you would:
            # 1. Create a Google Docs document
            # 2. Insert the formatted content
            # 3. Return the document URL
            
            # For now, return demo URL
            return f"https://docs.google.com/document/d/demo_doc_id/edit"
            
        except Exception as e:
            st.error(f"Failed to create document: {str(e)}")
            return None

    def _create_demo_document(self, learning_path: Dict[str, Any]) -> str:
        """Create demo document (save locally)"""
        try:
            # Create local documents directory if it doesn't exist
            docs_dir = "local_documents"
            os.makedirs(docs_dir, exist_ok=True)
            
            # Generate filename
            goal = learning_path.get('goal', 'learning_path')
            safe_goal = "".join(c for c in goal if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{safe_goal.replace(' ', '_')}_learning_path.txt"
            filepath = os.path.join(docs_dir, filename)
            
            # Format content
            content = self._format_learning_path_content(learning_path)
            
            # Save to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return f"Local document saved: {filepath}"
            
        except Exception as e:
            st.error(f"Failed to create demo document: {str(e)}")
            return "Demo document creation failed"

    def _format_learning_path_content(self, learning_path: Dict[str, Any]) -> str:
        """Format learning path content for document"""
        goal = learning_path.get('goal', 'Learning Path')
        duration = learning_path.get('duration_days', 0)
        difficulty = learning_path.get('difficulty', 'Unknown')
        description = learning_path.get('description', '')
        daily_plans = learning_path.get('daily_plans', [])
        path_type = learning_path.get('type', 'normal')
        
        content = f"""
# {goal} - Learning Path

## Overview
- **Duration**: {duration} days
- **Difficulty**: {difficulty}
- **Type**: {path_type.upper()}
- **Description**: {description}

## Daily Learning Plan

"""
        
        for plan in daily_plans:
            day = plan.get('day', 1)
            title = plan.get('title', f'Day {day}')
            objectives = plan.get('objectives', [])
            content_text = plan.get('content', '')
            activities = plan.get('activities', [])
            estimated_time = plan.get('estimated_time', 'Unknown')
            resources = plan.get('resources', [])
            key_concepts = plan.get('key_concepts', [])
            
            content += f"""
### {title}

**Estimated Time**: {estimated_time}

**Learning Objectives**:
"""
            for obj in objectives:
                content += f"- {obj}\n"
            
            content += f"""
**Content**:
{content_text}

**Activities**:
"""
            for activity in activities:
                content += f"- {activity}\n"
            
            if key_concepts:
                content += "\n**Key Concepts**:\n"
                for concept in key_concepts:
                    content += f"- {concept}\n"
            
            if resources:
                content += "\n**Resources**:\n"
                for resource in resources:
                    content += f"- {resource}\n"
            
            content += "\n" + "="*50 + "\n"
        
        # Add MCP-specific content if applicable
        if path_type == 'mcp':
            mcp_features = learning_path.get('mcp_features', {})
            if mcp_features:
                content += f"""
## MCP Features

**Personalization Level**: {mcp_features.get('personalization_level', 'Standard')}
**Context Awareness**: {mcp_features.get('context_awareness', False)}
**Real-time Adaptation**: {mcp_features.get('real_time_adaptation', False)}

**Adaptive Checkpoints**:
"""
                for checkpoint in mcp_features.get('adaptive_checkpoints', []):
                    content += f"- Day {checkpoint.get('day', 'N/A')}: {checkpoint.get('description', 'Assessment')}\n"
        
        content += f"""

## Progress Tracking

Use this document to track your daily progress:

"""
        
        for i in range(1, duration + 1):
            content += f"[ ] Day {i}: _________________ (Date completed)\n"
        
        content += f"""

## Notes and Reflections

Use this space to write your thoughts, insights, and questions as you progress through the learning path:

_____________________________________________________________________
_____________________________________________________________________
_____________________________________________________________________

---
Generated by AI Learning Path Generator
Creation Date: {learning_path.get('created_at', 'Unknown')}
"""
        
        return content

    def create_folder(self, folder_name: str, parent_folder_id: str = None) -> Optional[str]:
        """Create a folder in Google Drive"""
        if self.demo_mode:
            return self._create_demo_folder(folder_name)

        try:
            # In real implementation:
            # folder_metadata = {
            #     'name': folder_name,
            #     'mimeType': 'application/vnd.google-apps.folder'
            # }
            # if parent_folder_id:
            #     folder_metadata['parents'] = [parent_folder_id]
            # 
            # folder = self.service.files().create(body=folder_metadata).execute()
            # return folder.get('id')
            
            return f"demo_folder_{folder_name}"
            
        except Exception as e:
            st.error(f"Failed to create folder: {str(e)}")
            return None

    def _create_demo_folder(self, folder_name: str) -> str:
        """Create demo folder (local directory)"""
        try:
            folder_path = os.path.join("local_documents", folder_name)
            os.makedirs(folder_path, exist_ok=True)
            return folder_path
        except Exception as e:
            st.error(f"Failed to create demo folder: {str(e)}")
            return "demo_folder"

    def share_document(self, file_id: str, email: str = None) -> Optional[str]:
        """Share a document and return shareable link"""
        if self.demo_mode:
            return f"https://demo-drive.example.com/document/{file_id}/view"

        try:
            # In real implementation:
            # if email:
            #     permission = {
            #         'type': 'user',
            #         'role': 'reader',
            #         'emailAddress': email
            #     }
            #     self.service.permissions().create(fileId=file_id, body=permission).execute()
            # 
            # # Make publicly viewable
            # permission = {
            #     'type': 'anyone',
            #     'role': 'reader'
            # }
            # self.service.permissions().create(fileId=file_id, body=permission).execute()
            # 
            # return f"https://drive.google.com/file/d/{file_id}/view"
            
            return f"https://drive.google.com/file/d/{file_id}/view"
            
        except Exception as e:
            st.error(f"Failed to share document: {str(e)}")
            return None

    def export_learning_path_as_pdf(self, learning_path: Dict[str, Any]) -> Optional[bytes]:
        """Export learning path as PDF"""
        if self.demo_mode:
            return self._create_demo_pdf(learning_path)

        try:
            # In real implementation, you would:
            # 1. Create a Google Docs document
            # 2. Export it as PDF
            # 3. Return the PDF bytes
            
            return self._create_demo_pdf(learning_path)
            
        except Exception as e:
            st.error(f"Failed to export PDF: {str(e)}")
            return None

    def _create_demo_pdf(self, learning_path: Dict[str, Any]) -> bytes:
        """Create demo PDF content"""
        # Return empty bytes for demo - in real implementation, 
        # you'd use a library like reportlab to generate actual PDFs
        content = self._format_learning_path_content(learning_path)
        return content.encode('utf-8')

    def get_file_list(self, folder_id: str = None) -> list:
        """Get list of files in Drive folder"""
        if self.demo_mode:
            return [
                {
                    'id': 'demo_file_1',
                    'name': 'Sample Learning Path 1.docx',
                    'mimeType': 'application/vnd.google-apps.document',
                    'createdTime': '2024-01-01T00:00:00.000Z'
                },
                {
                    'id': 'demo_file_2',
                    'name': 'Sample Learning Path 2.docx',
                    'mimeType': 'application/vnd.google-apps.document',
                    'createdTime': '2024-01-02T00:00:00.000Z'
                }
            ]

        try:
            # In real implementation:
            # query = f"'{folder_id}' in parents" if folder_id else None
            # results = self.service.files().list(q=query, pageSize=50).execute()
            # return results.get('files', [])
            
            return []
            
        except Exception as e:
            st.error(f"Failed to get file list: {str(e)}")
            return []

drive_client = DriveClient()
