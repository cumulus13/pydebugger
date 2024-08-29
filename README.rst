pydebugger
==================

print objects stack info with colored.


Installing
-----------

Install and update using `pip`_:

.. code-block:: text

    $ pip install pydebugger

pydebugger supports Python 2 and newer, Python 3 and newer, and PyPy.

.. _pip: https://pip.pypa.io/en/stable/quickstart/


Example
----------------

What does it look like? Here is an example of a simple pydebugger program:

.. code-block:: python

    from pydebugger.debug import debug
    
    debug(variable1="data1", debug=True)


And what it looks like when run:

.. code-block:: text

    $ python hello.py 
    2019:04:18~13:20:19:286000 <module> -> variable1: data1 -> TYPE:<type 'str'> -> LEN:5 ->  [<FILE DIRECTORY>/test.py] [3] PID:10496

You can set OS Environment DEBUG=1 or DEBUG=True to avoid parameter "debug=True"

.. code-block:: python

    from pydebugger.debug import debug
    
    debug(variable1="data1")

or you just run "debug.py" to provider debug server with Client support OS Environment

.. code-block:: bash
    
	DEBUG_SERVER=1
	DEBUGGER_SERVER=0.0.0.0:50001


Support
--------

*   Python 2.7 +, Python 3.x
*   Windows, Linux

Links
------

*   License: `BSD <https://github.com/cumulus13/pydebugger/src/default/LICENSE.rst>`_
*   Code: https://github.com/cumulus13/pydebugger
*   Issue tracker: https://github.com/cumulus13/pydebugger/issues