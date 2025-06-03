"""
Direct testing script for the WorkoutHistory functionality.

This script directly tests the WorkoutHistory class methods without 
requiring API endpoint access.
"""

import os
import json
import sys
from datetime import datetime, timedelta

# Add parent directory to path to fix imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.models.workout_history import WorkoutHistory  # noqa: E402


def print_separator(title):
    """Print a separator with a title."""
    print("\n" + "=" * 40)
    print(f" {title} ".center(40, "-"))
    print("=" * 40)


def main():
    """Test the WorkoutHistory class functionality directly."""
    # Use a test file for history
    test_file = "test_workout_history_direct.json"
    
    # Delete the test file if it exists
    if os.path.exists(test_file):
        os.remove(test_file)
    
    # Create a WorkoutHistory instance
    history = WorkoutHistory(history_file_path=test_file)
    
    # 1. Test recording a workout
    print_separator("RECORDING A WORKOUT")
    result = history.record_workout("strength")
    print(f"Recorded workout result: {json.dumps(result, indent=2)}")
    
    # Verify workout was recorded
    print(f"Workout count: {len(history.workouts)}")
    print(f"Workout type: {history.workouts[0]['type']}")
    
    # 2. Test weekly goal achievement
    print_separator("WEEKLY GOAL ACHIEVEMENT")
    print("Recording 3 more workouts to reach weekly goal...")
    
    # Record 3 more workouts (total 4)
    for _ in range(3):
        history.record_workout("strength")
    
    # Get weekly count
    weekly_count = history.get_weekly_workout_count()
    print(f"Weekly workout count: {weekly_count}")
    
    # Get summary
    summary = history.get_workout_history_summary()
    print(f"Weekly completion percentage: "
          f"{summary['weekly_completion_percentage']}%")
    print("Recommendations:")
    print(json.dumps(summary.get('recommendations', []), indent=2))
    
    # 3. Test consecutive days rest recommendation
    print_separator("CONSECUTIVE DAYS REST RECOMMENDATION")
    
    # Reset the history
    if os.path.exists(test_file):
        os.remove(test_file)
    
    history = WorkoutHistory(history_file_path=test_file)
    
    # Record workouts for 3 consecutive days
    print("Recording workouts for 3 consecutive days...")
    for i in range(3):
        date = datetime.now() - timedelta(days=i)
        history.record_workout("strength", date=date)
    
    # Check consecutive days
    consecutive_days = history.get_consecutive_workout_days()
    print(f"Consecutive workout days: {consecutive_days}")
    
    # Check if rest is recommended
    should_rest = history.should_recommend_rest()
    print(f"Rest recommended: {should_rest}")
    
    # Get summary
    summary = history.get_workout_history_summary()
    print(f"Rest recommended in summary: {summary['rest_recommended']}")
    print("Recommendations:")
    print(json.dumps(summary.get('recommendations', []), indent=2))
    
    # 4. Test workout distribution
    print_separator("WORKOUT DISTRIBUTION")
    
    # Reset the history
    if os.path.exists(test_file):
        os.remove(test_file)
    
    history = WorkoutHistory(history_file_path=test_file)
    
    # Record different types of workouts
    print("Recording different types of workouts...")
    history.record_workout("strength")
    history.record_workout("yoga")
    history.record_workout("runs")
    
    # Get distribution
    distribution = history.get_workout_distribution()
    print(f"Workout distribution: {json.dumps(distribution, indent=2)}")
    
    # Clean up the test file
    if os.path.exists(test_file):
        os.remove(test_file)
    
    print_separator("TESTING COMPLETE")
    print("All WorkoutHistory functionality tests completed successfully!")


if __name__ == "__main__":
    main()