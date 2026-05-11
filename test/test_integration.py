import subprocess
import os
import glob
import shutil
import sys
import tempfile
from pathlib import Path
import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEST_DIR = Path(__file__).resolve().parent


def run_accert_and_check_output(input_file, expected_output_file):
    """Helper function to run ACCERT, check output file, and compare with expected result."""
    command = [sys.executable, str(PROJECT_ROOT / "src" / "Main.py"), "-i", str(PROJECT_ROOT / input_file)]
    test_db = Path(tempfile.mkdtemp()) / "accertdb.sqlite"
    shutil.copy2(PROJECT_ROOT / "src" / "accertdb.sqlite", test_db)
    env = os.environ.copy()
    env["ACCERT_SQLITE_DB"] = str(test_db)
    
    # Run the command
    result = subprocess.run(command, cwd=TEST_DIR, env=env, capture_output=True, text=True)
    assert result.returncode == 0, f"ACCERT run failed: {result.stderr}"

    # Check if output.out is generated
    assert (TEST_DIR / "output.out").exists(), "output.out file was not generated"

    # Compare output.out content with expected output
    with open(TEST_DIR / "output.out", "r") as output_file:
        output_content = output_file.read()
    with open(TEST_DIR / expected_output_file, "r") as expected_output:
        expected_output_content = expected_output.read()

    # compare the content of the output.out file with the expected output
    # compare each line of the output.out file with the expected output
    # if the content of the output.out file print the line that does not match the expected output
    if output_content != expected_output_content:
        output_lines = output_content.splitlines()
        expected_output_lines = expected_output_content.splitlines()
        for i in range(len(output_lines)):
            if output_lines[i] != expected_output_lines[i]:
                print(f"Line {i+1} does not match:")
                print(f"Output: {output_lines[i]}")
                print(f"Expected: {expected_output_lines[i]}")
          
    assert output_content == expected_output_content, "output.out content does not match expected output"

def check_excel_files(excel_patterns):
    """Helper function to check if relevant Excel files are generated."""
    
    for pattern in excel_patterns:
        files = glob.glob(str(TEST_DIR / pattern))
        assert len(files) > 0, f"No Excel files matching {pattern} were generated"

# Test functions
def test_integration_with_fusion_son(prepare_environment):
    """Test ACCERT with fusion.son input."""
    run_accert_and_check_output("tutorial/accert/Fusion.son", "gold/output.fusion.out")
    
    # For fusion.son, only check for the updated_account.xlsx file
    check_excel_files(["*_updated_account.xlsx"])

def test_integration_with_pwr_son(prepare_environment,excel_patterns):
    """Test ACCERT with pwr.son input."""
    run_accert_and_check_output("tutorial/accert/PWR12-BE.son", "gold/output.pwr12be.out")
    
    # Check all three relevant Excel files
    check_excel_files(excel_patterns)

def test_integration_with_abr_son(prepare_environment,excel_patterns):
    """Test ACCERT with abr.son input."""
    run_accert_and_check_output("tutorial/accert/ABR1000.son", "gold/output.abr1000.out")
    
    # Check all three relevant Excel files
    check_excel_files(excel_patterns)

def test_integration_with_heatpipe_son(prepare_environment,excel_patterns):
    """Test ACCERT with heatpipe.son input."""
    run_accert_and_check_output("tutorial/accert/heatpipe.son", "gold/output.heatpipe.out")
    
    # Check all three relevant Excel files
    check_excel_files(excel_patterns)
