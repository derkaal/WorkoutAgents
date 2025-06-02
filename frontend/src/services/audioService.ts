/**
 * Audio Service
 * 
 * This service provides functionality for playing audio content,
 * including base64 encoded audio and text-to-speech fallback.
 */

/**
 * AudioService class for handling audio playback in the application
 */
export class AudioService {
  private currentAudio: HTMLAudioElement | null = null;
  private isSpeaking: boolean = false;

  /**
   * Plays audio content from either a base64 string or falls back to speech synthesis
   * 
   * @param audioBase64 - Optional base64 encoded audio string (typically MP3 format)
   * @param textFallback - Optional text to be used for speech synthesis if audio playback fails or is not provided
   * @returns Promise that resolves when audio playback starts or rejects if all playback methods fail
   * 
   * @example
   * // Play base64 audio with text fallback
   * await audioService.playAgentAudio(base64AudioString, "Hello, this is fallback text");
   * 
   * @example
   * // Use only text-to-speech
   * await audioService.playAgentAudio(null, "This will be spoken using speech synthesis");
   */
  async playAgentAudio(audioBase64?: string | null, textFallback?: string): Promise<void> {
    // Stop any currently playing audio first
    this.stopAudio();

    // Try to play base64 audio if provided
    if (audioBase64) {
      try {
        const audio = new Audio(`data:audio/mp3;base64,${audioBase64}`);
        
        // Set up event listeners for tracking playback state
        audio.addEventListener('ended', () => {
          this.currentAudio = null;
        });
        
        audio.addEventListener('error', (e) => {
          console.error('Error playing audio:', e);
          this.currentAudio = null;
          
          // If audio playback fails and we have a text fallback, try speech synthesis
          if (textFallback) {
            this.useSpeechSynthesis(textFallback).catch(err => {
              console.error('Speech synthesis fallback also failed:', err);
            });
          }
        });
        
        // Start playback
        await audio.play();
        this.currentAudio = audio;
        return;
      } catch (error) {
        console.error('Failed to play base64 audio:', error);
        // Continue to speech synthesis fallback if available
      }
    }
    
    // If we reach here, either:
    // 1. No base64 audio was provided, or
    // 2. Base64 audio playback failed
    // Try speech synthesis if text fallback is available
    if (textFallback) {
      try {
        await this.useSpeechSynthesis(textFallback);
      } catch (error) {
        console.error('Speech synthesis failed:', error);
        throw new Error('All audio playback methods failed');
      }
    }
  }

  /**
   * Uses the Web Speech API for text-to-speech synthesis
   * 
   * @param text - The text to be spoken
   * @returns Promise that resolves when speech begins or rejects if speech synthesis is unavailable
   * @private
   */
  private useSpeechSynthesis(text: string): Promise<void> {
    return new Promise((resolve, reject) => {
      // Check if speech synthesis is available in the browser
      if (!window.speechSynthesis) {
        reject(new Error('Speech synthesis not supported in this browser'));
        return;
      }

      try {
        // Create a new utterance with the provided text
        const utterance = new SpeechSynthesisUtterance(text);
        
        // Set up event listeners
        utterance.onstart = () => {
          this.isSpeaking = true;
          resolve();
        };
        
        utterance.onend = () => {
          this.isSpeaking = false;
        };
        
        utterance.onerror = (event) => {
          this.isSpeaking = false;
          reject(new Error(`Speech synthesis error: ${event.error}`));
        };
        
        // Start speaking
        window.speechSynthesis.speak(utterance);
      } catch (error) {
        reject(error);
      }
    });
  }

  /**
   * Stops any currently playing audio or speech
   * 
   * @example
   * // Stop current audio playback
   * audioService.stopAudio();
   */
  stopAudio(): void {
    // Stop HTML Audio element if it exists
    if (this.currentAudio) {
      this.currentAudio.pause();
      this.currentAudio.currentTime = 0;
      this.currentAudio = null;
    }
    
    // Stop speech synthesis if it's active
    if (window.speechSynthesis && this.isSpeaking) {
      window.speechSynthesis.cancel();
      this.isSpeaking = false;
    }
  }

  /**
   * Checks if audio is currently playing
   * 
   * @returns Boolean indicating whether audio is currently playing
   * 
   * @example
   * if (audioService.isPlaying()) {
   *   console.log('Audio is currently playing');
   * }
   */
  isPlaying(): boolean {
    return !!(this.currentAudio && !this.currentAudio.paused) || this.isSpeaking;
  }
}

/**
 * Default audio service instance
 */
export const audioService = new AudioService();
