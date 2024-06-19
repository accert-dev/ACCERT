# Getting Started

The main function of ACCERT (The Algorithm for the Capital Cost Estimation of Reactor Technologies) is to provide an item-by-item estimate of the cost of a facility, at present a nuclear reactor complex, primarily nuclear power stations. The core of ACCERT is the large number of algorithms that have been developed and will continue to be developed. ACCERT is also a general methodology for identifying and organizing the individual items that are estimated using the ACCERT algorithms. ACCERT also summarize status and results; to save results and pull information from previous analyses; and to provide an interactive dynamic graphical user interface for a wide range of functions and visualizations. 


The software comprises three major components:
*	Relational Database
    *	Creation, editing, and linking of different element types
    *	Report generation (queries)
    *	Search
*	Equation solvers (extraction of information from elements and evaluation/updating of fields in the database)
    *	Algorithms
    *	Escalation
    *	Cost aggregation
*	Interactive Graphical User Interface
    *	Dynamic windows


ACCERT is designed for integration with the [NEAMS
Workbench](https://www.ornl.gov/project/neams-workbench) and relies on input
files using Workbench's SON format. Instructions for installing ACCERT both
with and without Workbench are provided in this README.

## Installation

### Clone ACCERT

* For Windows user, obtain and install the [Git bash](https://git-scm.com/download/win)



*   Open a terminal window and cd into the folder where you want to install ACCERT (e.g., CODE)
    ```console
    [~]> mkdir CODE  
    [~]> cd CODE   
    [~/CODE]> git clone https://github.com/accert-dev/ACCERT.git  
    [~/CODE]> cd ACCERT
    ```

### Installation of MySQL Community Server

* Obtain the [MySQL Community Server](https://dev.mysql.com/downloads/mysql/)
* Install MySQL Community Server

    [__NOTE__] You'll need to enter a __strong password__ under Root Account Password. Don't forget your password! 
    It's extremely important that you keep track of your **root password for MySQL**, as it's difficult to reset. Write 
    it down somewhere easily accessible, or add it to a password manager to keep it secure.


### Installation of NEAMS Workbench

*   Obtain and install the [NEAMS Workbench](https://code.ornl.gov/neams-workbench/downloads)
*   **Run NEAMS Workbench** before install ACCERT

### Set up ACCERT

* Change into the src folder 

    ```console
    [~/ACCERT]> cd src 
    ```

* Edit the workbench.sh file, provide workbench_path to your NEAMS workbench location, do not include '/' at the end.

    * For Mac the default location is: 
        ```console
        workbench_path="/Applications/workbench-<version-number>.app/Contents"
        ```

    * For Windows:

        ```console
        workbench_path="/c/Workbench-<version-number>"
        ```
    * For Unix:
        ```
        workbench_path="/home/<USERNAME>/Workbench-<version-number>"
        ```

* Run __setup_accert.sh__
    ```console
    [~/src]> ./setup_accert.sh 
    ```

* Edit or create the file `install.conf` in `src` folder and change "yourpassword" to your MySQL root password.

    ```console
    [INSTALL]

    PASSWD = yourpassword

    # NOTE: ALL OTHER information should be set up later 
    # INSTALL_PATH = /usr/local 
    # DATADIR =/mysql/data
    # INSTALL_PACKAGE = 
    # EXP_DIR = 
    ```   

*   Change "yourpassword" to your **MySQL root password**.

* Run `database_install.py` to install the accertdb database.
    ```console
    [~/src]> python database_install.py
    ```

## Test installation 

*   Test ACCERT 
    ```console
    [~/src]> cd ../test 
    [~/test]> pytest
    ```


## Configuration with Workbench

* For Windows user only:
    * Go to `ACCERT/src` folder and right-click on the `Main.py` file and select `Properties` from the context menu.
    * In the Properties window, select the `Security` tab.
    * Click on the `Edit` button to change the permissions.
    * Click on `Add` to add a new user or group to the permissions list.
    * Enter your username or group name and click on `Check Names` to verify it.
    * Click on `OK` to add the user or group to the list.
    * Select the user or group that you just added from the list.
    * In the `Permissions` section, check the box next to `Full Control` to grant full control permissions to the user or group.
    * Click on `OK` to save the changes and close the Properties window.


* Open workbench, and open `Workbench/Configurations` hit `add` on the top
* Select `Accert` from the drop-down menu, hit `OK`
* In `executable`: give full path to the directory containing ACCERT/src/Main.py
* In configuration, hit `load gramma`

## ACCERT Execution

ACCERT can be executed both through the Workbench interface by pressing `run` or through the command lines:
`python ACCERT/src/Main.py -i myinput.son`



# A Tool for Quantifying Capital Cost Reduction Reduction Pathways for Advanced Nuclear Reactors
- A new tool has been developed to simulate the different pathways to reduce the costs of advanced nuclear power plants when constructed through large order books. This tool inputs various levers that represent high-level decision making and outputs the capital costs and construction duration starting from the first plant to the last plant in the order book.

-The methodology and assumptions behind this tool are documented [here]: https://inldigitallibrary.inl.gov/sites/sti/sti/Sort_109810.pdf
- There are two versions of this tool,
	1. A Python Jupyter Notebook in the folder, "Cost_Reduction". 
	2. An excel spreadsheet that can be found [here](https://fuelcycleoptions.inl.gov/Shared%20Documents/Nuclear-Reactor-Capital-Cost-Reduction-Pathway-Tool.pdf).

As currently implemented, this cost reduction tool is separate from the ACCERT cost estimation tool. In the future, the ACCERT cost estimation and cost reduction tools may be integrated so that users can estimate the costs of their own design using the estimation tool and use the cost reduction tool to simulate the evolution of its capital costs from FOAK to NOAK plants.
