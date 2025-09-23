import hashlib
import secrets
import string
import re
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
import streamlit as st

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone_number(phone: str) -> bool:
    """Validate phone number format"""
    # Remove all non-digit characters
    cleaned = re.sub(r'\D', '', phone)
    # Check if it's a valid length (10-15 digits)
    return 10 <= len(cleaned) <= 15

def hash_password(password: str) -> str:
    """Hash password using SHA-256 with salt"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{password_hash}"

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    try:
        salt, password_hash = hashed.split(':')
        return hashlib.sha256((password + salt).encode()).hexdigest() == password_hash
    except ValueError:
        return False

def generate_secure_token(length: int = 32) -> str:
    """Generate a secure random token"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent injection attacks"""
    if not isinstance(text, str):
        return str(text)

    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&', '%', ';', '(', ')', '+', 'script']
    for char in dangerous_chars:
        text = text.replace(char, '')

    return text.strip()

def format_duration(seconds: float) -> str:
    """Format duration in seconds to readable format"""
    if seconds < 60:
        return f"{seconds:.0f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"

def calculate_reading_time(text: str, words_per_minute: int = 200) -> int:
    """Calculate estimated reading time in minutes"""
    word_count = len(text.split())
    reading_time = max(1, word_count // words_per_minute)
    return reading_time

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def format_progress_percentage(completed: int, total: int) -> float:
    """Calculate and format progress percentage"""
    if total == 0:
        return 0.0
    return round((completed / total) * 100, 1)

def get_difficulty_color(difficulty: str) -> str:
    """Get color code for difficulty level"""
    colors = {
        'beginner': '#4CAF50',    # Green
        'intermediate': '#FF9800', # Orange
        'advanced': '#F44336',     # Red
        'expert': '#9C27B0'        # Purple
    }
    return colors.get(difficulty.lower(), '#757575')  # Default gray

def format_date_relative(date: datetime) -> str:
    """Format date as relative time (e.g., '2 days ago')"""
    if not isinstance(date, datetime):
        return "Unknown"

    now = datetime.now(timezone.utc)
    if date.tzinfo is None:
        date = date.replace(tzinfo=timezone.utc)

    diff = now - date

    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    else:
        return "Just now"

def create_progress_bar_html(percentage: float, color: str = "#4CAF50") -> str:
    """Create HTML progress bar"""
    return f"""
    <div style="background-color: #f0f0f0; border-radius: 10px; overflow: hidden; height: 20px;">
        <div style="background-color: {color}; height: 100%; width: {percentage}%;
                    transition: width 0.3s ease-in-out; border-radius: 10px;
                    display: flex; align-items: center; justify-content: center;
                    color: white; font-size: 12px; font-weight: bold;">
            {percentage:.1f}%
        </div>
    </div>
    """

def display_success_message(message: str):
    """Display success message with styling"""
    st.success(f"✅ {message}")

def display_error_message(message: str):
    """Display error message with styling"""
    st.error(f"❌ {message}")

def display_warning_message(message: str):
    """Display warning message with styling"""
    st.warning(f"⚠️ {message}")

def display_info_message(message: str):
    """Display info message with styling"""
    st.info(f"ℹ️ {message}")

def create_metric_card(title: str, value: str, delta: Optional[str] = None) -> None:
    """Create a metric card display"""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.metric(label=title, value=value, delta=delta)

def safe_get_nested_value(data: Dict[str, Any], keys: List[str], default: Any = None) -> Any:
    """Safely get nested dictionary value"""
    try:
        result = data
        for key in keys:
            result = result[key]
        return result
    except (KeyError, TypeError):
        return default

def format_learning_stats(stats: Dict[str, Any]) -> Dict[str, str]:
    """Format learning statistics for display"""
    return {
        'Total Paths': str(stats.get('total_paths', 0)),
        'Completed': str(stats.get('completed_paths', 0)),
        'In Progress': str(stats.get('active_paths', 0)),
        'Avg. Completion': f"{stats.get('average_completion_rate', 0):.1f}%",
        'Total Study Time': format_duration(stats.get('total_study_time', 0)),
        'Streak Days': str(stats.get('streak_days', 0))
    }

def generate_color_palette(count: int) -> List[str]:
    """Generate a color palette for charts"""
    colors = [
        '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57',
        '#FF9FF3', '#54A0FF', '#5F27CD', '#00D2D3', '#FF9F43',
        '#10AC84', '#EE5A24', '#0984E3', '#6C5CE7', '#FDCB6E'
    ]

    if count <= len(colors):
        return colors[:count]

    # If we need more colors, generate additional ones
    extra_colors = []
    for i in range(count - len(colors)):
        # Generate colors based on HSL
        hue = (i * 137.5) % 360  # Golden angle approximation
        extra_colors.append(f"hsl({hue}, 70%, 60%)")

    return colors + extra_colors

def validate_learning_goal(goal: str) -> bool:
    """Validate learning goal input"""
    if not goal or len(goal.strip()) < 3:
        return False

    # Check for meaningful content
    words = goal.strip().split()
    return len(words) >= 2 and len(goal.strip()) <= 200

def estimate_learning_duration(goal: str, difficulty: str) -> Dict[str, int]:
    """Estimate appropriate learning duration based on goal and difficulty"""
    base_days = {
        'beginner': 7,
        'intermediate': 14,
        'advanced': 21,
        'expert': 30
    }

    goal_lower = goal.lower()
    complexity_indicators = ['programming', 'development', 'advanced', 'professional', 'certification']

    multiplier = 1.0
    for indicator in complexity_indicators:
        if indicator in goal_lower:
            multiplier = 1.5
            break

    base = base_days.get(difficulty.lower(), 14)
    estimated = int(base * multiplier)

    return {
        'min_days': max(3, estimated - 5),
        'recommended_days': estimated,
        'max_days': min(90, estimated + 10)
    }

class SessionState:
    """Manage session state for Streamlit apps"""

    @staticmethod
    def get_user_session() -> Dict[str, Any]:
        """Get current user session data"""
        if 'user_session' not in st.session_state:
            st.session_state.user_session = {
                'authenticated': False,
                'user_id': None,
                'user_email': None,
                'login_time': None
            }
        return st.session_state.user_session

    @staticmethod
    def set_user_session(user_id: str, email: str):
        """Set user session data"""
        st.session_state.user_session = {
            'authenticated': True,
            'user_id': user_id,
            'user_email': email,
            'login_time': datetime.now()
        }

    @staticmethod
    def clear_user_session():
        """Clear user session data"""
        st.session_state.user_session = {
            'authenticated': False,
            'user_id': None,
            'user_email': None,
            'login_time': None
        }

    @staticmethod
    def is_authenticated() -> bool:
        """Check if user is authenticated"""
        session = SessionState.get_user_session()
        return session.get('authenticated', False)

    @staticmethod
    def get_user_id() -> Optional[str]:
        """Get current user ID"""
        session = SessionState.get_user_session()
        return session.get('user_id')

    @staticmethod
    def get_user_email() -> Optional[str]:
        """Get current user email"""
        session = SessionState.get_user_session()
        return session.get('user_email')

def create_download_link(content: str, filename: str, mime_type: str = "text/plain") -> str:
    """Create a download link for content"""
    import base64

    b64 = base64.b64encode(content.encode()).decode()
    return f'<a href="data:{mime_type};base64,{b64}" download="{filename}">📥 Download {filename}</a>'

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"

def get_user_timezone() -> str:
    """Get user's timezone (simplified - you might want to use a more sophisticated method)"""
    # This is a simplified version - in a real app you might use JavaScript or IP geolocation
    return "UTC"

def schedule_notification_time(base_time: str, timezone: str = "UTC") -> datetime:
    """Calculate notification time in user's timezone"""
    # Parse base time (e.g., "09:00")
    hour, minute = map(int, base_time.split(':'))

    # Create datetime object for today at specified time
    now = datetime.now()
    scheduled_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

    # If the time has already passed today, schedule for tomorrow
    if scheduled_time <= now:
        scheduled_time = scheduled_time + timedelta(days=1)

    return scheduled_time
