"""
Workout History Module

This module provides classes for tracking workout history, including:
- Weekly workout count
- Consecutive workout days
- File-based persistence
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import logging

# Configure logging
logger = logging.getLogger(__name__)


class WorkoutHistory:
    """
    Class to track workout history including weekly count and consecutive days.
    
    Attributes:
        history_file_path: Path to the file where workout history is stored
        workouts: List of workout records with date and type
        max_consecutive_days: Maximum allowed consecutive workout days
        weekly_goal: Number of workouts per week to aim for
    """
    
    def __init__(self, history_file_path: str = "workout_history.json"):
        """
        Initialize the workout history tracker.
        
        Args:
            history_file_path: Path to the file where workout history is stored
        """
        self.history_file_path = history_file_path
        self.workouts = []
        self.max_consecutive_days = 3  # Maximum consecutive workout days
        self.weekly_goal = 4  # Weekly target of workouts
        
        # Load existing history if file exists
        self._load_history()
    
    def _load_history(self) -> None:
        """Load workout history from file if it exists."""
        try:
            if os.path.exists(self.history_file_path):
                with open(self.history_file_path, 'r') as f:
                    data = json.load(f)
                    # Convert string dates back to datetime objects
                    self.workouts = [
                        {
                            'date': datetime.fromisoformat(workout['date']),
                            'type': workout['type']
                        }
                        for workout in data.get('workouts', [])
                    ]
                    logger.info(
                        f"Loaded {len(self.workouts)} workout records from history file"
                    )
            else:
                logger.info(
                    f"No history file found at {self.history_file_path}, "
                    f"starting with empty history"
                )
        except Exception as e:
            logger.error(f"Error loading workout history: {str(e)}")
            # Start with empty history if there's an error
            self.workouts = []
    
    def _save_history(self) -> None:
        """Save workout history to file."""
        try:
            # Convert datetime objects to strings for JSON serialization
            data = {
                'workouts': [
                    {
                        'date': workout['date'].isoformat(),
                        'type': workout['type']
                    }
                    for workout in self.workouts
                ]
            }
            
            # Create directory if it doesn't exist
            os.makedirs(
                os.path.dirname(os.path.abspath(self.history_file_path)),
                exist_ok=True
            )
            
            with open(self.history_file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(
                f"Saved {len(self.workouts)} workout records to history file"
            )
        except Exception as e:
            logger.error(f"Error saving workout history: {str(e)}")
    
    def record_workout(
        self, workout_type: str, date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Record a completed workout.
        
        Args:
            workout_type: Type of workout ('strength', 'yoga', 'runs')
            date: Date of the workout (defaults to current date)
            
        Returns:
            Dict with status and any warnings/recommendations
        """
        if date is None:
            date = datetime.now()
        
        # Add the workout to history
        self.workouts.append({
            'date': date,
            'type': workout_type
        })
        
        # Save the updated history
        self._save_history()
        
        # Check for any warnings or recommendations
        result = {
            'status': 'success',
            'message': 'Workout recorded successfully',
            'warnings': [],
            'recommendations': []
        }
        
        # Check consecutive days
        consecutive_days = self.get_consecutive_workout_days()
        if consecutive_days >= self.max_consecutive_days:
            result['warnings'].append(
                f"You've worked out {consecutive_days} days in a row. "
                f"Consider taking a rest day."
            )
        
        # Check weekly goal
        weekly_count = self.get_weekly_workout_count()
        if weekly_count >= self.weekly_goal:
            result['recommendations'].append(
                f"You've reached your weekly goal of {self.weekly_goal} workouts! "
                f"Great job!"
            )
        
        return result
    
    def get_consecutive_workout_days(self) -> int:
        """
        Calculate the current streak of consecutive workout days.
        
        Returns:
            Number of consecutive days with workouts up to today
        """
        if not self.workouts:
            return 0
        
        # Sort workouts by date
        # Sort workouts by date for reference (though we'll use the set approach)
        # This is more explicit for code clarity
        
        # Start from the most recent day and count backwards
        current_date = datetime.now().date()
        consecutive_days = 0
        
        # Create a set of dates that have workouts
        workout_dates = {workout['date'].date() for workout in self.workouts}
        
        # Count backward from today to find consecutive days
        for i in range(7):  # Check up to a week back
            check_date = current_date - timedelta(days=i)
            if check_date in workout_dates:
                consecutive_days += 1
            else:
                # Break at the first day without a workout
                break
        
        return consecutive_days
    
    def get_weekly_workout_count(self) -> int:
        """
        Calculate the number of workouts in the current week.
        
        Returns:
            Number of workouts in the current week (last 7 days)
        """
        if not self.workouts:
            return 0
        
        # Get the date 7 days ago
        week_ago = datetime.now() - timedelta(days=7)
        
        # Count workouts in the last 7 days
        count = sum(
            1 for workout in self.workouts if workout['date'] >= week_ago
        )
        
        return count
    
    def get_workout_distribution(self) -> Dict[str, float]:
        """
        Calculate the distribution of workout types in the current week.
        
        Returns:
            Dictionary with workout types as keys and percentages as values
        """
        # Get workouts from the last 7 days
        week_ago = datetime.now() - timedelta(days=7)
        recent_workouts = [w for w in self.workouts if w['date'] >= week_ago]
        
        if not recent_workouts:
            return {'strength': 0, 'yoga': 0, 'runs': 0}
        
        # Count each type
        type_counts = {'strength': 0, 'yoga': 0, 'runs': 0}
        for workout in recent_workouts:
            workout_type = workout['type']
            if workout_type in type_counts:
                type_counts[workout_type] += 1
        
        # Calculate percentages
        total = sum(type_counts.values())
        if total > 0:
            distribution = {
                workout_type: (count / total) * 100
                for workout_type, count in type_counts.items()
            }
        else:
            distribution = {workout_type: 0 for workout_type in type_counts}
        
        return distribution
    
    def should_recommend_rest(self) -> bool:
        """
        Determine if a rest day should be recommended based on history.
        
        Returns:
            Boolean indicating whether a rest day is recommended
        """
        # Recommend rest if reached maximum consecutive days
        consecutive_days = self.get_consecutive_workout_days()
        if consecutive_days >= self.max_consecutive_days:
            return True
        
        return False
    
    def get_workout_history_summary(self) -> Dict[str, Any]:
        """
        Generate a summary of workout history.
        
        Returns:
            Dictionary with summary statistics
        """
        weekly_count = self.get_weekly_workout_count()
        consecutive_days = self.get_consecutive_workout_days()
        distribution = self.get_workout_distribution()
        
        return {
            'weekly_count': weekly_count,
            'weekly_goal': self.weekly_goal,
            'weekly_completion_percentage': min(
                (weekly_count / self.weekly_goal) * 100, 100
            ),
            'consecutive_days': consecutive_days,
            'max_consecutive_days': self.max_consecutive_days,
            'distribution': distribution,
            'rest_recommended': self.should_recommend_rest()
        }