.. Log - Logger

.. toctree::
    :maxdepth: 2

Log - Logger
============
The :mod:`geosutils.log` module wraps the standard Python :mod:`logging`
module and abstract some of the messy parts.  :mod:`logging` itself is
is similar to (possibly even motivated by) the
`log4j <http://http://logging.apache.org/log4j/1.2/>`_ facility.
Most importantly, :mod:`logging` guarantees a singleton object that can be
used throughout your project.

One of the handiest features with :mod:`geosutils.log` is that it
automatically detects the output stream and is able to direct the logging
ouput to ``STDOUT`` or to a file stream (if configured).

Simplest Usage (Console)
------------------------

Simply import the :mod:`geosutils.log` ``log`` handler object into your
project.


    .. note::

        Behind the scenes, the :mod:`geosutils.log` ``log`` handler object
        is instantiated through the module-level function
        ``logging.getLogger(name)``.  Multiple calls to :func:`getLogger`
        with the same name will always return a reference to the same
        Logger object.
        
        ``name`` is defined as the highest level Python calling module.  For
        example, in the :ref:`module_usage_file_based_configuration`
        sample below, ``name`` will be ``you_beaut.py``.  For normal
        console-based output, name would be ``<stdin>``.

The following example demonstrates usage directly under the Python
interpreter::

    $ python
    >>> from geosutils.log import log
    >>> log.debug('This is a DEBUG level logging')
    2014-06-26 10:07:59,297 DEBUG:: This is a DEBUG level logging
    >>> log.info('This is a INFO level logging')
    2014-06-26 10:08:12,481 INFO:: This is a INFO level logging

.. note::

    This example demonstrates console-based usage that writes to ``STDOUT``

.. _module_usage_file_based_configuration:

Module Usage (File-based Configuration)
---------------------------------------

Logging from your ``*.py`` is probably a more useful proposition.
Similarly, import the :mod:`geosutils.log` to your python module.
To demonstrate, add the following code into a file called ``you_beaut.py``::

    from geosutils.log import log

    log.debug('Log from inside my Python module')

To execute::

    $ python you_beaut.py
    2014-06-26 10:41:15,036 DEBUG:: Log from inside my Python module

But what if you want to log to a file?  In this case you will have to
provide a configuration file.  The structure of the config is
standard :mod:`logging`.  In this case, place the following into
a the file called ``log.conf`` in the same directory as ``you_beaut.py``::

    [loggers]
    keys=root,you_beaut.py,console

    [handlers]
    keys=youBeautFileHandler,consoleHandler

    [formatters]
    keys=simpleFormatter

    [logger_root]
    level=DEBUG
    handlers=consoleHandler

    [logger_console]
    level=DEBUG
    handlers=consoleHandler
    qualname=console
    propagate=0

    [logger_you_beaut.py]
    level=DEBUG
    qualname=you_beaut.py
    handlers=youBeautFileHandler

    [handler_youBeautFileHandler]
    class=handlers.TimedRotatingFileHandler
    level=DEBUG
    formatter=simpleFormatter
    args=(os.path.join(os.sep, 'var', 'tmp', 'you_beaut.log'), 'midnight')

    [handler_consoleHandler]
    class=StreamHandler
    level=DEBUG
    formatter=simpleFormatter
    args=(sys.stdout, )

    [formatter_simpleFormatter]
    format=%(asctime)s (%(levelname)s): %(message)s
    datefmt=

Now when you ``$ python you_beaut.py`` you will notice that output to
the console is suppressed.  Instead, the output is directed to a file
stream defined by ``handler_youBeautFileHandler`` section from the
``log.conf`` file.  To verify::

    $ cat /var/tmp/you_beaut.log
    2014-06-26 11:39:34,903 (DEBUG): Log from inside my Python module

Functions
---------
.. currentmodule:: geosutils.log
.. autofunction:: set_console
.. autofunction:: set_log_level
.. autofunction:: suppress_logging
.. autofunction:: enable_logging
.. autofunction:: autolog

Indices and tables
------------------
 
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
