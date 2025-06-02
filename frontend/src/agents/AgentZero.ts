
// Control Agent (Agent Zero) - Rule-based validator
export interface WorkoutConfig {
  maxRunsPerWeek: number;
  yogaEveryNSessions: number;
  equipment: string[];
  targetDuration: number;
}

export interface WorkoutValidation {
  isValid: boolean;
  adjustments: string[];
  suggestedWorkout?: any;
}

export class AgentZero {
  private config: WorkoutConfig;
  
  constructor() {
    this.config = {
      maxRunsPerWeek: 2,
      yogaEveryNSessions: 3,
      equipment: ['mat', 'dumbbells', 'bag', 'wall'],
      targetDuration: 30
    };
  }

  validateWorkout(workout: any, weeklyHistory: any[]): WorkoutValidation {
    const adjustments: string[] = [];
    let isValid = true;

    // Check running frequency
    const runsThisWeek = weeklyHistory.filter(w => w.type === 'Running').length;
    if (workout.type === 'Running' && runsThisWeek >= this.config.maxRunsPerWeek) {
      isValid = false;
      adjustments.push(`Swapped running for yoga for balance. Max ${this.config.maxRunsPerWeek} runs per week.`);
    }

    // Check yoga frequency
    const sessionsSinceYoga = this.getSessionsSinceLastYoga(weeklyHistory);
    if (sessionsSinceYoga >= this.config.yogaEveryNSessions && workout.type !== 'Hip + Yoga') {
      adjustments.push('Added yoga elements for recovery balance.');
    }

    // Duration check
    if (workout.duration > this.config.targetDuration + 5) {
      adjustments.push(`Adjusted duration to ~${this.config.targetDuration} minutes.`);
    }

    return {
      isValid,
      adjustments,
      suggestedWorkout: isValid ? workout : this.generateBalancedWorkout(weeklyHistory)
    };
  }

  private getSessionsSinceLastYoga(history: any[]): number {
    for (let i = 0; i < history.length; i++) {
      if (history[i].type?.includes('Yoga')) {
        return i;
      }
    }
    return history.length;
  }

  private generateBalancedWorkout(history: any[]): any {
    const workoutTypes = ['Core + Hip', 'Upper Body + Core', 'Hip + Yoga'];
    const typeCounts = workoutTypes.map(type => ({
      type,
      count: history.filter(w => w.type === type).length
    }));

    // Find least used workout type
    const leastUsed = typeCounts.reduce((min, current) => 
      current.count < min.count ? current : min
    );

    return {
      type: leastUsed.type,
      duration: 30,
      exercises: this.getExercisesForType(leastUsed.type)
    };
  }

  private getExercisesForType(type: string): any[] {
    const exerciseDatabase = {
      'Core + Hip': [
        { name: 'Glute Bridges', duration: 45, equipment: 'mat' },
        { name: 'Plank', duration: 45, equipment: 'mat' },
        { name: 'Hip Circles', duration: 45, equipment: 'none' }
      ],
      'Upper Body + Core': [
        { name: 'Push-ups', duration: 45, equipment: 'mat' },
        { name: 'Dumbbell Rows', duration: 45, equipment: 'dumbbells' },
        { name: 'Mountain Climbers', duration: 45, equipment: 'mat' }
      ],
      'Hip + Yoga': [
        { name: "Child's Pose", duration: 60, equipment: 'mat' },
        { name: 'Cat-Cow', duration: 45, equipment: 'mat' },
        { name: 'Hip Flexor Stretch', duration: 45, equipment: 'mat' }
      ]
    };

    return exerciseDatabase[type] || [];
  }

  getAdjustmentSummary(): string {
    return "Agent Zero monitoring for optimal balance.";
  }
}
