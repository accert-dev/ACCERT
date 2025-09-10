Webhost Output Visualization
============================

The ACCERT webhost module provides a web-based interface for processing and visualizing ACCERT output data. This tool allows you to upload output files, extract tabular data, and view interactive tables and charts through your web browser.

Installation Requirements
-------------------------

Prerequisites
~~~~~~~~~~~~~

- Python 3.7 or higher
- Web browser (Chrome, Firefox, Safari, or Edge)

Installing Dependencies
~~~~~~~~~~~~~~~~~~~~~~~

1. Navigate to the webhost directory:

   .. code-block:: bash

      cd src/webhost

2. Install the required Python packages:

   .. code-block:: bash

      pip install -r requirements.txt

   This will install:
   
   - Flask 2.3.3 (web framework)
   - Werkzeug 2.3.7 (WSGI utility library)

Starting the Local Server
--------------------------

Method 1: Using Python (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Open a terminal/command prompt and navigate to the webhost directory:

   .. code-block:: bash

      cd src/webhost

2. Start the Flask server:

   .. code-block:: bash

      python server.py

3. You should see output similar to:

   .. code-block:: text

      Starting ACCERT Output Processor Server...
      Access the application at: http://localhost:3000
      Upload page: http://localhost:3000
      Table display: http://localhost:3000/table_display.html
       * Running on all addresses (0.0.0.0)
       * Running on http://127.0.0.1:3000
       * Running on http://[::]:3000

Method 2: Using Windows Batch File
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

On Windows systems, you can use the provided batch file:

1. Double-click ``start_server.bat`` in the webhost directory
2. The server will start automatically in a command prompt window

Accessing the Web Interface
----------------------------

Once the server is running, open your web browser and navigate to:

- **Main page**: http://localhost:3000
- **Upload processor**: http://localhost:3000/upload_processor.html
- **Table display**: http://localhost:3000/table_display.html
- **Debug viewer**: http://localhost:3000/debug_table.html

Using the Webhost Application
------------------------------

Step 1: Upload and Process Output Files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Go to the **Upload Processor** page (http://localhost:3000)

   .. image:: ../_static/ACCERT_Screenshot (1).png
      :alt: ACCERT Output Processor main page
      :width: 800px
      :align: center

   *Figure 1: Main ACCERT Output Processor interface*

2. Click "Choose File" and select your ACCERT output file (``.out`` extension)

   .. image:: ../_static/ACCERT_Screenshot (2).png
      :alt: File upload interface
      :width: 800px
      :align: center

   *Figure 2: File upload interface with file selection*

3. Click "Process File" to extract the tabular data

   .. image:: ../_static/ACCERT_Screenshot (3).png
      :alt: File processing in progress
      :width: 800px
      :align: center

   *Figure 3: File processing interface showing upload status*

4. The system will process the file and create ``init_process_data.csv``

   .. image:: ../_static/ACCERT_Screenshot (4).png
      :alt: Processing results and success message
      :width: 800px
      :align: center

   *Figure 4: Processing complete with success message*

5. You'll see a success message when processing is complete

Step 2: View Processed Data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Navigate to the **Table Display** page (http://localhost:3000/table_display.html)

   .. image:: ../_static/ACCERT_Screenshot (5).png
      :alt: Table display page with data loaded
      :width: 800px
      :align: center

   *Figure 5: Table display page showing processed data*

2. The page will automatically load the processed CSV data

   .. image:: ../_static/ACCERT_Screenshot (6).png
      :alt: Data table with search and filter options
      :width: 800px
      :align: center

   *Figure 6: Interactive data table with search functionality*

3. Use the available features:

   **Search and Filter:**
   
   - Use the search box to filter rows by any column content
   - Results update in real-time as you type

   .. image:: ../_static/ACCERT_Screenshot (7).png
      :alt: Search and filtering interface
      :width: 800px
      :align: center

   *Figure 7: Search and filtering options*

   **Data Grouping:**
   
   - Toggle "Group by Level" to organize data hierarchically
   - Select different account levels (0-4) using the dropdown
   - Filter accounts by code or description

   **Interactive Charts:**
   
   - Click "Show Charts" to enable visualization
   - Select specific accounts to chart using the multi-select dropdown
   - Use "Select All" or "Clear Selection" for quick selection
   - Refresh charts with updated data using "Refresh Chart"

   **Data Export:**
   
   - Click "Download CSV" to save the current filtered data

Step 3: View Detailed Data Analysis
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The processed data can be viewed in various formats:

.. image:: ../_static/ACCERT_Screenshot (8).png
   :alt: Detailed data view with multiple columns
   :width: 800px
   :align: center

*Figure 8: Detailed data view showing comprehensive table structure*

.. image:: ../_static/ACCERT_Screenshot (9).png
   :alt: Filtered data view
   :width: 800px
   :align: center

*Figure 9: Filtered data view with specific criteria applied*

.. image:: ../_static/ACCERT_Screenshot (10).png
   :alt: Final data analysis view
   :width: 800px
   :align: center

*Figure 10: Final data analysis view with complete dataset*

Step 4: Debug Data Issues
~~~~~~~~~~~~~~~~~~~~~~~~~

If you encounter issues with data processing:

1. Visit the **Debug Table** page (http://localhost:3000/debug_table.html)
2. This page shows:
   
   - CSV file loading status
   - Parse errors (if any)
   - Column information
   - First 5 rows of data
   - Detailed error messages

File Structure and Processing
-----------------------------

Input File Requirements
~~~~~~~~~~~~~~~~~~~~~~~

The webhost application expects ACCERT output files with:

- Markdown-style table format
- Column separator: ``|`` (pipe character)
- Header containing ``code_of_account``
- Horizontal rules with ``+--`` pattern

Output File Location
~~~~~~~~~~~~~~~~~~~~

Processed CSV files are saved as:

- **Filename**: ``init_process_data.csv``
- **Location**: Same directory as the webhost application (``src/webhost/``)

Command Line Processing
~~~~~~~~~~~~~~~~~~~~~~~

You can also process files directly using the command line:

.. code-block:: bash

   cd src/webhost
   python csv_extractor.py /path/to/your/output_file.out

This will create ``init_process_data.csv`` in the webhost directory.

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**Server won't start:**

- Check if Python is installed: ``python --version``
- Verify dependencies are installed: ``pip list | grep Flask``
- Try a different port if 3000 is busy

**File upload fails:**

- Ensure file size is under 16MB
- Check file format (should be plain text with table structure)
- Verify the file contains a table with ``code_of_account`` header

**CSV not displaying:**

- Check if ``init_process_data.csv`` exists in the webhost directory
- Try the debug page to see detailed error information
- Refresh the browser page

**Charts not showing:**

- Enable "Group by Level" first
- Click "Show Charts" button
- Select at least one account from the dropdown
- Try "Refresh Chart" if data seems stale

Cross-Platform Compatibility
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The webhost application works on:

- **Windows**: Use ``start_server.bat`` or ``python server.py``
- **macOS**: Use ``python server.py`` in Terminal
- **Linux**: Use ``python server.py`` in terminal

All file paths and operations are cross-platform compatible.

Stopping the Server
--------------------

To stop the webhost server:

1. Return to the terminal/command prompt where the server is running
2. Press ``Ctrl+C`` (Windows/Linux) or ``Cmd+C`` (macOS)
3. The server will shut down gracefully

Advanced Configuration
----------------------

Port Configuration
~~~~~~~~~~~~~~~~~~

To change the default port (3000), modify ``server.py``:

.. code-block:: python

   app.run(debug=True, host='0.0.0.0', port=YOUR_PORT_NUMBER)

File Size Limits
~~~~~~~~~~~~~~~~

To modify the maximum upload file size, edit ``server.py``:

.. code-block:: python

   app.config['MAX_CONTENT_LENGTH'] = SIZE_IN_BYTES

Development Mode
~~~~~~~~~~~~~~~~

The server runs in debug mode by default. For production use, change:

.. code-block:: python

   app.run(debug=False, host='0.0.0.0', port=3000)
