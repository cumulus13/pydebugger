# pydebugger

print objects stack info with colored.


## Installing


Install and update using `pip`

```python:

    $ pip install pydebugger
```

pydebugger supports Python 2 and newer, Python 3 and newer, and PyPy.


## Example

What does it look like? Here is an example of a simple pydebugger program:

```python:
    # hello.py

    from pydebugger.debug import debug
    
    debug(variable1="data1", debug=True)
```

And what does it look like when it's run and printed in color:

```bash

    $ python hello.py 
    2024:09:12~18:21:45:822673 C:\TEMP\hello.py -> variable1: data1 -> TYPE:<class 'str'> -> LEN:5 -> [C:\TEMP\hello.py] [3] PID:21428
```

You can set OS Environment DEBUG=1 or DEBUG=True to avoid parameter "debug=1" or "debug=True"

```python:

    from pydebugger.debug import debug
    
    debug(variable1="data1")
```

or you just run "debug.py" to provider debug server with Client support OS Environment

```bash:
    # on terminal 

	export DEBUG_SERVER=1
	export DEBUGGER_SERVER=127.0.0.1:50001
    # then run hello.py
```
this will send all of info to debug server run on '127.0.0.1' with port 50001

or you can run debug server on spesific port number
```bash
$ debug.py 50005
```

Support
--------

*   Python 2.7+, Python 3.x
*   Windows, Linux

## author
[Hadi Cahyadi](mailto:cumulus13@gmail.com)
    

[![Donate via Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/cumulus13)
 [Support me on Patreon](https://www.patreon.com/cumulus13)
