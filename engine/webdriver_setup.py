"""
WebDriver Setup Helper for Spitch AI Assistant
Handles automatic WebDriver installation and configuration
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from typing import Optional


def get_chrome_driver(headless: bool = False, user_agent: str = None) -> Optional[webdriver.Chrome]:
    """
    Get configured Chrome WebDriver with automatic driver management
    
    Args:
        headless: Run in headless mode (no GUI)
        user_agent: Custom user agent string
    
    Returns:
        Chrome WebDriver instance or None if failed
    """
    try:
        # Try to use webdriver-manager for automatic ChromeDriver installation
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())
            print("[WebDriverSetup] Using webdriver-manager for ChromeDriver")
        except ImportError:
            # Fallback to system ChromeDriver
            service = Service()
            print("[WebDriverSetup] Using system ChromeDriver (webdriver-manager not installed)")
        
        # Configure Chrome options
        options = Options()
        
        # Headless mode
        if headless:
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
        
        # Security and performance options
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        # Hide automation indicators
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Custom user agent
        if user_agent:
            options.add_argument(f'user-agent={user_agent}')
        
        # Disable logging
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        # Create driver
        driver = webdriver.Chrome(service=service, options=options)
        
        # Set page load timeout
        driver.set_page_load_timeout(30)
        
        # Maximize window (if not headless)
        if not headless:
            driver.maximize_window()
        
        print("[WebDriverSetup] Chrome WebDriver initialized successfully")
        return driver
        
    except Exception as e:
        print(f"[WebDriverSetup] Failed to initialize Chrome WebDriver: {e}")
        return None


def get_firefox_driver(headless: bool = False) -> Optional[webdriver.Firefox]:
    """
    Get configured Firefox WebDriver (alternative to Chrome)
    
    Args:
        headless: Run in headless mode
    
    Returns:
        Firefox WebDriver instance or None if failed
    """
    try:
        from selenium.webdriver.firefox.service import Service as FirefoxService
        from selenium.webdriver.firefox.options import Options as FirefoxOptions
        
        try:
            from webdriver_manager.firefox import GeckoDriverManager
            service = FirefoxService(GeckoDriverManager().install())
        except ImportError:
            service = FirefoxService()
        
        options = FirefoxOptions()
        if headless:
            options.add_argument('--headless')
        
        driver = webdriver.Firefox(service=service, options=options)
        driver.set_page_load_timeout(30)
        
        if not headless:
            driver.maximize_window()
        
        print("[WebDriverSetup] Firefox WebDriver initialized successfully")
        return driver
        
    except Exception as e:
        print(f"[WebDriverSetup] Failed to initialize Firefox WebDriver: {e}")
        return None


def check_driver_availability() -> dict:
    """
    Check which WebDrivers are available on the system
    
    Returns:
        Dictionary with driver availability status
    """
    availability = {
        'chrome': False,
        'firefox': False,
        'webdriver_manager': False
    }
    
    # Check for webdriver-manager
    try:
        import webdriver_manager
        availability['webdriver_manager'] = True
    except ImportError:
        pass
    
    # Check Chrome
    try:
        driver = get_chrome_driver(headless=True)
        if driver:
            driver.quit()
            availability['chrome'] = True
    except:
        pass
    
    # Check Firefox
    try:
        driver = get_firefox_driver(headless=True)
        if driver:
            driver.quit()
            availability['firefox'] = True
    except:
        pass
    
    return availability
