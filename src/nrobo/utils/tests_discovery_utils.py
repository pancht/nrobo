import os


def has_pytest_tests(test_dir="tests"):
    for root, _, files in os.walk(test_dir):
        for f in files:
            if f.startswith("test_") and f.endswith(".py"):
                print(f"✅ Found test file: {os.path.join(root, f)}")
                return True
    return False
