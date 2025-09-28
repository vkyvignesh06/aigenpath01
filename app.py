import streamlit as st
import os
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# Import our modules
from auth.firebase_auth import firebase_auth
from services.learning_service import learning_service
from services.notification_service import notification_service
from ai_services.mcp_integration import mcp_integration
from integrations.youtube_client import youtube_client
from integrations.elevenlabs_client import elevenlabs_client
from integrations.twilio_client import twilio_client
from integrations.drive_client import drive_client
from utils.helpers import *
from config.settings import settings

# Page configuration
st.set_page_config(
    page_title="AI Learning Path Generator",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem;
    }
    
    .progress-container {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .day-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }
    
    .day-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        transform: translateY(-2px);
    }
    
    .completed-day {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main application function"""
    
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    # Check authentication
    if not st.session_state.authenticated:
        show_auth_page()
    else:
        show_main_app()

def show_auth_page():
    """Show authentication page"""
    st.markdown("""
    <div class="main-header">
        <h1>🎓 AI Learning Path Generator</h1>
        <p>Personalized Learning with Model Context Protocol</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Demo mode notice
    if settings.is_demo_mode:
        st.info("🚀 Running in Demo Mode - Full functionality available without API keys!")
    
    tab1, tab2 = st.tabs(["🔑 Sign In", "📝 Sign Up"])
    
    with tab1:
        show_signin_form()
    
    with tab2:
        show_signup_form()

def show_signin_form():
    """Show sign in form"""
    st.subheader("Welcome Back!")
    
    with st.form("signin_form"):
        email = st.text_input("Email", placeholder="your.email@example.com")
        password = st.text_input("Password", type="password")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.form_submit_button("🔑 Sign In", use_container_width=True):
                if email and password:
                    user = firebase_auth.sign_in_with_email_password(email, password)
                    if user:
                        st.session_state.authenticated = True
                        st.session_state.user = user
                        st.success("Welcome back!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
                else:
                    st.error("Please fill in all fields")
        
        with col2:
            if st.form_submit_button("🌐 Google Sign In", use_container_width=True):
                user = firebase_auth.sign_in_with_google()
                if user:
                    st.session_state.authenticated = True
                    st.session_state.user = user
                    st.success("Welcome!")
                    st.rerun()
        
        with col3:
            if st.form_submit_button("🎯 Demo Login", use_container_width=True):
                # Quick demo login
                user = firebase_auth.sign_in_with_email_password("demo@example.com", "demo123")
                if user:
                    st.session_state.authenticated = True
                    st.session_state.user = user
                    st.success("Demo mode activated!")
                    st.rerun()

def show_signup_form():
    """Show sign up form"""
    st.subheader("Join the Learning Revolution!")
    
    with st.form("signup_form"):
        name = st.text_input("Full Name", placeholder="Your Name")
        email = st.text_input("Email", placeholder="your.email@example.com")
        password = st.text_input("Password", type="password", help="Minimum 6 characters")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        if st.form_submit_button("🚀 Create Account", use_container_width=True):
            if not all([name, email, password, confirm_password]):
                st.error("Please fill in all fields")
            elif password != confirm_password:
                st.error("Passwords don't match")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters")
            elif not validate_email(email):
                st.error("Please enter a valid email address")
            else:
                user = firebase_auth.create_user_with_email_password(email, password, name)
                if user:
                    st.session_state.authenticated = True
                    st.session_state.user = user
                    st.success("Account created successfully!")
                    st.rerun()
                else:
                    st.error("Failed to create account")

def show_main_app():
    """Show main application"""
    user = st.session_state.get('user', {})
    user_name = user.get('name', 'User')
    user_id = user.get('user_id', '')
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; color: white; margin-bottom: 1rem;">
            <h3>👋 Welcome, {user_name}!</h3>
        </div>
        """, unsafe_allow_html=True)
        
        page = st.selectbox(
            "Navigate",
            ["🏠 Dashboard", "➕ Create Learning Path", "📚 My Learning Paths", 
             "📊 Progress Analytics", "🔔 Notifications", "⚙️ Settings"],
            key="main_navigation"
        )
        
        st.markdown("---")
        
        if st.button("🚪 Sign Out", use_container_width=True):
            firebase_auth.sign_out()
            st.session_state.authenticated = False
            if 'user' in st.session_state:
                del st.session_state.user
            st.rerun()
    
    # Main content based on selected page
    # Handle redirects
    if 'redirect_to' in st.session_state:
        page = st.session_state.redirect_to
        del st.session_state.redirect_to
    
    if page == "🏠 Dashboard":
        show_dashboard(user_id)
    elif page == "➕ Create Learning Path":
        show_create_learning_path(user_id)
    elif page == "📚 My Learning Paths":
        show_learning_paths(user_id)
    elif page == "📊 Progress Analytics":
        show_analytics(user_id)
    elif page == "🔔 Notifications":
        show_notifications(user_id)
    elif page == "⚙️ Settings":
        show_settings(user_id)

def show_dashboard(user_id: str):
    """Show dashboard"""
    st.markdown("""
    <div class="main-header">
        <h1>🎓 Your Learning Dashboard</h1>
        <p>Track your progress and continue your learning journey</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get user analytics
    analytics = learning_service.get_learning_analytics(user_id)
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h2>{analytics.get('total_paths', 0)}</h2>
            <p>Learning Paths</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h2>{analytics.get('completed_paths', 0)}</h2>
            <p>Completed</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h2>{analytics.get('total_days_studied', 0)}</h2>
            <p>Days Studied</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h2>{analytics.get('current_streak', 0)}</h2>
            <p>Current Streak</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Recent learning paths
    st.subheader("📚 Recent Learning Paths")
    learning_paths = learning_service.get_user_learning_paths(user_id)
    
    if learning_paths:
        for path in learning_paths[:3]:  # Show last 3
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.markdown(f"""
                    <div class="feature-card">
                        <h4>{path.get('goal', 'Learning Path')}</h4>
                        <p><strong>Duration:</strong> {path.get('duration_days', 0)} days | 
                           <strong>Difficulty:</strong> {path.get('difficulty', 'Unknown').title()} |
                           <strong>Type:</strong> {path.get('type', 'normal').upper()}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    completion = path.get('completion_percentage', 0)
                    st.metric("Progress", f"{completion:.1f}%")
                
                with col3:
                    if st.button(f"Continue", key=f"continue_{path.get('id', '')}"):
                        st.session_state.selected_path = path
                        st.session_state.redirect_to = "📚 My Learning Paths"
                        st.rerun()
    else:
        st.info("🚀 Ready to start your learning journey? Create your first learning path!")
        if st.button("➕ Create Learning Path", use_container_width=True):
            st.session_state.redirect_to = "➕ Create Learning Path"
            st.rerun()
    
    # Learning recommendations
    st.subheader("💡 Recommended Learning Paths")
    recommendations = learning_service.get_learning_recommendations(user_id)
    
    if recommendations:
        cols = st.columns(min(3, len(recommendations)))
        for i, rec in enumerate(recommendations[:3]):
            with cols[i]:
                st.markdown(f"""
                <div class="feature-card">
                    <h4>{rec.get('title', 'Recommendation')}</h4>
                    <p>{rec.get('description', '')}</p>
                    <p><strong>Duration:</strong> {rec.get('estimated_duration', 7)} days</p>
                    <p><strong>Difficulty:</strong> {rec.get('difficulty', 'beginner').title()}</p>
                </div>
                """, unsafe_allow_html=True)

def show_create_learning_path(user_id: str):
    """Show create learning path page"""
    st.markdown("""
    <div class="main-header">
        <h1>➕ Create Your Learning Path</h1>
        <p>Let AI design a personalized learning journey for you</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Path type selection
    path_type = st.radio(
        "Choose Learning Path Type",
        ["🎯 Normal Path", "🧠 MCP (Adaptive) Path"],
        help="Normal paths provide structured learning. MCP paths adapt to your progress and learning style."
    )
    
    with st.form("create_path_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            goal = st.text_input(
                "Learning Goal",
                placeholder="e.g., Learn Python Programming, Master Communication Skills",
                help="Be specific about what you want to learn"
            )
            
            duration = st.slider(
                "Duration (days)",
                min_value=3,
                max_value=90,
                value=14,
                help="How many days do you want to dedicate to this learning path?"
            )
        
        with col2:
            difficulty = st.selectbox(
                "Difficulty Level",
                ["beginner", "intermediate", "advanced", "expert"],
                help="Choose based on your current knowledge level"
            )
            
            include_practice = st.checkbox(
                "Include Hands-on Practice",
                value=True,
                help="Add practical exercises and projects to your learning path"
            )
        
        # MCP-specific options
        if "MCP" in path_type:
            st.subheader("🧠 MCP Configuration")
            
            col1, col2 = st.columns(2)
            with col1:
                learning_style = st.selectbox(
                    "Preferred Learning Style",
                    ["visual", "auditory", "kinesthetic", "mixed"],
                    help="How do you learn best?"
                )
                
                time_per_day = st.selectbox(
                    "Available Time per Day",
                    ["30 minutes", "1 hour", "2 hours", "3+ hours"],
                    index=1
                )
            
            with col2:
                previous_experience = st.text_area(
                    "Previous Experience",
                    placeholder="Describe any related knowledge or experience you have",
                    height=100
                )
                
                specific_interests = st.text_input(
                    "Specific Interests",
                    placeholder="Any particular aspects you're most interested in?"
                )
        
        if st.form_submit_button("🚀 Generate Learning Path", use_container_width=True):
            if not goal:
                st.error("Please enter a learning goal")
            elif not validate_learning_goal(goal):
                st.error("Please enter a more specific learning goal (at least 2 words)")
            else:
                with st.spinner("🤖 AI is creating your personalized learning path..."):
                    path_data = {
                        'goal': goal,
                        'duration': duration,
                        'difficulty': difficulty,
                        'type': 'mcp' if "MCP" in path_type else 'normal',
                        'include_practice': include_practice
                    }
                    
                    # Add MCP-specific data
                    if "MCP" in path_type:
                        path_data['mcp_context'] = {
                            'learning_style': learning_style,
                            'time_per_day': time_per_day,
                            'previous_experience': previous_experience,
                            'specific_interests': specific_interests
                        }
                    
                    path_id = learning_service.create_learning_path(user_id, path_data)
                    
                    if path_id:
                        st.success("🎉 Learning path created successfully!")
                        st.balloons()
                        
                        # Show quick preview
                        learning_paths = learning_service.get_user_learning_paths(user_id)
                        created_path = None
                        for path in learning_paths:
                            if path.get('id') == path_id:
                                created_path = path
                                break
                        
                        if created_path:
                            st.subheader("📋 Quick Preview")
                            st.write(f"**Goal:** {created_path.get('goal', '')}")
                            st.write(f"**Duration:** {created_path.get('duration_days', 0)} days")
                            st.write(f"**Type:** {created_path.get('type', 'normal').upper()}")
                            
                            if st.button("📚 View Full Learning Path"):
                                st.session_state.selected_path = created_path
                                st.session_state.redirect_to = "📚 My Learning Paths"
                                st.rerun()

def show_learning_paths(user_id: str):
    """Show user's learning paths"""
    st.markdown("""
    <div class="main-header">
        <h1>📚 My Learning Paths</h1>
        <p>Manage and track your learning journeys</p>
    </div>
    """, unsafe_allow_html=True)
    
    learning_paths = learning_service.get_user_learning_paths(user_id)
    
    if not learning_paths:
        st.info("🚀 You haven't created any learning paths yet!")
        if st.button("➕ Create Your First Learning Path", use_container_width=True):
            st.session_state.redirect_to = "➕ Create Learning Path"
            st.rerun()
        return
    
    # Filter and sort options
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_type = st.selectbox("Filter by Type", ["All", "Normal", "MCP"])
    with col2:
        filter_status = st.selectbox("Filter by Status", ["All", "In Progress", "Completed"])
    with col3:
        sort_by = st.selectbox("Sort by", ["Recent", "Progress", "Duration"])
    
    # Apply filters
    filtered_paths = learning_paths.copy()
    
    if filter_type != "All":
        filtered_paths = [p for p in filtered_paths if p.get('type', 'normal').upper() == filter_type.upper()]
    
    if filter_status == "In Progress":
        filtered_paths = [p for p in filtered_paths if 0 < p.get('completion_percentage', 0) < 100]
    elif filter_status == "Completed":
        filtered_paths = [p for p in filtered_paths if p.get('completion_percentage', 0) >= 100]
    
    # Display learning paths
    for path in filtered_paths:
        with st.expander(f"📖 {path.get('goal', 'Learning Path')} ({path.get('completion_percentage', 0):.1f}% complete)"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Duration:** {path.get('duration_days', 0)} days")
                st.write(f"**Difficulty:** {path.get('difficulty', 'Unknown').title()}")
                st.write(f"**Type:** {path.get('type', 'normal').upper()}")
                st.write(f"**Description:** {path.get('description', 'No description available')}")
                
                # Progress bar
                completion = path.get('completion_percentage', 0)
                st.markdown(create_progress_bar_html(completion), unsafe_allow_html=True)
            
            with col2:
                if st.button(f"📖 View Details", key=f"view_{path.get('id', '')}"):
                    show_learning_path_details(user_id, path)
                
                if st.button(f"🔔 Set Reminders", key=f"remind_{path.get('id', '')}"):
                    show_notification_setup(user_id, path.get('id', ''))
                
                if st.button(f"📄 Export", key=f"export_{path.get('id', '')}"):
                    export_data = learning_service.export_learning_path(user_id, path.get('id', ''), 'json')
                    if export_data:
                        st.download_button(
                            "📥 Download JSON",
                            export_data,
                            f"{path.get('goal', 'learning_path')}.json",
                            "application/json"
                        )

def show_learning_path_details(user_id: str, path: dict):
    """Show detailed view of a learning path"""
    st.subheader(f"📖 {path.get('goal', 'Learning Path')}")
    
    # Path info
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Duration", f"{path.get('duration_days', 0)} days")
    with col2:
        st.metric("Difficulty", path.get('difficulty', 'Unknown').title())
    with col3:
        st.metric("Type", path.get('type', 'normal').upper())
    with col4:
        completion = path.get('completion_percentage', 0)
        st.metric("Progress", f"{completion:.1f}%")
    
    # Daily plans
    st.subheader("📅 Daily Learning Plan")
    
    daily_plans = path.get('daily_plans', [])
    progress = path.get('progress', {})
    completed_days = progress.get('completed_days', {})
    
    # Calendar view toggle
    view_mode = st.radio("View Mode", ["📋 List View", "📅 Calendar View"], horizontal=True)
    
    if view_mode == "📅 Calendar View":
        show_calendar_view(user_id, path.get('id', ''), daily_plans, completed_days)
    else:
        show_list_view(user_id, path.get('id', ''), daily_plans, completed_days)

def show_calendar_view(user_id: str, path_id: str, daily_plans: list, completed_days: dict):
    """Show calendar view of learning progress"""
    if not daily_plans:
        st.info("No daily plans available")
        return
    
    # Create calendar data
    calendar_data = []
    for plan in daily_plans:
        day = plan.get('day', 1)
        completed = completed_days.get(str(day), False)
        
        calendar_data.append({
            'Day': day,
            'Title': plan.get('title', f'Day {day}'),
            'Status': 'Completed' if completed else 'Pending',
            'Objectives': len(plan.get('objectives', [])),
            'Estimated Time': plan.get('estimated_time', 'Unknown')
        })
    
    # Display as interactive calendar
    df = pd.DataFrame(calendar_data)
    
    # Create calendar visualization
    fig = px.scatter(
        df, 
        x='Day', 
        y=[1] * len(df),
        color='Status',
        size='Objectives',
        hover_data=['Title', 'Estimated Time'],
        color_discrete_map={'Completed': '#4CAF50', 'Pending': '#FF9800'},
        title="Learning Progress Calendar"
    )
    
    fig.update_layout(
        showlegend=True,
        yaxis=dict(visible=False),
        height=200
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Interactive day selection
    selected_day = st.selectbox("Select Day to View Details", range(1, len(daily_plans) + 1))
    
    if selected_day:
        plan = daily_plans[selected_day - 1]
        show_daily_plan_details(user_id, path_id, plan, completed_days)

def show_list_view(user_id: str, path_id: str, daily_plans: list, completed_days: dict):
    """Show list view of daily plans"""
    for plan in daily_plans:
        day = plan.get('day', 1)
        completed = completed_days.get(str(day), False)
        
        # Day card
        card_class = "day-card completed-day" if completed else "day-card"
        
        with st.container():
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"""
                <div class="{card_class}">
                    <h4>Day {day}: {plan.get('title', 'Learning Day')}</h4>
                    <p><strong>Estimated Time:</strong> {plan.get('estimated_time', 'Unknown')}</p>
                    <p><strong>Objectives:</strong> {len(plan.get('objectives', []))} learning objectives</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # Toggle completion
                new_status = st.checkbox(
                    "✅ Completed" if completed else "⏳ Mark Complete",
                    value=completed,
                    key=f"day_{day}_{path_id}"
                )
                
                if new_status != completed:
                    success = learning_service.update_daily_progress(user_id, path_id, day, new_status)
                    if success:
                        st.rerun()
                
                # View details button
                if st.button(f"👁️ Details", key=f"details_{day}_{path_id}"):
                    show_daily_plan_details(user_id, path_id, plan, completed_days)

def show_daily_plan_details(user_id: str, path_id: str, plan: dict, completed_days: dict):
    """Show detailed view of a daily plan"""
    day = plan.get('day', 1)
    
    st.markdown(f"""
    <div class="feature-card">
        <h3>Day {day}: {plan.get('title', 'Learning Day')}</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Plan details
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Learning Objectives")
        objectives = plan.get('objectives', [])
        for i, obj in enumerate(objectives, 1):
            st.write(f"{i}. {obj}")
        
        st.subheader("📝 Activities")
        activities = plan.get('activities', [])
        for i, activity in enumerate(activities, 1):
            st.write(f"{i}. {activity}")
    
    with col2:
        st.subheader("🔑 Key Concepts")
        concepts = plan.get('key_concepts', [])
        for concept in concepts:
            st.write(f"• {concept}")
        
        st.subheader("📚 Resources")
        resources = plan.get('resources', [])
        for resource in resources:
            st.write(f"• {resource}")
    
    # Content
    st.subheader("📖 Learning Content")
    content = plan.get('content', 'No content available')
    st.write(content)
    
    # Multimedia content
    if plan.get('recommended_videos'):
        st.subheader("🎥 Recommended Videos")
        videos = plan.get('recommended_videos', [])
        
        cols = st.columns(min(3, len(videos)))
        for i, video in enumerate(videos[:3]):
            with cols[i]:
                st.markdown(f"""
                <div class="feature-card">
                    <h5>{video.get('title', 'Video')}</h5>
                    <p>{video.get('channel', 'Unknown Channel')}</p>
                    <a href="{video.get('url', '#')}" target="_blank">🎥 Watch Video</a>
                </div>
                """, unsafe_allow_html=True)
    
    # Audio content
    if plan.get('audio_available'):
        st.subheader("🎧 Audio Content")
        st.info(f"🔊 Audio version available (Duration: {plan.get('audio_duration', '5m')})")
        
        if st.button("🎵 Generate Audio", key=f"audio_{day}"):
            with st.spinner("Generating audio..."):
                audio_data = elevenlabs_client.create_audio_for_daily_plan(plan)
                if audio_data:
                    st.success("Audio generated successfully!")
                    # In a real implementation, you'd provide audio playback here

def show_analytics(user_id: str):
    """Show analytics dashboard"""
    st.markdown("""
    <div class="main-header">
        <h1>📊 Learning Analytics</h1>
        <p>Insights into your learning journey</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get analytics data
    analytics = learning_service.get_learning_analytics(user_id)
    learning_paths = learning_service.get_user_learning_paths(user_id)
    
    if not learning_paths:
        st.info("📈 Start learning to see your analytics!")
        return
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Paths", analytics.get('total_paths', 0))
    with col2:
        st.metric("Completed", analytics.get('completed_paths', 0))
    with col3:
        st.metric("Days Studied", analytics.get('total_days_studied', 0))
    with col4:
        st.metric("Avg. Completion", f"{analytics.get('average_completion_rate', 0):.1f}%")
    
    # Progress over time
    st.subheader("📈 Progress Over Time")
    
    # Create progress data
    progress_data = []
    for path in learning_paths:
        progress = path.get('progress', {})
        completed_days = progress.get('completed_days', {})
        
        for day_str, completed in completed_days.items():
            if completed:
                progress_data.append({
                    'Date': datetime.now() - timedelta(days=int(day_str)),
                    'Path': path.get('goal', 'Unknown'),
                    'Day': int(day_str),
                    'Completed': 1
                })
    
    if progress_data:
        df = pd.DataFrame(progress_data)
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Daily completion chart
        daily_completion = df.groupby('Date')['Completed'].sum().reset_index()
        
        fig = px.line(
            daily_completion, 
            x='Date', 
            y='Completed',
            title='Daily Learning Activity',
            labels={'Completed': 'Days Completed', 'Date': 'Date'}
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Learning path breakdown
        st.subheader("📚 Learning Path Breakdown")
        
        path_data = []
        for path in learning_paths:
            path_data.append({
                'Goal': path.get('goal', 'Unknown'),
                'Progress': path.get('completion_percentage', 0),
                'Type': path.get('type', 'normal').upper(),
                'Difficulty': path.get('difficulty', 'unknown').title()
            })
        
        df_paths = pd.DataFrame(path_data)
        
        # Progress by path
        fig = px.bar(
            df_paths,
            x='Goal',
            y='Progress',
            color='Type',
            title='Progress by Learning Path',
            labels={'Progress': 'Completion %'}
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Difficulty distribution
        col1, col2 = st.columns(2)
        
        with col1:
            difficulty_counts = df_paths['Difficulty'].value_counts()
            fig = px.pie(
                values=difficulty_counts.values,
                names=difficulty_counts.index,
                title='Learning Paths by Difficulty'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            type_counts = df_paths['Type'].value_counts()
            fig = px.pie(
                values=type_counts.values,
                names=type_counts.index,
                title='Learning Paths by Type'
            )
            st.plotly_chart(fig, use_container_width=True)

def show_notifications(user_id: str):
    """Show notifications management"""
    st.markdown("""
    <div class="main-header">
        <h1>🔔 Notification Center</h1>
        <p>Manage your learning reminders and notifications</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["⚙️ Setup Reminders", "📱 Test Notifications", "📋 History"])
    
    with tab1:
        show_notification_setup(user_id)
    
    with tab2:
        show_notification_test()
    
    with tab3:
        show_notification_history(user_id)

def show_notification_setup(user_id: str, path_id: str = None):
    """Show notification setup"""
    st.subheader("⚙️ Setup Learning Reminders")
    
    # Get user's learning paths
    learning_paths = learning_service.get_user_learning_paths(user_id)
    
    if not learning_paths:
        st.info("Create a learning path first to set up reminders!")
        return
    
    with st.form("notification_setup"):
        # Select learning path
        if path_id:
            selected_path = next((p for p in learning_paths if p.get('id') == path_id), None)
            st.info(f"Setting up reminders for: {selected_path.get('goal', 'Unknown') if selected_path else 'Unknown'}")
        else:
            path_options = {p.get('goal', f"Path {i}"): p.get('id', '') for i, p in enumerate(learning_paths)}
            selected_goal = st.selectbox("Select Learning Path", list(path_options.keys()))
            path_id = path_options.get(selected_goal, '')
        
        col1, col2 = st.columns(2)
        
        with col1:
            phone_number = st.text_input(
                "Phone Number",
                placeholder="+1234567890",
                help="Include country code (e.g., +1 for US)"
            )
            
            notification_method = st.selectbox(
                "Notification Method",
                ["sms", "whatsapp", "voice"],
                format_func=lambda x: {"sms": "📱 SMS", "whatsapp": "💬 WhatsApp", "voice": "📞 Voice Call"}[x]
            )
        
        with col2:
            reminder_time = st.time_input(
                "Reminder Time",
                value=datetime.strptime("09:00", "%H:%M").time(),
                help="When should we send daily reminders?"
            )
            
            days_to_remind = st.multiselect(
                "Days to Send Reminders",
                ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                default=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            )
        
        if st.form_submit_button("🔔 Setup Reminders", use_container_width=True):
            if not phone_number:
                st.error("Please enter a phone number")
            elif not validate_phone_number(phone_number):
                st.error("Please enter a valid phone number with country code")
            elif not days_to_remind:
                st.error("Please select at least one day for reminders")
            else:
                reminder_settings = {
                    'phone_number': phone_number,
                    'method': notification_method,
                    'time': reminder_time.strftime("%H:%M"),
                    'days': [i for i, day in enumerate(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]) if day in days_to_remind]
                }
                
                success = notification_service.schedule_learning_reminder(user_id, path_id, reminder_settings)
                if success:
                    st.success("🎉 Reminders set up successfully!")
                    st.balloons()

def show_notification_test():
    """Show notification testing"""
    st.subheader("📱 Test Your Notifications")
    
    with st.form("test_notification"):
        col1, col2 = st.columns(2)
        
        with col1:
            test_phone = st.text_input(
                "Phone Number",
                placeholder="+1234567890",
                help="Include country code"
            )
        
        with col2:
            test_method = st.selectbox(
                "Test Method",
                ["sms", "whatsapp", "voice"],
                format_func=lambda x: {"sms": "📱 SMS", "whatsapp": "💬 WhatsApp", "voice": "📞 Voice Call"}[x]
            )
        
        if st.form_submit_button("🧪 Send Test Notification", use_container_width=True):
            if not test_phone:
                st.error("Please enter a phone number")
            elif not validate_phone_number(test_phone):
                st.error("Please enter a valid phone number")
            else:
                with st.spinner("Sending test notification..."):
                    success = notification_service.test_notification(test_phone, test_method)
                    if success:
                        st.success("✅ Test notification sent successfully!")
                    else:
                        st.error("❌ Failed to send test notification")

def show_notification_history(user_id: str):
    """Show notification history"""
    st.subheader("📋 Notification History")
    
    history = notification_service.get_notification_history(user_id)
    
    if not history:
        st.info("No notification history available yet.")
        return
    
    for notification in history:
        with st.container():
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"**{notification.get('type', 'Unknown').title()}** - {notification.get('path_goal', 'Unknown Path')}")
            
            with col2:
                method_icon = {"sms": "📱", "whatsapp": "💬", "voice": "📞"}.get(notification.get('method', ''), "📧")
                st.write(f"{method_icon} {notification.get('method', 'Unknown').upper()}")
            
            with col3:
                sent_at = notification.get('sent_at', datetime.now())
                st.write(format_date_relative(sent_at))

def show_settings(user_id: str):
    """Show settings page"""
    st.markdown("""
    <div class="main-header">
        <h1>⚙️ Settings</h1>
        <p>Customize your learning experience</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["👤 Profile", "🔧 Preferences", "🔗 Integrations"])
    
    with tab1:
        show_profile_settings(user_id)
    
    with tab2:
        show_preference_settings(user_id)
    
    with tab3:
        show_integration_settings()

def show_profile_settings(user_id: str):
    """Show profile settings"""
    st.subheader("👤 Profile Settings")
    
    user = st.session_state.get('user', {})
    
    with st.form("profile_settings"):
        name = st.text_input("Full Name", value=user.get('name', ''))
        email = st.text_input("Email", value=user.get('email', ''), disabled=True)
        
        # Learning preferences
        st.subheader("🎯 Learning Preferences")
        
        col1, col2 = st.columns(2)
        with col1:
            preferred_difficulty = st.selectbox(
                "Preferred Difficulty",
                ["beginner", "intermediate", "advanced", "expert"],
                index=0
            )
            
            preferred_duration = st.slider(
                "Preferred Path Duration (days)",
                min_value=3,
                max_value=30,
                value=14
            )
        
        with col2:
            learning_style = st.selectbox(
                "Learning Style",
                ["visual", "auditory", "kinesthetic", "mixed"],
                index=3
            )
            
            daily_time = st.selectbox(
                "Available Daily Time",
                ["30 minutes", "1 hour", "2 hours", "3+ hours"],
                index=1
            )
        
        if st.form_submit_button("💾 Save Profile", use_container_width=True):
            # In a real implementation, you'd save these settings
            st.success("Profile updated successfully!")

def show_preference_settings(user_id: str):
    """Show preference settings"""
    st.subheader("🔧 Preferences")
    
    with st.form("preferences"):
        # Notification preferences
        st.subheader("🔔 Notification Preferences")
        
        enable_notifications = st.checkbox("Enable Notifications", value=True)
        enable_email_notifications = st.checkbox("Email Notifications", value=True)
        enable_push_notifications = st.checkbox("Push Notifications", value=True)
        
        # Content preferences
        st.subheader("📚 Content Preferences")
        
        col1, col2 = st.columns(2)
        with col1:
            include_videos = st.checkbox("Include YouTube Videos", value=True)
            include_audio = st.checkbox("Generate Audio Content", value=True)
        
        with col2:
            include_practice = st.checkbox("Include Practice Exercises", value=True)
            include_projects = st.checkbox("Include Projects", value=True)
        
        # AI preferences
        st.subheader("🤖 AI Preferences")
        
        ai_creativity = st.slider(
            "AI Creativity Level",
            min_value=0.1,
            max_value=1.0,
            value=0.7,
            help="Higher values make AI more creative but less predictable"
        )
        
        prefer_mcp = st.checkbox(
            "Prefer MCP (Adaptive) Paths",
            value=False,
            help="Use adaptive learning paths by default"
        )
        
        if st.form_submit_button("💾 Save Preferences", use_container_width=True):
            st.success("Preferences saved successfully!")

def show_integration_settings():
    """Show integration settings"""
    st.subheader("🔗 Integration Status")
    
    # API status indicators
    integrations = [
        ("🤖 Google Gemini AI", settings.GEMINI_API_KEY != "demo_key", "AI-powered learning path generation"),
        ("🎥 YouTube API", settings.YOUTUBE_API_KEY != "demo_key", "Curated video recommendations"),
        ("🔊 ElevenLabs TTS", settings.ELEVENLABS_API_KEY != "demo_key", "Text-to-speech audio generation"),
        ("📱 Twilio SMS/Voice", settings.TWILIO_ACCOUNT_SID != "demo_sid", "SMS, WhatsApp, and voice reminders"),
        ("☁️ Firebase", not settings.is_demo_mode, "User authentication and data storage"),
        ("📄 Google Drive", settings.GOOGLE_CLIENT_ID != "demo_client_id", "Document creation and storage")
    ]
    
    for name, is_configured, description in integrations:
        col1, col2, col3 = st.columns([2, 1, 3])
        
        with col1:
            st.write(f"**{name}**")
        
        with col2:
            if is_configured:
                st.success("✅ Active")
            else:
                st.warning("🔧 Demo Mode")
        
        with col3:
            st.write(description)
    
    if settings.is_demo_mode:
        st.info("""
        🚀 **Demo Mode Active**
        
        The application is running in demo mode with full functionality. 
        To enable real integrations, configure the following environment variables:
        
        - `GEMINI_API_KEY`: Google Gemini API key
        - `YOUTUBE_API_KEY`: YouTube Data API v3 key
        - `ELEVENLABS_API_KEY`: ElevenLabs API key
        - `TWILIO_ACCOUNT_SID` & `TWILIO_AUTH_TOKEN`: Twilio credentials
        - Firebase configuration variables
        """)

if __name__ == "__main__":
    main()