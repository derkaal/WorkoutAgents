import React, { useState } from 'react';
import { HomeScreen } from '../components/HomeScreen';
import { WorkoutScreen } from '../components/WorkoutScreen';
import { ProgressDashboard } from '../components/ProgressDashboard';
import { Button } from '@/components/ui/button';
import { Home, Activity, BarChart3, Volume2, VolumeX, Dumbbell } from 'lucide-react';
import { audioService } from '../services/audioService';
import WorkoutGeneratorPage from './WorkoutGenerator';
import ProgressDashboardPage from './ProgressDashboard';
import { BriefingProvider } from '../context/BriefingContext';

type Screen = 'home' | 'workout' | 'progress' | 'generator';

const Index = () => {
  const [currentScreen, setCurrentScreen] = useState<Screen>('home');
  const [currentWorkout, setCurrentWorkout] = useState<any>(null);
  const [voiceEnabled, setVoiceEnabled] = useState(true);

  const handleStartWorkout = (workout: any) => {
    setCurrentWorkout(workout);
    setCurrentScreen('workout');
  };

  const handleCompleteWorkout = () => {
    setCurrentScreen('home');
    setCurrentWorkout(null);
  };

  const handleBack = () => {
    setCurrentScreen('home');
  };

  const toggleVoice = () => {
    setVoiceEnabled(!voiceEnabled);
    
    // Stop any ongoing audio playback
    audioService.stopAudio();
  };

  const renderScreen = () => {
    switch (currentScreen) {
      case 'home':
        return (
          <HomeScreen
            onStartWorkout={handleStartWorkout}
            voiceEnabled={voiceEnabled}
            onToggleVoice={toggleVoice}
          />
        );
      case 'workout':
        return (
          <WorkoutScreen
            workout={currentWorkout}
            onCompleteWorkout={handleCompleteWorkout}
            onBack={handleBack}
            voiceEnabled={voiceEnabled}
          />
        );
      case 'progress':
        return (
          <ProgressDashboardPage />
        );
      case 'generator':
        return (
          <WorkoutGeneratorPage />
        );
      default:
        return null;
    }
  };

  return (
    <BriefingProvider>
      <div className="relative min-h-screen">
        {renderScreen()}
        
        {/* Bottom Navigation */}
      {currentScreen !== 'workout' && (
        <div className="fixed bottom-0 left-0 right-0 bg-gray-900/95 backdrop-blur-sm border-t border-gray-700">
          <div className="max-w-md mx-auto px-4 py-3">
            <div className="flex justify-around items-center">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setCurrentScreen('home')}
                className={`flex flex-col items-center space-y-1 ${
                  currentScreen === 'home' ? 'text-cyan-400' : 'text-gray-400'
                }`}
              >
                <Home size={20} />
                <span className="text-xs">Home</span>
              </Button>

              <Button
                variant="ghost"
                size="sm"
                onClick={() => setCurrentScreen('generator')}
                className={`flex flex-col items-center space-y-1 ${
                  currentScreen === 'generator' ? 'text-purple-400' : 'text-gray-400'
                }`}
              >
                <Dumbbell size={20} />
                <span className="text-xs">Generator</span>
              </Button>

              <Button
                variant="ghost"
                size="sm"
                onClick={() => setCurrentScreen('progress')}
                className={`flex flex-col items-center space-y-1 ${
                  currentScreen === 'progress' ? 'text-cyan-400' : 'text-gray-400'
                }`}
              >
                <BarChart3 size={20} />
                <span className="text-xs">Progress</span>
              </Button>

              <Button
                variant="ghost"
                size="sm"
                onClick={toggleVoice}
                className={`flex flex-col items-center space-y-1 ${
                  voiceEnabled ? 'text-green-400' : 'text-gray-400'
                }`}
              >
                {voiceEnabled ? <Volume2 size={20} /> : <VolumeX size={20} />}
                <span className="text-xs">Voice</span>
              </Button>
            </div>
          </div>
        </div>
      )}
      </div>
    </BriefingProvider>
  );
};

export default Index;
