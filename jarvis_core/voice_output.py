"""
JARVIS Voice Output - Text-to-Speech
Uses pyttsx3 or coqui-tts for offline TTS.
"""

import threading
import time
from typing import Optional

try:
    import pyttsx3
    HAS_TTS = True
except ImportError:
    HAS_TTS = False

try:
    from TTS.api import TTS
    HAS_COQUI = True
except ImportError:
    HAS_COQUI = False

from jarvis_core.logger import get_logger


logger = get_logger()


class VoiceOutput:
    """
    Voice output handler for JARVIS.
    Supports pyttsx3 (offline) and coqui-tts.
    """
    
    def __init__(
        self,
        engine: str = "pyttsx3",
        rate: int = 150,
        volume: float = 1.0,
        voice: str = None
    ):
        self.engine_type = engine
        self.rate = rate
        self.volume = volume
        self.voice = voice
        self.speaking = False
        self.interrupted = False
        self._init_engine()
    
    def _init_engine(self):
        """Initialize the TTS engine."""
        if self.engine_type == "pyttsx3" and HAS_TTS:
            try:
                self.engine = pyttsx3.init()
                self.engine.setProperty('rate', self.rate)
                self.engine.setProperty('volume', self.volume)
                
                # Set voice if specified
                if self.voice:
                    voices = self.engine.getProperty('voices')
                    for v in voices:
                        if self.voice.lower() in v.name.lower():
                            self.engine.setProperty('voice', v.id)
                            break
                
                logger.info("Initialized pyttsx3 engine")
                
            except Exception as e:
                logger.error(f"Failed to init pyttsx3: {e}")
                self.engine = None
        
        elif self.engine_type == "coqui" and HAS_COQUI:
            try:
                # Use coqui TTS
                self.tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DCA", gpu=False)
                logger.info("Initialized coqui-tts engine")
            except Exception as e:
                logger.error(f"Failed to init coqui: {e}")
                self.tts = None
    
    def speak(self, text: str, async_mode: bool = False):
        """
        Speak text to speech.
        
        Args:
            text: Text to speak
            async_mode: If True, don't wait for completion
        """
        if not text:
            return
        
        self.interrupted = False
        self.speaking = True
        
        logger.info(f"Speaking: {text[:50]}...")
        
        if self.engine_type == "pyttsx3" and self.engine:
            self._speak_pyttsx3(text, async_mode)
        
        elif self.engine_type == "coqui" and hasattr(self, 'tts') and self.tts:
            self._speak_coqui(text, async_mode)
        
        else:
            # Fallback - just log
            logger.warning(f"Would speak (no TTS): {text}")
            self.speaking = False
    
    def _speak_pyttsx3(self, text: str, async_mode: bool = False):
        """Speak using pyttsx3."""
        def speak():
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                logger.error(f"TTS error: {e}")
            finally:
                self.speaking = False
        
        if async_mode:
            thread = threading.Thread(target=speak, daemon=True)
            thread.start()
        else:
            speak()
    
    def _speak_coqui(self, text: str, async_mode: bool = False):
        """Speak using coqui-tts."""
        def speak():
            try:
                # Generate speech
                self.tts.tts_to_file(
                    text=text,
                    file_path="logs/tts_output.wav"
                )
                # Could play using playsound or similar
                logger.debug(f"Generated TTS to file")
            except Exception as e:
                logger.error(f"Coqui TTS error: {e}")
            finally:
                self.speaking = False
        
        if async_mode:
            thread = threading.Thread(target=speak, daemon=True)
            thread.start()
        else:
            speak()
    
    def stop(self):
        """Stop speaking."""
        if not self.speaking:
            return
        
        self.interrupted = True
        
        if self.engine_type == "pyttsx3" and self.engine:
            try:
                self.engine.stop()
            except:
                pass
        
        self.speaking = False
        logger.info("Stopped speaking")
    
    def set_rate(self, rate: int):
        """Set speech rate (words per minute)."""
        self.rate = max(50, min(300, rate))
        
        if self.engine_type == "pyttsx3" and self.engine:
            self.engine.setProperty('rate', self.rate)
        
        logger.info(f"Set rate to {self.rate}")
    
    def set_volume(self, volume: float):
        """Set volume (0.0 to 1.0)."""
        self.volume = max(0.0, min(1.0, volume))
        
        if self.engine_type == "pyttsx3" and self.engine:
            self.engine.setProperty('volume', self.volume)
        
        logger.info(f"Set volume to {self.volume}")
    
    def set_voice(self, voice: str):
        """Set voice by name."""
        self.voice = voice
        
        if self.engine_type == "pyttsx3" and self.engine:
            voices = self.engine.getProperty('voices')
            for v in voices:
                if voice.lower() in v.name.lower():
                    self.engine.setProperty('voice', v.id)
                    logger.info(f"Set voice to {v.name}")
                    break
    
    def get_voices(self) -> list:
        """Get available voices."""
        if self.engine_type == "pyttsx3" and self.engine:
            return [
                {"id": v.id, "name": v.name}
                for v in self.engine.getProperty('voices')
            ]
        return []
    
    def say(self, text: str):
        """Quick speak (same as speak)."""
        self.speak(text)


# Global voice output instance
_voice_output = None


def get_voice_output(
    engine: str = "pyttsx3",
    rate: int = 150
) -> VoiceOutput:
    """Get or create the voice output handler."""
    global _voice_output
    if _voice_output is None:
        _voice_output = VoiceOutput(engine=engine, rate=rate)
    return _voice_output


def speak(text: str):
    """Quick speak function."""
    get_voice_output().speak(text)


def say(text: str):
    """Quick say function."""
    get_voice_output().speak(text)