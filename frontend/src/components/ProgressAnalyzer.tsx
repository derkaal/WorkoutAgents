import React, { useState, useContext } from 'react';
import { Play, Volume2, VolumeX, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { analyzeProgress } from '../services/apiService';
import { audioService } from '../services/audioService';
import { BriefingContext } from '../context/BriefingContext';

interface ProgressAnalyzerProps {
  onAnalysisComplete?: (analysis: any) => void;
}

export const ProgressAnalyzer: React.FC<ProgressAnalyzerProps> = ({
  onAnalysisComplete
}) => {
  // Access the briefing context
  const { setBriefing } = useContext(BriefingContext);
  // State management
  const [progressInput, setProgressInput] = useState<{
    strength_done: number;
    yoga_done: number;
    runs_done: number;
    notes: string;
  }>({
    strength_done: 0,
    yoga_done: 0,
    runs_done: 0,
    notes: ''
  });
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [trysteroResponseText, setTrysteroResponseText] = useState<string | null>(null);
  const [trysteroBriefing, setTrysteroBriefing] = useState<object | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Handle input changes
  const handleInputChange = (field: string, value: string | number) => {
    setProgressInput(prev => ({
      ...prev,
      [field]: field === 'notes' ? value : Number(value)
    }));
  };

  // Handle progress analysis
  const handleAnalyzeProgress = async () => {
    // Stop any previously playing audio
    audioService.stopAudio();
    
    // Reset states and set loading
    setIsLoading(true);
    setTrysteroResponseText(null);
    setTrysteroBriefing(null);
    setErrorMessage(null);
    
    try {
      // Call the API with progress data
      const response = await analyzeProgress({ 
        progress_data: progressInput 
      });
      
      // Update state with response
      setTrysteroResponseText(response.insights || response.trystero_feedback_text || '');
      setTrysteroBriefing(response.chart_data || null);
      
      // Update the shared briefing context
      if (response.briefing_for_next_plan) {
        setBriefing(response.briefing_for_next_plan);
        console.log('Briefing updated in context:', response.briefing_for_next_plan);
      }
      
      // Play audio if available
      if (response.audio_insight) {
        await audioService.playAgentAudio(
          response.audio_insight,
          response.insights
        );
      }
      
      // Call the callback if provided
      if (onAnalysisComplete) {
        onAnalysisComplete(response);
      }
    } catch (error) {
      // Handle errors
      console.error('Error analyzing progress:', error);
      setErrorMessage(error instanceof Error ? error.message : 'Failed to analyze progress');
    } finally {
      // Reset loading state
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <Card className="bg-gray-800/50 border-green-500/30 shadow-xl shadow-green-500/10">
        <CardHeader>
          <CardTitle className="text-green-400 text-xl">
            Trystero Progress Analyzer
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <label htmlFor="strength-input" className="text-sm text-gray-300">
                Strength Workouts Completed
              </label>
              <Input
                id="strength-input"
                type="number"
                min="0"
                placeholder="0"
                value={progressInput.strength_done}
                onChange={(e) => handleInputChange('strength_done', e.target.value)}
                className="bg-gray-700/50 border-gray-600 text-white"
                disabled={isLoading}
              />
            </div>
            
            <div className="space-y-2">
              <label htmlFor="yoga-input" className="text-sm text-gray-300">
                Yoga Sessions Completed
              </label>
              <Input
                id="yoga-input"
                type="number"
                min="0"
                placeholder="0"
                value={progressInput.yoga_done}
                onChange={(e) => handleInputChange('yoga_done', e.target.value)}
                className="bg-gray-700/50 border-gray-600 text-white"
                disabled={isLoading}
              />
            </div>
            
            <div className="space-y-2">
              <label htmlFor="runs-input" className="text-sm text-gray-300">
                Runs Completed
              </label>
              <Input
                id="runs-input"
                type="number"
                min="0"
                placeholder="0"
                value={progressInput.runs_done}
                onChange={(e) => handleInputChange('runs_done', e.target.value)}
                className="bg-gray-700/50 border-gray-600 text-white"
                disabled={isLoading}
              />
            </div>
          </div>
          
          <div className="space-y-2">
            <label htmlFor="notes-input" className="text-sm text-gray-300">
              Additional Notes
            </label>
            <Textarea
              id="notes-input"
              placeholder="Any challenges, achievements, or feedback about your workouts..."
              value={progressInput.notes}
              onChange={(e) => handleInputChange('notes', e.target.value)}
              className="bg-gray-700/50 border-gray-600 text-white min-h-[100px]"
              disabled={isLoading}
            />
          </div>

          <div className="flex space-x-2">
            <Button 
              onClick={handleAnalyzeProgress}
              className="bg-gradient-to-r from-green-500 to-cyan-500 hover:from-green-600 hover:to-cyan-600 text-white font-semibold"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 size={16} className="mr-2 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Play size={16} className="mr-2" />
                  Analyze Progress
                </>
              )}
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

          {/* Trystero's Response */}
          {trysteroResponseText && (
            <div className="mt-4 p-4 bg-gray-700/30 rounded-lg border border-green-500/20">
              <h3 className="text-green-400 font-semibold mb-2">Trystero's Analysis</h3>
              <div className="text-gray-300 text-sm whitespace-pre-line">
                {trysteroResponseText}
              </div>
            </div>
          )}
          
          {/* Briefing for Next Plan */}
          {trysteroBriefing && (
            <div className="mt-4 p-4 bg-gray-700/30 rounded-lg border border-cyan-500/20">
              <h3 className="text-cyan-400 font-semibold mb-2">Briefing for Next Plan</h3>
              <div className="text-gray-300 text-sm">
                <pre className="whitespace-pre-wrap font-sans">
                  {JSON.stringify(trysteroBriefing, null, 2)}
                </pre>
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