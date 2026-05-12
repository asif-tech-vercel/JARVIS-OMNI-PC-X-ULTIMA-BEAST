"""
JARVIS Browser Control
Web automation using Playwright/Selenium.
"""

import os
import time
from typing import Optional, Dict, Any, List

try:
    from playwright.sync_api import sync_playwright, Browser, Page, Element
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    HAS_SELENIUM = True
except ImportError:
    HAS_SELENIUM = False

from jarvis_core.logger import get_logger


logger = get_logger()


class BrowserControl:
    """Web browser automation."""
    
    def __init__(self, browser_type: str = "chromium"):
        self.browser_type = browser_type
        self.playwright = None
        self.browser = None
        self.page = None
        self.driver = None
        self.headless = False
    
    # ==================== BROWSER CONTROL ====================
    
    def open(self, url: str = "about:blank", headless: bool = False) -> Dict[str, Any]:
        """Open browser and navigate to URL."""
        self.headless = headless
        
        if HAS_PLAYWRIGHT:
            return self._open_playwright(url)
        elif HAS_SELENIUM:
            return self._open_selenium(url)
        else:
            return {"success": False, "error": "No browser automation available"}
    
    def _open_playwright(self, url: str) -> Dict[str, Any]:
        """Open with Playwright."""
        try:
            if not self.playwright:
                self.playwright = sync_playwright().start()
            
            if not self.browser:
                self.browser = self.playwright[self.browser_type].launch(
                    headless=self.headless
                )
            
            if not self.page:
                self.page = self.browser.new_page()
            
            self.page.goto(url)
            
            logger.action(f"Open browser: {url}", "SUCCESS", "low")
            return {"success": True, "url": url}
            
        except Exception as e:
            logger.error(f"Failed to open browser: {e}")
            return {"success": False, "error": str(e)}
    
    def _open_selenium(self, url: str) -> Dict[str, Any]:
        """Open with Selenium."""
        try:
            options = webdriver.ChromeOptions()
            if self.headless:
                options.add_argument("--headless")
            
            self.driver = webdriver.Chrome(options=options)
            self.driver.get(url)
            
            logger.action(f"Open browser: {url}", "SUCCESS", "low")
            return {"success": True, "url": url}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def close(self) -> Dict[str, Any]:
        """Close the browser."""
        try:
            if HAS_PLAYWRIGHT:
                if self.page:
                    self.page.close()
                    self.page = None
                if self.browser:
                    self.browser.close()
                    self.browser = None
                if self.playwright:
                    self.playwright.stop()
                    self.playwright = None
            
            elif HAS_SELENIUM and self.driver:
                self.driver.quit()
                self.driver = None
            
            logger.action("Close browser", "SUCCESS", "low")
            return {"success": True}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ==================== NAVIGATION ====================
    
    def navigate(self, url: str) -> Dict[str, Any]:
        """Navigate to URL."""
        try:
            if HAS_PLAYWRIGHT and self.page:
                self.page.goto(url)
            elif HAS_SELENIUM and self.driver:
                self.driver.get(url)
            
            logger.action(f"Navigate: {url}", "SUCCESS", "low")
            return {"success": True, "url": url}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def go_back(self) -> Dict[str, Any]:
        """Go back in history."""
        try:
            if HAS_PLAYWRIGHT and self.page:
                self.page.go_back()
            elif HAS_SELENIUM and self.driver:
                self.driver.back()
            return {"success": True}
        except:
            return {"success": False, "error": "Navigation failed"}
    
    def go_forward(self) -> Dict[str, Any]:
        """Go forward in history."""
        try:
            if HAS_PLAYWRIGHT and self.page:
                self.page.go_forward()
            elif HAS_SELENIUM and self.driver:
                self.driver.forward()
            return {"success": True}
        except:
            return {"success": False, "error": "Navigation failed"}
    
    def reload(self) -> Dict[str, Any]:
        """Reload the page."""
        try:
            if HAS_PLAYWRIGHT and self.page:
                self.page.reload()
            elif HAS_SELENIUM and self.driver:
                self.driver.refresh()
            return {"success": True}
        except:
            return {"success": False, "error": "Reload failed"}
    
    # ==================== SEARCH ====================
    
    def search(self, query: str, engine: str = "google") -> Dict[str, Any]:
        """Search the web."""
        engines = {
            "google": "https://google.com/search?q=",
            "bing": "https://www.bing.com/search?q=",
            "duckduckgo": "https://duckduckgo.com/?q=",
            "youtube": "https://www.youtube.com/results?search_query="
        }
        
        if engine.lower() not in engines:
            engine = "google"
        
        url = engines[engine.lower()] + query.replace(" ", "+")
        return self.navigate(url)
    
    def search_google(self, query: str) -> Dict[str, Any]:
        """Search Google."""
        return self.search(query, "google")
    
    def search_youtube(self, query: str) -> Dict[str, Any]:
        """Search YouTube."""
        return self.search(query, "youtube")
    
    # ==================== ELEMENTS ====================
    
    def click(self, selector: str) -> Dict[str, Any]:
        """Click element by selector."""
        try:
            if HAS_PLAYWRIGHT and self.page:
                self.page.click(selector)
            elif HAS_SELENIUM and self.driver:
                self.driver.find_element(By.CSS_SELECTOR, selector).click()
            
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def type(self, selector: str, text: str, clear_first: bool = True) -> Dict[str, Any]:
        """Type into element."""
        try:
            if HAS_PLAYWRIGHT and self.page:
                if clear_first:
                    self.page.fill(selector, text)
                else:
                    self.page.type(selector, text)
            elif HAS_SELENIUM and self.driver:
                elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                if clear_first:
                    elem.clear()
                elem.send_keys(text)
            
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def select(self, selector: str, value: str) -> Dict[str, Any]:
        """Select option in select element."""
        try:
            if HAS_PLAYWRIGHT and self.page:
                self.page.select_option(selector, value)
            elif HAS_SELENIUM and self.driver:
                from selenium.webdriver.support.ui import Select
                select = Select(self.driver.find_element(By.CSS_SELECTOR, selector))
                select.select_by_value(value)
            
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ==================== CONTENT ====================
    
    def get_title(self) -> str:
        """Get page title."""
        try:
            if HAS_PLAYWRIGHT and self.page:
                return self.page.title()
            elif HAS_SELENIUM and self.driver:
                return self.driver.title
        except:
            return ""
    
    def get_url(self) -> str:
        """Get current URL."""
        try:
            if HAS_PLAYWRIGHT and self.page:
                return self.page.url
            elif HAS_SELENIUM and self.driver:
                return self.driver.current_url
        except:
            return ""
    
    def get_text(self, selector: str = None) -> str:
        """Get text content."""
        try:
            if HAS_PLAYWRIGHT and self.page:
                if selector:
                    return self.page.inner_text(selector)
                else:
                    return self.page.content()
            elif HAS_SELENIUM and self.driver:
                if selector:
                    return self.driver.find_element(By.CSS_SELECTOR, selector).text
                else:
                    return self.driver.page_source
        except:
            return ""
    
    def get_links(self) -> List[str]:
        """Get all links on page."""
        try:
            if HAS_PLAYWRIGHT and self.page:
                links = self.page.query_selector_all("a")
                return [link.get_attribute("href") for link in links if link]
            elif HAS_SELENIUM and self.driver:
                links = self.driver.find_elements(By.TAG_NAME, "a")
                return [link.get_attribute("href") for link in links if link]
        except:
            return []
    
    # ==================== DOWNLOADS ====================
    
    def download(self, url: str, filepath: str = None) -> Dict[str, Any]:
        """Download file."""
        try:
            if not filepath:
                # Use Downloads folder
                filepath = os.path.join(
                    os.path.expanduser("~"),
                    "Downloads",
                    url.split("/")[-1]
                )
            
            # Simple download with requests
            import requests
            response = requests.get(url)
            
            with open(filepath, "wb") as f:
                f.write(response.content)
            
            logger.action(f"Download: {filepath}", "SUCCESS", "medium")
            return {"success": True, "filepath": filepath}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ==================== SCREENSHOTS ====================
    
    def screenshot(self, filepath: str = None) -> str:
        """Take browser screenshot."""
        try:
            if not filepath:
                filepath = f"logs/browser_{int(time.time())}.png"
            
            if HAS_PLAYWRIGHT and self.page:
                self.page.screenshot(path=filepath)
                return filepath
            elif HAS_SELENIUM and self.driver:
                self.driver.save_screenshot(filepath)
                return filepath
                
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            return None


# Global browser control
_browser = None


def get_browser(browser_type: str = "chromium") -> BrowserControl:
    """Get or create browser control."""
    global _browser
    if _browser is None:
        _browser = BrowserControl(browser_type)
    return _browser


# Convenience functions
def open_browser(url: str = "about:blank") -> Dict[str, Any]:
    """Quick open browser."""
    return get_browser().open(url)

def search_web(query: str) -> Dict[str, Any]:
    """Quick search."""
    return get_browser().search_google(query)