******************************************************************
  NeoCogs - Toolkit for developing command-line utilities in Python
******************************************************************

Overview
========

NeoCogs is a toolkit for developing command-line utilities in Python. It
handles common operations such as parsing command-line parameters,
dispatching commands and loading configuration files. It is targeted to
developers, sysadmins, testers, or anyone who needs to script their
routine tasks.

NeoCogs is a rework of a free software licensed under MIT license.
Cogs is written by Kirill Simonov from Prometheus Research, LLC,
NeoCogs is written by Luis S. (MoccaDev).


Getting Started
===============

You can install NeoCogs using `PIP package manager`_::

    # pip install NeoCogs

.. _PIP package manager: http://www.pip-installer.org/

This operation installs a command-line utility ``neocogs`` and a Python
package of the same name. The ``neocogs`` utility is a dispatcher which
lets you select and execute your scripts (called *tasks*). Let us
show how to do it with a simple example.

In the current directory, create a file ``cogs.local.py`` with the
following content::

    from neocogs import task
    import os

    @task
    def Hello(name=None):
        """greet someone (if not specified, the current user)"""
        if name is None:
            name = os.getlogin()
        print("Hello, %s!" % name.capitalize())

Now run::

    $ neocogs hello world
    Hello, World!

    $ neocogs hello
    Hello, User!

    $ neocogs help hello
    HELLO - greet someone (if not specified, the current user)
    Usage: neocogs hello [<name>]

NeoCogs converts function ``Hello()`` into a command-line script with
parameters inferred from the function signature, so when you
execute a command ``neocogs hello world``, you invoke a function
``Hello('world')``.


Loading Extensions
==================

In this section, we describe how NeoCogs finds and loads extensions.

NeoCogs loads extensions from two places:

* ``cogs.local.py`` or ``cogs.local/__init__.py`` module in the current
  directory;
* all Python packages under ``neocogs.extensions`` entry point.

The easiest way to add an extension is to create a ``cogs.local.py``
module and add your tasks there. If you want to split the module into
multiple files, create a ``cogs.local`` subdirectory with an
``__init__.py`` module. ``cogs.local.py`` or ``cogs.local/__init__.py``
are executed by NeoCogs on startup. The modules must be owned by the same
user who runs the ``neocogs`` script, or by ``root``; otherwise they are
ignored.

If you need to package and distribute your NeoCogs extensions, using
``cogs.local`` may be inconvenient. In this case, you may package your
NeoCogs extensions as a regular Python distribution.

Suppose we want to pack the ``hello`` task as a separate package.
Create a directory tree with the following structure::

    NeoCogs-Hello/
        src/
            neocogs/
                __init__.py
                hello.py
        setup.py

The file ``neocogs/hello.py`` contains the definition of the ``hello`` task
and has the same content as ``cogs.local.py`` in our previous example.

The file ``neocogs/__init__.py`` contains just one line::

    __import__('pkg_resources').declare_namespace(__name__)

The file ``setup.py`` contains the meta-data of the package and may
look like this::

    from setuptools import setup

    setup(
        name='NeoCogs-Hello',
        version='0.1',
        description="""A NeoCogs task to greet somebody""",
        packages=['neocogs'],
        namespace_packages=['neocogs'],
        package_dir={'': 'src'},
        install_requires=['NeoCogs'],
        entry_points={ 'neocogs.extensions': ['Hello = neocogs.hello'] },
    )

Note the parameter ``entry_points`` in ``setup()`` invocation; it adds
an entry point ``neocogs.extensions`` named ``Hello`` that refers to module
``neocogs.hello``. On startup, NeoCogs finds and loads all packages defined
for the entry point ``neocogs.extensions``.


Defining Tasks
==============

A task can be created from a function or a class by augmenting it with
the ``task`` decorator::

    from neocogs import task, argument
    from neocogs.log import log, fail

    @task
    def Factorial(n):
        """calculate n!

        This task calculates the value of the factorial of the given
        positive number `n`.  Factorial of n, also known as n!, is
        defined by the formula:

            n! = 1*2*...*(n-1)*n
        """
        try:
            n = int(n)
        except ValueError:
            raise fail("n must be an integer")
        if n < 1:
            raise fail("n must be positive")
        f = 1
        for k in range(2, n+1):
            f *= k
        log("{}! = `{}`", n, f)

    @task
    class Fibonacci:
        """calculate the n-th Fibonacci number

        The n-th Fibonacci number `F_n` is defined by:

            F_0 = 0
            F_1 = 1
            F_n = F_{n-1}+F_{n-2} (n>1)
        """

        n = argument(int)

        def __init__(self, n):
            if n < 0:
                raise ValueError("n must be non-negative")
            self.n = n

        def __call__(self):
            p, q = 0, 1
            for k in range(self.n):
                p, q = p+q, p
            log("F_{} = `{}`", self.n, p)

You can now execute the tasks by running::

    $ neocogs factorial 10
    10! = 3628800

    $ neocogs fibonacci 10
    F_10 = 55

NeoCogs uses the name of the function or the class as the task identifier.
The name is normalized: it is converted to lower case and has all
underscore characters converted to the dash symbol.

If the task is derived from a function, the task arguments are inferred
from the function signature. NeoCogs executes such task by calling the
function with the parsed command-line parameters.

If the task is derived from a class, the task arguments and options must
be defined using ``argument()`` and ``option()`` descriptors. To
execute a task, NeoCogs creates an instance of the class passing the task
parameters as the constructor arguments. Then NeoCogs invokes the
``__call__`` method of the instance. Thus the call of::

    $ neocogs factorial 10

is translated to::

    Factorial('10')

and the call of::

    $ neocogs fibonacci 10

is translated to::

    t = Fibonacci(10)
    t()

The docstring of the function or the class becomes the task
description::

    $ neocogs help factorial
    FACTORIAL - calculate n!
    Usage: neocogs factorial <n>

    This task calculates the value of the factorial of the given
    positive number n.  Factorial of n, also known as n!, is
    defined by the formula:

        n! = 1*2*...*(n-1)*n

    $ neocogs help fibonacci
    Usage: neocogs fibonacci <n>

    The n-th Fibonacci number F_n is defined by:

        F_0 = 0
        F_1 = 1
        F_n = F_{n-1}+F_{n-2} (n>1)

A task derived from a function cannot have options. To add an option to
a task derived from a class, use the ``option()`` descriptor. For
example::

    from neocogs import task, argument, option
    import sys, os

    @task
    class Write_Hello:

        name = argument(default=None)
        output = option(key='o', default=None)

        def __init__(self, name, output):
            if name is None:
                name = os.getlogin()
            self.name = name
            if output is None:
                self.file = sys.stdout
            else:
                self.file = open(output, 'w')

        def __call__(self):
            self.file.write("Hello, %s!\n" % self.name.capitalize())

You can execute this task with option ``--output`` or ``-o`` to redirect
the output to a file::

    $ neocogs write-hello world -o hello.txt


Configuration and Environment
=============================

NeoCogs allows you to define custom configuration parameters. For example::

    from neocogs import env, task, setting
    import os

    @setting
    def Default_Name(name=None):
        """the name to use for greetings (if not set: login name)"""
        if name is None or name == '':
            name = os.getlogin()
        if not isinstance(name, str):
            raise ValueError("a string value is expected")
        env.add(default_name=name)

    @task
    def Hello_With_Configuration(name=None):
        if name is None:
            name = env.default_name
        print("Hello, %s!" % name.capitalize())

Now you could specify the name as a configuration parameter
``default-name``. One way to do it is to use global option
``--default-name``::

    $ neocogs --default-name=world hello-with-configuration

You could also pass a configuration parameter using an environment
variable::

    $ NEOCOGS_DEFAULT_NAME=world neocogs hello-with-configuration

Alternatively, you can put parameters to a configuration file. In the
current directory, create a file ``cogs.conf`` with the following
content::

    default-name: world

Now run::

    $ neocogs hello-with-configuration

NeoCogs reads configuration from the following locations:

* ``/etc/cogs.conf``
* ``$PREFIX/etc/cogs.conf``
* ``$HOME/.cogs/cogs.conf``
* ``./cogs.conf``
* program environment
* command-line parameters

If you'd like to specify the usage of a configuration file that is in a
different location than the standard locations listed above, you can use
the global option ``--config`` as follows::

    $ neocogs --config=alternate-cogs.conf hello-with-configuration

To create a new configuration parameter, wrap a function named after the
parameter with the ``@setting`` decorator. The function must accept
zero or one argument: the function is called without arguments if the
parameter is not specified explicitly, and is called with the value of
the parameter if it was set using one of the methods described above.

NeoCogs does not impose any rules on what to do with the parameter value,
but we recommend to store the value in the global ``env`` variable. The
call of ``env.add(default_name=name)`` adds a new parameter
``default_name`` which could then be accessed as ``env.default_name``.


API Reference
=============

``neocogs.core``
----------------

Classes and functions defined in ``neocogs.core`` are also importable from
the ``neocogs`` package.

``@task``
    The ``@task`` decorator converts the wrapped function or class into
    a task. Task properties are inferred from the wrapped object as
    follows:

    *name*
        Generated from the function or the class name. The name is
        converted to lower case and all underscores are replaced with
        dashes.

    *documentation*
        Generated from the docstring. The first line of the docstring
        produces a one-line *hint* string, the rest of the docstring
        produces a multi-line *help* string.

    *arguments*
        When the task is inferred from a function, the arguments are
        generated from the function signature. Each function parameter
        becomes a task argument, those which have default values are
        optional.

        If the task is inferred from a class, the arguments must be
        specified using the ``argument()`` descriptor.

    *options*
        A task inferred from a function has no options. A task inferred
        from a class may have options specified using the ``option()``
        descriptor.

    When a task is executed, the wrapped object is invoked according
    to the following rules:

    * If the task is inferred from a function, parsed command-line
      parameters are passed as the function arguments.
    * If the task is inferred from a class, command-line parameters
      are passed to the class constructor, then the ``__call__``
      method is called on the instance.

``@setting``
    The ``@setting`` decorator converts the wrapped function to a
    configuration parameter, which properties are inferred from the
    function attributes.

    The setting name is generated from the function name. The name is
    converted to lower case and has all underscores replaced with
    dashes.

    The setting documentation is generated from the function docstring.

    The function must be able to accept zero and one parameter. The
    function is called at startup with no parameters if the setting is
    not explicitly set by the user; otherwise it is called with the
    value of the setting. The function is responsible for storing the
    value in the ``env`` object.

``argument(check, default, plural=False)``
    Describes a task argument.

    ``check``
        A function which is called to check and/or transform the
        argument value. The function must return the transformed value
        or raise ``ValueError`` exception on error.

    ``default``
        The default value to be used if the argument is optional and not
        specified. If this parameter is not set, the argument is
        mandatory.

    ``plural``
        If set, the argument consumes all the remaining command-line
        parameters. Must be the last argument specified.

``option(key, check, default, plural=False, value_name=None, hint=None)``
    Describes a task option.

    ``key``
        A one-character shorthand.

    ``check``
        A function called to check and transform the value of the
        option. The function must return the transformed value or raise
        ``ValueError`` exception on error.

    ``default``
        The default value used when the option is not specified. If
        this parameter is not set, the option does not accept a value.
        Such an option is treated is a toggle and takes a value ``True``
        if set and ``False`` if not set.

    ``plural``
        If set, indicates that the option could be specified more than
        once.

    ``value_name``
        The preferred name for the option value; used for the task
        description.

    ``hint``
        A one-line description of the option; used for the task
        description.

``env``
    A global object that keeps values of configuration parameters and
    other properties.

    ``env.add(**keywords)``
        Add new parameters.

    ``env.set(**keywords)``
        Set values for existing parameters.

    ``env.push(**keywords)``
        Save the current state and set new values for existing
        parameters.

    ``env.pop()``
        Restore a previously saved state of parameters and values.

    ``env(**keywords)``
        A context manager for ``with`` statement. On entering, saves
        the current state and sets new parameter values. On exiting,
        restores the saved state.

``neocogs.log``
---------------

Printing utilities.

``log(msg="", *args, **kwds)``
    Print the message to the standard output.

    If extra positional or keyword arguments are given, they are
    formatted with ``format()`` function using ``msg`` as the template.

    ``log()`` supports output coloring: a substring of the form::

        `...`

    or::

        :fmt:`...`

    is colorized when displayed on a color terminal. The supported
    formats are: *default* (white), ``debug`` (dark grey),
    ``warning`` (red), ``success`` (green).

``debug(msg, *args, **kwds)``
    Print the message when the ``env.debug`` parameter is set. We
    recommend to accompany any permanent change to the filesystem or
    other system state with a respective ``debug()`` call.

    Add command-line parameter ``--debug`` or set environment variable
    ``NEOCOGS_DEBUG=1`` to see debug output.

``warn(msg, *args, **kwds)``
    Display a warning. ``warn()`` should be used for reporting error
    conditions which do not prevent the script from continuing the job.

``fail(msg, *args, **kwds)``
    Display an error message and return an exception object. It should
    be used in the following manner::

        raise fail("no more beer in the refrigerator")

``neocogs.fs``
--------------

File and system utilities.

``cp(src, dst)``
    Copy a file or a directory tree.

``mv(src, dst)``
    Move a file or a directory tree.

``rm(path)``
    Remove a file.

``mktree(path)``
    Create all directories in the path.

``rmtree(path)``
    Remove a directory tree.

``exe(cmd, cd=None, environ=None)``
    Replace the current process with the given shell command.

    If ``cd`` is given, changes the directory to the specified
    path before executing the command.

    If ``environ`` is given, adds the given parameters to the
    environment before executing the command.

``sh(cmd, data=None, cd=None, environ=None)``
    Execute a shell command with the given input and working directory.

``pipe(cmd, data=None, cd=None, environ=None)``
    Execute a shell command with the given input and working directory;
    return the command output.


.. vim: set spell spelllang=en textwidth=72:
