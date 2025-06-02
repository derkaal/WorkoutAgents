
import React, { useState, useEffect } from 'react';
import { Play, Pause, SkipForward, CheckCircle, Volume2, ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { apiService } from '../services/apiService';
import { audioService } from '../services/audioService';

interface WorkoutScreenProps {
  workout: any;
  onCompleteWorkout: () => void;
  onBack: () => void;
  voiceEnabled: boolean;
}

export const WorkoutScreen: React.FC<WorkoutScreenProps> = ({ 
  workout, 
  onCompleteWorkout, 
  onBack,
  voiceEnabled 
}) => {
  const [currentExerciseIndex, setCurrentExerciseIndex] = useState(0);
  const [timeRemaining, setTimeRemaining] = useState(45);
  const [isActive, setIsActive] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [completedExercises, setCompletedExercises] = useState<number[]>([]);
  const [isCompletingWorkout, setIsCompletingWorkout] = useState(false);

  const exercises = workout?.generated_plan?.exercises || [];
  const currentExercise = exercises[currentExerciseIndex];
  const totalExercises = exercises.length;
  const progressPercentage = totalExercises > 0 ? ((currentExerciseIndex + 1) / totalExercises) * 100 : 0;

  useEffect(() => {
    if (currentExercise) {
      setTimeRemaining(currentExercise.duration || 45);
    }
  }, [currentExerciseIndex, currentExercise]);

  useEffect(() => {
    let interval: NodeJS.Timeout | null = null;
    
    if (isActive && !isPaused && timeRemaining > 0) {
      interval = setInterval(() => {
        setTimeRemaining(time => {
          if (time <= 1) {
            handleExerciseComplete();
            return 0;
          }
          return time - 1;
        });
      }, 1000);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isActive, isPaused, timeRemaining]);

  const handleExerciseComplete = () => {
    // Haptic feedback
    if (navigator.vibrate) {
      navigator.vibrate([200, 100, 200]);
    }

    setCompletedExercises(prev => [...prev, currentExerciseIndex]);
    
    if (currentExerciseIndex < totalExercises - 1) {
      setCurrentExerciseIndex(prev => prev + 1);
      setIsActive(false);
      setIsPaused(false);
    } else {
      handleWorkoutComplete();
    }
  };

  const handleWorkoutComplete = async () => {
    setIsCompletingWorkout(true);
    
    try {
      const completionData = {
        workout_id: workout.workout_id,
        type: workout.type,
        completed_exercises: exercises.map((exercise, index) => ({
          name: exercise.name,
          duration: exercise.duration,
          completed: completedExercises.includes(index) || index === currentExerciseIndex
        })),
        total_duration: exercises.reduce((sum, ex) => sum + ex.duration, 0),
        completion_timestamp: new Date().toISOString()
      };

      const response = await apiService.logWorkoutCompletion(completionData);
      
      if (voiceEnabled && response.audio_completion) {
        await audioService.playBase64Audio(response.audio_completion);
      } else if (voiceEnabled) {
        // Fallback to speech synthesis
        const message = response.message || "Progress noted. Well done.";
        if ('speechSynthesis' in window) {
          const utterance = new SpeechSynthesisUtterance(message);
          speechSynthesis.speak(utterance);
        }
      }
      
      onCompleteWorkout();
    } catch (error) {
      console.error('Error completing workout:', error);
      // Still complete the workout locally even if backend fails
      onCompleteWorkout();
    } finally {
      setIsCompletingWorkout(false);
    }
  };

  const playInstructions = async () => {
    if (!voiceEnabled || !currentExercise) return;
    
    try {
      const instructionData = await apiService.getExerciseInstructions(currentExercise.name);
      
      if (instructionData.audio) {
        await audioService.playBase64Audio(instructionData.audio);
      } else {
        // Fallback to speech synthesis
        const instructions = instructionData.instructions || currentExercise.instruction;
        if ('speechSynthesis' in window) {
          const utterance = new SpeechSynthesisUtterance(instructions);
          speechSynthesis.speak(utterance);
        }
      }
    } catch (error) {
      console.error('Error playing instructions:', error);
      // Fallback to local instruction text
      if ('speechSynthesis' in window && currentExercise.instruction) {
        const utterance = new SpeechSynthesisUtterance(currentExercise.instruction);
        speechSynthesis.speak(utterance);
      }
    }
  };

  const toggleTimer = () => {
    if (!isActive) {
      setIsActive(true);
      setIsPaused(false);
    } else {
      setIsPaused(!isPaused);
    }
  };

  const skipExercise = () => {
    handleExerciseComplete();
  };

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (!workout || !currentExercise) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-red-400">No workout data available</div>
      </div>
    );
  }

  const isCompleted = completedExercises.includes(currentExerciseIndex);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-4">
      <div className="max-w-md mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between pt-8">
          <Button
            variant="ghost"
            onClick={onBack}
            className="text-white hover:text-cyan-400"
            id="workout-back-btn"
          >
            <ArrowLeft size={20} className="mr-2" />
            Back
          </Button>
          <h1 className="text-xl font-bold text-white">{workout.type}</h1>
        </div>

        {/* Progress Bar */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm text-gray-400">
            <span>Exercise {currentExerciseIndex + 1} of {totalExercises}</span>
            <span>{Math.round(progressPercentage)}% Complete</span>
          </div>
          <Progress value={progressPercentage} className="h-2" />
        </div>

        {/* Current Exercise Card */}
        <Card className="bg-gray-800/50 border-cyan-500/30 shadow-xl">
          <CardHeader>
            <CardTitle className="text-cyan-400 text-xl flex items-center justify-between">
              <span id="current-exercise-name">{currentExercise.name}</span>
              {isCompleted && <CheckCircle className="text-green-400" size={24} />}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="aspect-video bg-gradient-to-r from-purple-600 to-cyan-600 rounded-lg flex items-center justify-center">
              <img 
                src={currentExercise.image || `https://via.placeholder.com/300x200?text=${currentExercise.name.replace(' ', '+')}`}
                alt={currentExercise.name}
                className="w-full h-full object-cover rounded-lg opacity-80"
                onError={(e) => {
                  e.currentTarget.src = 'https://via.placeholder.com/300x200?text=Exercise';
                }}
              />
            </div>

            <p className="text-gray-300 text-sm" id="exercise-instruction">
              {currentExercise.instruction}
            </p>

            {/* Timer Display */}
            <div className="text-center">
              <div className="text-4xl font-bold text-white mb-2" id="exercise-timer">
                {formatTime(timeRemaining)}
              </div>
              <div className="text-gray-400 text-sm">
                {isActive && !isPaused ? 'Active' : isPaused ? 'Paused' : 'Ready'}
              </div>
            </div>

            {/* Control Buttons */}
            <div className="flex justify-center gap-4">
              <Button
                onClick={toggleTimer}
                className="bg-gradient-to-r from-cyan-500 to-purple-500 hover:from-cyan-600 hover:to-purple-600"
                size="lg"
                id="exercise-timer-btn"
              >
                {isActive && !isPaused ? (
                  <Pause size={20} className="mr-2" />
                ) : (
                  <Play size={20} className="mr-2" />
                )}
                {isActive && !isPaused ? 'Pause' : 'Start'}
              </Button>

              <Button
                onClick={skipExercise}
                variant="outline"
                className="border-gray-500 text-gray-400 hover:bg-gray-700"
                id="skip-exercise-btn"
              >
                <SkipForward size={20} className="mr-2" />
                Skip
              </Button>

              {voiceEnabled && (
                <Button
                  onClick={playInstructions}
                  variant="outline"
                  className="border-purple-500/50 text-purple-400 hover:bg-purple-500/10"
                  id="play-instructions-btn"
                >
                  <Volume2 size={20} />
                </Button>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Complete Workout Button */}
        {currentExerciseIndex === totalExercises - 1 && isCompleted && (
          <Button
            onClick={handleWorkoutComplete}
            disabled={isCompletingWorkout}
            className="w-full bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white font-bold py-3"
            id="complete-workout-btn"
          >
            <CheckCircle size={20} className="mr-2" />
            {isCompletingWorkout ? 'Completing...' : 'Complete Workout'}
          </Button>
        )}
      </div>
    </div>
  );
};
