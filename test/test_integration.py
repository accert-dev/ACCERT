import subprocess
import os
import glob
import shutil
import sys
import tempfile
import re
from itertools import zip_longest
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

    output_content = normalize_output(output_content)
    expected_output_content = normalize_output(expected_output_content)

    # compare the content of the output.out file with the expected output
    # compare each line of the output.out file with the expected output
    # if the content of the output.out file print the line that does not match the expected output
    if output_content != expected_output_content:
        output_lines = output_content.splitlines()
        expected_output_lines = expected_output_content.splitlines()
        for i, (output_line, expected_output_line) in enumerate(zip_longest(output_lines, expected_output_lines, fillvalue="<missing>")):
            if output_line != expected_output_line:
                print(f"Line {i+1} does not match:")
                print(f"Output: {output_line}")
                print(f"Expected: {expected_output_line}")
                break
          
    assert output_content == expected_output_content, "output.out content does not match expected output"

def normalize_output(output):
    """Normalize timestamped CSV and legacy Excel output lines."""
    output = re.sub(
        r"Successfully created CSV file .+_(aff_ce|upd_ce|upd_acc)_\d{8}_\d{6}\.csv",
        r"Successfully created output file \1",
        output,
    )
    output = re.sub(
        r"Successfully created excel file .+_(variable_affected_cost_elements|updated_cost_element|updated_account)\.xlsx",
        lambda match: {
            "variable_affected_cost_elements": "Successfully created output file aff_ce",
            "updated_cost_element": "Successfully created output file upd_ce",
            "updated_account": "Successfully created output file upd_acc",
        }[match.group(1)],
        output,
    )
    return "\n".join(re.sub(r" {2,}", " ", line).rstrip() for line in output.splitlines())

def check_csv_files(csv_patterns):
    """Helper function to check if relevant CSV files are generated."""
    
    for pattern in csv_patterns:
        files = glob.glob(str(TEST_DIR / pattern))
        assert len(files) > 0, f"No CSV files matching {pattern} were generated"

# Test functions
def test_integration_with_fusion_son(prepare_environment):
    """Test ACCERT with fusion.son input."""
    run_accert_and_check_output("tutorial/accert/Fusion.son", "gold/output.fusion.out")
    
    # For fusion.son, only check for the updated account CSV file
    check_csv_files(["*_upd_acc_*.csv"])

def test_integration_with_pwr_son(prepare_environment,csv_patterns):
    """Test ACCERT with pwr.son input."""
    run_accert_and_check_output("tutorial/accert/PWR12-BE.son", "gold/output.pwr12be.out")
    
    # Check all three relevant CSV files
    check_csv_files(csv_patterns)

def test_integration_with_abr_son(prepare_environment,csv_patterns):
    """Test ACCERT with abr.son input."""
    run_accert_and_check_output("tutorial/accert/ABR1000.son", "gold/output.abr1000.out")
    
    # Check all three relevant CSV files
    check_csv_files(csv_patterns)

def test_integration_with_heatpipe_son(prepare_environment,csv_patterns):
    """Test ACCERT with heatpipe.son input."""
    run_accert_and_check_output("tutorial/accert/heatpipe.son", "gold/output.heatpipe.out")
    
    # Check all three relevant CSV files
    check_csv_files(csv_patterns)

def test_integration_with_lpsr_son(prepare_environment,csv_patterns):
    """Test ACCERT with the LPSR tutorial input."""
    command = [sys.executable, str(PROJECT_ROOT / "src" / "Main.py"), "-i", str(PROJECT_ROOT / "tutorial" / "accert" / "LPSR.son")]
    test_db = Path(tempfile.mkdtemp()) / "accertdb.sqlite"
    shutil.copy2(PROJECT_ROOT / "src" / "accertdb.sqlite", test_db)
    env = os.environ.copy()
    env["ACCERT_SQLITE_DB"] = str(test_db)

    result = subprocess.run(command, cwd=TEST_DIR, env=env, capture_output=True, text=True)
    assert result.returncode == 0, f"ACCERT LPSR run failed: {result.stderr}"
    output_content = (TEST_DIR / "output.out").read_text()
    assert 'Reference model is "LPSR"' in output_content
    assert "Total OCC" in output_content
    assert "2024 ($/kW)" in output_content
    check_csv_files(["lpsr_upd_acc_*.csv", "lpsr_upd_ce_*.csv", "lpsr_aff_ce_*.csv", "lpsr_post_*.csv"])


def test_integration_with_ap1000_son(prepare_environment):
    """Test ACCERT with the AP1000 tutorial input."""
    command = [sys.executable, str(PROJECT_ROOT / "src" / "Main.py"), "-i", str(PROJECT_ROOT / "tutorial" / "accert" / "AP1000.son")]
    test_db = Path(tempfile.mkdtemp()) / "accertdb.sqlite"
    shutil.copy2(PROJECT_ROOT / "src" / "accertdb.sqlite", test_db)
    env = os.environ.copy()
    env["ACCERT_SQLITE_DB"] = str(test_db)

    result = subprocess.run(command, cwd=TEST_DIR, env=env, capture_output=True, text=True)
    assert result.returncode == 0, f"ACCERT AP1000 run failed: {result.stderr}"
    output_content = (TEST_DIR / "output.out").read_text()
    assert 'Reference model is "AP1000"' in output_content
    assert "Total OCC" in output_content
    assert "2024 ($/kW)" in output_content
    check_csv_files(["ap1000_upd_acc_*.csv", "ap1000_upd_ce_*.csv", "ap1000_aff_ce_*.csv", "ap1000_post_*.csv"])
