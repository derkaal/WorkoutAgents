
import { API_CONFIG } from '../config';
import { apiClient, ApiError } from './apiClient';

const API_BASE_URL = API_CONFIG.API_URL;

export interface WorkoutResponse {
  workout_id?: string;
  type?: string;
  intro?: string;
  generated_plan?: {
    exercises: Array<{
      name: string;
      duration: number;
      instruction: string;
      image?: string;
    }>;
  };
  audio_intro?: string; // Base64 encoded audio
  
  // Additional properties from backend schema
  mike_response_text?: string;
  audio_base64?: string;
}

export interface ProgressResponse {
  insights: string;
  detailed_feedback: string;
  chart_data: {
    labels: string[];
    data: number[];
  };
  audio_insight?: string; // Base64 encoded audio
  briefing_for_next_plan?: object | null; // Briefing from Trystero for Mike
  trystero_feedback_text?: string; // Alternative property name used in backend
}

export interface WorkoutCompletionResponse {
  message: string;
  audio_completion?: string; // Base64 encoded audio
}

class ApiService {
  private async makeRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`API call failed: ${response.statusText}`);
    }

    return response.json();
  }

  async generateWorkout(userPreferences: any = {}): Promise<WorkoutResponse> {
    return this.makeRequest<WorkoutResponse>('/generate-workout/', {
      method: 'POST',
      body: JSON.stringify(userPreferences),
    });
  }

  async switchWorkout(currentWorkout: any): Promise<WorkoutResponse> {
    return this.makeRequest<WorkoutResponse>('/switch-workout/', {
      method: 'POST',
      body: JSON.stringify({ current_workout: currentWorkout }),
    });
  }

  async analyzeProgress(): Promise<ProgressResponse> {
    return this.makeRequest<ProgressResponse>('/analyze-progress/');
  }

  async logWorkoutCompletion(workoutData: any): Promise<WorkoutCompletionResponse> {
    return this.makeRequest<WorkoutCompletionResponse>('/log-workout/', {
      method: 'POST',
      body: JSON.stringify(workoutData),
    });
  }

  async getExerciseInstructions(exerciseName: string): Promise<{ instructions: string; audio?: string }> {
    return this.makeRequest<{ instructions: string; audio?: string }>(`/exercise-instructions/${encodeURIComponent(exerciseName)}/`);
  }

  async getDetailedFeedback(): Promise<{ reasoning: string; audio?: string }> {
    return this.makeRequest<{ reasoning: string; audio?: string }>('/detailed-feedback/');
  }
}

export const apiService = new ApiService();

// For Mike Lawry's workout generation
export const generateWorkout = async (preferences: {
  userInput: string;
  trysteroBriefing?: object | string | null
}): Promise<WorkoutResponse> => {
  try {
    // Transform the request to match the backend's expected format
    const transformedRequest = {
      user_input: preferences.userInput,
      trystero_briefing: preferences.trysteroBriefing
    };
    
    const response = await apiClient.post<WorkoutResponse>('/generate-workout/', transformedRequest);
    return response.data;
  } catch (error) {
    if (error instanceof ApiError) {
      console.error('Workout generation failed:', error.message);
      throw error;
    }
    throw new Error(`Failed to generate workout: ${error instanceof Error ? error.message : String(error)}`);
  }
};

// For Trystero's progress analysis
export const analyzeProgress = async (workoutHistory: {
  progress_data: object
}): Promise<ProgressResponse> => {
  try {
    const response = await apiClient.post<ProgressResponse>('/analyze-progress/', workoutHistory);
    return response.data;
  } catch (error) {
    if (error instanceof ApiError) {
      console.error('Progress analysis failed:', error.message);
      throw error;
    }
    throw new Error(`Failed to analyze progress: ${error instanceof Error ? error.message : String(error)}`);
  }
};
