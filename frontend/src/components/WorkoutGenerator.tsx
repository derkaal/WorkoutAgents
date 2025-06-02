import React, { useState, useContext } from 'react';
import { Play, Volume2, VolumeX } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { generateWorkout, WorkoutResponse } from '../services/apiService';
import { audioService } from '../services/audioService';
import { BriefingContext } from '../context/BriefingContext';

interface WorkoutGeneratorProps {
  onWorkoutGenerated?: (workout: any) => void;
}

export const WorkoutGenerator: React.FC<WorkoutGeneratorProps> = ({
  onWorkoutGenerated
}) => {
  // Access the briefing context
  const { briefing } = useContext(BriefingContext);
  // State management
  const [userInput, setUserInput] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [mikeResponseText, setMikeResponseText] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Handle workout generation
  const handleGetWorkout = async () => {
    // Stop any previously playing audio
    audioService.stopAudio();
    
    // Reset states and set loading
    setIsLoading(true);
    setMikeResponseText(null);
    setErrorMessage(null);
    
    try {
      // Call the API with user input and Trystero's briefing if available
      const response = await generateWorkout({
        userInput: userInput,
        trysteroBriefing: briefing
      });
      
      console.log('Using briefing from context:', briefing);
      
      // Update state with response
      // The response might have different structures depending on the API
      // Check for mike_response_text first (from backend schema)
      if ('mike_response_text' in response && response.mike_response_text) {
        setMikeResponseText(response.mike_response_text as string);
        
        // Play audio if available
        if ('audio_base64' in response && response.audio_base64) {
          await audioService.playAgentAudio(
            response.audio_base64 as string,
            response.mike_response_text as string
          );
        }
      }
      // Fallback to intro (from frontend schema)
      else if ('intro' in response && response.intro) {
        setMikeResponseText(response.intro as string);
        
        // Play audio if available
        if ('audio_intro' in response && response.audio_intro) {
          await audioService.playAgentAudio(
            response.audio_intro as string,
            response.intro as string
          );
        }
      }
      
      // Call the callback if provided
      if (onWorkoutGenerated) {
        onWorkoutGenerated(response);
      }
    } catch (error) {
      // Handle errors
      console.error('Error generating workout:', error);
      setErrorMessage(error instanceof Error ? error.message : 'Failed to generate workout');
    } finally {
      // Reset loading state
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <Card className="bg-gray-800/50 border-cyan-500/30 shadow-xl shadow-cyan-500/10">
        <CardHeader>
          <CardTitle className="text-cyan-400 text-xl">
            Mike Lawry Workout Generator
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <label htmlFor="workout-input" className="text-sm text-gray-300">
              What kind of workout are you looking for today?
            </label>
            <Input
              id="workout-input"
              placeholder="e.g., 'A 20-minute HIIT workout focusing on core strength'"
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              className="bg-gray-700/50 border-gray-600 text-white"
              disabled={isLoading}
            />
          </div>

          <div className="flex space-x-2">
            <Button 
              onClick={handleGetWorkout}
              className="bg-gradient-to-r from-cyan-500 to-purple-500 hover:from-cyan-600 hover:to-purple-600 text-white font-semibold"
              disabled={isLoading || !userInput.trim()}
            >
              <Play size={16} className="mr-2" />
              {isLoading ? 'Generating...' : 'Get Workout'}
            </Button>
            
            <Button 
              onClick={() => audioService.stopAudio()}
              variant="outline"
              className="border-red-500/50 text-red-400 hover:bg-red-500/10"
              disabled={isLoading}
            >
              <VolumeX size={16} className="mr-2" />
              Stop Audio
            </Button>
          </div>

          {/* Mike's Response */}
          {mikeResponseText && (
            <div className="mt-4 p-4 bg-gray-700/30 rounded-lg border border-cyan-500/20">
              <h3 className="text-cyan-400 font-semibold mb-2">Mike's Workout Plan</h3>
              <div className="text-gray-300 text-sm whitespace-pre-line">
                {mikeResponseText}
              </div>
            </div>
          )}

          {/* Error Message */}
          {errorMessage && (
            <div className="mt-4 p-4 bg-red-900/20 rounded-lg border border-red-500/30">
              <h3 className="text-red-400 font-semibold mb-2">Error</h3>
              <div className="text-gray-300 text-sm">
                {errorMessage}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};