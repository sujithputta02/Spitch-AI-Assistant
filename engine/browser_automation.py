"""
Browser Automation Engine for Spitch AI Assistant
Provides automated web browsing, form filling, data extraction, and testing capabilities
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from typing import Optional, List, Dict, Any
import time
import os
from datetime import datetime


class BrowserAutomation:
    """Core browser automation engine using Selenium WebDriver"""
    
    def __init__(self):
        """Initialize browser automation engine"""
        self.driver: Optional[webdriver.Chrome] = None
        self.wait_timeout = 10
        self.screenshot_dir = "browser_screenshots"
        
        # Create screenshot directory if it doesn't exist
        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)
        
        print("[BrowserAutomation] Engine initialized")
    
    def initialize_driver(self, headless: bool = False) -> bool:
        """
        Initialize Chrome WebDriver
        
        Args:
            headless: Run browser in headless mode (no GUI)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.chrome.options import Options
            
            # Try to use webdriver-manager for automatic driver management
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                service = Service(ChromeDriverManager().install())
            except ImportError:
                # Fallback to system ChromeDriver
                print("[BrowserAutomation] webdriver-manager not found, using system ChromeDriver")
                service = Service()
            
            # Configure Chrome options
            options = Options()
            if headless:
                options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Initialize driver
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.maximize_window()
            
            # Add visual indicator that browser is under automation
            self._add_automation_indicator()
            
            print(f"[BrowserAutomation] Chrome driver initialized (headless={headless})")
            return True
            
        except Exception as e:
            print(f"[BrowserAutomation] Failed to initialize driver: {e}")
            return False
    
    def _add_automation_indicator(self):
        """Add visual indicator (Spitch AI branded border) to show browser is under automation"""
        if not self.driver:
            return
        
        try:
            # Inject CSS and create border element with Spitch AI colors
            script = """
            // Create automation indicator overlay with Spitch AI branding
            const indicator = document.createElement('div');
            indicator.id = 'spitch-automation-indicator';
            indicator.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                pointer-events: none;
                z-index: 2147483647;
                border: 5px solid transparent;
                border-image: linear-gradient(
                    135deg,
                    #8b5cf6,
                    #06b6d4,
                    #f43f5e,
                    #06b6d4,
                    #8b5cf6
                ) 1;
                animation: spitch-border-pulse 4s ease-in-out infinite;
                box-shadow: inset 0 0 30px rgba(139, 92, 246, 0.3);
            `;
            
            // Add keyframe animation
            const style = document.createElement('style');
            style.textContent = `
                @keyframes spitch-border-pulse {
                    0%, 100% {
                        border-width: 5px;
                        opacity: 0.9;
                        filter: brightness(1);
                    }
                    50% {
                        border-width: 6px;
                        opacity: 1;
                        filter: brightness(1.2);
                    }
                }
                
                @keyframes spitch-gradient-shift {
                    0% {
                        background-position: 0% 50%;
                    }
                    50% {
                        background-position: 100% 50%;
                    }
                    100% {
                        background-position: 0% 50%;
                    }
                }
            `;
            
            document.head.appendChild(style);
            document.body.appendChild(indicator);
            
            // Add badge in top-right corner with Spitch AI branding
            const badge = document.createElement('div');
            badge.id = 'spitch-automation-badge';
            badge.innerHTML = '<span style="font-size: 16px;">🎙️</span> Spitch AI Automation';
            badge.style.cssText = `
                position: fixed;
                top: 12px;
                right: 12px;
                background: linear-gradient(135deg, #8b5cf6, #06b6d4);
                background-size: 200% 200%;
                color: white;
                padding: 10px 18px;
                border-radius: 24px;
                font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
                font-weight: 600;
                z-index: 2147483647;
                box-shadow: 0 4px 20px rgba(139, 92, 246, 0.5),
                            0 0 40px rgba(6, 182, 212, 0.3);
                pointer-events: none;
                animation: spitch-badge-fade-in 0.6s ease-out,
                           spitch-gradient-shift 3s ease infinite;
                border: 1px solid rgba(255, 255, 255, 0.2);
                backdrop-filter: blur(10px);
                display: flex;
                align-items: center;
                gap: 6px;
            `;
            
            const badgeStyle = document.createElement('style');
            badgeStyle.textContent = `
                @keyframes spitch-badge-fade-in {
                    from {
                        opacity: 0;
                        transform: translateY(-10px) scale(0.9);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0) scale(1);
                    }
                }
            `;
            
            document.head.appendChild(badgeStyle);
            document.body.appendChild(badge);
            
            console.log('[Spitch AI] Browser automation indicator active');
            """
            
            # Wait a moment for page to be ready
            time.sleep(0.5)
            self.driver.execute_script(script)
            print("[BrowserAutomation] Spitch AI visual indicator added")
            
        except Exception as e:
            # Don't fail if indicator can't be added
            print(f"[BrowserAutomation] Could not add visual indicator: {e}")
    
    def navigate_to(self, url: str) -> bool:
        """
        Navigate to a URL
        
        Args:
            url: URL to navigate to
        
        Returns:
            True if successful, False otherwise
        """
        if not self.driver:
            print("[BrowserAutomation] Driver not initialized")
            return False
        
        try:
            # Add https:// if not present
            if not url.startswith('http'):
                url = 'https://' + url
            
            print(f"[BrowserAutomation] Navigating to {url}")
            self.driver.get(url)
            time.sleep(2)  # Wait for page to start loading
            
            # Re-add visual indicator after navigation
            self._add_automation_indicator()
            
            return True
            
        except Exception as e:
            print(f"[BrowserAutomation] Navigation failed: {e}")
            return False
    
    def find_element(self, selector: str, by: str = 'css', timeout: int = None) -> Optional[Any]:
        """
        Find an element on the page
        
        Args:
            selector: Element selector (CSS, XPath, ID, etc.)
            by: Selector type ('css', 'xpath', 'id', 'name', 'class', 'tag')
            timeout: Wait timeout in seconds
        
        Returns:
            WebElement if found, None otherwise
        """
        if not self.driver:
            return None
        
        timeout = timeout or self.wait_timeout
        
        # Map selector types to Selenium By constants
        by_map = {
            'css': By.CSS_SELECTOR,
            'xpath': By.XPATH,
            'id': By.ID,
            'name': By.NAME,
            'class': By.CLASS_NAME,
            'tag': By.TAG_NAME
        }
        
        by_type = by_map.get(by.lower(), By.CSS_SELECTOR)
        
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.presence_of_element_located((by_type, selector)))
            return element
        except TimeoutException:
            print(f"[BrowserAutomation] Element not found: {selector}")
            return None
        except Exception as e:
            print(f"[BrowserAutomation] Error finding element: {e}")
            return None
    
    def click_element(self, selector: str, by: str = 'css') -> bool:
        """
        Click an element
        
        Args:
            selector: Element selector
            by: Selector type
        
        Returns:
            True if successful, False otherwise
        """
        element = self.find_element(selector, by)
        if element:
            try:
                # Wait for element to be clickable
                wait = WebDriverWait(self.driver, self.wait_timeout)
                clickable = wait.until(EC.element_to_be_clickable(element))
                clickable.click()
                print(f"[BrowserAutomation] Clicked element: {selector}")
                time.sleep(1)  # Wait for action to complete
                return True
            except Exception as e:
                print(f"[BrowserAutomation] Click failed: {e}")
                return False
        return False
    
    def fill_input(self, selector: str, text: str, by: str = 'css', clear_first: bool = True) -> bool:
        """
        Fill an input field with text
        
        Args:
            selector: Element selector
            text: Text to enter
            by: Selector type
            clear_first: Clear field before typing
        
        Returns:
            True if successful, False otherwise
        """
        element = self.find_element(selector, by)
        if element:
            try:
                if clear_first:
                    element.clear()
                element.send_keys(text)
                print(f"[BrowserAutomation] Filled input '{selector}' with '{text}'")
                time.sleep(0.5)
                return True
            except Exception as e:
                print(f"[BrowserAutomation] Fill input failed: {e}")
                return False
        return False
    
    def get_text(self, selector: str, by: str = 'css') -> Optional[str]:
        """
        Get text content of an element
        
        Args:
            selector: Element selector
            by: Selector type
        
        Returns:
            Text content or None
        """
        element = self.find_element(selector, by)
        if element:
            try:
                text = element.text
                print(f"[BrowserAutomation] Got text from '{selector}': {text[:50]}...")
                return text
            except Exception as e:
                print(f"[BrowserAutomation] Get text failed: {e}")
                return None
        return None
    
    def get_all_text(self, selector: str, by: str = 'css') -> List[str]:
        """
        Get text from all matching elements
        
        Args:
            selector: Element selector
            by: Selector type
        
        Returns:
            List of text content
        """
        if not self.driver:
            return []
        
        by_map = {
            'css': By.CSS_SELECTOR,
            'xpath': By.XPATH,
            'id': By.ID,
            'name': By.NAME,
            'class': By.CLASS_NAME,
            'tag': By.TAG_NAME
        }
        
        by_type = by_map.get(by.lower(), By.CSS_SELECTOR)
        
        try:
            elements = self.driver.find_elements(by_type, selector)
            texts = [elem.text for elem in elements if elem.text]
            print(f"[BrowserAutomation] Found {len(texts)} elements with text")
            return texts
        except Exception as e:
            print(f"[BrowserAutomation] Get all text failed: {e}")
            return []
    
    def take_screenshot(self, filename: str = None) -> str:
        """
        Take a screenshot of the current page
        
        Args:
            filename: Screenshot filename (auto-generated if not provided)
        
        Returns:
            Path to screenshot file
        """
        if not self.driver:
            return ""
        
        try:
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"screenshot_{timestamp}.png"
            
            filepath = os.path.join(self.screenshot_dir, filename)
            self.driver.save_screenshot(filepath)
            print(f"[BrowserAutomation] Screenshot saved: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"[BrowserAutomation] Screenshot failed: {e}")
            return ""
    
    def wait_for_element(self, selector: str, by: str = 'css', timeout: int = None) -> bool:
        """
        Wait for an element to appear
        
        Args:
            selector: Element selector
            by: Selector type
            timeout: Wait timeout in seconds
        
        Returns:
            True if element appears, False otherwise
        """
        element = self.find_element(selector, by, timeout)
        return element is not None
    
    def execute_script(self, script: str) -> Any:
        """
        Execute JavaScript on the page
        
        Args:
            script: JavaScript code to execute
        
        Returns:
            Script return value
        """
        if not self.driver:
            return None
        
        try:
            result = self.driver.execute_script(script)
            print(f"[BrowserAutomation] Executed script: {script[:50]}...")
            return result
        except Exception as e:
            print(f"[BrowserAutomation] Script execution failed: {e}")
            return None
    
    def scroll_to_element(self, selector: str, by: str = 'css') -> bool:
        """
        Scroll to an element
        
        Args:
            selector: Element selector
            by: Selector type
        
        Returns:
            True if successful, False otherwise
        """
        element = self.find_element(selector, by)
        if element:
            try:
                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                time.sleep(0.5)
                print(f"[BrowserAutomation] Scrolled to element: {selector}")
                return True
            except Exception as e:
                print(f"[BrowserAutomation] Scroll failed: {e}")
                return False
        return False
    
    def scroll_page(self, direction: str = 'down', amount: int = 300) -> bool:
        """
        Scroll the page
        
        Args:
            direction: 'up' or 'down'
            amount: Pixels to scroll
        
        Returns:
            True if successful, False otherwise
        """
        if not self.driver:
            return False
        
        try:
            scroll_amount = amount if direction == 'down' else -amount
            self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            time.sleep(0.5)
            print(f"[BrowserAutomation] Scrolled {direction} by {amount}px")
            return True
        except Exception as e:
            print(f"[BrowserAutomation] Scroll failed: {e}")
            return False
    
    def get_page_source(self) -> str:
        """
        Get the HTML source of the current page
        
        Returns:
            HTML source code
        """
        if not self.driver:
            return ""
        
        try:
            source = self.driver.page_source
            print(f"[BrowserAutomation] Got page source ({len(source)} chars)")
            return source
        except Exception as e:
            print(f"[BrowserAutomation] Get page source failed: {e}")
            return ""
    
    def get_current_url(self) -> str:
        """
        Get the current URL
        
        Returns:
            Current URL
        """
        if not self.driver:
            return ""
        
        try:
            url = self.driver.current_url
            return url
        except Exception as e:
            print(f"[BrowserAutomation] Get current URL failed: {e}")
            return ""
    
    def submit_form(self, selector: str = None, by: str = 'css') -> bool:
        """
        Submit a form (either by selector or by pressing Enter in last focused field)
        
        Args:
            selector: Form element selector (optional)
            by: Selector type
        
        Returns:
            True if successful, False otherwise
        """
        if selector:
            element = self.find_element(selector, by)
            if element:
                try:
                    element.submit()
                    print(f"[BrowserAutomation] Submitted form: {selector}")
                    time.sleep(2)  # Wait for form submission
                    return True
                except Exception as e:
                    print(f"[BrowserAutomation] Form submit failed: {e}")
                    return False
        else:
            # Press Enter key
            try:
                from selenium.webdriver.common.action_chains import ActionChains
                ActionChains(self.driver).send_keys(Keys.RETURN).perform()
                print("[BrowserAutomation] Submitted form via Enter key")
                time.sleep(2)
                return True
            except Exception as e:
                print(f"[BrowserAutomation] Form submit failed: {e}")
                return False
        return False
    
    def close_browser(self) -> bool:
        """
        Close the browser and cleanup
        
        Returns:
            True if successful, False otherwise
        """
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
                print("[BrowserAutomation] Browser closed")
                return True
            except Exception as e:
                print(f"[BrowserAutomation] Close browser failed: {e}")
                return False
        return True
    
    def is_browser_open(self) -> bool:
        """
        Check if browser is currently open
        
        Returns:
            True if browser is open, False otherwise
        """
        return self.driver is not None


# Global instance
browser_automation = BrowserAutomation()
