import importlib
import json
import time
import traceback
from pathlib import Path


# -----------------------------------------
# CONFIGURATION
# -----------------------------------------

METHODS_DIR = Path(__file__).resolve().parent.parent / "ppst_methods"
SHARED_TEST_DATA = Path(__file__).resolve().parent / "shared_test_data.json"

# Expected interface
EXPECTED_FUNCTION_NAME = "run_method"


# -----------------------------------------
# HELPER FUNCTIONS
# -----------------------------------------

def load_shared_test_data():
    """Load shared test data from JSON file."""
    try:
        with open(SHARED_TEST_DATA, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to load shared test data: {e}")
        return None


def import_method_module(method_file):
    """Dynamically import a method_X.py module."""
    module_name = f"ppst_methods.{method_file.stem}"
    try:
        return importlib.import_module(module_name)
    except Exception as e:
        print(f"[ERROR] Could not import {module_name}: {e}")
        return None


def run_single_test(method_name, method_module, test_input):
    """Run a single method and evaluate its behavior."""
    results = {
        "method": method_name,
        "import_success": True,
        "has_run_method": False,
        "output_is_dict": False,
        "contains_required_keys": False,
        "execution_time_ms": None,
        "error": None,
    }

    # Check if run_method exists
    if hasattr(method_module, EXPECTED_FUNCTION_NAME):
        results["has_run_method"] = True
        run_method = getattr(method_module, EXPECTED_FUNCTION_NAME)
    else:
        results["error"] = f"Missing required function '{EXPECTED_FUNCTION_NAME}'"
        return results

    # Run the method and measure performance
    try:
        start = time.time()
        output = run_method(test_input)
        end = time.time()

        results["execution_time_ms"] = round((end - start) * 1000, 3)

        # Validate output
        if isinstance(output, dict):
            results["output_is_dict"] = True

            if all(key in output for key in ["success", "data", "errors"]):
                results["contains_required_keys"] = True

        else:
            results["error"] = "Output is not a dictionary"

    except Exception as e:
        results["error"] = f"Exception during execution: {e}\n{traceback.format_exc()}"

    return results


# -----------------------------------------
# MAIN TEST RUNNER
# -----------------------------------------

def evaluate_all_methods():
    print("\n=== Running Standardized Backend Method Tests ===\n")

    test_data = load_shared_test_data()
    if test_data is None:
        print("[FATAL] Cannot run tests without shared test data.")
        return

    method_files = sorted(METHODS_DIR.glob("method_*.py"))

    if not method_files:
        print("[ERROR] No method_X.py files found in ppst_methods/")
        return

    all_results = []

    for method_file in method_files:
        method_name = method_file.stem
        print(f"--- Testing {method_name} ---")

        module = import_method_module(method_file)
        if module is None:
            all_results.append({
                "method": method_name,
                "import_success": False,
                "error": "Import failed"
            })
            continue

        result = run_single_test(method_name, module, test_data)
        all_results.append(result)

        print(f"Result: {result}\n")

    print("\n=== Test Summary ===\n")
    for r in all_results:
        print(r)


if __name__ == "__main__":
    evaluate_all_methods()