
// Tracking Agent (Trystero) - Warmly honest, playful progress tracker
export class Trystero {
  private personality = {
    tone: 'warm',
    honesty: 'gentle',
    playfulness: 'subtle'
  };

  async logWorkoutCompletion(workout: any): Promise<void> {
    const completions = this.getWorkoutHistory();
    const newEntry = {
      id: Date.now(),
      type: workout.type,
      duration: workout.duration,
      completedAt: new Date().toISOString(),
      exercises: workout.exercises?.length || 0
    };

    completions.push(newEntry);
    localStorage.setItem('workout_history', JSON.stringify(completions));
    
    console.log('Trystero: Progress noted. Another step forward.');
  }

  getWorkoutHistory(): any[] {
    const stored = localStorage.getItem('workout_history');
    return stored ? JSON.parse(stored) : [];
  }

  generateProgressInsight(): string {
    const history = this.getWorkoutHistory();
    
    if (history.length === 0) {
      return "Ready to begin? Every journey starts with a single step.";
    }

    const recentWorkouts = history.slice(-7); // Last 7 workouts
    const workoutTypes = [...new Set(recentWorkouts.map(w => w.type))];
    
    if (history.length <= 3) {
      return `${history.length} workouts done. A clear step forward.`;
    }

    // Check for patterns
    const yogaMissed = this.checkYogaPattern(recentWorkouts);
    const runningBalance = this.checkRunningBalance(recentWorkouts);

    if (yogaMissed > 2) {
      return `${history.length} workouts completed. Yoga missed ${yogaMissed} times; it aids recovery.`;
    }

    if (runningBalance > 2) {
      return `Strong running streak! Balance with core work serves you well.`;
    }

    return `${history.length} workouts done. ${workoutTypes.length} different types. Variety builds strength.`;
  }

  private checkYogaPattern(workouts: any[]): number {
    return workouts.filter(w => !w.type.includes('Yoga')).length;
  }

  private checkRunningBalance(workouts: any[]): number {
    return workouts.filter(w => w.type === 'Running').length;
  }

  generateDetailedFeedback(): string {
    const history = this.getWorkoutHistory();
    
    if (history.length < 5) {
      return "Building momentum takes time. Each session matters.";
    }

    const weeklyData = this.getWeeklyBreakdown();
    const insights = [
      `Weekly average: ${weeklyData.average} sessions`,
      `Most frequent: ${weeklyData.mostCommon}`,
      `Recovery balance: ${weeklyData.recoveryScore}/10`
    ];

    return insights.join(' • ');
  }

  private getWeeklyBreakdown(): any {
    const history = this.getWorkoutHistory();
    const lastWeek = history.filter(w => {
      const workoutDate = new Date(w.completedAt);
      const weekAgo = new Date();
      weekAgo.setDate(weekAgo.getDate() - 7);
      return workoutDate > weekAgo;
    });

    const typeCounts = lastWeek.reduce((acc, workout) => {
      acc[workout.type] = (acc[workout.type] || 0) + 1;
      return acc;
    }, {});

    const mostCommon = Object.keys(typeCounts).reduce((a, b) => 
      typeCounts[a] > typeCounts[b] ? a : b, 'None'
    );

    return {
      average: lastWeek.length,
      mostCommon,
      recoveryScore: this.calculateRecoveryScore(lastWeek)
    };
  }

  private calculateRecoveryScore(workouts: any[]): number {
    const hasYoga = workouts.some(w => w.type.includes('Yoga'));
    const runningRatio = workouts.filter(w => w.type === 'Running').length / workouts.length;
    
    let score = 5; // Base score
    if (hasYoga) score += 3;
    if (runningRatio <= 0.4) score += 2; // Good running balance
    
    return Math.min(score, 10);
  }
}
