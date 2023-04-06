
# Contributing


## Governance

Contributions to ACCERT must be made through a merge request (MR) at
https://github.com/accert-dev/ACCERT. Even long-term members and
developers must submit changes via MRs to provide a consistent record of the
purpose of contributions as well as to allow other maintainers/developers to
provide feedback on code changes and design decisions.

No merge request should be merged to the `main` branch without independent
review.

If objections to certain merge requests are raised, the author of the merge
request and reviewers should seek to arrive at a consensus before the MR is
either merged or closed (rejected).

## Code Review Criteria

In order to be considered suitable for inclusion in the ACCERT repository, the
following criteria must be satisfied for all proposed changes:

  - Changes have a clear purpose and are useful.

  - All continuous integration tests pass in gitlab's CI.

  - If appropriate, test cases are added to regression or unit test suites.

  - Conforms to the [PEP8](https://www.python.org/dev/peps/pep-0008/) style guide where possible.

  - New features/input are documented.

  - No unnecessary external software dependencies are introduced.

## Workflow

We currently encourage a forking workflow for contributions to ACCERT. This
workflow involves the following steps:

  1. Fork the main ACCERT repository under your user account at
     https://github.com/accert-dev/ACCERT 
  2. Clone your fork of ACCERT locally to make changes to the code.
  ```shell
  $ git clone https://github.com/your_username/ACCERT
  $ cd ACCERT
  $ git checkout -b new_branch main
  ```
  3. Make your changes in your local branch and push the branch to your fork
     when ready.

  4. Open a merge request on gitlab to the main ACCERT repository with a
     description of the changes along with motivation for these changes if they
     aren't adressing an open issue in ACCERT.
  5. Another maintainer/developer will review your merge request based on the
     criteria above. Any issues with the merge request can be discussed directly
     on in the MR.
  6. When the merge request has been approved, it will be merged into the main
     branch of ACCERT.
