
import os
from pathlib import Path

# Use the test's temporary directory
TEST_DIR = Path(r"C:\Users\Mi\Kiro\PythonCodeTester\temp_pytest\test_teardown_actions_success0")

def create_file(filename, content):
    file_path = TEST_DIR / filename
    with open(file_path, 'w') as f:
        f.write(content)
    return f"Created {filename}"

def read_file(filename):
    file_path = TEST_DIR / filename
    with open(file_path, 'r') as f:
        return f.read()

def delete_file(filename):
    file_path = TEST_DIR / filename
    if file_path.exists():
        file_path.unlink()
        return f"Deleted {filename}"
    return f"File {filename} not found"
