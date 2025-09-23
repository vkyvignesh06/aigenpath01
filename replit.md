# AI Learning Path Generator

## Overview

This is a comprehensive AI-powered learning management system that generates personalized day-by-day learning plans with multi-modal content delivery. The platform creates structured learning paths using AI, integrates voice synthesis for audio learning, and provides automated reminders through multiple channels. It supports both Normal learning paths (structured with curated content) and MCP (Model Context Protocol) paths for adaptive learning experiences.

The system is designed with a demo-first approach, allowing full functionality testing without requiring API keys, while seamlessly scaling to production with real integrations.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Streamlit Web Application**: Modern single-page application with responsive design
- **Multi-page Navigation**: Sidebar-based navigation with role-based access control
- **Interactive Visualizations**: Plotly integration for progress tracking and analytics dashboards
- **Real-time Updates**: Dynamic content updates without page refreshes
- **Custom CSS Styling**: Gradient-based UI with professional visual design

### Backend Architecture
- **Modular Service Architecture**: Separated concerns with dedicated services for learning, notifications, and integrations
- **AI-Powered Content Generation**: Dual AI approach with Normal paths and MCP (Model Context Protocol) for adaptive learning
- **Demo-First Design**: Comprehensive demo mode that works without external API dependencies
- **Configuration-Driven Setup**: Environment-based configuration with graceful fallback to demo mode

### Authentication & Authorization
- **Firebase Authentication**: Google login and email/password registration with demo fallback
- **Role-Based Access Control**: Student and Admin roles with appropriate permissions
- **User Data Isolation**: Each user maintains dedicated database space
- **Secure Session Management**: Session-based authentication with secure token generation

### Data Storage Solutions
- **Firestore Database**: Primary cloud database with local JSON fallback for demo mode
- **Local File System**: Demo data stored in JSON files for development and testing
- **User Profile Management**: Comprehensive user data including preferences, progress, and learning history
- **Learning Path Persistence**: Structured storage of daily plans, objectives, and progress tracking

### AI Integration Architecture
- **Google Gemini API**: Primary AI service for learning path generation with structured output
- **Model Context Protocol (MCP)**: Advanced adaptive learning with user context analysis
- **Structured Response Format**: Pydantic models ensure consistent AI response formatting
- **Fallback Demo Content**: Pre-generated learning paths for testing without API access

### Multi-Modal Content Delivery
- **Text-Based Learning**: Structured daily plans with objectives, activities, and resources
- **Video Integration**: YouTube API integration for curated educational content
- **Audio Synthesis**: ElevenLabs text-to-speech for accessible audio learning
- **Document Generation**: Google Drive integration for learning path documentation

### Progress Tracking System
- **Interactive Calendar Views**: Multiple visualization formats (grid, timeline, heatmap)
- **Real-Time Progress Updates**: Click-to-toggle completion status
- **Analytics Dashboard**: Comprehensive learning statistics and performance metrics
- **Streak Tracking**: Motivation through consistency measurement

### Notification Architecture
- **Multi-Channel Delivery**: SMS, WhatsApp, and voice call reminders via Twilio
- **Scheduled Notifications**: Daily learning reminders at user-preferred times
- **Progress Milestones**: Automated celebration of learning achievements
- **Adaptive Messaging**: Context-aware motivational messages based on user progress

## External Dependencies

### AI Services
- **Google Gemini API**: Primary AI service for intelligent learning path generation and content creation
- **Model Context Protocol (MCP)**: Advanced adaptive learning system for personalized content delivery

### Authentication & Database
- **Firebase Authentication**: Secure user authentication with Google login and email/password options
- **Firebase Firestore**: Cloud NoSQL database for user data, learning paths, and progress tracking

### Communication Services
- **Twilio API**: Multi-channel notification delivery (SMS, WhatsApp, voice calls) for learning reminders
- **ElevenLabs API**: High-quality text-to-speech synthesis for audio learning content

### Content Integration
- **YouTube Data API v3**: Curated educational video recommendations for daily learning plans
- **Google Drive API**: Automated document creation and sharing for learning path materials
- **Google Docs API**: Structured learning path documentation generation

### Development & Infrastructure
- **Streamlit**: Modern web application framework for rapid development and deployment
- **Plotly**: Interactive data visualizations for progress tracking and analytics
- **Python-dotenv**: Environment variable management for secure configuration
- **Schedule**: Python job scheduling for automated notification delivery

### Security & Utilities
- **Hashlib & Secrets**: Secure password hashing and token generation
- **Firebase Admin SDK**: Server-side Firebase integration for secure data operations
- **Google Auth Libraries**: OAuth2 flow implementation for Google service integrations

All external services include comprehensive demo modes that provide full functionality testing without requiring API keys, ensuring smooth development and evaluation experiences.