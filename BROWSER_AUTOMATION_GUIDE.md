# Browser Automation Feature - User Guide

## Overview

Spitch AI Assistant now includes powerful browser automation capabilities using Selenium WebDriver. You can control web browsers, fill forms, extract data, and automate repetitive web tasks using natural voice commands or text input.

## Installation

### 1. Install Dependencies

```bash
pip install selenium>=4.15.0 webdriver-manager>=4.0.1
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

### 2. Chrome Browser

Make sure Google Chrome is installed on your system. The WebDriver will be automatically downloaded and managed.

## Voice Commands

### Basic Browser Control

**Open Browser:**
- "Open browser"
- "Start browser"
- "Open browser and go to google.com"

**Navigate to URL:**
- "Go to amazon.com"
- "Navigate to github.com"
- "Open youtube.com in browser"

**Close Browser:**
- "Close browser"
- "Close the browser"

### Form Interaction

**Fill Input Fields:**
- "Fill the search box with Python tutorials"
- "Fill form field username with john@email.com"
- "Fill the email field with test@example.com"

**Submit Forms:**
- "Fill search box with laptops and submit"
- "Fill the form and press enter"
- "Submit the form"

### Element Interaction

**Click Elements:**
- "Click the login button"
- "Click on search"
- "Click the submit button"

### Data Extraction

**Extract Text:**
- "Extract all product titles"
- "Get text from the heading"
- "Extract all links from the page"

### Screenshots

**Capture Screenshots:**
- "Take a screenshot of the page"
- "Screenshot the page"
- "Take a screenshot and save as test.png"

### Complex Workflows

**Multi-Step Commands:**
- "Open browser, go to google.com, search for Python, and take a screenshot"
- "Open browser, navigate to github.com, and screenshot the page"
- "Fill the search box with wireless mouse, submit, and take a screenshot"

## Programmatic Usage

### Basic Example

```python
from engine.ai_task_agent import ai_task_agent

# Execute browser automation command
result = ai_task_agent.execute_task("open browser and go to google.com")

if result['success']:
    print("Success:", result['message'])
else:
    print("Failed:", result['message'])
```

### Direct Browser Control

```python
from engine.browser_automation import browser_automation

# Initialize browser
browser_automation.initialize_driver()

# Navigate to URL
browser_automation.navigate_to("https://google.com")

# Fill input field
browser_automation.fill_input("input[name='q']", "Python tutorials")

# Click search button
browser_automation.click_element("input[value='Google Search']")

# Take screenshot
browser_automation.take_screenshot("google_search.png")

# Close browser
browser_automation.close_browser()
```

### Advanced Selectors

```python
# CSS Selector
browser_automation.find_element("input[name='username']", by='css')

# XPath
browser_automation.find_element("//input[@name='username']", by='xpath')

# ID
browser_automation.find_element("login-button", by='id')

# Class Name
browser_automation.find_element("search-input", by='class')
```

## Use Cases

### 1. Automated Testing

Test your web applications automatically:

```
"Open browser, go to myapp.com/login, fill username with test@example.com, fill password with test123, click login button, and take a screenshot"
```

### 2. Data Collection

Extract information from websites:

```
"Open browser, go to news.ycombinator.com, extract all article titles"
```

### 3. Form Automation

Fill repetitive forms quickly:

```
"Open browser, go to survey.com, fill name with John Doe, fill email with john@example.com, and submit"
```

### 4. Price Monitoring

Check prices on e-commerce sites:

```
"Open browser, go to amazon.com, search for wireless mouse, extract all prices"
```

### 5. Web Research

Automate research tasks:

```
"Open browser, search Google for Python best practices, take a screenshot, close browser"
```

## API Reference

### BrowserAutomation Class

#### Methods

**initialize_driver(headless=False)**
- Initialize Chrome WebDriver
- `headless`: Run in headless mode (no GUI)
- Returns: `True` if successful

**navigate_to(url)**
- Navigate to a URL
- `url`: URL to navigate to
- Returns: `True` if successful

**find_element(selector, by='css', timeout=10)**
- Find an element on the page
- `selector`: Element selector
- `by`: Selector type ('css', 'xpath', 'id', 'name', 'class', 'tag')
- `timeout`: Wait timeout in seconds
- Returns: WebElement or None

**click_element(selector, by='css')**
- Click an element
- Returns: `True` if successful

**fill_input(selector, text, by='css', clear_first=True)**
- Fill an input field
- `text`: Text to enter
- `clear_first`: Clear field before typing
- Returns: `True` if successful

**get_text(selector, by='css')**
- Get text content of an element
- Returns: Text string or None

**get_all_text(selector, by='css')**
- Get text from all matching elements
- Returns: List of text strings

**take_screenshot(filename=None)**
- Take a screenshot
- `filename`: Optional filename (auto-generated if not provided)
- Returns: Path to screenshot file

**submit_form(selector=None, by='css')**
- Submit a form
- `selector`: Optional form selector
- Returns: `True` if successful

**scroll_page(direction='down', amount=300)**
- Scroll the page
- `direction`: 'up' or 'down'
- `amount`: Pixels to scroll
- Returns: `True` if successful

**close_browser()**
- Close the browser
- Returns: `True` if successful

## Screenshots

All screenshots are automatically saved to the `browser_screenshots` directory in the project root.

## Troubleshooting

### Chrome Not Found

**Error:** "Failed to open browser. Make sure Chrome is installed."

**Solution:** Install Google Chrome from https://www.google.com/chrome/

### WebDriver Issues

**Error:** "WebDriver not found"

**Solution:** Install webdriver-manager:
```bash
pip install webdriver-manager
```

### Element Not Found

**Error:** "Element not found: input[name='search']"

**Solutions:**
1. Wait for page to load completely
2. Use more specific selectors
3. Check if element is in an iframe
4. Verify the selector is correct

### Timeout Errors

**Error:** "TimeoutException: Element not found within timeout"

**Solutions:**
1. Increase wait timeout
2. Check if page is loading slowly
3. Verify element exists on the page

## Safety & Security

### Domain Whitelisting

For security, you can restrict browser automation to specific domains:

```python
from engine.safety_sandbox import ALLOWED_DOMAINS

# Add allowed domains
ALLOWED_DOMAINS.extend([
    'mycompany.com',
    'trusted-site.com'
])
```

### User Confirmation

For sensitive actions, the system will request user confirmation before proceeding.

## Examples

### Example 1: Google Search

```python
result = ai_task_agent.execute_task(
    "open browser, go to google.com, search for Python tutorials, and take a screenshot"
)
```

### Example 2: GitHub Navigation

```python
result = ai_task_agent.execute_task(
    "open browser, navigate to github.com, and screenshot the page"
)
```

### Example 3: Form Filling

```python
result = ai_task_agent.execute_task(
    "fill the email field with test@example.com, fill password with test123, and click login"
)
```

## Testing

Run the test suite to verify browser automation:

```bash
python test_browser_automation.py
```

This will run through various test cases including:
- Basic navigation
- Form filling
- Screenshot capture
- Complex workflows

## Future Enhancements

Planned features for future releases:
- Multi-tab support
- Cookie management
- File downloads
- Proxy support
- Browser profiles
- Visual regression testing
- Performance metrics
- Accessibility testing

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the test script for examples
3. Check browser console for errors
4. Ensure all dependencies are installed

## License

This feature is part of Spitch AI Assistant and follows the same license terms.
