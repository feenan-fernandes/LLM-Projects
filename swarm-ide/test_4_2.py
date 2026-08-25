import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.loop.builder_loop import run_builder_loop

def test_builder_loop():
    print("Testing Builder Loop State Machine...")
    
    mocked_responses = [
        # Iteration 1: Write file
        "<think>I should write a flask app</think>\n<write_file>\n<path>app.py</path>\n<content>print('hello flask')</content>\n</write_file>",
        # Iteration 2: Execute bash to test
        "<think>Now I test it</think>\n<execute_bash>\n<cmd>python app.py</cmd>\n</execute_bash>",
        # Iteration 3: Finish
        "<think>It worked</think>\n<finish status='success'>Wrote hello world flask route</finish>"
    ]
    
    success, iterations, summary = run_builder_loop("write a hello world Flask route", task_id="test_loop", mock_responses=mocked_responses)
    
    if success and iterations <= 3:
        print(f"SUCCESS: Loop completed successfully in {iterations} iterations.")
        return True
    else:
        print(f"FAIL: Loop did not complete as expected. Success: {success}, Iterations: {iterations}")
        return False

if __name__ == "__main__":
    success = test_builder_loop()
    
    # Cleanup
    if os.path.exists('app.py'):
        os.remove('app.py')
        
    sys.exit(0 if success else 1)
