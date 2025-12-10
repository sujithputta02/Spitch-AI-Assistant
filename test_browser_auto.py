"""
Automated Browser Automation Test Suite (No User Input Required)
Tests small, medium, and large tasks automatically
"""

from engine.ai_task_agent import ai_task_agent
import time


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def run_test(test_name, command, wait_time=2):
    """Run a single test command"""
    print(f"\n[TEST] {test_name}")
    print(f"[COMMAND] {command}")
    print("-" * 70)
    
    try:
        result = ai_task_agent.execute_task(command)
        
        if result['success']:
            print(f"[RESULT] SUCCESS")
            print(f"[MESSAGE] {result['message']}")
            if result.get('steps'):
                print(f"[STEPS] Completed {len(result['steps'])} steps:")
                for step in result['steps']:
                    status = "OK" if step['success'] else "FAIL"
                    print(f"  - Step {step['step']}: {step['action']} [{status}]")
        else:
            print(f"[RESULT] FAILED")
            print(f"[MESSAGE] {result['message']}")
        
        # Wait between tests
        time.sleep(wait_time)
        return result['success']
        
    except Exception as e:
        print(f"[RESULT] ERROR")
        print(f"[ERROR] {e}")
        return False


# Track results
passed = 0
failed = 0
total = 0

print_section("BROWSER AUTOMATION - AUTOMATED TEST SUITE")
print("\nTesting browser automation from simple to complex tasks...")
print("Tests will run automatically.\n")

# ========== SMALL TASKS ==========
print_section("PART 1: SMALL TASKS (Single Actions)")

tests = [
    ("1. Open Browser", "open browser"),
    ("2. Navigate to Google", "navigate to google.com"),
    ("3. Take Screenshot", "take a screenshot of the page"),
]

for test_name, command in tests:
    total += 1
    if run_test(test_name, command, wait_time=3):
        passed += 1
    else:
        failed += 1

# ========== MEDIUM TASKS ==========
print_section("PART 2: MEDIUM TASKS (2-3 Step Workflows)")

tests = [
    ("4. Navigate and Screenshot", "go to github.com and take a screenshot"),
    ("5. Multiple Navigation", "navigate to youtube.com and take a screenshot"),
]

for test_name, command in tests:
    total += 1
    if run_test(test_name, command, wait_time=4):
        passed += 1
    else:
        failed += 1

# ========== LARGE TASKS ==========
print_section("PART 3: LARGE TASKS (Complex Multi-Step)")

# Close and reopen for clean test
print("\n[INFO] Closing browser for clean test...")
ai_task_agent.execute_task("close browser")
time.sleep(2)

tests = [
    (
        "6. Complete Search Workflow",
        "open browser, go to google.com, and take a screenshot"
    ),
    (
        "7. Multi-Site Tour",
        "navigate to github.com, take a screenshot, go to youtube.com, and take a screenshot"
    ),
]

for test_name, command in tests:
    total += 1
    if run_test(test_name, command, wait_time=5):
        passed += 1
    else:
        failed += 1

# ========== CLEANUP ==========
print("\n[INFO] Final cleanup...")
try:
    ai_task_agent.execute_task("close browser")
    print("[INFO] Browser closed successfully")
except:
    print("[INFO] Browser already closed")

# ========== RESULTS ==========
print_section("TEST RESULTS SUMMARY")

print(f"\nTotal Tests: {total}")
print(f"Passed: {passed} ({passed/total*100:.1f}%)")
print(f"Failed: {failed} ({failed/total*100:.1f}%)")

if failed == 0:
    print("\n" + "=" * 70)
    print("  ALL TESTS PASSED! Browser automation is fully functional!")
    print("=" * 70)
else:
    print("\n" + "=" * 70)
    print(f"  {failed} test(s) failed. Review output above.")
    print("=" * 70)

print("\n[INFO] Screenshots saved in 'browser_screenshots' folder")
print("[INFO] Browser automation is ready to use in Spitch!")
