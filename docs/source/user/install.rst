
Installation Guide
==================

This guide provides step-by-step instructions to install ACCERT on **Windows**, **macOS**, and **Linux** systems. Please ensure you have administrative privileges on your device, as some steps require it.


Prerequisites
-------------

- **Git**: Ensure Git is installed on your system.

  - Download from `Git - Downloads <https://git-scm.com/downloads>`_ if not already installed.
  - Verify installation by typing ``git`` in your terminal; if commands appear, Git is installed.
- **Python Coding Environment**: While not required, using an IDE like Visual Studio Code is recommended.
- **MySQL Community Server**: Required for database functionalities.
- **NEAMS Workbench**: Necessary for integrating ACCERT with the Workbench interface.

Installation Instructions
-------------------------

Choose your operating system to proceed with the installation:

- `Installation on Windows`_
- `Installation on macOS`_
- `Installation on Linux`_

Installation on Windows
-----------------------

.. _Installation on Windows:

For certain aspects of this process, you will need administrative privileges.

Cloning ACCERT
~~~~~~~~~~~~~~

1. **Create a Directory for ACCERT**:

   - Open your file explorer and create a folder where you want to install ACCERT (e.g., ``CODE``).

2. **Open Git Bash or Terminal**:

   - Navigate to the directory you just created.

3. **Clone the ACCERT Repository**:

   .. code-block:: shell

       $ cd /path/to/CODE
       $ git clone https://github.com/accert-dev/ACCERT.git
       $ cd ACCERT

   - Replace ``/path/to/CODE`` with the actual path to your ``CODE`` directory.

4. **Verify Cloning**:

   - Ensure the ACCERT folder contains files similar to the ACCERT Git repository.

Install MySQL Community Server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Download MySQL**:

   - Visit `MySQL Community Server <https://dev.mysql.com/downloads/mysql/>`_ and download the recommended version for Windows.

2. **Install MySQL**:

   - Follow the installation prompts, selecting the **Developer Default** setup when available.

   .. admonition:: Important
      :class: important

      During installation, you will be prompted to create a **root password** for MySQL. **Keep this password secure and accessible**; resetting it can be time-consuming and difficult.

   .. image:: ../_static/password1.png
      :width: 600
      :alt: MySQL Password Setup

   .. image:: ../_static/password2.png
      :width: 600
      :alt: MySQL Configuration

Install NEAMS Workbench
~~~~~~~~~~~~~~~~~~~~~~~

1. **Download NEAMS Workbench**:

   - Go to `NEAMS Workbench Downloads <https://code.ornl.gov/neams-workbench/downloads>`_.
   - Download the `.exe` file for Windows.

2. **Run the Installer**:

   - Execute the downloaded file and follow the installation instructions.
   - **Note**: Your system may flag the installer as unsafe. The file is safe; proceed by selecting the option to keep or run the file.

3. **Launch NEAMS Workbench**:

   - Open the Workbench application before proceeding to the next steps.

Setting Up ACCERT
~~~~~~~~~~~~~~~~~

1. **Navigate to the `src` Directory**:

   .. code-block:: shell

       $ cd src

2. **Edit the `workbench.sh` File**:

   - Open `workbench.sh` in your Python coding application.
   - Set the `workbench_path` variable to point to your NEAMS Workbench installation directory.
     - For example:

   .. code-block:: shell

      workbench_path="C:/Path/To/Workbench-<version-number>"

     - Replace `<version-number>` with the actual version number (e.g., `Workbench-5.3.1`).
     - **Ensure there are no spaces in the folder path**, as this may cause issues.
   - Save the file.

3. **Run the Setup Script**:

   - Open a terminal in the `src` directory.
   - Execute the setup script:

     .. code-block:: shell

         $ ./setup_accert.sh

   - **Note**: If you encounter issues running the script, ensure that Git Bash or a Unix-compatible terminal is used.

4. **Copy Executables to ACCERT `bin` Directory**:

   - Manually create a `bin` directory inside your `ACCERT` folder if it doesn't exist.
   - Navigate to the `bin` folder inside your NEAMS Workbench installation.
   - Copy `sonvalidxml` from the Workbench `bin` folder to the `ACCERT/bin` folder.

Create and Edit `install.conf`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Create `install.conf`**:

   - In the `src` directory, create a new file named `install.conf`.

2. **Add the Following Content**:

   .. code-block:: ini

       [INSTALL]
       PASSWD = yourpassword

       # NOTE: ALL OTHER information should be set up later
       # INSTALL_PATH = /usr/local
       # DATADIR = /mysql/data
       # INSTALL_PACKAGE =
       # EXP_DIR =

   - Replace ``yourpassword`` with your MySQL root password.
   - Save the file with the exact name `install.conf`.
   - **Ensure file extensions are visible**:
     - In File Explorer, go to `View` > `Show` > `File name extensions`.
     - Verify that the file is not saved as `install.conf.txt`.

Install database
~~~~~~~~~~~~~~~~

1. **Navigate to ACCERT/src folder**:
   - type "cmd" in the address bar of the file explorer and press enter.
   
   .. code-block:: shell

      $ mysql -h localhost -u root -p 

   - Enter your MySQL root password when prompted.
   - Run the following command to create the ACCERT database:
   
   .. code-block:: shell

      mysql> source accertdb.sql
   
   - Verify that the database has been created by running the following command:
   
   .. code-block:: shell

      mysql> show databases;

   - You should see `accert_db` in the list of databases. Then exit the MySQL shell by typing:

   .. code-block:: shell

      mysql> \q


   


Installation on macOS
---------------------

.. _Installation on macOS:

For certain aspects of this process, you will need administrative privileges.

Cloning ACCERT
~~~~~~~~~~~~~~

1. **Create a Directory for ACCERT**:

   - Open your file explorer and create a folder where you want to install ACCERT (e.g., ``CODE``).

2. **Open Git Bash or Terminal**:

   - Navigate to the directory you just created.

3. **Clone the ACCERT Repository**:

   .. code-block:: shell

       $ cd /path/to/CODE
       $ git clone https://github.com/accert-dev/ACCERT.git
       $ cd ACCERT

   - Replace ``/path/to/CODE`` with the actual path to your ``CODE`` directory.

4. **Verify Cloning**:

   - Ensure the ACCERT folder contains files similar to the ACCERT Git repository.

Install MySQL Community Server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Download MySQL**:

   - Visit `MySQL Community Server <https://dev.mysql.com/downloads/mysql/>`_ and download the recommended version for macOS.

2. **Install MySQL**:

   - Follow the installation prompts, selecting the **Developer Default** setup when available.
   - Remember to keep your MySQL root password secure.

Install NEAMS Workbench
~~~~~~~~~~~~~~~~~~~~~~~

1. **Download NEAMS Workbench**:

   - Go to `NEAMS Workbench Downloads <https://code.ornl.gov/neams-workbench/downloads>`_.
   - Download the `.dmg` file for macOS.

2. **Run the Installer**:

   - Open the downloaded `.dmg` file and follow the installation instructions.
   - **Note**: Your system may flag the installer as unsafe. The file is safe; proceed accordingly.

3. **Launch NEAMS Workbench**:

   - Open the Workbench application before proceeding to the next steps.

Setting Up ACCERT
~~~~~~~~~~~~~~~~~

1. **Navigate to the `src` Directory**:

   .. code-block:: shell

       $ cd src

2. **Edit the `workbench.sh` File**:

   - Open `workbench.sh` in your Python coding application.
   - Set the `workbench_path` variable to point to your NEAMS Workbench installation directory:

     .. code-block:: shell

         workbench_path="/Applications/Workbench-<version-number>.app/Contents"

     - Replace `<version-number>` with the actual version number (e.g., `Workbench-5.3.1`).
   - Save the file.

3. **Run the Setup Script**:

   - Make the setup script executable:

     .. code-block:: shell

         $ chmod +x setup_accert.sh

   - Execute the setup script:

     .. code-block:: shell

         $ ./setup_accert.sh

Create and Edit `install.conf`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Create `install.conf`**:

   - In the `src` directory, create a new file named `install.conf`.

2. **Add the Following Content**:

   .. code-block:: ini

       [INSTALL]
       PASSWD = yourpassword

       # NOTE: ALL OTHER information should be set up later
       # INSTALL_PATH = /usr/local
       # DATADIR = /mysql/data
       # INSTALL_PACKAGE =
       # EXP_DIR =

   - Replace ``yourpassword`` with your MySQL root password.
   - Save the file with the exact name `install.conf`.
   - **Ensure file extensions are visible**:
     - In File Explorer, go to `View` > `Show` > `File name extensions`.
     - Verify that the file is not saved as `install.conf.txt`.

Install database
~~~~~~~~~~~~~~~~

1. ** connect to MySQL**:
   .. code-block:: shell

      $ mysql -h localhost -u root -p 

   - Enter your MySQL root password when prompted.
   - Run the following command to create the ACCERT database:
   
   .. code-block:: shell

      mysql> source accertdb.sql
   
   - Verify that the database has been created by running the following command:
   
   .. code-block:: shell

      mysql> show databases;

   - You should see `accert_db` in the list of databases. Then exit the MySQL shell by typing:

   .. code-block:: shell

      mysql> \q





Installation on Linux
---------------------

.. _Installation on Linux:

For certain aspects of this process, you will need administrative privileges.

Cloning ACCERT
~~~~~~~~~~~~~~

1. **Create a Directory for ACCERT**:

   - Open your file explorer and create a folder where you want to install ACCERT (e.g., ``CODE``).

2. **Open Git Bash or Terminal**:

   - Navigate to the directory you just created.

3. **Clone the ACCERT Repository**:

   .. code-block:: shell

       $ cd /path/to/CODE
       $ git clone https://github.com/accert-dev/ACCERT.git
       $ cd ACCERT

   - Replace ``/path/to/CODE`` with the actual path to your ``CODE`` directory.

4. **Verify Cloning**:

   - Ensure the ACCERT folder contains files similar to the ACCERT Git repository.

Install MySQL Community Server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Download and Install MySQL**:

   - Install MySQL using your distribution's package manager, or download it from `MySQL Community Server <https://dev.mysql.com/downloads/mysql/>`_.

   .. code-block:: shell

       # For Debian/Ubuntu
       $ sudo apt-get update
       $ sudo apt-get install mysql-server

       # For CentOS/RHEL
       $ sudo yum install mysql-server

2. **Secure MySQL Installation**:

   .. code-block:: shell

       $ sudo mysql_secure_installation

   - Set the root password and follow the prompts.

Install NEAMS Workbench
~~~~~~~~~~~~~~~~~~~~~~~

1. **Download NEAMS Workbench**:

   - Go to `NEAMS Workbench Downloads <https://code.ornl.gov/neams-workbench/downloads>`_.
   - Download the `.tar.gz` file for Linux.

2. **Extract and Install**:

   .. code-block:: shell

       $ tar -xzvf Workbench-<version-number>.tar.gz
       $ cd Workbench-<version-number>

3. **Run the Installer**:

   - Follow any additional installation instructions provided.

4. **Launch NEAMS Workbench**:

   - Run the Workbench application before proceeding to the next steps.

Setting Up ACCERT
~~~~~~~~~~~~~~~~~

1. **Navigate to the `src` Directory**:

   .. code-block:: shell

       $ cd src

2. **Edit the `workbench.sh` File**:

   - Open `workbench.sh` in your Python coding application.
   - Set the `workbench_path` variable to point to your NEAMS Workbench installation directory:

     .. code-block:: shell

         workbench_path="/path/to/Workbench-<version-number>"

     - Replace `<version-number>` with the actual version number.
   - Save the file.

3. **Run the Setup Script**:

   - Make the setup script executable:

     .. code-block:: shell

         $ chmod +x setup_accert.sh

   - Execute the setup script:

     .. code-block:: shell

         $ ./setup_accert.sh

Create and Edit `install.conf`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Create `install.conf`**:

   - In the `src` directory, create a new file named `install.conf`.

2. **Add the Following Content**:

   .. code-block:: ini

       [INSTALL]
       PASSWD = yourpassword

       # NOTE: ALL OTHER information should be set up later
       # INSTALL_PATH = /usr/local
       # DATADIR = /mysql/data
       # INSTALL_PACKAGE =
       # EXP_DIR =

   - Replace ``yourpassword`` with your MySQL root password.
   - Save the file with the exact name `install.conf`.

Install database
~~~~~~~~~~~~~~~~

1. ** connect to MySQL**:
   .. code-block:: shell

      $ mysql -h localhost -u root -p 

   - Enter your MySQL root password when prompted.
   - Run the following command to create the ACCERT database:
   
   .. code-block:: shell

      mysql> source accertdb.sql
   
   - Verify that the database has been created by running the following command:
   
   .. code-block:: shell

      mysql> show databases;

   - You should see `accert_db` in the list of databases. Then exit the MySQL shell by typing:

   .. code-block:: shell

      mysql> \q


Testing the Installation
-------------------------
1. **Navigate to the Test Directory**:

   .. code-block:: shell

       $ cd ../test

2. **Run Tests Using Pytest**:

   .. code-block:: shell

       $ pytest

   - This will run the test suite to verify that ACCERT is installed correctly.

Configuration with NEAMS Workbench
----------------------------------

1. **Open NEAMS Workbench**.

2. **Add ACCERT Configuration**:

   - Go to `Workbench` > `Configurations` and click `Add`.
   - Select `Accert` from the drop-down menu and click `OK`.

3. **Set Executable Path**:

   - In the configuration settings, set the **Executable** field to the full path of `Main.py` in the `ACCERT/src/` directory.

4. **Load Grammar**:

   - In the configuration, click `Load Grammar` to load ACCERT's input grammar into Workbench.

ACCERT Execution
----------------

**Through NEAMS Workbench**


- Press the `Run` button within the Workbench interface to execute ACCERT with your selected input file.

**Through Command Line**


- Execute ACCERT using Python:

  .. code-block:: shell

      $ python ACCERT/src/Main.py -i myinput.son

  - Replace `myinput.son` with your input file, such as `PWR12-BE.son` or `ABR1000.son`.

Troubleshooting
---------------

- **Conda Errors**:

  - Ensure that Conda is correctly installed and accessible in your system's PATH.
  - Running ``conda install -r requirements.txt`` should be done in the environment where ACCERT will run.
  - If you encounter an error like ``bash: ./conda: Is a directory``, ensure you're referencing the correct path to the Conda executable.

- **Workbench Connection Issues**:

  - If ACCERT cannot connect to Workbench:
    - Verify that the `workbench_path` in `workbench.sh` is correct and does not contain spaces.
    - Ensure that you have the necessary permissions to execute scripts.

- **Password Issues**:

  - If you forget your MySQL root password, refer to MySQL's official documentation on how to reset the password.
  - It's crucial to keep your password secure and accessible.

- **File Extensions on Windows**:

  - Ensure that file extensions are visible:
    - In File Explorer, go to `View` > `Show` > `File name extensions`.
  - Verify that `install.conf` is not mistakenly saved as `install.conf.txt`.

Additional Resources
--------------------

- **ACCERT GitHub Repository**:
  - `https://github.com/accert-dev/ACCERT <https://github.com/accert-dev/ACCERT>`_
- **NEAMS Workbench Documentation**:
  - `NEAMS Workbench User Guide <https://code.ornl.gov/neams-workbench/documentation>`_




