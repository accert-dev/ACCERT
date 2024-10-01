import re
import os
import textwrap

current_dir = os.path.dirname(os.path.abspath(__file__))
sql_file_path = os.path.join(current_dir, '../..', 'src', 'accertdb.sql')
# Path to your SQL file use absolute path
# ../../sql/your_sql_file.sql
# os.path.abspath('../src/accertdb.sql')
sql_file_path = os.path.abspath(sql_file_path)
# Output directory for Markdown files
# output_dir = 'source/reference/database/'

output_dir = os.path.join(current_dir,'reference','database')
# Path to the Toctree file
# toctree_file_path = 'source/reference/database.rst'
toctree_file_path = os.path.join(current_dir,'reference','database.rst')

def clean_output_directory(directory):
    """
    Removes all .md files in the specified directory to clean up old documentation.
    """
    if os.path.exists(directory):
        for filename in os.listdir(directory):
            if filename.endswith('.md'):
                file_path = os.path.join(directory, filename)
                os.remove(file_path)
                print(f'Removed old Markdown file: {file_path}')
    else:
        os.makedirs(directory, exist_ok=True)
        print(f'Created output directory: {directory}')

def append_to_toctree(sp_name):
    """
    Appends the generated Markdown file to the Toctree in 'source/reference/database.rst'.
    """
    with open(toctree_file_path, 'a', encoding='utf-8') as toctree_file:
        toctree_file.write(f'   database/{sp_name}\n')

def generate_markdown_table(parameters):
    """
    Generates a Markdown table for the given parameters.
    """
    if not parameters:
        return """
| None | No parameters. |
|------|-----------------|
"""

    # Define table header
    table = """
| **Name** | **Type** |
|----------|----------|
"""
    # Add each parameter as a table row
    for param in parameters:
        name = param['name']
        input_type = param['type']
        # Escape pipe characters in descriptions to prevent table issues
        input_type = input_type.replace('|', '\\|')
        table += f"| {name} | {input_type} |\n"

    return table

def main():
    print(f"Reading SQL file from path: {sql_file_path}")
    print(f"Output directory: {output_dir}")
    print(f"Toctree file path: {toctree_file_path}")

    # Step 1: Clean up old Markdown files
    clean_output_directory(output_dir)

    # remove the old toctree file if it exists
    if os.path.exists(toctree_file_path):
        os.remove(toctree_file_path)
    # create a new toctree file
    with open(toctree_file_path, 'w', encoding='utf-8') as toctree_file:
            toctree_file.write(f"""
                               
Database Stored Procedures
==========================

.. toctree::
   :maxdepth: 1
   :caption: Contents:
                               
""")
    
    # Step 2: Read the SQL file
    try:
        with open(sql_file_path, 'r', encoding='utf-8') as file:
            sql_content = file.read()
    except FileNotFoundError:
        print(f"SQL file not found at path: {sql_file_path}")
        return
    
    # Step 3: Define Regex to match stored procedures
    # This regex accounts for:
    # - Optional DEFINER clause
    # - Procedure name with backticks
    # - Multiline parameters
    # - Custom delimiter ;;
    sp_pattern = re.compile(
        r'CREATE\s+DEFINER=`[^`]+`@`[^`]+`\s+PROCEDURE\s+`(\w+)`\s*\((.*?)\)\s*BEGIN\s*(.*?)END\s*;;',
        re.IGNORECASE | re.DOTALL
    )
    
    # Step 4: Find all stored procedures
    stored_procedures = sp_pattern.findall(sql_content)
    
    if not stored_procedures:
        print("No stored procedures found in the SQL file.")
        return
    
    # Step 5: Process each stored procedure
    for sp_name, params, body in stored_procedures:
        # Clean and process the SQL body
        sp_sql = textwrap.dedent(body).strip()

        # Attempt to extract description from comments (if any)
        # Assuming descriptions are provided in comments like /*! Description: ... */
        sp_description_match = re.search(r'/\*!\s*Description\s*:\s*(.*?)\s*\*/', sp_sql, re.DOTALL | re.IGNORECASE)
        if sp_description_match:
            sp_description = sp_description_match.group(1).strip()
            # Remove the description comment from the SQL body
            sp_sql = re.sub(r'/\*!\s*Description\s*:\s*.*?\s*\*/', '', sp_sql, flags=re.DOTALL | re.IGNORECASE).strip()
        else:
            sp_description = '\n'

        # Extract parameters: Assuming parameters are defined as IN param_name param_type
        # This regex captures "IN param_name param_type", "OUT param_name param_type", etc.
        # Additionally, it captures optional inline comments for descriptions
        sp_parameters = re.findall(r'\b(IN|OUT|INOUT)\s+(\w+)\s+([^\s,]+)(?:\s*/\*\s*(.*?)\s*\*/)?', params, re.IGNORECASE)

        # Format parameters for the table
        parameters = []
        for direction, param_name, param_type, param_desc in sp_parameters:
            parameters.append({
                'name': param_name,
                'type': param_type
            })

        # Generate the Markdown table for parameters
        parameters_table = generate_markdown_table(parameters)

        # Prepare the full SQL definition
        formatted_params = ', '.join([f'{dir} {pname} {ptype}' for dir, pname, ptype, _ in sp_parameters])
        full_sp_sql = f"CREATE PROCEDURE `{sp_name}`({formatted_params})\nBEGIN\n{textwrap.indent(sp_sql, '    ')}\nEND;;"

        # Create Markdown content using a multi-line f-string with proper formatting
        rst_content = f"""---
title: {sp_name}
---

# {sp_name}

{sp_description}

## Parameters

{parameters_table}

## SQL Definition

```sql
{full_sp_sql}
"""
        # Define the output Markdown file path
        md_file_path = os.path.join(output_dir, f'{sp_name}.md')

        # Write Markdown content to file
        try:
            with open(md_file_path, 'w', encoding='utf-8') as md_file:
                md_file.write(rst_content)
        except Exception as e:
            print(f'Error writing Markdown file for {sp_name}: {e}')
            continue
    # Append the Markdown file to the Toctree
        append_to_toctree(sp_name)
        
    print("All stored procedures have been documented successfully.")

if __name__ == '__main__':
    main()
    