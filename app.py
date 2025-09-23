import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import base64
import io
import json
import time

# Import custom modules
from config.settings import settings
from auth.firebase_auth import firebase_auth
from database.firestore_client import firestore_client
from services.learning_service import learning_service
from services.notification_service import notification_service
from utils.helpers import *

# Page configuration
st.set_page_config(
    page_title="AI Learning Path Generator",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }

    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .learning-card {
        background: rgba(255, 255, 255, 0.95);
        padding: 2rem;
        border-radius: 20px;
        margin: 1rem 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border: 1px solid rgba(102, 126, 234, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    .learning-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.15);
    }

    .day-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 0.8rem 0;
        border-left: 4px solid #667eea;
        transition: all 0.3s ease;
    }

    .day-card:hover {
        transform: translateX(5px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }

    .audio-player {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }

    .notification-settings {
        background: linear-gradient(135deg, #f1f3f4 0%, #e8eaf6 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        border: 1px solid rgba(102, 126, 234, 0.2);
    }

    .success-animation {
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }

    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
        }
        
        .learning-card {
            padding: 1rem;
        }
        
        .metric-container {
            padding: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main application function"""
    
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    # Sidebar
    render_sidebar()
    
    # Main content
    if st.session_state.authenticated:
        render_authenticated_app()
    else:
        render_authentication_page()

def render_sidebar():
    """Render sidebar with navigation and settings"""
    with st.sidebar:
        st.markdown("# 🎓 AI Learning Path")
        
        # Demo mode indicator
        if settings.is_demo_mode:
            st.warning("🔧 Demo Mode Active")
            st.info("Add API keys in settings for full functionality")
        
        # Authentication status
        if st.session_state.authenticated:
            user_email = SessionState.get_user_email()
            st.success(f"✅ Logged in as: {user_email}")
            
            if st.button("🚪 Sign Out", use_container_width=True):
                firebase_auth.sign_out()
                SessionState.clear_user_session()
                st.session_state.authenticated = False
                st.rerun()
        
        # Navigation
        if st.session_state.authenticated:
            st.markdown("---")
            st.markdown("### 📋 Navigation")
            
            # Navigation options
            nav_options = [
                "🏠 Dashboard",
                "➕ Generate Learning Path",
                "📊 Progress Calendar",
                "🔔 Notifications",
                "📈 Analytics",
                "⚙️ Settings"
            ]
            
            if 'selected_nav' not in st.session_state:
                st.session_state.selected_nav = nav_options[0]
            
            for option in nav_options:
                if st.button(option, use_container_width=True):
                    st.session_state.selected_nav = option
                    st.rerun()
        
        # API Configuration
        render_api_configuration()
        
        # Help and Info
        st.markdown("---")
        st.markdown("### 📞 Support")
        st.markdown("""
        **Need Help?**
        - 📧 Email: support@ailearningpath.com
        - 💬 Chat: Available 24/7
        - 📚 Docs: [View Documentation](https://docs.ailearningpath.com)
        """)

def render_api_configuration():
    """Render API configuration section"""
    st.markdown("---")
    st.markdown("### ⚙️ API Configuration")
    
    with st.expander("🔧 Configure API Keys", expanded=False):
        st.markdown("**Current Status:**")
        
        # Check API status
        api_status = {
            "Gemini AI": "✅ Active" if settings.GEMINI_API_KEY != "demo_key" else "⚪ Demo",
            "YouTube": "✅ Active" if settings.YOUTUBE_API_KEY != "demo_key" else "⚪ Demo",
            "ElevenLabs": "✅ Active" if settings.ELEVENLABS_API_KEY != "demo_key" else "⚪ Demo",
            "Twilio": "✅ Active" if settings.TWILIO_ACCOUNT_SID != "demo_sid" else "⚪ Demo"
        }
        
        for service, status in api_status.items():
            st.markdown(f"- **{service}**: {status}")
        
        st.markdown("---")
        st.markdown("**Setup Instructions:**")
        st.markdown("""
        1. **Gemini AI**: Get free API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
        2. **YouTube**: Enable YouTube Data API v3 in [Google Cloud Console](https://console.cloud.google.com/)
        3. **ElevenLabs**: Sign up at [ElevenLabs](https://elevenlabs.io/) for voice synthesis
        4. **Twilio**: Create account at [Twilio](https://www.twilio.com/) for SMS/WhatsApp
        """)
        
        if st.button("🔄 Refresh API Status"):
            st.rerun()

def render_authentication_page():
    """Render authentication page"""
    st.markdown('<h1 class="main-header">🎓 AI Learning Path Generator</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; margin-bottom: 3rem;">
        <h3>Transform Your Learning Journey with AI-Powered Personalized Paths</h3>
        <p style="font-size: 1.2rem; color: #666;">
            Generate custom learning plans, track progress, and stay motivated with intelligent reminders
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Features overview
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-container">
            <h4>🧠 AI-Powered</h4>
            <p>Generate personalized learning paths using advanced AI</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-container">
            <h4>📱 Smart Reminders</h4>
            <p>Stay consistent with automated SMS and WhatsApp notifications</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-container">
            <h4>🔊 Voice Learning</h4>
            <p>Listen to your lessons with AI-generated voice narration</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Authentication tabs
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["🔐 Sign In", "👤 Sign Up"])
    
    with tab1:
        render_signin_form()
    
    with tab2:
        render_signup_form()

def render_signin_form():
    """Render sign-in form"""
    st.markdown("### Welcome Back!")
    
    with st.form("signin_form"):
        email = st.text_input("📧 Email", placeholder="Enter your email")
        password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.form_submit_button("🚀 Sign In", use_container_width=True):
                if email and password:
                    if validate_email(email):
                        user = firebase_auth.sign_in_with_email_password(email, password)
                        if user:
                            SessionState.set_user_session(user['user_id'], user['email'])
                            st.session_state.authenticated = True
                            display_success_message("Successfully signed in!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            display_error_message("Invalid email or password")
                    else:
                        display_error_message("Please enter a valid email address")
                else:
                    display_error_message("Please fill in all fields")
        
        with col2:
            if st.form_submit_button("🌐 Google Sign In", use_container_width=True):
                user = firebase_auth.sign_in_with_google()
                if user:
                    SessionState.set_user_session(user['user_id'], user['email'])
                    st.session_state.authenticated = True
                    display_success_message("Successfully signed in with Google!")
                    time.sleep(1)
                    st.rerun()
    
    # Demo account info
    st.markdown("---")
    st.info("🚀 **Quick Start**: Try the demo account - Email: `demo@example.com`, Password: `demo123`")

def render_signup_form():
    """Render sign-up form"""
    st.markdown("### Create Your Account")
    
    with st.form("signup_form"):
        name = st.text_input("👤 Full Name", placeholder="Enter your full name")
        email = st.text_input("📧 Email", placeholder="Enter your email")
        password = st.text_input("🔒 Password", type="password", placeholder="Create a password")
        confirm_password = st.text_input("🔒 Confirm Password", type="password", placeholder="Confirm your password")
        
        # Terms and conditions
        terms_accepted = st.checkbox("I agree to the Terms of Service and Privacy Policy")
        
        if st.form_submit_button("✨ Create Account", use_container_width=True):
            if all([name, email, password, confirm_password]):
                if not validate_email(email):
                    display_error_message("Please enter a valid email address")
                elif password != confirm_password:
                    display_error_message("Passwords do not match")
                elif len(password) < 6:
                    display_error_message("Password must be at least 6 characters long")
                elif not terms_accepted:
                    display_error_message("Please accept the terms and conditions")
                else:
                    user = firebase_auth.create_user_with_email_password(email, password, name)
                    if user:
                        SessionState.set_user_session(user['user_id'], user['email'])
                        st.session_state.authenticated = True
                        display_success_message(f"Account created successfully! Welcome {name}!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        display_error_message("Failed to create account. Email might already exist.")
            else:
                display_error_message("Please fill in all fields")

def render_authenticated_app():
    """Render main application for authenticated users"""
    # Get selected navigation
    selected_nav = st.session_state.get('selected_nav', '🏠 Dashboard')
    
    if selected_nav == '🏠 Dashboard':
        render_dashboard()
    elif selected_nav == '➕ Generate Learning Path':
        render_generate_path()
    elif selected_nav == '📊 Progress Calendar':
        render_progress_calendar()
    elif selected_nav == '🔔 Notifications':
        render_notifications()
    elif selected_nav == '📈 Analytics':
        render_analytics()
    elif selected_nav == '⚙️ Settings':
        render_settings()

def render_dashboard():
    """Render user dashboard"""
    st.markdown('<h1 class="main-header">🏠 Your Learning Dashboard</h1>', unsafe_allow_html=True)
    
    user_id = SessionState.get_user_id()
    user_email = SessionState.get_user_email()
    
    if not user_id:
        st.error("User not properly authenticated")
        return
    
    # Welcome message
    st.markdown(f"""
    <div class="learning-card">
        <h3>Welcome back! 👋</h3>
        <p>Ready to continue your learning journey? Here's your progress overview.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get user's learning paths
    learning_paths = learning_service.get_user_learning_paths(user_id)
    
    if not learning_paths:
        # Empty state
        st.markdown("""
        <div class="learning-card" style="text-align: center; padding: 3rem;">
            <h3>🎯 Start Your Learning Journey!</h3>
            <p style="font-size: 1.2rem; margin: 2rem 0;">
                You haven't created any learning paths yet. Let's get started!
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("✨ Create Your First Learning Path", use_container_width=True):
                st.session_state.selected_nav = '➕ Generate Learning Path'
                st.rerun()
    else:
        # Learning statistics
        render_learning_statistics(learning_paths)
        
        # Recent learning paths
        st.markdown("## 📚 Your Learning Paths")
        
        for path in learning_paths[:5]:  # Show recent 5
            render_learning_path_card(path, user_id)
        
        if len(learning_paths) > 5:
            if st.button(f"📋 View All {len(learning_paths)} Learning Paths"):
                st.session_state.selected_nav = '📊 Progress Calendar'
                st.rerun()

def render_learning_statistics(learning_paths: list):
    """Render learning statistics overview"""
    # Calculate statistics
    total_paths = len(learning_paths)
    completed_paths = sum(1 for path in learning_paths if path.get('completion_percentage', 0) >= 100)
    active_paths = sum(1 for path in learning_paths if 0 < path.get('completion_percentage', 0) < 100)
    avg_completion = sum(path.get('completion_percentage', 0) for path in learning_paths) / total_paths if total_paths > 0 else 0
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📚 Total Paths", total_paths)
    
    with col2:
        st.metric("✅ Completed", completed_paths)
    
    with col3:
        st.metric("🔄 In Progress", active_paths)
    
    with col4:
        st.metric("📊 Avg. Completion", f"{avg_completion:.1f}%")

def render_learning_path_card(path: dict, user_id: str):
    """Render a learning path card"""
    path_id = path.get('id', '')
    goal = path.get('goal', 'Learning Path')
    duration = path.get('duration_days', 0)
    difficulty = path.get('difficulty', 'beginner')
    path_type = path.get('type', 'normal')
    completion_percentage = path.get('completion_percentage', 0)
    
    # Progress color
    progress_color = get_difficulty_color(difficulty) if completion_percentage > 0 else '#e0e0e0'
    
    with st.container():
        st.markdown(f"""
        <div class="learning-card">
            <div style="display: flex; justify-content: between; align-items: center; margin-bottom: 1rem;">
                <h4 style="margin: 0; color: #333;">{goal}</h4>
                <span style="background: {get_difficulty_color(difficulty)}; color: white; padding: 0.2rem 0.8rem; border-radius: 15px; font-size: 0.8rem;">
                    {difficulty.upper()}
                </span>
            </div>
            
            <div style="margin-bottom: 1rem;">
                <strong>Type:</strong> {path_type.upper()} | <strong>Duration:</strong> {duration} days
            </div>
            
            {create_progress_bar_html(completion_percentage, progress_color)}
            
            <div style="margin-top: 1rem; font-size: 0.9rem; color: #666;">
                Created: {format_date_relative(path.get('created_at', datetime.now()))}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Action buttons
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📖 View Details", key=f"view_{path_id}"):
                render_learning_path_details(path, user_id)
        
        with col2:
            if st.button("📊 Progress", key=f"progress_{path_id}"):
                render_path_progress(path, user_id)
        
        with col3:
            if st.button("🔔 Notifications", key=f"notify_{path_id}"):
                render_path_notifications(path, user_id)
        
        with col4:
            if st.button("📥 Export", key=f"export_{path_id}"):
                render_export_options(path, user_id)

def render_learning_path_details(path: dict, user_id: str):
    """Render detailed view of learning path"""
    with st.expander(f"📚 {path.get('goal', 'Learning Path')} - Details", expanded=True):
        
        # Path information
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**Duration:** {path.get('duration_days', 0)} days")
            st.markdown(f"**Difficulty:** {path.get('difficulty', 'beginner').title()}")
            st.markdown(f"**Type:** {path.get('type', 'normal').upper()}")
        
        with col2:
            st.markdown(f"**Progress:** {path.get('completion_percentage', 0):.1f}%")
            st.markdown(f"**Created:** {format_date_relative(path.get('created_at', datetime.now()))}")
        
        # Description
        description = path.get('description', 'No description available')
        st.markdown(f"**Description:** {description}")
        
        # Daily plans
        daily_plans = path.get('daily_plans', [])
        
        if daily_plans:
            st.markdown("### 📅 Daily Learning Plan")
            
            # Progress tracking
            progress = path.get('progress', {})
            completed_days = progress.get('completed_days', {})
            
            for plan in daily_plans:
                day = plan.get('day', 1)
                title = plan.get('title', f'Day {day}')
                objectives = plan.get('objectives', [])
                content = plan.get('content', '')
                activities = plan.get('activities', [])
                estimated_time = plan.get('estimated_time', 'Unknown')
                
                # Day completion status
                is_completed = completed_days.get(str(day), False)
                status_icon = "✅" if is_completed else "⏳"
                status_color = "#4CAF50" if is_completed else "#ff9800"
                
                with st.container():
                    st.markdown(f"""
                    <div class="day-card" style="border-left-color: {status_color};">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <h5 style="margin: 0;">{status_icon} {title}</h5>
                            <span style="font-size: 0.9rem; color: #666;">⏱️ {estimated_time}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Toggle completion
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        # Show objectives
                        if objectives:
                            st.markdown("**Learning Objectives:**")
                            for obj in objectives[:2]:  # Show first 2
                                st.markdown(f"• {obj}")
                    
                    with col2:
                        if st.button(
                            "✅ Complete" if not is_completed else "↩️ Undo",
                            key=f"toggle_{path.get('id', '')}_{day}"
                        ):
                            success = learning_service.update_daily_progress(
                                user_id, path.get('id', ''), day, not is_completed
                            )
                            if success:
                                st.success("Progress updated!")
                                time.sleep(0.5)
                                st.rerun()
                    
                    # Show more details on click
                    with st.expander(f"📖 Day {day} Details"):
                        st.markdown(f"**Content:** {content}")
                        
                        if activities:
                            st.markdown("**Activities:**")
                            for activity in activities:
                                st.markdown(f"• {activity}")
                        
                        # Recommended videos
                        videos = plan.get('recommended_videos', [])
                        if videos:
                            st.markdown("**📺 Recommended Videos:**")
                            for video in videos[:2]:
                                st.markdown(f"• [{video.get('title', 'Video')}]({video.get('url', '#')})")
                        
                        # Audio option
                        if plan.get('audio_available', False):
                            st.markdown("**🔊 Audio Available**")
                            if st.button(f"🎧 Play Audio", key=f"audio_{path.get('id', '')}_{day}"):
                                st.info("Audio playback would start here (ElevenLabs integration)")

def render_path_progress(path: dict, user_id: str):
    """Render progress view for a specific path"""
    with st.expander(f"📊 Progress: {path.get('goal', 'Learning Path')}", expanded=True):
        
        progress = path.get('progress', {})
        completed_days = progress.get('completed_days', {})
        total_days = path.get('duration_days', 0)
        
        if total_days > 0:
            # Progress overview
            completed_count = sum(1 for completed in completed_days.values() if completed)
            completion_rate = (completed_count / total_days) * 100
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Completed Days", completed_count, f"/{total_days}")
            
            with col2:
                st.metric("Progress", f"{completion_rate:.1f}%")
            
            with col3:
                remaining_days = total_days - completed_count
                st.metric("Remaining", remaining_days, "days")
            
            # Progress visualization
            st.markdown("#### 📅 Daily Progress")
            
            # Create progress chart
            days = list(range(1, total_days + 1))
            progress_status = [1 if completed_days.get(str(day), False) else 0 for day in days]
            
            fig = go.Figure(data=go.Bar(
                x=days,
                y=progress_status,
                marker_color=['#4CAF50' if status else '#e0e0e0' for status in progress_status],
                text=[f"Day {day}" for day in days],
                textposition="auto",
            ))
            
            fig.update_layout(
                title="Daily Completion Status",
                xaxis_title="Days",
                yaxis_title="Completed",
                showlegend=False,
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        else:
            st.warning("No progress data available")

def render_path_notifications(path: dict, user_id: str):
    """Render notification settings for a specific path"""
    with st.expander(f"🔔 Notifications: {path.get('goal', 'Learning Path')}", expanded=True):
        
        st.markdown("#### Set up daily learning reminders")
        
        with st.form(f"notification_form_{path.get('id', '')}"):
            
            # Notification method
            method = st.selectbox(
                "📱 Notification Method",
                ["sms", "whatsapp", "voice"],
                format_func=lambda x: {
                    "sms": "📱 SMS",
                    "whatsapp": "💬 WhatsApp", 
                    "voice": "📞 Voice Call"
                }[x]
            )
            
            # Phone number
            phone = st.text_input("📞 Phone Number", placeholder="+1234567890")
            
            # Reminder time
            reminder_time = st.time_input("⏰ Daily Reminder Time", value=datetime.strptime("09:00", "%H:%M").time())
            
            # Days of week
            days = st.multiselect(
                "📅 Days of Week",
                ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                default=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.form_submit_button("🔔 Schedule Reminders"):
                    if phone and validate_phone_number(phone):
                        
                        reminder_settings = {
                            'phone_number': phone,
                            'method': method,
                            'time': reminder_time.strftime("%H:%M"),
                            'days': [i for i, day in enumerate(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]) if day in days]
                        }
                        
                        success = notification_service.schedule_learning_reminder(
                            user_id, path.get('id', ''), reminder_settings
                        )
                        
                        if success:
                            display_success_message("Reminders scheduled successfully!")
                    else:
                        display_error_message("Please enter a valid phone number")
            
            with col2:
                if st.form_submit_button("📤 Send Test"):
                    if phone and validate_phone_number(phone):
                        success = notification_service.test_notification(phone, method)
                        if success:
                            display_success_message("Test notification sent!")
                    else:
                        display_error_message("Please enter a valid phone number")

def render_export_options(path: dict, user_id: str):
    """Render export options for a learning path"""
    with st.expander(f"📥 Export: {path.get('goal', 'Learning Path')}", expanded=True):
        
        st.markdown("#### Download your learning path")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📄 Export as PDF", use_container_width=True):
                pdf_data = learning_service.export_learning_path(user_id, path.get('id', ''), 'pdf')
                if pdf_data:
                    st.download_button(
                        label="📥 Download PDF",
                        data=pdf_data,
                        file_name=f"{path.get('goal', 'learning_path').replace(' ', '_')}.pdf",
                        mime="application/pdf"
                    )
        
        with col2:
            if st.button("📊 Export as JSON", use_container_width=True):
                json_data = learning_service.export_learning_path(user_id, path.get('id', ''), 'json')
                if json_data:
                    st.download_button(
                        label="📥 Download JSON",
                        data=json_data,
                        file_name=f"{path.get('goal', 'learning_path').replace(' ', '_')}.json",
                        mime="application/json"
                    )

def render_generate_path():
    """Render learning path generation page"""
    st.markdown('<h1 class="main-header">➕ Generate Learning Path</h1>', unsafe_allow_html=True)
    
    user_id = SessionState.get_user_id()
    
    # Introduction
    st.markdown("""
    <div class="learning-card">
        <h3>Create Your Personalized Learning Journey 🚀</h3>
        <p>Our AI will generate a customized day-by-day learning plan based on your goals, preferred difficulty, and learning style.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Two path types tabs
    tab1, tab2 = st.tabs(["🎯 Normal Learning Path", "🧠 MCP Learning Path (Advanced)"])
    
    with tab1:
        render_normal_path_generator(user_id)
    
    with tab2:
        render_mcp_path_generator(user_id)

def render_normal_path_generator(user_id: str):
    """Render normal learning path generator"""
    st.markdown("### 🎯 Standard Learning Path")
    st.markdown("Perfect for focused learning with structured daily plans and curated content.")
    
    with st.form("normal_path_form"):
        
        # Learning goal
        goal = st.text_input(
            "🎯 What do you want to learn?",
            placeholder="e.g., Python Programming, Digital Marketing, Data Science",
            help="Be specific about your learning goal"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Duration
            duration = st.slider(
                "📅 Learning Duration (days)",
                min_value=3,
                max_value=90,
                value=14,
                help="How many days do you want to dedicate to this learning path?"
            )
        
        with col2:
            # Difficulty
            difficulty = st.selectbox(
                "📊 Difficulty Level",
                ["beginner", "intermediate", "advanced", "expert"],
                help="Choose based on your current knowledge level"
            )
        
        # Additional options
        include_practice = st.checkbox(
            "🛠️ Include hands-on practice exercises",
            value=True,
            help="Add practical exercises and projects to reinforce learning"
        )
        
        # Estimated completion info
        if goal and difficulty:
            duration_estimate = estimate_learning_duration(goal, difficulty)
            st.info(f"""
            💡 **AI Recommendation**: Based on your goal and difficulty level:
            - Minimum: {duration_estimate['min_days']} days
            - Recommended: {duration_estimate['recommended_days']} days
            - Maximum: {duration_estimate['max_days']} days
            """)
        
        # Generate button
        if st.form_submit_button("✨ Generate Learning Path", use_container_width=True):
            if not goal or not validate_learning_goal(goal):
                display_error_message("Please enter a valid learning goal (at least 2 words, max 200 characters)")
            else:
                with st.spinner("🤖 AI is creating your personalized learning path..."):
                    
                    path_data = {
                        'goal': sanitize_input(goal),
                        'duration': duration,
                        'difficulty': difficulty,
                        'type': 'normal',
                        'include_practice': include_practice
                    }
                    
                    path_id = learning_service.create_learning_path(user_id, path_data)
                    
                    if path_id:
                        display_success_message("🎉 Learning path created successfully!")
                        
                        # Show success animation
                        st.balloons()
                        
                        # Redirect to dashboard
                        time.sleep(2)
                        st.session_state.selected_nav = '🏠 Dashboard'
                        st.rerun()
                    else:
                        display_error_message("Failed to create learning path. Please try again.")

def render_mcp_path_generator(user_id: str):
    """Render MCP learning path generator"""
    st.markdown("### 🧠 MCP Learning Path (Advanced)")
    st.markdown("Model Context Protocol powered learning with adaptive content and personalized recommendations.")
    
    # MCP Information
    with st.expander("ℹ️ What is MCP Learning?", expanded=False):
        st.markdown("""
        **Model Context Protocol (MCP) Learning** provides:
        
        - 🎯 **Adaptive Content**: Adjusts based on your progress and performance
        - 🔄 **Real-time Modifications**: Updates difficulty and pacing automatically  
        - 📊 **Learning Analytics**: Tracks your learning patterns and preferences
        - 🎨 **Personalized Style**: Adapts to your preferred learning methods
        - 🔍 **Context Awareness**: Considers your background and experience
        - 📈 **Smart Recommendations**: Suggests optimal next steps
        """)
    
    with st.form("mcp_path_form"):
        
        # Basic information
        goal = st.text_input(
            "🎯 Learning Goal",
            placeholder="e.g., Master Machine Learning, Advanced JavaScript",
            help="What specific skill or knowledge do you want to acquire?"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            duration = st.slider("📅 Duration (days)", 7, 60, 21)
        
        with col2:
            difficulty = st.selectbox("📊 Difficulty", ["beginner", "intermediate", "advanced", "expert"])
        
        # MCP-specific settings
        st.markdown("#### 🧠 MCP Personalization Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            learning_style = st.selectbox(
                "🎨 Learning Style",
                ["visual", "auditory", "kinesthetic", "mixed"],
                help="How do you learn best?"
            )
            
            current_level = st.selectbox(
                "📈 Current Experience Level",
                ["complete_beginner", "some_experience", "intermediate", "advanced"],
                help="Your current level with this topic"
            )
        
        with col2:
            time_per_day = st.selectbox(
                "⏰ Available Study Time",
                ["30-60 minutes", "1-2 hours", "2-3 hours", "3+ hours"],
                help="How much time can you dedicate daily?"
            )
            
            pace_preference = st.selectbox(
                "🏃 Learning Pace",
                ["slow", "moderate", "fast"],
                help="How quickly do you prefer to learn?"
            )
        
        # Additional context
        st.markdown("#### 📝 Additional Context (Optional)")
        
        previous_experience = st.text_area(
            "📚 Previous Learning Experience",
            placeholder="Tell us about your background with similar topics...",
            help="This helps the AI personalize your learning path"
        )
        
        specific_interests = st.text_area(
            "🎯 Specific Interests",
            placeholder="Are there particular aspects you're most interested in?",
            help="Focus areas within your learning goal"
        )
        
        # Generate MCP path
        if st.form_submit_button("🚀 Generate Adaptive Learning Path", use_container_width=True):
            if not goal or not validate_learning_goal(goal):
                display_error_message("Please enter a valid learning goal")
            else:
                with st.spinner("🧠 Creating your adaptive MCP learning path..."):
                    
                    # Prepare context data for MCP
                    context_data = {
                        'learning_style': learning_style,
                        'current_level': current_level,
                        'time_per_day': time_per_day,
                        'pace_preference': pace_preference,
                        'previous_experience': previous_experience,
                        'specific_interests': specific_interests
                    }
                    
                    path_data = {
                        'goal': sanitize_input(goal),
                        'duration': duration,
                        'difficulty': difficulty,
                        'type': 'mcp',
                        'context_data': context_data
                    }
                    
                    path_id = learning_service.create_learning_path(user_id, path_data)
                    
                    if path_id:
                        display_success_message("🎉 Adaptive learning path created!")
                        st.balloons()
                        
                        # Show MCP features
                        st.success("""
                        🧠 **MCP Features Activated:**
                        - ✅ Adaptive content delivery
                        - ✅ Real-time progress analysis  
                        - ✅ Personalized recommendations
                        - ✅ Learning style optimization
                        """)
                        
                        time.sleep(3)
                        st.session_state.selected_nav = '🏠 Dashboard'
                        st.rerun()

def render_progress_calendar():
    """Render progress calendar page"""
    st.markdown('<h1 class="main-header">📊 Progress Calendar</h1>', unsafe_allow_html=True)
    
    user_id = SessionState.get_user_id()
    learning_paths = learning_service.get_user_learning_paths(user_id)
    
    if not learning_paths:
        st.markdown("""
        <div class="learning-card" style="text-align: center;">
            <h3>📅 No Learning Paths Yet</h3>
            <p>Create your first learning path to see your progress calendar here.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("➕ Create Learning Path"):
            st.session_state.selected_nav = '➕ Generate Learning Path'
            st.rerun()
        return
    
    # Path selector
    st.markdown("### Select a Learning Path")
    
    path_options = {f"{path.get('goal', 'Unknown')} ({path.get('type', 'normal').upper()})": path for path in learning_paths}
    selected_path_name = st.selectbox("📚 Learning Path", list(path_options.keys()))
    
    if selected_path_name:
        selected_path = path_options[selected_path_name]
        
        # Path overview
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Duration", f"{selected_path.get('duration_days', 0)} days")
        
        with col2:
            st.metric("Progress", f"{selected_path.get('completion_percentage', 0):.1f}%")
        
        with col3:
            difficulty = selected_path.get('difficulty', 'unknown')
            st.metric("Difficulty", difficulty.title())
        
        with col4:
            path_type = selected_path.get('type', 'normal')
            st.metric("Type", path_type.upper())
        
        st.markdown("---")
        
        # Calendar views
        render_progress_calendar_views(selected_path, user_id)

def render_progress_calendar_views(path: dict, user_id: str):
    """Render different calendar views for progress tracking"""
    
    # Calendar view options
    view_options = ["📅 Monthly Grid", "📊 Timeline View", "🔥 Heatmap View"]
    selected_view = st.radio("Calendar View", view_options, horizontal=True)
    
    # Get progress data
    progress = path.get('progress', {})
    completed_days = progress.get('completed_days', {})
    total_days = path.get('duration_days', 0)
    
    if selected_view == "📅 Monthly Grid":
        render_monthly_grid_view(path, completed_days, total_days, user_id)
    elif selected_view == "📊 Timeline View":
        render_timeline_view(path, completed_days, total_days, user_id)
    elif selected_view == "🔥 Heatmap View":
        render_heatmap_view(path, completed_days, total_days)

def render_monthly_grid_view(path: dict, completed_days: dict, total_days: int, user_id: str):
    """Render monthly grid calendar view"""
    st.markdown("### 📅 Monthly Progress Grid")
    
    # Create grid layout
    days_per_row = 7
    rows = (total_days + days_per_row - 1) // days_per_row
    
    for row in range(rows):
        cols = st.columns(days_per_row)
        
        for col_idx, col in enumerate(cols):
            day = row * days_per_row + col_idx + 1
            
            if day <= total_days:
                is_completed = completed_days.get(str(day), False)
                
                with col:
                    # Day button styling
                    if is_completed:
                        button_style = "✅"
                        button_color = "success"
                    else:
                        button_style = "⏳"
                        button_color = "secondary"
                    
                    # Create clickable day button
                    if st.button(
                        f"{button_style} {day}",
                        key=f"day_{day}_{path.get('id', '')}",
                        help=f"Day {day} - {'Completed' if is_completed else 'Pending'}"
                    ):
                        # Toggle completion status
                        success = learning_service.update_daily_progress(
                            user_id, path.get('id', ''), day, not is_completed
                        )
                        if success:
                            st.success(f"Day {day} marked as {'incomplete' if is_completed else 'complete'}!")
                            time.sleep(0.5)
                            st.rerun()

def render_timeline_view(path: dict, completed_days: dict, total_days: int, user_id: str):
    """Render timeline view of progress"""
    st.markdown("### 📊 Learning Timeline")
    
    # Create timeline data
    days = list(range(1, total_days + 1))
    completion_status = [1 if completed_days.get(str(day), False) else 0 for day in days]
    
    # Create timeline chart
    fig = go.Figure()
    
    # Add completion data
    fig.add_trace(go.Scatter(
        x=days,
        y=completion_status,
        mode='lines+markers',
        name='Progress',
        line=dict(color='#4CAF50', width=3),
        marker=dict(
            size=10,
            color=[('#4CAF50' if status else '#e0e0e0') for status in completion_status]
        ),
        fill='tonexty',
        fillcolor='rgba(76, 175, 80, 0.2)'
    ))
    
    fig.update_layout(
        title=f"Learning Progress: {path.get('goal', 'Learning Path')}",
        xaxis_title="Days",
        yaxis_title="Completion Status",
        yaxis=dict(tickmode='array', tickvals=[0, 1], ticktext=['Pending', 'Complete']),
        height=500,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Progress statistics
    completed_count = sum(completion_status)
    completion_rate = (completed_count / total_days * 100) if total_days > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Days Completed", completed_count, f"/{total_days}")
    
    with col2:
        st.metric("Completion Rate", f"{completion_rate:.1f}%")
    
    with col3:
        streak = calculate_current_streak(completed_days)
        st.metric("Current Streak", f"{streak} days")

def render_heatmap_view(path: dict, completed_days: dict, total_days: int):
    """Render heatmap view of progress"""
    st.markdown("### 🔥 Progress Heatmap")
    
    # Create heatmap data (simulated for weeks)
    weeks = (total_days + 6) // 7
    heatmap_data = []
    
    for week in range(weeks):
        week_data = []
        for day_of_week in range(7):
            day = week * 7 + day_of_week + 1
            if day <= total_days:
                completion = 1 if completed_days.get(str(day), False) else 0
                week_data.append(completion)
            else:
                week_data.append(None)  # No data
        heatmap_data.append(week_data)
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data,
        colorscale=[[0, '#e0e0e0'], [1, '#4CAF50']],
        showscale=False,
        hoverongaps=False
    ))
    
    fig.update_layout(
        title=f"Weekly Progress Heatmap: {path.get('goal', 'Learning Path')}",
        xaxis=dict(
            title="Day of Week",
            tickmode='array',
            tickvals=list(range(7)),
            ticktext=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        ),
        yaxis=dict(title="Week", autorange='reversed'),
        height=300
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Legend
    st.markdown("""
    **Legend:** 
    - 🟢 Green = Completed day
    - ⚪ Gray = Pending day
    """)

def calculate_current_streak(completed_days: dict) -> int:
    """Calculate current learning streak"""
    if not completed_days:
        return 0
    
    # Find the highest day number that's completed
    max_day = max(int(day) for day in completed_days.keys() if completed_days[day])
    
    # Count backwards from max day
    streak = 0
    for day in range(max_day, 0, -1):
        if completed_days.get(str(day), False):
            streak += 1
        else:
            break
    
    return streak

def render_notifications():
    """Render notifications page"""
    st.markdown('<h1 class="main-header">🔔 Notifications & Reminders</h1>', unsafe_allow_html=True)
    
    user_id = SessionState.get_user_id()
    
    # Notification overview
    st.markdown("""
    <div class="learning-card">
        <h3>Stay Consistent with Smart Reminders 📱</h3>
        <p>Set up automated SMS, WhatsApp, and voice call reminders to keep your learning on track.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs for different notification features
    tab1, tab2, tab3 = st.tabs(["⚙️ Setup Reminders", "📤 Send Now", "📈 History"])
    
    with tab1:
        render_notification_setup(user_id)
    
    with tab2:
        render_send_immediate_notifications(user_id)
    
    with tab3:
        render_notification_history(user_id)

def render_notification_setup(user_id: str):
    """Render notification setup interface"""
    st.markdown("### ⚙️ Configure Learning Reminders")
    
    # Get user's learning paths
    learning_paths = learning_service.get_user_learning_paths(user_id)
    
    if not learning_paths:
        st.warning("Create a learning path first to set up reminders.")
        return
    
    # Path selection
    path_options = {f"{path.get('goal', 'Unknown')}": path for path in learning_paths}
    selected_path_name = st.selectbox("📚 Select Learning Path", list(path_options.keys()))
    
    if selected_path_name:
        selected_path = path_options[selected_path_name]
        
        with st.form("notification_setup_form"):
            st.markdown(f"**Setting up reminders for:** {selected_path_name}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Contact information
                phone_number = st.text_input(
                    "📞 Phone Number",
                    placeholder="+1234567890",
                    help="Include country code"
                )
                
                notification_method = st.selectbox(
                    "📱 Notification Method",
                    ["sms", "whatsapp", "voice"],
                    format_func=lambda x: {
                        "sms": "📱 SMS Text",
                        "whatsapp": "💬 WhatsApp",
                        "voice": "📞 Voice Call"
                    }[x]
                )
            
            with col2:
                # Timing settings
                reminder_time = st.time_input(
                    "⏰ Daily Reminder Time",
                    value=datetime.strptime("09:00", "%H:%M").time(),
                    help="When should we send daily reminders?"
                )
                
                reminder_days = st.multiselect(
                    "📅 Reminder Days",
                    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                    default=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
                    help="Which days should we send reminders?"
                )
            
            # Additional settings
            st.markdown("#### 🎯 Reminder Preferences")
            
            col1, col2 = st.columns(2)
            
            with col1:
                include_progress = st.checkbox("📊 Include progress updates", value=True)
                include_motivation = st.checkbox("💪 Include motivational messages", value=True)
            
            with col2:
                send_completion_celebration = st.checkbox("🎉 Send completion celebrations", value=True)
                send_streak_updates = st.checkbox("🔥 Send streak milestones", value=True)
            
            # Form submission
            if st.form_submit_button("🔔 Setup Reminders", use_container_width=True):
                if not phone_number or not validate_phone_number(phone_number):
                    display_error_message("Please enter a valid phone number")
                elif not reminder_days:
                    display_error_message("Please select at least one reminder day")
                else:
                    # Prepare reminder settings
                    reminder_settings = {
                        'phone_number': phone_number,
                        'method': notification_method,
                        'time': reminder_time.strftime("%H:%M"),
                        'days': [i for i, day in enumerate(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]) if day in reminder_days],
                        'include_progress': include_progress,
                        'include_motivation': include_motivation,
                        'send_completion_celebration': send_completion_celebration,
                        'send_streak_updates': send_streak_updates
                    }
                    
                    # Schedule reminders
                    success = notification_service.schedule_learning_reminder(
                        user_id, selected_path.get('id', ''), reminder_settings
                    )
                    
                    if success:
                        display_success_message("✅ Reminders scheduled successfully!")
                        st.balloons()

def render_send_immediate_notifications(user_id: str):
    """Render interface to send immediate notifications"""
    st.markdown("### 📤 Send Immediate Notifications")
    
    learning_paths = learning_service.get_user_learning_paths(user_id)
    
    if not learning_paths:
        st.warning("Create a learning path first to send notifications.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Learning reminder
        st.markdown("#### 📚 Learning Reminder")
        
        with st.form("immediate_reminder_form"):
            path_options = {f"{path.get('goal', 'Unknown')}": path for path in learning_paths}
            selected_path_name = st.selectbox("Learning Path", list(path_options.keys()), key="reminder_path")
            
            phone_number = st.text_input("Phone Number", placeholder="+1234567890", key="reminder_phone")
            
            method = st.selectbox(
                "Method",
                ["sms", "whatsapp", "voice"],
                format_func=lambda x: {"sms": "SMS", "whatsapp": "WhatsApp", "voice": "Voice"}[x],
                key="reminder_method"
            )
            
            if st.form_submit_button("📤 Send Reminder"):
                if phone_number and validate_phone_number(phone_number) and selected_path_name:
                    selected_path = path_options[selected_path_name]
                    
                    success = notification_service.send_immediate_reminder(
                        user_id, selected_path.get('id', ''), phone_number, method
                    )
                    
                    if success:
                        display_success_message("Reminder sent successfully!")
    
    with col2:
        # Motivation message
        st.markdown("#### 💪 Motivation Message")
        
        with st.form("motivation_form"):
            path_options = {f"{path.get('goal', 'Unknown')}": path for path in learning_paths}
            selected_path_name = st.selectbox("Learning Path", list(path_options.keys()), key="motivation_path")
            
            phone_number = st.text_input("Phone Number", placeholder="+1234567890", key="motivation_phone")
            
            method = st.selectbox(
                "Method",
                ["sms", "whatsapp", "voice"],
                format_func=lambda x: {"sms": "SMS", "whatsapp": "WhatsApp", "voice": "Voice"}[x],
                key="motivation_method"
            )
            
            if st.form_submit_button("💪 Send Motivation"):
                if phone_number and validate_phone_number(phone_number) and selected_path_name:
                    selected_path = path_options[selected_path_name]
                    
                    success = notification_service.send_motivation_message(
                        user_id, selected_path.get('id', ''), phone_number, method
                    )
                    
                    if success:
                        display_success_message("Motivation message sent!")
    
    # Test notifications
    st.markdown("---")
    st.markdown("#### 🧪 Test Notifications")
    
    with st.form("test_notification_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            test_phone = st.text_input("Test Phone Number", placeholder="+1234567890")
        
        with col2:
            test_method = st.selectbox(
                "Test Method",
                ["sms", "whatsapp", "voice"],
                format_func=lambda x: {"sms": "SMS", "whatsapp": "WhatsApp", "voice": "Voice"}[x]
            )
        
        if st.form_submit_button("🧪 Send Test Message"):
            if test_phone and validate_phone_number(test_phone):
                success = notification_service.test_notification(test_phone, test_method)
                if success:
                    display_success_message("Test notification sent!")
            else:
                display_error_message("Please enter a valid phone number")

def render_notification_history(user_id: str):
    """Render notification history"""
    st.markdown("### 📈 Notification History")
    
    # Get notification history
    history = notification_service.get_notification_history(user_id)
    
    if not history:
        st.info("No notification history available yet.")
        return
    
    # Display history in table format
    history_df = pd.DataFrame(history)
    
    if not history_df.empty:
        # Format the data for display
        history_df['sent_at'] = pd.to_datetime(history_df['sent_at']).dt.strftime('%Y-%m-%d %H:%M')
        history_df['Type'] = history_df['type'].str.title()
        history_df['Method'] = history_df['method'].str.title()
        history_df['Status'] = history_df['status'].str.title()
        history_df['Sent At'] = history_df['sent_at']
        history_df['Learning Path'] = history_df['path_goal']
        
        # Display table
        st.dataframe(
            history_df[['Type', 'Method', 'Status', 'Sent At', 'Learning Path']],
            use_container_width=True
        )
        
        # Summary statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Notifications", len(history_df))
        
        with col2:
            delivered_count = len(history_df[history_df['status'] == 'delivered'])
            st.metric("Delivered", delivered_count)
        
        with col3:
            success_rate = (delivered_count / len(history_df) * 100) if len(history_df) > 0 else 0
            st.metric("Success Rate", f"{success_rate:.1f}%")

def render_analytics():
    """Render analytics page"""
    st.markdown('<h1 class="main-header">📈 Learning Analytics</h1>', unsafe_allow_html=True)
    
    user_id = SessionState.get_user_id()
    
    # Get analytics data
    analytics = learning_service.get_learning_analytics(user_id)
    
    if not analytics or analytics.get('total_paths', 0) == 0:
        st.markdown("""
        <div class="learning-card" style="text-align: center;">
            <h3>📊 No Analytics Data Yet</h3>
            <p>Complete some learning activities to see your analytics here.</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Overview metrics
    st.markdown("### 🎯 Learning Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "📚 Total Paths",
            analytics.get('total_paths', 0),
            help="Total number of learning paths created"
        )
    
    with col2:
        st.metric(
            "✅ Completed",
            analytics.get('completed_paths', 0),
            help="Learning paths completed (100%)"
        )
    
    with col3:
        st.metric(
            "🔄 Active",
            analytics.get('active_paths', 0),
            help="Learning paths in progress"
        )
    
    with col4:
        st.metric(
            "📊 Avg. Completion",
            f"{analytics.get('average_completion_rate', 0):.1f}%",
            help="Average completion rate across all paths"
        )
    
    # Charts and visualizations
    learning_paths = learning_service.get_user_learning_paths(user_id)
    
    if learning_paths:
        # Completion rate chart
        st.markdown("### 📊 Completion Progress")
        
        path_names = [path.get('goal', 'Unknown')[:30] for path in learning_paths]
        completion_rates = [path.get('completion_percentage', 0) for path in learning_paths]
        
        fig = px.bar(
            x=completion_rates,
            y=path_names,
            orientation='h',
            title="Completion Rate by Learning Path",
            labels={'x': 'Completion %', 'y': 'Learning Paths'},
            color=completion_rates,
            color_continuous_scale='Viridis'
        )
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Learning path types distribution
        st.markdown("### 🧠 Learning Path Types")
        
        path_types = [path.get('type', 'unknown') for path in learning_paths]
        type_counts = pd.Series(path_types).value_counts()
        
        fig = px.pie(
            values=type_counts.values,
            names=type_counts.index,
            title="Distribution of Learning Path Types",
            color_discrete_map={
                'normal': '#4CAF50',
                'mcp': '#2196F3',
                'unknown': '#757575'
            }
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Difficulty level analysis
        st.markdown("### 📈 Difficulty Level Analysis")
        
        difficulties = [path.get('difficulty', 'unknown') for path in learning_paths]
        difficulty_completion = {}
        
        for path in learning_paths:
            difficulty = path.get('difficulty', 'unknown')
            completion = path.get('completion_percentage', 0)
            
            if difficulty not in difficulty_completion:
                difficulty_completion[difficulty] = []
            difficulty_completion[difficulty].append(completion)
        
        # Calculate average completion by difficulty
        avg_completion_by_difficulty = {
            diff: sum(completions) / len(completions) if completions else 0
            for diff, completions in difficulty_completion.items()
        }
        
        fig = px.bar(
            x=list(avg_completion_by_difficulty.keys()),
            y=list(avg_completion_by_difficulty.values()),
            title="Average Completion Rate by Difficulty Level",
            labels={'x': 'Difficulty Level', 'y': 'Average Completion %'},
            color=list(avg_completion_by_difficulty.values()),
            color_continuous_scale='RdYlGn'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Recommendations based on analytics
        render_analytics_recommendations(analytics, learning_paths)

def render_analytics_recommendations(analytics: dict, learning_paths: list):
    """Render recommendations based on analytics"""
    st.markdown("### 💡 Personalized Recommendations")
    
    recommendations = []
    
    # Analyze completion patterns
    avg_completion = analytics.get('average_completion_rate', 0)
    
    if avg_completion < 30:
        recommendations.append({
            'icon': '🎯',
            'title': 'Focus on Shorter Paths',
            'description': 'Try creating shorter learning paths (5-7 days) to build momentum and confidence.',
            'action': 'Create a 5-day learning path'
        })
    elif avg_completion > 80:
        recommendations.append({
            'icon': '🚀',
            'title': 'Challenge Yourself',
            'description': 'You\'re doing great! Consider more advanced or longer learning paths.',
            'action': 'Try an advanced or MCP learning path'
        })
    
    # Analyze learning path types
    normal_paths = sum(1 for path in learning_paths if path.get('type') == 'normal')
    mcp_paths = sum(1 for path in learning_paths if path.get('type') == 'mcp')
    
    if normal_paths > 0 and mcp_paths == 0:
        recommendations.append({
            'icon': '🧠',
            'title': 'Try MCP Learning',
            'description': 'Experience adaptive learning with our advanced MCP (Model Context Protocol) paths.',
            'action': 'Create your first MCP learning path'
        })
    
    # Check for incomplete paths
    incomplete_paths = sum(1 for path in learning_paths if 0 < path.get('completion_percentage', 0) < 100)
    
    if incomplete_paths > 2:
        recommendations.append({
            'icon': '✅',
            'title': 'Complete Existing Paths',
            'description': f'You have {incomplete_paths} paths in progress. Consider focusing on completion.',
            'action': 'Set up daily reminders for active paths'
        })
    
    # Display recommendations
    if recommendations:
        for rec in recommendations:
            st.markdown(f"""
            <div class="learning-card">
                <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                    <span style="font-size: 2rem; margin-right: 1rem;">{rec['icon']}</span>
                    <div>
                        <h4 style="margin: 0;">{rec['title']}</h4>
                        <p style="margin: 0; color: #666;">{rec['description']}</p>
                    </div>
                </div>
                <div style="text-align: right;">
                    <em style="color: #4CAF50;">💡 Suggested action: {rec['action']}</em>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("🎉 Great job! You're on track with your learning goals.")

def render_settings():
    """Render settings page"""
    st.markdown('<h1 class="main-header">⚙️ Settings</h1>', unsafe_allow_html=True)
    
    user_id = SessionState.get_user_id()
    user_email = SessionState.get_user_email()
    
    # Settings tabs
    tab1, tab2, tab3, tab4 = st.tabs(["👤 Profile", "🔧 Preferences", "🔑 API Keys", "💾 Data"])
    
    with tab1:
        render_profile_settings(user_id, user_email)
    
    with tab2:
        render_preferences_settings(user_id)
    
    with tab3:
        render_api_settings()
    
    with tab4:
        render_data_settings(user_id)

def render_profile_settings(user_id: str, user_email: str):
    """Render profile settings"""
    st.markdown("### 👤 Profile Settings")
    
    # Get user profile
    profile = firestore_client.get_user_profile(user_id) or {}
    
    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name", value=profile.get('name', ''))
            email = st.text_input("Email", value=user_email, disabled=True)
        
        with col2:
            phone = st.text_input("Phone Number", value=profile.get('phone', ''), placeholder="+1234567890")
            timezone = st.selectbox(
                "Timezone",
                ["UTC", "America/New_York", "America/Los_Angeles", "Europe/London", "Asia/Tokyo"],
                index=0
            )
        
        # Learning preferences
        st.markdown("#### 📚 Learning Preferences")
        
        col1, col2 = st.columns(2)
        
        with col1:
            preferred_difficulty = st.selectbox(
                "Preferred Difficulty",
                ["beginner", "intermediate", "advanced", "expert"],
                index=0
            )
        
        with col2:
            preferred_duration = st.slider(
                "Preferred Path Duration (days)",
                min_value=3,
                max_value=90,
                value=14
            )
        
        if st.form_submit_button("💾 Save Profile"):
            updated_profile = {
                'name': name,
                'phone': phone,
                'timezone': timezone,
                'preferred_difficulty': preferred_difficulty,
                'preferred_duration': preferred_duration,
                'updated_at': datetime.now()
            }
            
            # Update profile in database
            success = firestore_client.create_user_profile(user_id, updated_profile)
            if success:
                display_success_message("Profile updated successfully!")

def render_preferences_settings(user_id: str):
    """Render user preferences"""
    st.markdown("### 🔧 App Preferences")
    
    with st.form("preferences_form"):
        # Notification preferences
        st.markdown("#### 🔔 Notification Preferences")
        
        col1, col2 = st.columns(2)
        
        with col1:
            enable_notifications = st.checkbox("Enable notifications", value=True)
            email_notifications = st.checkbox("Email notifications", value=True)
        
        with col2:
            sms_notifications = st.checkbox("SMS notifications", value=False)
            push_notifications = st.checkbox("Push notifications", value=True)
        
        # Learning preferences
        st.markdown("#### 📚 Learning Preferences")
        
        col1, col2 = st.columns(2)
        
        with col1:
            auto_advance = st.checkbox("Auto-advance to next day", value=False)
            show_progress_animations = st.checkbox("Show progress animations", value=True)
        
        with col2:
            enable_voice_synthesis = st.checkbox("Enable voice synthesis", value=True)
            dark_mode = st.checkbox("Dark mode (coming soon)", value=False, disabled=True)
        
        # Privacy preferences
        st.markdown("#### 🔒 Privacy Preferences")
        
        col1, col2 = st.columns(2)
        
        with col1:
            analytics_tracking = st.checkbox("Allow analytics tracking", value=True)
            share_progress = st.checkbox("Share progress publicly", value=False)
        
        with col2:
            email_marketing = st.checkbox("Receive marketing emails", value=False)
            data_sharing = st.checkbox("Allow anonymous data sharing for research", value=True)
        
        if st.form_submit_button("💾 Save Preferences"):
            preferences = {
                'notifications': {
                    'enabled': enable_notifications,
                    'email': email_notifications,
                    'sms': sms_notifications,
                    'push': push_notifications
                },
                'learning': {
                    'auto_advance': auto_advance,
                    'progress_animations': show_progress_animations,
                    'voice_synthesis': enable_voice_synthesis,
                    'dark_mode': dark_mode
                },
                'privacy': {
                    'analytics_tracking': analytics_tracking,
                    'share_progress': share_progress,
                    'email_marketing': email_marketing,
                    'data_sharing': data_sharing
                },
                'updated_at': datetime.now()
            }
            
            # Save preferences
            success = firestore_client.save_notification_settings(user_id, preferences)
            if success:
                display_success_message("Preferences saved successfully!")

def render_api_settings():
    """Render API settings"""
    st.markdown("### 🔑 API Configuration")
    
    # Current API status
    st.markdown("#### 📊 Current API Status")
    
    api_services = [
        ("Gemini AI", settings.GEMINI_API_KEY != "demo_key", "Generate AI learning content"),
        ("YouTube Data", settings.YOUTUBE_API_KEY != "demo_key", "Find educational videos"),
        ("ElevenLabs", settings.ELEVENLABS_API_KEY != "demo_key", "Text-to-speech synthesis"),
        ("Twilio", settings.TWILIO_ACCOUNT_SID != "demo_sid", "SMS/WhatsApp notifications"),
    ]
    
    for service, is_active, description in api_services:
        status = "✅ Active" if is_active else "⚪ Demo Mode"
        color = "green" if is_active else "orange"
        
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; 
                    padding: 1rem; margin: 0.5rem 0; background: #f8f9fa; border-radius: 8px;">
            <div>
                <strong>{service}</strong><br>
                <small style="color: #666;">{description}</small>
            </div>
            <span style="color: {color}; font-weight: bold;">{status}</span>
        </div>
        """, unsafe_allow_html=True)
    
    # API setup instructions
    st.markdown("#### 📋 Setup Instructions")
    
    with st.expander("🔧 How to Configure APIs", expanded=False):
        st.markdown("""
        **To enable full functionality, set up these environment variables:**
        
        1. **Gemini AI API Key**
           - Visit: [Google AI Studio](https://aistudio.google.com/app/apikey)
           - Create a free API key
           - Set: `GEMINI_API_KEY=your_api_key`
        
        2. **YouTube Data API Key**
           - Go to: [Google Cloud Console](https://console.cloud.google.com/)
           - Enable YouTube Data API v3
           - Create credentials → API Key
           - Set: `YOUTUBE_API_KEY=your_api_key`
        
        3. **ElevenLabs API Key**
           - Sign up at: [ElevenLabs](https://elevenlabs.io/)
           - Get your API key from profile settings
           - Set: `ELEVENLABS_API_KEY=your_api_key`
        
        4. **Twilio Configuration**
           - Create account at: [Twilio](https://www.twilio.com/)
           - Get Account SID and Auth Token
           - Set: `TWILIO_ACCOUNT_SID=your_sid`
           - Set: `TWILIO_AUTH_TOKEN=your_token`
           - Set: `TWILIO_PHONE_NUMBER=your_phone`
        
        **Note:** Restart the application after setting environment variables.
        """)

def render_data_settings(user_id: str):
    """Render data management settings"""
    st.markdown("### 💾 Data Management")
    
    # Data overview
    learning_paths = learning_service.get_user_learning_paths(user_id)
    
    st.markdown("#### 📊 Your Data Overview")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Learning Paths", len(learning_paths))
    
    with col2:
        total_days = sum(path.get('duration_days', 0) for path in learning_paths)
        st.metric("Total Learning Days", total_days)
    
    with col3:
        # Estimate data size (rough calculation)
        estimated_size = len(learning_paths) * 50 + 100  # KB
        st.metric("Estimated Data Size", f"{estimated_size} KB")
    
    # Export options
    st.markdown("#### 📥 Export Your Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 Export All Learning Paths (JSON)", use_container_width=True):
            if learning_paths:
                export_data = {
                    'user_id': user_id,
                    'exported_at': datetime.now().isoformat(),
                    'learning_paths': learning_paths
                }
                
                json_data = json.dumps(export_data, indent=2, default=str)
                
                st.download_button(
                    label="📥 Download JSON Export",
                    data=json_data,
                    file_name=f"learning_paths_export_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json"
                )
            else:
                st.warning("No learning paths to export")
    
    with col2:
        if st.button("📊 Export Progress Report (CSV)", use_container_width=True):
            if learning_paths:
                # Create progress report
                report_data = []
                for path in learning_paths:
                    report_data.append({
                        'Goal': path.get('goal', ''),
                        'Type': path.get('type', '').upper(),
                        'Difficulty': path.get('difficulty', '').title(),
                        'Duration (days)': path.get('duration_days', 0),
                        'Progress (%)': path.get('completion_percentage', 0),
                        'Created': path.get('created_at', '').split('T')[0] if path.get('created_at') else ''
                    })
                
                df = pd.DataFrame(report_data)
                csv_data = df.to_csv(index=False)
                
                st.download_button(
                    label="📥 Download CSV Report",
                    data=csv_data,
                    file_name=f"progress_report_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No progress data to export")
    
    # Data deletion
    st.markdown("---")
    st.markdown("#### 🗑️ Delete Data")
    
    st.warning("⚠️ **Danger Zone**: These actions cannot be undone!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Delete All Learning Paths", use_container_width=True):
            st.error("This feature is not implemented in demo mode for safety.")
    
    with col2:
        if st.button("❌ Delete Account", use_container_width=True):
            st.error("Account deletion is not available in demo mode.")
    
    st.markdown("""
    <small style="color: #666;">
    <strong>Data Privacy:</strong> Your data is stored locally in demo mode. 
    In production, all data would be encrypted and stored securely in Firebase.
    </small>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
