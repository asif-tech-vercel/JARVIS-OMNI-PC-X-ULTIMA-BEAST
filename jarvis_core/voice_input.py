"""
JARVIS Voice Input - Speech-to-Text
Uses Vosk or Whisper for offline STT.
"""

import threading
import queue
import time
from typing import Optional, Callable

try:
    import vosk
    HAS_VOSK = True
except ImportError:
    HAS_VOSK = False

try:
    import speech_recognition as sr
    HAS_SR = True
except ImportError:
    HAS_SR = False

from jarvis_core.logger import get_logger


logger = get_logger()


class VoiceInput:
    """
    Voice input handler for JARVIS.
    Supports Vosk (offline) and Google Speech Recognition.
    """
    
    def __init__(
        self,
        model_path: str = "models/vosk-model-en-us",
        sample_rate: int = 16000
    ):
        self.model_path = model_path
        self.sample_rate = sample_rate
        self.recognizer = None
        self.microphone = None
        self.listening = False
        self.wake_word_enabled = False
        self.wake_word = "jarvis"
        self.callback = None
        self.audio_queue = queue.Queue()
        self._init_recognizer()
    
    def _init_recognizer(self):
        """Initialize the speech recognizer."""
        if HAS_SR:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            
            # Try to calibrate for ambient noise
            try:
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                logger.debug("Microphone calibrated for ambient noise")
            except:
                logger.warning("Could not calibrate microphone")
    
    def start_listening(
        self,
        continuous: bool = False,
        callback: Optional[Callable] = None
    ) -> bool:
        """
        Start listening for voice input.
        
        Args:
            continuous: If True, keep listening indefinitely
            callback: Function to call with transcribed text
        
        Returns:
            True if started successfully
        """
        if not HAS_SR:
            logger.error("Speech recognition library not available")
            return False
        
        if self.listening:
            logger.warning("Already listening")
            return False
        
        self.callback = callback
        self.listening = True
        
        # Start listening in background
        if continuous:
            thread = threading.Thread(target=self._continuous_listen, daemon=True)
            thread.start()
        else:
            thread = threading.Thread(target=self._listen_once, daemon=True)
            thread.start()
        
        logger.info("Started voice listening")
        return True
    
    def stop_listening(self):
        """Stop listening for voice input."""
        self.listening = False
        logger.info("Stopped voice listening")
    
    def _listen_once(self):
        """Listen once and return result."""
        if not HAS_SR:
            return
        
        try:
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            # TryVosk first (offline)
            if HAS_VOSK:
                text = self._recognize_vosk(audio)
                if text:
                    self._handle_result(text)
                    return
            
            # Fallback to Google (online)
            text = self.recognizer.recognize_google(audio)
            self._handle_result(text)
            
        except sr.WaitTimeoutError:
            logger.debug("No speech detected within timeout")
        except sr.UnknownValueError:
            logger.debug("Speech not understood")
        except Exception as e:
            logger.error(f"Recognition error: {e}")
        finally:
            self.listening = False
    
    def _continuous_listen(self):
        """Continuously listen for voice input."""
        if not HAS_SR:
            return
        
        while self.listening:
            self._listen_once()
            time.sleep(0.1)
    
    def _recognize_vosk(self, audio) -> Optional[str]:
        """Recognize audio using Vosk."""
        if not HAS_VOSK or not hasattr(self, 'vosk_model'):
            return None
        
        try:
            # Get raw audio data
            raw_data = audio.get_raw_data()
            
            # Recognize
            if self.vosk_recognizer:
                result = self.vosk_recognizer.PartialResult()
                if result:
                    return result.get("partial", "")
                result = self.vosk_recognizer.FinalResult()
                if result:
                    return result.get("text", "")
        except:
            pass
        
        return None
    
    def _handle_result(self, text: str):
        """Handle recognized text."""
        logger.info(f"Voice input: {text}")
        
        # Check for wake word
        if self.wake_word_enabled:
            if self.wake_word.lower() in text.lower():
                # Remove wake word from command
                command = text.lower().replace(self.wake_word.lower(), "").strip()
                if command and self.callback:
                    self.callback(command)
        else:
            if self.callback:
                self.callback(text)
    
    def listen_keyword(self, keyword: str) -> Optional[str]:
        """
        Listen until a keyword is detected.
        
        Args:
            keyword: Keyword to listen for
        
        Returns:
            Transcribed text or None
        """
        if not HAS_SR:
            return None
        
        result_text = None
        
        def callback(text: str):
            nonlocal result_text
            if keyword.lower() in text.lower():
                result_text = text
                self.listening = False
        
        self.start_listening(callback=callback)
        
        # Wait for result
        while self.listening:
            time.sleep(0.1)
        
        return result_text
    
    def recognize_file(self, audio_file: str) -> Optional[str]:
        """
        Recognize audio from file.
        
        Args:
            audio_file: Path to audio file
        
        Returns:
            Transcribed text
        """
        if not HAS_SR:
            return None
        
        try:
            with sr.AudioFile(audio_file) as source:
                audio = self.recognizer.record(source)
            
            # Try Google first
            text = self.recognizer.recognize_google(audio)
            logger.info(f"File recognized: {text}")
            return text
            
        except Exception as e:
            logger.error(f"File recognition error: {e}")
            return None
    
    def load_vosk_model(self, model_path: str) -> bool:
        """Load Vosk model for offline recognition."""
        if not HAS_VOSK:
            logger.warning("Vosk not available")
            return False
        
        try:
            self.vosk_model = vosk.Model(model_path)
            self.vosk_recognizer = vosk.KaldiRecognizer(self.vosk_model, self.sample_rate)
            logger.info(f"Loaded Vosk model: {model_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load Vosk model: {e}")
            return False
    
    def set_wake_word(self, wake_word: str):
        """Set the wake word."""
        self.wake_word = wake_word
        self.wake_word_enabled = True
        logger.info(f"Wake word set to: {wake_word}")
    
    def enable_wake_word(self, enabled: bool = True):
        """Enable or disable wake word detection."""
        self.wake_word_enabled = enabled
        logger.info(f"Wake word {'enabled' if enabled else 'disabled'}")


# Global voice input instance
_voice_input = None


def get_voice_input(
    model_path: str = "models/vosk-model-en-us"
) -> VoiceInput:
    """Get or create the voice input handler."""
    global _voice_input
    if _voice_input is None:
        _voice_input = VoiceInput(model_path)
    return _voice_input