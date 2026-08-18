Mirror Example
==============

The Mirror example demonstrates the magnetic-mirror fusion reference model
ported from upstream ACCERT PR #50. The input file is located at
``ACCERT/tutorial/accert/Mirror.son``.

Example input
-------------

.. literalinclude:: ../../../tutorial/accert/Mirror.son
   :language: none

The example selects ``ref_model = "mirror"`` and updates the ``r_magnet``
variable. The current Mirror reference data is account-table based and does
not include a cost-element table.

Running the example
-------------------

From ``tutorial/accert``:

.. code-block:: shell

   python ../../src/Main.py -i Mirror.son

ACCERT writes the updated account output using the ``mirror`` model prefix.
