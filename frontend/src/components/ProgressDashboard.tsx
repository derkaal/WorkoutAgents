import React, { useState, useEffect } from 'react';
import { Bar } from 'react-chartjs-2';
import { ArrowLeft, Volume2, HelpCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { apiService, ProgressResponse } from '../services/apiService';
import { audioService } from '../services/audioService';
import { Trystero } from '../agents/Trystero';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface ProgressDashboardProps {
  onBack: () => void;
  voiceEnabled: boolean;
}

export const ProgressDashboard: React.FC<ProgressDashboardProps> = ({ 
  onBack, 
  voiceEnabled 
}) => {
  const [progressData, setProgressData] = useState<any>(null);
  const [insights, setInsights] = useState<string>('');
  const [detailedFeedback, setDetailedFeedback] = useState<string>('');
  const [progressAudio, setProgressAudio] = useState<string>('');
  const [showReasoning, setShowReasoning] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [stats, setStats] = useState({
    totalWorkouts: 0,
    totalHours: 0,
    workoutTypes: 0
  });

  useEffect(() => {
    loadProgressData();
  }, []);

  const loadProgressData = async () => {
    setIsLoading(true);
    try {
      const progressResponse = await apiService.analyzeProgress();
      
      // Set insights and audio
      setInsights(progressResponse.insights);
      setProgressAudio(progressResponse.audio_insight || '');
      setDetailedFeedback(progressResponse.detailed_feedback);
      
      // Process chart data
      if (progressResponse.chart_data) {
        const chartData = {
          labels: progressResponse.chart_data.labels,
          datasets: [
            {
              label: 'Workouts Completed',
              data: progressResponse.chart_data.data,
              backgroundColor: [
                'rgba(6, 182, 212, 0.8)', // cyan
                'rgba(168, 85, 247, 0.8)', // purple
                'rgba(34, 197, 94, 0.8)',  // green
                'rgba(251, 146, 60, 0.8)', // orange
              ],
              borderColor: [
                'rgba(6, 182, 212, 1)',
                'rgba(168, 85, 247, 1)',
                'rgba(34, 197, 94, 1)',
                'rgba(251, 146, 60, 1)',
              ],
              borderWidth: 2,
            },
          ],
        };
        setProgressData(chartData);
        
        // Calculate stats from chart data
        const totalWorkouts = progressResponse.chart_data.data.reduce((sum, count) => sum + count, 0);
        const workoutTypes = progressResponse.chart_data.labels.length;
        const totalHours = Math.round(totalWorkouts * 30 / 60); // Assuming 30min per workout
        
        setStats({
          totalWorkouts,
          totalHours,
          workoutTypes
        });
      }
    } catch (error) {
      console.error('Error loading progress data:', error);
      setInsights('Complete your first workout to see progress insights.');
      // Set fallback chart data
      setProgressData({
        labels: [],
        datasets: [{
          label: 'Workouts Completed',
          data: [],
          backgroundColor: [],
          borderColor: [],
          borderWidth: 2,
        }]
      });
    } finally {
      setIsLoading(false);
    }
  };

  const loadDetailedFeedback = async () => {
    try {
      const feedbackData = await apiService.getDetailedFeedback();
      setDetailedFeedback(feedbackData.reasoning);
    } catch (error) {
      console.error('Error loading detailed feedback:', error);
    }
  };

  const playProgress = async () => {
    if (!voiceEnabled) return;
    
    try {
      if (progressAudio) {
        await audioService.playBase64Audio(progressAudio);
      } else {
        // Fallback to speech synthesis
        if ('speechSynthesis' in window) {
          const utterance = new SpeechSynthesisUtterance(insights);
          speechSynthesis.speak(utterance);
        }
      }
    } catch (error) {
      console.error('Error playing progress:', error);
    }
  };

  const toggleReasoning = async () => {
    if (!showReasoning && !detailedFeedback) {
      await loadDetailedFeedback();
    }
    setShowReasoning(!showReasoning);
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          color: '#ffffff',
        },
      },
      title: {
        display: true,
        text: 'Workout Types Completed',
        color: '#ffffff',
        font: {
          size: 16,
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          color: '#ffffff',
          stepSize: 1,
        },
        grid: {
          color: 'rgba(255, 255, 255, 0.1)',
        },
      },
      x: {
        ticks: {
          color: '#ffffff',
          maxRotation: 45,
        },
        grid: {
          color: 'rgba(255, 255, 255, 0.1)',
        },
      },
    },
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-cyan-400 text-xl">Loading your progress...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-4">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between pt-8">
          <Button
            variant="ghost"
            onClick={onBack}
            className="text-white hover:text-cyan-400"
            id="progress-back-btn"
          >
            <ArrowLeft size={20} className="mr-2" />
            Back
          </Button>
          <h1 className="text-2xl font-bold text-white">Progress Dashboard</h1>
        </div>

        {/* Chart Card */}
        <Card className="bg-gray-800/50 border-cyan-500/30 shadow-2xl">
          <CardHeader>
            <CardTitle className="text-cyan-400 text-xl">Workout Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            {progressData && progressData.labels.length > 0 ? (
              <div className="h-64">
                <Bar data={progressData} options={chartOptions} />
              </div>
            ) : (
              <div className="h-64 flex items-center justify-center text-gray-400">
                <p>No workout data available yet. Complete your first workout!</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Trystero's Insights */}
        <Card className="bg-gray-800/30 border-green-500/30 shadow-xl">
          <CardHeader>
            <CardTitle className="text-green-400 text-xl flex items-center justify-between">
              Trystero's Analysis
              <div className="flex gap-2">
                {voiceEnabled && (
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={playProgress}
                    className="text-green-400 hover:text-green-300"
                    id="play-analysis-btn"
                  >
                    <Volume2 size={16} />
                  </Button>
                )}
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={toggleReasoning}
                  className="text-green-400 hover:text-green-300"
                  id="toggle-reasoning-btn"
                >
                  <HelpCircle size={16} />
                </Button>
              </div>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-gray-300" id="trystero-analysis-text">{insights}</p>
            
            {showReasoning && (
              <div className="bg-gray-700/50 p-4 rounded-lg border-l-4 border-green-500">
                <h4 className="text-green-400 font-semibold mb-2">Why this feedback?</h4>
                <p className="text-gray-300 text-sm" id="detailed-feedback-text">{detailedFeedback}</p>
                <p className="text-gray-400 text-xs mt-2">
                  Trystero analyzes your workout patterns, frequency, and balance to provide 
                  personalized insights for optimal progress.
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card className="bg-gray-800/30 border-purple-500/30">
            <CardContent className="pt-6 text-center">
              <div className="text-2xl font-bold text-purple-400" id="total-workouts-stat">
                {stats.totalWorkouts}
              </div>
              <div className="text-gray-400 text-sm">Total Workouts</div>
            </CardContent>
          </Card>

          <Card className="bg-gray-800/30 border-cyan-500/30">
            <CardContent className="pt-6 text-center">
              <div className="text-2xl font-bold text-cyan-400" id="total-hours-stat">
                {stats.totalHours}h
              </div>
              <div className="text-gray-400 text-sm">Time Trained</div>
            </CardContent>
          </Card>

          <Card className="bg-gray-800/30 border-green-500/30">
            <CardContent className="pt-6 text-center">
              <div className="text-2xl font-bold text-green-400" id="workout-types-stat">
                {stats.workoutTypes}
              </div>
              <div className="text-gray-400 text-sm">Workout Types</div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};
