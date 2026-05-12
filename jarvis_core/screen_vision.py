"""
JARVIS Screen Vision - OCR and Element Detection
Screenshot, OCR, button detection, vision-based clicking.
"""

import os
import time
from typing import Tuple, Optional, List, Dict, Any

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False

try:
    import pytesseract
    HAS_TESSERACT = True
except ImportError:
    HAS_TESSERACT = False

try:
    import mss
    HAS_MSS = True
except ImportError:
    HAS_MSS = False

try:
    from PIL import Image, ImageEnhance
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

from jarvis_core.logger import get_logger


logger = get_logger()


class ScreenVision:
    """
    Screen vision capabilities - capture, OCR, element detection.
    """
    
    def __init__(self, tesseract_cmd: str = None):
        self.tesseract_cmd = tesseract_cmd
        self.screenshot_dir = "logs/screenshots"
        os.makedirs(self.screenshot_dir, exist_ok=True)
        
        # Configure tesseract if path provided
        if tesseract_cmd and HAS_TESSERACT:
            import pytesseract
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    
    # ==================== SCREENSHOT ====================
    
    def capture(self, filename: str = None, region: Tuple[int, int, int, int] = None) -> str:
        """
        Capture screenshot.
        
        Args:
            filename: Output filename (None = auto-generate)
            region: x, y, width, height (None = full screen)
        
        Returns:
            Path to captured image
        """
        if not HAS_MSS:
            return self._capture_fallback(filename, region)
        
        try:
            with mss.mss() as sct:
                if region:
                    x, y, w, h = region
                    monitor = {"top": y, "left": x, "width": w, "height": h}
                else:
                    monitor = sct.monitors[0]
                
                # Capture
                if filename is None:
                    filename = f"screenshot_{int(time.time())}.png"
                
                path = os.path.join(self.screenshot_dir, filename)
                sct.shot(output=path, mon=monitor)
                
                logger.action(f"Capture screenshot: {filename}", "SUCCESS", "low")
                return path
                
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            return None
    
    def _capture_fallback(self, filename: str, region) -> str:
        """Fallback screenshot using PIL."""
        if not HAS_PIL:
            return None
        
        # Not ideal but try
        logger.warning("Using fallback screenshot")
        
        if filename is None:
            filename = f"screenshot_{int(time.time())}.png"
        
        path = os.path.join(self.screenshot_dir, filename)
        
        try:
            # Create a basic screenshot
            # This won't work without proper mss
            logger.error(f"Cannot capture: mss not available")
            return None
        except:
            return None
    
    def capture_window(self, title: str, filename: str = None) -> str:
        """Capture specific window."""
        if not HAS_CV2 or not HAS_MSS:
            return None
        
        try:
            # Find window (simplified - would need pygetwindow)
            # For now just capture full screen
            return self.capture(filename)
        except Exception as e:
            logger.error(f"Window capture failed: {e}")
            return None
    
    # ==================== OCR ====================
    
    def read_text(self, image_path: str = None, region: Tuple = None) -> str:
        """
        Read text from image or screen region.
        
        Args:
            image_path: Path to image (None = take screenshot)
            region: screen region to capture
        
        Returns:
            Extracted text
        """
        if not image_path and not HAS_MSS:
            return None
        
        # Capture if no image provided
        if not image_path:
            image_path = self.capture(region=region)
            if not image_path:
                return None
        
        if not os.path.exists(image_path):
            return None
        
        if not HAS_TESSERACT:
            return self._read_text_basic(image_path)
        
        try:
            # Read with tesseract
            text = pytesseract.image_to_string(Image.open(image_path))
            
            logger.info(f"OCR read {len(text)} characters")
            return text.strip()
            
        except Exception as e:
            logger.error(f"OCR failed: {e}")
            return None
    
    def _read_text_basic(self, image_path: str) -> str:
        """Basic text reading fallback."""
        # Would need easyocr or other
        logger.warning("Tesseract not available")
        return None
    
    def read_boxes(self, image_path: str = None) -> List[Dict]:
        """
        Read text with bounding boxes.
        
        Returns:
            List of {'text': str, 'box': (x1,y1,x2,y2)}
        """
        if not image_path:
            return []
        
        if not HAS_TESSERACT:
            return []
        
        try:
            img = Image.open(image_path)
            
            # Get boxes
            boxes = pytesseract.image_to_data(
                img,
                output_type=pytesseract.Output.DICT
            )
            
            results = []
            n_boxes = len(boxes['text'])
            
            for i in range(n_boxes):
                text = boxes['text'][i].strip()
                if text:
                    x = boxes['left'][i]
                    y = boxes['top'][i]
                    w = boxes['width'][i]
                    h = boxes['height'][i]
                    
                    results.append({
                        'text': text,
                        'box': (x, y, x + w, y + h),
                        'confidence': boxes['conf'][i]
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Box detection failed: {e}")
            return []
    
    # ==================== ELEMENT DETECTION ====================
    
    def find_text(self, text: str, image_path: str = None) -> Tuple[int, int]:
        """
        Find text on screen and return coordinates.
        
        Returns:
            (x, y) center of text or None
        """
        boxes = self.read_boxes(image_path)
        
        for box in boxes:
            if text.lower() in box['text'].lower():
                # Calculate center
                x1, y1, x2, y2 = box['box']
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                
                logger.info(f"Found text '{text}' at ({center_x}, {center_y})")
                return (center_x, center_y)
        
        return None
    
    def find_image(self, template_path: str, confidence: float = 0.8) -> Tuple[int, int]:
        """
        Find image template on screen.
        
        Args:
            template_path: Path to template image
            confidence: Match confidence (0-1)
        
        Returns:
            (x, y) center of match or None
        """
        if not HAS_CV2:
            return None
        
        try:
            # Capture screen
            screen_path = self.capture()
            if not screen_path:
                return None
            
            # Load images
            screen = cv2.imread(screen_path)
            template = cv2.imread(template_path)
            
            if screen is None or template is None:
                return None
            
            # Match template
            result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val >= confidence:
                # Calculate center
                h, w = template.shape[:2]
                center_x = max_loc[0] + w // 2
                center_y = max_loc[1] + h // 2
                
                logger.info(f"Found template at ({center_x}, {center_y})")
                return (center_x, center_y)
            
            return None
            
        except Exception as e:
            logger.error(f"Template matching failed: {e}")
            return None
    
    def find_button(self, button_text: str) -> Optional[Tuple[int, int]]:
        """
        Find button by text.
        
        Returns:
            Button center coordinates
        """
        # Take screenshot and find text
        screen_path = self.capture()
        if not screen_path:
            return None
        
        boxes = self.read_boxes(screen_path)
        
        for box in boxes:
            if button_text.lower() in box['text'].lower():
                x1, y1, x2, y2 = box['box']
                return ((x1 + x2) // 2, (y1 + y2) // 2)
        
        return None
    
    # ==================== REGION DETECTION ====================
    
    def detect_windows(self) -> List[Dict]:
        """Detect window regions on screen."""
        if not HAS_CV2:
            return []
        
        # Would need proper window detection
        # Simplified - just detect UI elements
        screen_path = self.capture()
        if not screen_path:
            return []
        
        boxes = self.read_boxes(screen_path)
        
        # Filter for likely buttons/labels
        ui_elements = []
        for box in boxes:
            text = box['text']
            if len(text) < 30:  # Likely UI text
                ui_elements.append({
                    'text': text,
                    'box': box['box']
                })
        
        return ui_elements
    
    def is_loading(self) -> bool:
        """Detect if screen shows loading spinner."""
        # Would need more sophisticated detection
        screen_path = self.capture()
        if not screen_path:
            return False
        
        # Check for common loading text
        text = self.read_text(screen_path)
        loading_indicators = ["loading", "please wait", "processing", "spinner"]
        
        text_lower = text.lower() if text else ""
        return any(ind in text_lower for ind in loading_indicators)


# Global screen vision instance
_screen_vision = None


def get_screen_vision(
    tesseract_cmd: str = None
) -> ScreenVision:
    """Get or create screen vision."""
    global _screen_vision
    if _screen_vision is None:
        _screen_vision = ScreenVision(tesseract_cmd)
    return _screen_vision


def capture_screen(region: Tuple = None) -> str:
    """Quick screen capture."""
    return get_screen_vision().capture(region=region)


def read_screen_text() -> str:
    """Quick text read from screen."""
    return get_screen_vision().read_text()


def click_text(text: str) -> Tuple[int, int]:
    """Find and return click coordinates for text."""
    return get_screen_vision().find_text(text)