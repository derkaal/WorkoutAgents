
import React, { useState, useEffect } from 'react';
import { Play, RotateCcw, Volume2, VolumeX } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { apiService, WorkoutResponse, ProgressResponse, generateWorkout, analyzeProgress } from '../services/apiService';
import { audioService } from '../services/audioService';

interface HomeScreenProps {
  onStartWorkout: (workout: WorkoutResponse | null) => void;
  voiceEnabled: boolean;
  onToggleVoice: () => void;
}

export const HomeScreen: React.FC<HomeScreenProps> = ({ 
  onStartWorkout, 
  voiceEnabled, 
  onToggleVoice 
}) => {
  const [todaysWorkout, setTodaysWorkout] = useState<WorkoutResponse | null>(null);
  const [progressInsight, setProgressInsight] = useState<string>('');
  const [progressAudio, setProgressAudio] = useState<string>('');
  const [switchCount, setSwitchCount] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingSwitch, setIsLoadingSwitch] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadTodaysWorkout();
    loadProgressInsight();
  }, []);

  const loadTodaysWorkout = async () => {
    setIsLoading(true);
    setError(null);
    try {
      // Use the standalone function with proper parameters
      const workout = await generateWorkout({
        userInput: "Give me a general workout for today"
      });
      
      setTodaysWorkout(workout);
    } catch (error) {
      console.error('Error loading workout:', error);
      setError('Failed to load today\'s workout. Please try again.');
      // Fallback to cached data or default workout
      loadFallbackWorkout();
    } finally {
      setIsLoading(false);
    }
  };

  const loadProgressInsight = async () => {
    try {
      // Use the standalone function with proper parameters
      const progressData = await analyzeProgress({
        progress_data: {
          strength_done: 0,
          yoga_done: 0,
          runs_done: 0,
          notes: "First time user"
        }
      });
      
      setProgressInsight(progressData.insights || progressData.trystero_feedback_text || '');
      setProgressAudio(progressData.audio_insight || '');
    } catch (error) {
      console.error('Error loading progress insight:', error);
      setProgressInsight('Welcome back! Complete your first workout to see progress insights.');
    }
  };

  const loadFallbackWorkout = () => {
    // Fallback workout structure
    setTodaysWorkout({
      workout_id: 'fallback-001',
      type: 'Core + Hip',
      intro: "Let's get this workout started!",
      generated_plan: {
        exercises: [
          { name: 'Plank', duration: 60, instruction: 'Hold a strong plank position' },
          { name: 'Hip Circles', duration: 45, instruction: 'Gentle hip mobility circles' }
        ]
      }
    });
  };

  const handleSwitchWorkout = async () => {
    if (switchCount >= 2) {
      alert('Maximum 2 switches per week reached!');
      return;
    }
    
    setIsLoadingSwitch(true);
    try {
      const newWorkout = await apiService.switchWorkout(todaysWorkout);
      setTodaysWorkout(newWorkout);
      setSwitchCount(prev => prev + 1);
    } catch (error) {
      console.error('Error switching workout:', error);
      alert('Failed to switch workout. Please try again.');
    } finally {
      setIsLoadingSwitch(false);
    }
  };

  const playWorkoutIntro = async () => {
    if (!voiceEnabled || !todaysWorkout) return;
    
    try {
      if (todaysWorkout.audio_intro) {
        await audioService.playAgentAudio(todaysWorkout.audio_intro);
      } else {
        // Fallback to text-to-speech
        if ('speechSynthesis' in window) {
          const utterance = new SpeechSynthesisUtterance(todaysWorkout.intro);
          speechSynthesis.speak(utterance);
        }
      }
    } catch (error) {
      console.error('Error playing workout intro:', error);
    }
  };

  const playProgressSummary = async () => {
    if (!voiceEnabled) return;
    
    try {
      if (progressAudio) {
        await audioService.playAgentAudio(progressAudio);
      } else {
        // Fallback to text-to-speech
        if ('speechSynthesis' in window) {
          const utterance = new SpeechSynthesisUtterance(progressInsight);
          speechSynthesis.speak(utterance);
        }
      }
    } catch (error) {
      console.error('Error playing progress summary:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-cyan-400 text-xl">Preparing your workout...</div>
      </div>
    );
  }

  if (error && !todaysWorkout) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-4">
        <div className="text-center space-y-4">
          <div className="text-red-400 text-xl">{error}</div>
          <Button onClick={loadTodaysWorkout} className="bg-cyan-500 hover:bg-cyan-600">
            Retry
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-4">
      <div className="max-w-md mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between pt-8">
          <h1 className="text-2xl font-bold text-white">Today's Workout</h1>
          <Button
            variant="ghost"
            size="sm"
            onClick={onToggleVoice}
            className="text-cyan-400 hover:text-cyan-300"
            id="voice-toggle-btn"
          >
            {voiceEnabled ? <Volume2 size={20} /> : <VolumeX size={20} />}
          </Button>
        </div>

        {/* Today's Workout Card */}
        <Card className="bg-gray-800/50 border-cyan-500/30 shadow-xl shadow-cyan-500/10">
          <CardHeader>
            <CardTitle className="text-cyan-400 text-xl">
              {todaysWorkout?.type || 'Core + Hip'}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="aspect-video bg-gradient-to-r from-purple-600 to-cyan-600 rounded-lg flex items-center justify-center">
              <img 
                src={`https://via.placeholder.com/300x200?text=${todaysWorkout?.type?.replace(' ', '+')}`}
                alt={todaysWorkout?.type}
                className="w-full h-full object-cover rounded-lg opacity-80"
                onError={(e) => {
                  e.currentTarget.src = 'https://via.placeholder.com/300x200?text=Workout';
                }}
              />
            </div>
            
            <p className="text-gray-300 text-sm">
              {todaysWorkout?.intro || "Let's get this workout started!"}
            </p>

            <div className="flex flex-wrap gap-2">
              <Button 
                onClick={() => onStartWorkout(todaysWorkout)}
                className="bg-gradient-to-r from-cyan-500 to-purple-500 hover:from-cyan-600 hover:to-purple-600 text-white font-semibold px-6 py-2 rounded-lg shadow-lg"
                id="start-workout-btn"
              >
                <Play size={16} className="mr-2" />
                Start Workout
              </Button>
              
              <Button 
                onClick={handleSwitchWorkout}
                variant="outline"
                className="border-cyan-500/50 text-cyan-400 hover:bg-cyan-500/10"
                disabled={switchCount >= 2 || isLoadingSwitch}
                id="switch-workout-btn"
              >
                <RotateCcw size={16} className="mr-2" />
                {isLoadingSwitch ? 'Switching...' : `Switch (${2 - switchCount} left)`}
              </Button>
              
              {voiceEnabled && (
                <Button 
                  onClick={playWorkoutIntro}
                  variant="outline"
                  className="border-purple-500/50 text-purple-400 hover:bg-purple-500/10"
                  id="play-intro-btn"
                >
                  <Volume2 size={16} className="mr-2" />
                  Play Intro
                </Button>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Trystero's Progress Summary */}
        <Card className="bg-gray-800/30 border-green-500/30">
          <CardContent className="pt-6">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h3 className="text-green-400 font-semibold mb-2">Trystero's Insight</h3>
                <p className="text-gray-300 text-sm" id="trystero-insight-text">{progressInsight}</p>
              </div>
              {voiceEnabled && (
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={playProgressSummary}
                  className="text-green-400 hover:text-green-300 ml-2"
                  id="play-progress-btn"
                >
                  <Volume2 size={16} />
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
