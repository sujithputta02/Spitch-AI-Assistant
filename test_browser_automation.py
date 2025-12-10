"""
Test script for browser automation capabilities
Demonstrates various browser automation features
"""

from engine.ai_task_agent import ai_task_agent


def test_basic_browser():
    """Test basic browser opening and navigation"""
    print("=" * 60)
    print("TEST 1: Basic Browser Navigation")
    print("=" * 60)
    
    command = "open browser and go to google.com"
    print(f"\nCommand: {command}")
    result = ai_task_agent.execute_task(command)
    
    print(f"\nSuccess: {result['success']}")
    print(f"Message: {result['message']}")
    
    if result.get('steps'):
        print(f"\nSteps executed: {len(result['steps'])}")
        for step in result['steps']:
            print(f"  - Step {step['step']}: {step['action']} - {'✓' if step['success'] else '✗'}")
    
    input("\nPress Enter to continue to next test...")


def test_form_filling():
    """Test form filling and submission"""
    print("\n" + "=" * 60)
    print("TEST 2: Form Filling")
    print("=" * 60)
    
    command = "fill the search box with Python tutorials and submit"
    print(f"\nCommand: {command}")
    result = ai_task_agent.execute_task(command)
    
    print(f"\nSuccess: {result['success']}")
    print(f"Message: {result['message']}")
    
    input("\nPress Enter to continue to next test...")


def test_screenshot():
    """Test screenshot capture"""
    print("\n" + "=" * 60)
    print("TEST 3: Screenshot Capture")
    print("=" * 60)
    
    command = "take a screenshot of the page"
    print(f"\nCommand: {command}")
    result = ai_task_agent.execute_task(command)
    
    print(f"\nSuccess: {result['success']}")
    print(f"Message: {result['message']}")
    
    input("\nPress Enter to continue to next test...")


def test_complex_workflow():
    """Test complex multi-step workflow"""
    print("\n" + "=" * 60)
    print("TEST 4: Complex Workflow")
    print("=" * 60)
    
    command = "open browser, go to github.com, and take a screenshot"
    print(f"\nCommand: {command}")
    result = ai_task_agent.execute_task(command)
    
    print(f"\nSuccess: {result['success']}")
    print(f"Message: {result['message']}")
    
    if result.get('steps'):
        print(f"\nSteps executed: {len(result['steps'])}")
        for step in result['steps']:
            print(f"  - Step {step['step']}: {step['action']} - {'✓' if step['success'] else '✗'}")
    
    input("\nPress Enter to close browser...")


def test_close_browser():
    """Test browser closing"""
    print("\n" + "=" * 60)
    print("TEST 5: Close Browser")
    print("=" * 60)
    
    command = "close browser"
    print(f"\nCommand: {command}")
    result = ai_task_agent.execute_task(command)
    
    print(f"\nSuccess: {result['success']}")
    print(f"Message: {result['message']}")


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("BROWSER AUTOMATION TEST SUITE")
    print("=" * 60)
    print("\nThis will test the browser automation capabilities.")
    print("Make sure Chrome is installed on your system.")
    input("\nPress Enter to start tests...")
    
    try:
        # Run tests
        test_basic_browser()
        test_form_filling()
        test_screenshot()
        test_complex_workflow()
        test_close_browser()
        
        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED")
        print("=" * 60)
        print("\nCheck the 'browser_screenshots' folder for captured screenshots.")
        
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
        # Try to close browser if open
        try:
            from engine.browser_automation import browser_automation
            if browser_automation.is_browser_open():
                browser_automation.close_browser()
                print("Browser closed.")
        except:
            pass
    except Exception as e:
        print(f"\n\nError during tests: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
