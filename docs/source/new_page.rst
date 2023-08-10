Using ACCERT (With Python)
==========================
.. admonition:: Using ACCERT!

    To begin using ACCERT, there are terms and applications to familiarize yourself with.

*   Code of Account (COA)

    *   Every component of a nuclear reactor has its own unique COA.

        *   The codes have different varying levels, even some up to 5.
        *   Most codes are between levels 0-3.
        *   The levels just break down each cost element by different subtasks within them.

    *   The COA has a cost aggregation that consists of three sub-categories at its most basic level.

        *   Factory equipment, which is usually described in dollars, or could be automatically converted.
        *   Labor costs.
        *   Material costs, which have specific quantities. (square feet, tons, cubic yards, linear feet, etc.)

*   Workbench

    *   ACCERT uses the workbench interface to display a table of costs.

*   Databases

    *   ACCERT, as mentioned before, comprises of three major components, one of them being the relational database.
    *   The relational database compiles all the different costs of various lower-level costs, and displays them based on their level.
    *   The databases are based off of cost reports of two model reactors as of June 2023:

        *   The Pressurized Water Reactor (PWR12-BE)
        *   The Advanced Burner reactor (ABR-1000)

    *   ACCERT bases all of the algorithms off of previously estimated reactors, and uses something called an elevation element to account for inflation throughout the years.

**Testing Python**

*   To begin, open up a command terminal, and type the following into it.

.. code-block:: text

      $ cd ACCERT
      $ python -m pip install --upgrade pip


*	If python is installed, it will uninstall pip and reinstall it.

*	Install pip requirements

.. code-block:: text

      $ pip install -r requirements.txt


*	A lot of code pops up, and at the end it should say a lot of different things were successfully installed.

*   Next in the command terminal, type the following:

.. code-block:: text
      
        $ cd test
        $ pytest

*	This part might take a minute or two, and at the end there will be a few different percentages, hopefully with the code passing the tests.

**Using Python to Run ACCERT**

*   Begin by opening your Python text editor of choice. (Visual Studio Code is a good option.) 

    *   Open the file of the reference reactor you would like to compare your cost estimate to.
    *   There are two required parameters that need to be changed based on the theoretical reactor you are creating.

        *   The thermal and electrical power produced by the theoretical reactor should be put into the parameters listed in the first few lines of code.
        *   There are also several variables or parameters that the user can change to fit their theoretical reactor design.
        *   For example, one of the radii of the theoretical design can be written in the code as var(Cont_rad_out_m){value = xx unit = m}. 
        *   The value would be the variable that the user can change, and would alter every cost estimate that the COA has ties to.

*   After making all the adjustments to the desired variables, move into the tutorial folder in the command terminal and run the python code.

.. code-block:: text
    
        $ cd ..
        $ cd tutorial
        $ python ../src/Main.py -i myinput.son
        $ code output.out

.. admonition:: NOTICE!

    Replace **../src/Main.py** with the path to your Main.py file, and the **myinput.son** file with the desired reactor .son file.

*  This is used to collect various inputs from any given database for a nuclear reactor.

      *  For example:

.. code-block:: text

        $ python ACCERT/src/Main.py -i PWR12-BE.son

*   After running the code, open the output.out file in a python coding application.

    *   This will display a list of variables that the user altered, and the cost elements associated with it.
    *   With this, the cost aggregation algorithm will start to work on summing up the costs with respect to the changed parameters.
    *   ACCERT will then sum up all the costs and display it into one easy to read graph that displays the COA, account description, costs, unit, level, and the review status.

        *   The review status is just whether or not the COA or any of it's sub-levels have been changed.

.. admonition:: NOTICE!

    An output of ACCERT can be found in the "*Output of ACCERT*" tab.
