"""
Utility Functions for Infinity Kingdom Bot
"""

import time
import random
import math
from typing import Tuple, List, Optional
from datetime import datetime, timedelta


def random_delay(min_seconds: float = 0.1, max_seconds: float = 0.5) -> float:
    """
    Generate a random delay and sleep for that duration
    
    Args:
        min_seconds: Minimum delay
        max_seconds: Maximum delay
    
    Returns:
        The actual delay used
    """
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)
    return delay


def random_offset(base_x: int, base_y: int, max_offset: int = 5) -> Tuple[int, int]:
    """
    Add random offset to coordinates for more human-like behavior
    
    Args:
        base_x, base_y: Original coordinates
        max_offset: Maximum pixel offset
    
    Returns:
        Tuple of (x, y) with random offset
    """
    offset_x = random.randint(-max_offset, max_offset)
    offset_y = random.randint(-max_offset, max_offset)
    return (base_x + offset_x, base_y + offset_y)


def calculate_distance(x1: int, y1: int, x2: int, y2: int) -> float:
    """Calculate distance between two points"""
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)


def relative_to_absolute(
    rel_x: float,
    rel_y: float,
    width: int,
    height: int
) -> Tuple[int, int]:
    """
    Convert relative coordinates (0-1) to absolute pixel coordinates
    
    Args:
        rel_x, rel_y: Relative coordinates (0.0 to 1.0)
        width, height: Screen dimensions
    
    Returns:
        Absolute (x, y) coordinates
    """
    return (int(rel_x * width), int(rel_y * height))


def absolute_to_relative(
    x: int,
    y: int,
    width: int,
    height: int
) -> Tuple[float, float]:
    """
    Convert absolute pixel coordinates to relative (0-1)
    
    Args:
        x, y: Absolute pixel coordinates
        width, height: Screen dimensions
    
    Returns:
        Relative (x, y) coordinates
    """
    return (x / width, y / height)


def format_duration(seconds: int) -> str:
    """
    Format seconds into human-readable duration
    
    Args:
        seconds: Duration in seconds
    
    Returns:
        Formatted string like "2h 30m 15s"
    """
    if seconds < 60:
        return f"{seconds}s"
    
    minutes, secs = divmod(seconds, 60)
    hours, mins = divmod(minutes, 60)
    days, hrs = divmod(hours, 24)
    
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hrs > 0:
        parts.append(f"{hrs}h")
    if mins > 0:
        parts.append(f"{mins}m")
    if secs > 0 and days == 0:  # Skip seconds for long durations
        parts.append(f"{secs}s")
    
    return " ".join(parts)


def parse_duration(duration_str: str) -> int:
    """
    Parse duration string to seconds
    
    Args:
        duration_str: String like "2h30m" or "1d 5h"
    
    Returns:
        Duration in seconds
    """
    import re
    
    total = 0
    
    # Match patterns like "2d", "5h", "30m", "45s"
    patterns = [
        (r'(\d+)d', 86400),   # days
        (r'(\d+)h', 3600),    # hours
        (r'(\d+)m', 60),      # minutes
        (r'(\d+)s', 1),       # seconds
    ]
    
    for pattern, multiplier in patterns:
        match = re.search(pattern, duration_str)
        if match:
            total += int(match.group(1)) * multiplier
    
    return total


def format_number(num: int) -> str:
    """
    Format large numbers with K/M/B suffixes
    
    Args:
        num: Number to format
    
    Returns:
        Formatted string like "1.5M"
    """
    if num >= 1_000_000_000:
        return f"{num / 1_000_000_000:.1f}B"
    elif num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.1f}K"
    else:
        return str(num)


def time_until(target_time: datetime) -> timedelta:
    """Get timedelta until a target time"""
    return target_time - datetime.now()


def has_passed(target_time: datetime) -> bool:
    """Check if target time has passed"""
    return datetime.now() >= target_time


def get_daily_reset_time(reset_hour: int = 0) -> datetime:
    """
    Get the next daily reset time
    
    Args:
        reset_hour: Hour of daily reset (0-23)
    
    Returns:
        Datetime of next reset
    """
    now = datetime.now()
    today_reset = now.replace(hour=reset_hour, minute=0, second=0, microsecond=0)
    
    if now >= today_reset:
        return today_reset + timedelta(days=1)
    return today_reset


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp a value between min and max"""
    return max(min_val, min(max_val, value))


def lerp(start: float, end: float, t: float) -> float:
    """Linear interpolation between two values"""
    return start + (end - start) * clamp(t, 0, 1)


def ease_in_out(t: float) -> float:
    """Ease in-out interpolation (smooth start and end)"""
    if t < 0.5:
        return 2 * t * t
    else:
        return 1 - pow(-2 * t + 2, 2) / 2


def generate_bezier_path(
    start: Tuple[int, int],
    end: Tuple[int, int],
    control_points: int = 2,
    steps: int = 20
) -> List[Tuple[int, int]]:
    """
    Generate a bezier curve path between two points
    Useful for more natural mouse movements
    
    Args:
        start: Starting point
        end: Ending point
        control_points: Number of random control points
        steps: Number of points in the path
    
    Returns:
        List of (x, y) points along the curve
    """
    points = [start]
    
    # Generate random control points
    for _ in range(control_points):
        cx = random.randint(
            min(start[0], end[0]),
            max(start[0], end[0])
        )
        cy = random.randint(
            min(start[1], end[1]),
            max(start[1], end[1])
        )
        points.append((cx, cy))
    
    points.append(end)
    
    # Generate path using de Casteljau's algorithm
    path = []
    for i in range(steps + 1):
        t = i / steps
        point = _bezier_point(points, t)
        path.append((int(point[0]), int(point[1])))
    
    return path


def _bezier_point(
    control_points: List[Tuple[int, int]],
    t: float
) -> Tuple[float, float]:
    """Calculate a point on a bezier curve"""
    points = list(control_points)
    
    while len(points) > 1:
        new_points = []
        for i in range(len(points) - 1):
            x = lerp(points[i][0], points[i+1][0], t)
            y = lerp(points[i][1], points[i+1][1], t)
            new_points.append((x, y))
        points = new_points
    
    return points[0]


class RetryHandler:
    """
    Utility class for retry logic
    """
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        exponential: bool = True
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.exponential = exponential
        self.current_retry = 0
    
    def should_retry(self) -> bool:
        """Check if we should retry"""
        return self.current_retry < self.max_retries
    
    def wait_and_increment(self):
        """Wait for appropriate delay and increment counter"""
        if self.exponential:
            delay = self.base_delay * (2 ** self.current_retry)
        else:
            delay = self.base_delay
        
        # Add some randomness
        delay *= random.uniform(0.8, 1.2)
        
        time.sleep(delay)
        self.current_retry += 1
    
    def reset(self):
        """Reset retry counter"""
        self.current_retry = 0


class RateLimiter:
    """
    Simple rate limiter to prevent too many actions
    """
    
    def __init__(self, max_actions: int, period_seconds: float):
        self.max_actions = max_actions
        self.period = period_seconds
        self.actions: List[datetime] = []
    
    def can_act(self) -> bool:
        """Check if action is allowed"""
        self._cleanup_old()
        return len(self.actions) < self.max_actions
    
    def record_action(self):
        """Record an action"""
        self.actions.append(datetime.now())
    
    def _cleanup_old(self):
        """Remove old actions outside the period"""
        cutoff = datetime.now() - timedelta(seconds=self.period)
        self.actions = [a for a in self.actions if a > cutoff]
    
    def wait_if_needed(self):
        """Wait until we can act"""
        while not self.can_act():
            time.sleep(0.1)
