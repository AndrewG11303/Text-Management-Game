import time
import random
import math

def random_sleep(base_seconds, variance=0.5):
    """
    Sleeps for base_seconds +/- a random variance.
    """
    actual_sleep = base_seconds + random.uniform(-variance, variance)
    if actual_sleep < 0:
        actual_sleep = 0.1
    time.sleep(actual_sleep)

def randomize_coordinate(x, y, radius=5):
    """
    Returns a coordinate slightly offset from (x, y) by a random amount within radius.
    """
    offset_x = random.randint(-radius, radius)
    offset_y = random.randint(-radius, radius)
    return (x + offset_x, y + offset_y)

def distance(p1, p2):
    """
    Calculates Euclidean distance between two points (x1, y1) and (x2, y2).
    """
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def timestamp():
    """Returns current timestamp as string."""
    return time.strftime("%Y-%m-%d %H:%M:%S")
