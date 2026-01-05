"""
Task Scheduler Module for Infinity Kingdom Bot
Handles scheduling and execution of automated tasks
"""

import time
import random
from typing import Callable, Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
import threading
from queue import PriorityQueue
import heapq

from src.logger import get_logger


class TaskPriority(Enum):
    """Task priority levels"""
    CRITICAL = 0  # Safety tasks (react to attacks)
    HIGH = 1      # Time-sensitive (collect rewards before reset)
    NORMAL = 2    # Regular tasks (resource collection)
    LOW = 3       # Background tasks (optimization)
    IDLE = 4      # Only when nothing else to do


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()
    PAUSED = auto()


@dataclass(order=True)
class ScheduledTask:
    """Represents a scheduled task"""
    # For priority queue ordering
    next_run: datetime = field(compare=True)
    priority: int = field(compare=True, default=TaskPriority.NORMAL.value)
    
    # Task details (not used for comparison)
    task_id: str = field(compare=False, default="")
    name: str = field(compare=False, default="")
    callback: Callable = field(compare=False, default=None)
    args: tuple = field(compare=False, default_factory=tuple)
    kwargs: dict = field(compare=False, default_factory=dict)
    
    # Scheduling options
    interval_seconds: Optional[int] = field(compare=False, default=None)
    repeat: bool = field(compare=False, default=False)
    max_retries: int = field(compare=False, default=3)
    
    # State
    status: TaskStatus = field(compare=False, default=TaskStatus.PENDING)
    last_run: Optional[datetime] = field(compare=False, default=None)
    run_count: int = field(compare=False, default=0)
    fail_count: int = field(compare=False, default=0)
    
    def should_run(self) -> bool:
        """Check if task should run now"""
        return (
            self.status == TaskStatus.PENDING and
            datetime.now() >= self.next_run
        )
    
    def reschedule(self):
        """Reschedule for next run"""
        if self.repeat and self.interval_seconds:
            self.next_run = datetime.now() + timedelta(seconds=self.interval_seconds)
            self.status = TaskStatus.PENDING


class TaskScheduler:
    """
    Manages task scheduling and execution
    Uses priority queue for efficient task ordering
    """
    
    def __init__(self, config: dict):
        self.config = config
        self.logger = get_logger()
        
        # Task storage
        self.tasks: Dict[str, ScheduledTask] = {}
        self.task_queue: List[ScheduledTask] = []  # heap queue
        
        # Timing configuration
        timing = config.get('timing', {})
        self.min_task_interval = timing.get('action_delay', 1.0)
        
        # Control flags
        self.running = False
        self.paused = False
        
        # Statistics
        self.stats = {
            'tasks_executed': 0,
            'tasks_failed': 0,
            'total_runtime': timedelta(0)
        }
        
        # Callbacks
        self.on_task_complete: Optional[Callable] = None
        self.on_task_error: Optional[Callable] = None
        self.on_all_complete: Optional[Callable] = None
    
    def add_task(
        self,
        task_id: str,
        name: str,
        callback: Callable,
        priority: TaskPriority = TaskPriority.NORMAL,
        delay_seconds: int = 0,
        interval_seconds: Optional[int] = None,
        repeat: bool = False,
        args: tuple = (),
        kwargs: dict = None
    ) -> ScheduledTask:
        """
        Add a new task to the scheduler
        
        Args:
            task_id: Unique identifier for the task
            name: Human-readable task name
            callback: Function to execute
            priority: Task priority level
            delay_seconds: Initial delay before first run
            interval_seconds: Interval for repeating tasks
            repeat: Whether to repeat the task
            args: Positional arguments for callback
            kwargs: Keyword arguments for callback
        
        Returns:
            The created ScheduledTask
        """
        if kwargs is None:
            kwargs = {}
        
        task = ScheduledTask(
            task_id=task_id,
            name=name,
            callback=callback,
            priority=priority.value,
            next_run=datetime.now() + timedelta(seconds=delay_seconds),
            interval_seconds=interval_seconds,
            repeat=repeat,
            args=args,
            kwargs=kwargs
        )
        
        self.tasks[task_id] = task
        heapq.heappush(self.task_queue, task)
        
        self.logger.debug(f"Task added: {name} (priority={priority.name})")
        return task
    
    def add_recurring_task(
        self,
        task_id: str,
        name: str,
        callback: Callable,
        interval_minutes: int,
        priority: TaskPriority = TaskPriority.NORMAL,
        **kwargs
    ) -> ScheduledTask:
        """
        Convenience method to add a recurring task
        """
        return self.add_task(
            task_id=task_id,
            name=name,
            callback=callback,
            priority=priority,
            interval_seconds=interval_minutes * 60,
            repeat=True,
            **kwargs
        )
    
    def remove_task(self, task_id: str) -> bool:
        """Remove a task from the scheduler"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.status = TaskStatus.CANCELLED
            del self.tasks[task_id]
            self.logger.debug(f"Task removed: {task.name}")
            return True
        return False
    
    def pause_task(self, task_id: str) -> bool:
        """Pause a specific task"""
        if task_id in self.tasks:
            self.tasks[task_id].status = TaskStatus.PAUSED
            return True
        return False
    
    def resume_task(self, task_id: str) -> bool:
        """Resume a paused task"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            if task.status == TaskStatus.PAUSED:
                task.status = TaskStatus.PENDING
                task.next_run = datetime.now()
                return True
        return False
    
    def get_next_task(self) -> Optional[ScheduledTask]:
        """Get the next task that should be executed"""
        while self.task_queue:
            task = self.task_queue[0]
            
            # Skip cancelled or paused tasks
            if task.status in [TaskStatus.CANCELLED, TaskStatus.PAUSED]:
                heapq.heappop(self.task_queue)
                continue
            
            # Check if task should run
            if task.should_run():
                return heapq.heappop(self.task_queue)
            else:
                # Task not ready yet
                break
        
        return None
    
    def execute_task(self, task: ScheduledTask) -> bool:
        """
        Execute a single task
        
        Returns:
            True if task completed successfully
        """
        if task.status == TaskStatus.CANCELLED:
            return False
        
        task.status = TaskStatus.RUNNING
        task.last_run = datetime.now()
        task.run_count += 1
        
        self.logger.task(f"Executing: {task.name}")
        
        start_time = time.time()
        success = False
        
        try:
            # Execute the callback
            result = task.callback(*task.args, **task.kwargs)
            success = result is not False
            
            if success:
                task.status = TaskStatus.COMPLETED
                task.fail_count = 0
                self.stats['tasks_executed'] += 1
                self.logger.success(f"Completed: {task.name}")
            else:
                raise Exception("Task returned False")
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.fail_count += 1
            self.stats['tasks_failed'] += 1
            self.logger.error(f"Task failed: {task.name} - {e}")
            
            # Trigger error callback
            if self.on_task_error:
                self.on_task_error(task, e)
            
            # Retry logic
            if task.fail_count < task.max_retries:
                self.logger.info(f"Will retry {task.name} ({task.fail_count}/{task.max_retries})")
                task.status = TaskStatus.PENDING
                task.next_run = datetime.now() + timedelta(seconds=30)
        
        finally:
            # Record runtime
            runtime = time.time() - start_time
            self.stats['total_runtime'] += timedelta(seconds=runtime)
            
            # Reschedule if repeating
            if task.repeat and success:
                task.reschedule()
                heapq.heappush(self.task_queue, task)
            
            # Trigger completion callback
            if success and self.on_task_complete:
                self.on_task_complete(task)
        
        return success
    
    def run_once(self) -> bool:
        """
        Run one iteration of the scheduler
        Execute the next due task if any
        
        Returns:
            True if a task was executed
        """
        if self.paused:
            return False
        
        task = self.get_next_task()
        if task:
            self.execute_task(task)
            return True
        
        return False
    
    def run(self, duration_seconds: Optional[int] = None):
        """
        Run the scheduler continuously
        
        Args:
            duration_seconds: Maximum runtime (None = indefinite)
        """
        self.running = True
        start_time = datetime.now()
        
        self.logger.info("Task scheduler started")
        
        try:
            while self.running:
                # Check duration limit
                if duration_seconds:
                    elapsed = (datetime.now() - start_time).total_seconds()
                    if elapsed >= duration_seconds:
                        self.logger.info("Scheduler duration limit reached")
                        break
                
                # Run next task
                task_executed = self.run_once()
                
                if not task_executed:
                    # No tasks ready, sleep briefly
                    time.sleep(0.5)
                else:
                    # Brief pause between tasks
                    time.sleep(self.min_task_interval)
                
        except KeyboardInterrupt:
            self.logger.info("Scheduler interrupted by user")
        finally:
            self.running = False
            
            if self.on_all_complete:
                self.on_all_complete()
    
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        self.logger.info("Scheduler stopped")
    
    def pause(self):
        """Pause all task execution"""
        self.paused = True
        self.logger.info("Scheduler paused")
    
    def resume(self):
        """Resume task execution"""
        self.paused = False
        self.logger.info("Scheduler resumed")
    
    def get_pending_tasks(self) -> List[ScheduledTask]:
        """Get all pending tasks sorted by next run time"""
        pending = [
            t for t in self.tasks.values()
            if t.status == TaskStatus.PENDING
        ]
        return sorted(pending, key=lambda t: t.next_run)
    
    def get_status(self) -> Dict[str, Any]:
        """Get scheduler status"""
        return {
            'running': self.running,
            'paused': self.paused,
            'total_tasks': len(self.tasks),
            'pending_tasks': len([t for t in self.tasks.values() if t.status == TaskStatus.PENDING]),
            'stats': self.stats
        }
    
    def clear_all(self):
        """Clear all tasks"""
        self.tasks.clear()
        self.task_queue.clear()
        self.logger.info("All tasks cleared")


class TaskChain:
    """
    Execute a sequence of tasks in order
    Useful for complex multi-step operations
    """
    
    def __init__(self, name: str):
        self.name = name
        self.steps: List[tuple] = []  # (name, callback, args, kwargs)
        self.current_step = 0
        self.logger = get_logger()
    
    def add_step(
        self,
        name: str,
        callback: Callable,
        args: tuple = (),
        kwargs: dict = None
    ):
        """Add a step to the chain"""
        if kwargs is None:
            kwargs = {}
        self.steps.append((name, callback, args, kwargs))
        return self
    
    def execute(self) -> bool:
        """
        Execute all steps in sequence
        
        Returns:
            True if all steps completed successfully
        """
        self.logger.info(f"Starting task chain: {self.name}")
        
        for i, (step_name, callback, args, kwargs) in enumerate(self.steps):
            self.current_step = i
            self.logger.debug(f"  Step {i+1}/{len(self.steps)}: {step_name}")
            
            try:
                result = callback(*args, **kwargs)
                if result is False:
                    self.logger.error(f"Chain '{self.name}' failed at step: {step_name}")
                    return False
            except Exception as e:
                self.logger.error(f"Chain '{self.name}' error at step {step_name}: {e}")
                return False
        
        self.logger.success(f"Task chain completed: {self.name}")
        return True
    
    def reset(self):
        """Reset the chain for re-execution"""
        self.current_step = 0


class ConditionalTask:
    """
    A task that only executes when conditions are met
    """
    
    def __init__(
        self,
        name: str,
        condition: Callable[[], bool],
        action: Callable,
        args: tuple = (),
        kwargs: dict = None
    ):
        self.name = name
        self.condition = condition
        self.action = action
        self.args = args
        self.kwargs = kwargs or {}
        self.logger = get_logger()
    
    def check_and_execute(self) -> bool:
        """
        Check condition and execute if met
        
        Returns:
            True if condition was met and action succeeded
        """
        try:
            if self.condition():
                self.logger.debug(f"Condition met for: {self.name}")
                return self.action(*self.args, **self.kwargs) is not False
            return False
        except Exception as e:
            self.logger.error(f"Conditional task error: {self.name} - {e}")
            return False


def create_randomized_interval(base_minutes: int, variance_percent: int = 20) -> int:
    """
    Create a randomized interval to seem more human-like
    
    Args:
        base_minutes: Base interval in minutes
        variance_percent: Maximum variance percentage
    
    Returns:
        Interval in seconds with random variance
    """
    base_seconds = base_minutes * 60
    variance = base_seconds * (variance_percent / 100)
    
    return int(base_seconds + random.uniform(-variance, variance))
