import subprocess
import os
import glob
import pytest

def run_accert_and_check_output(input_file, expected_output_file):
    """Helper function to run ACCERT, check output file, and compare with expected result."""
    # Define the command to run the ACCERT script
    command = ["python", "../src/Main.py", "-i", input_file]
    
    # Run the command
    result = subprocess.run(command, capture_output=True, text=True)
    assert result.returncode == 0, f"ACCERT run failed: {result.stderr}"

    # Check if output.out is generated
    assert os.path.exists("output.out"), "output.out file was not generated"

    # Compare output.out content with expected output
    with open("output.out", "r") as output_file:
        output_content = output_file.read()
    with open(expected_output_file, "r") as expected_output:
        expected_output_content = expected_output.read()
    assert output_content == expected_output_content, "output.out content does not match expected output"

def check_excel_files(excel_patterns):
    """Helper function to check if relevant Excel files are generated."""
    
    for pattern in excel_patterns:
        files = glob.glob(pattern)
        assert len(files) > 0, f"No Excel files matching {pattern} were generated"

# Test functions
def test_integration_with_fusion_son(prepare_environment):
    """Test ACCERT with fusion.son input."""
    run_accert_and_check_output("../tutorial/fusion.son", "gold/output.fusion.out")
    
    # For fusion.son, only check for the updated_account.xlsx file
    check_excel_files(["*_updated_account.xlsx"])

def test_integration_with_pwr_son(prepare_environment,excel_patterns):
    """Test ACCERT with pwr.son input."""
    run_accert_and_check_output("../tutorial/PWR12-BE.son", "gold/output.pwr12be.out")
    
    # Check all three relevant Excel files
    check_excel_files(excel_patterns)

def test_integration_with_abr_son(prepare_environment,excel_patterns):
    """Test ACCERT with abr.son input."""
    run_accert_and_check_output("../tutorial/ABR1000.son", "gold/output.abr1000.out")
    
    # Check all three relevant Excel files
    check_excel_files(excel_patterns)

def test_integration_with_heatpipe_son(prepare_environment,excel_patterns):
    """Test ACCERT with heatpipe.son input."""
    run_accert_and_check_output("../tutorial/heatpipe.son", "gold/output.heatpipe.out")
    
    # Check all three relevant Excel files
    check_excel_files(excel_patterns)
