.. _contributing:

Contributing
------------

We welcome contributions to ACCERT! Whether it's reporting bugs, suggesting new features, or improving documentation, your input is valuable. Please follow the guidelines below to ensure smooth collaboration.

Getting Started
~~~~~~~~~~~~~~~

1. **Fork the Repository**:

- Navigate to the ACCERT repository on GitHub.
- Click the "Fork" button in the top-right corner to create a copy of the repository in your GitHub account.

2. **Clone the Forked Repository**:

- Clone your fork to your local machine:
     
.. code-block:: console

    git clone https://github.com/YOUR-USERNAME/ACCERT.git
    cd ACCERT

3. **Create a Branch**:

- It's best practice to create a new branch for each feature or fix you are working on:

.. code-block:: console

    git checkout -b my-new-feature

4. **Set Up Your Environment**:

- Ensure you have Python installed and set up your virtual environment and install the required dependencies by running:

     
.. code-block:: console

    python3 -m venv venv
    source venv/bin/activate  # On Windows use: venv\Scripts\activate
    pip install -r requirements.txt

5. **Run Tests**:

- Before making any changes, run the existing test suite to ensure everything works as expected:

.. code-block:: console

    pytest


Reporting Bugs
^^^^^^^^^^^^^^

If you encounter a bug, please report it by following these steps:

1. **Search Existing Issues**: 

- Check the `Issues section <https://github.com/accert-dev/ACCERT/issues>`_ to see if the bug has already been reported.

2. **Create a New Issue**:

- If the bug hasn’t been reported, open a new issue. Be sure to include:
   - A descriptive title.
   - A detailed description of the problem.
   - Steps to reproduce the issue.
   - Relevant logs or error messages.
   - The environment you are using (e.g., OS, Python version).

Suggesting Enhancements
^^^^^^^^^^^^^^^^^^^^^^^

If you have ideas for improving ACCERT, we encourage you to suggest enhancements.

1. **Check for Existing Suggestions**:
- Search the `Issues section <https://github.com/accert-dev/ACCERT/issues>`_ for existing enhancement requests.

2. **Propose a New Feature**:

- Open a new issue with the **Feature Request** template and provide as much detail as possible about the feature:

   - What problem does the enhancement solve?
   - How do you envision the feature being implemented?
   - Include any relevant examples or use cases.

Submitting Code Changes
^^^^^^^^^^^^^^^^^^^^^^^

If you'd like to contribute code, follow these steps:

1. **Work in a Branch**:

- Create a new branch for your contribution.

2. **Make Your Changes**:

- Follow the style guide of the existing codebase.
- Ensure that your changes don’t break existing functionality by running tests.

3. **Add Tests**:

- Any new features or bug fixes should be accompanied by appropriate tests.

4. **Run Tests**:

- Ensure that all tests pass:
     
.. code-block:: console

    pytest


5. **Commit Your Changes**:

- Write clear, concise commit messages that explain the purpose of the change:

.. code-block:: console

    git commit -m "Add new feature: description"

6. **Push to GitHub**:

- Push your branch to your forked repository:
   
.. code-block:: console

    git push origin my-new-feature


7. **Open a Pull Request (PR)**:

- Go to the original `ACCERT repository <https://github.com/accert-dev/ACCERT>`_ and open a new pull request:

   - Make sure to describe the changes you’ve made in the PR description.
   - Include any relevant issue numbers (e.g., `Fixes #123`).
   - If applicable, provide context on why certain decisions were made.

Reviewing and Merging
^^^^^^^^^^^^^^^^^^^^^^

Once your PR is submitted, it will be reviewed by one of the maintainers. Here’s what you can expect:

1. **Feedback**:

   - You may receive feedback on your PR. Be open to making adjustments or clarifications as needed.
   
2. **Revisions**:

   - If changes are requested, push the revisions to your branch. This will automatically update your PR.
   
3. **Merging**:

   - Once approved, your PR will be merged into the main branch. You may also be asked to rebase your branch if there are conflicts.


