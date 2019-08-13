.. -*- encoding: utf-8 -*-
.. -*- restructuredtext -*-


fancycompleter: colorful Python TAB completion
===============================================

What is is?
-----------

``fancycompleter`` is a module to improve your experience in Python by adding
TAB completion to the interactive prompt.  It is an extension of the stdlib's
rlcompleter_ module.

Its best feature is that the completions are displayed in different colors,
depending on their type:

.. image:: http://bitbucket.org/antocuni/fancycompleter/raw/5bf506e05ce7/screenshot.png

In the image above, strings are shown in green, functions in blue, integers
and boolean in yellows, ``None`` in gray, types and classes in
fuchsia. Everything else is plain white.

``fancycompleter`` is compatible with Python 3. However, by default colors
don't work on Python 3, see the section `How do I get colors?`_ for details.

Other features
--------------

* To save space on screen, ``fancycompleter`` only shows the characters "after
  the dot".  By contrast, in the example above ``rlcompleter`` shows
  everything prepended by "``sys.``".

* If we press ``<TAB>`` at the beginning of the line, a real tab character is
  inserted, instead of trying to complete.  This is useful when typing
  function bodies or multi-line statements at the prompt.

* Unlike ``rlcompleter``, ``fancycompleter`` **does** complete expressions
  containing dictionary or list indexing.  For example,
  ``mydict['foo'].<TAB>`` works (assuming that ``mydict`` is a dictionary and
  that it contains the key ``'foo'``, of course :-)).

* Starting from Python 2.6, if the completed name is a callable,
  ``rlcompleter`` automatically adds an open parenthesis ``(``.  This is
  annoying in case we do not want to really call it, so ``fancycompleter``
  disable this behaviour.

Installation
------------

First, install the module with ``pip`` or ``easy_install``::

    $ pip install fancycompleter

Then, at the Python interactive prompt::

    >>> import fancycompleter
    >>> fancycompleter.interact(persist_history=True)
    >>>

If you want to enable ``fancycompleter`` automatically at startup, you can add
those two lines at the end of your `PYTHONSTARTUP`_ script.

If you do **not** have a `PYTHONSTARTUP_` script, the following command will
create one for you in ``~/python_startup.py``::

    $ python -m fancycompleter install

On Windows, ``install`` automatically sets the ``PYTHONSTARTUP`` environment
variable. On other systems, you need to add the proper command in
``~/.bashrc`` or equivalent.

**Note**: depending on your particular system, ``interact`` might need to play
dirty tricks in order to display colors, although everything should "just
work™".  In particular, the call to ``interact`` should be the last line in
the startup file, else the next lines might not be executed. See section `What
is really going on?`_ for details.

How do I get colors?
---------------------

If you are using **PyPy**, you can stop reading now, as ``fancycompleter`` will
work out of the box.

If you are using **CPython on Linux/OSX** and you installed ``fancycompleter``
with ``pip`` or ``easy_install``, they automatically installed ``pyrepl`` as a
requirement, and you should also get colors out of the box.  If for some
reason you don't want to use ``pyrepl``, you should keep on reading.

By default, in CPython line input and TAB completion are handled by `GNU
readline`_ (at least on Linux).  However, ``readline`` explicitly strips
escape sequences from the completions, so completions with colors are not
displayed correctly.

There are two ways to solve it:

  * (suggested) don't use ``readline`` at all and rely on pyrepl_

  * use a patched version of ``readline`` to allow colors

By default, ``fancycompleter`` tries to use ``pyrepl`` if it finds it.  To get
colors you need a recent version, >= 0.8.2.

Starting from version 0.6.1, ``fancycompleter`` works also on **Windows**, relying
on pyreadline_. At the moment of writing, the latest version of ``pyreadline``
is 2.1, which does **not** support colored completions; here is the `pull
request`_ which adds support for them. To enable colors, you can install
``pyreadline`` from `this fork`_ using the following command::

  pip install --upgrade https://github.com/antocuni/pyreadline/tarball/master

.. _`pull request`: https://github.com/pyreadline/pyreadline/pull/48
.. _`this fork`: https://github.com/antocuni/pyreadline

If you are using **Python 3**, ``pyrepl`` does not work, and thus is not
installed. Your only option to get colors is to use a patched ``readline``, as
explained below.

I really want to use readline
------------------------------

This method is not really recommended, but if you really want, you can use use
a patched readline: you can find the patches in the ``misc/`` directory:

  * for `readline-5.2`_

  * for `readline-6.0`_

You can also try one of the following precompiled versions, which has been
tested on Ubuntu 10.10: remember to put them in a place where the linker can
find them, e.g. by setting ``LD_LIBRARY_PATH``:

  * readline-6.0 for `32-bit`_

  * readline-6.0 for `64-bit`_

Once it is installed, you should double-check that you can find it, e.g. by
running ``ldd`` on Python's ``readline.so`` module::

    $ ldd /usr/lib/python2.6/lib-dynload/readline.so | grep readline
            libreadline.so.6 => /home/antocuni/local/32/lib/libreadline.so.6 (0x00ee7000)

Finally, you need to force ``fancycompleter`` to use colors, since by default,
it uses colors only with ``pyrepl``: you can do it by placing a custom config
file in ``~/.fancycompleterrc.py``.  An example config file is `here`_ (remind
that you need to put a dot in front of the filename!).

.. _`readline-5.2`: http://bitbucket.org/antocuni/fancycompleter/src/tip/misc/readline-escape-5.2.patch
.. _`readline-6.0`: http://bitbucket.org/antocuni/fancycompleter/src/tip/misc/readline-escape-6.0.patch
.. _`32-bit`: http://bitbucket.org/antocuni/fancycompleter/src/tip/misc/libreadline.so.6-32bit
.. _`64-bit`: http://bitbucket.org/antocuni/fancycompleter/src/tip/misc/libreadline.so.6-64bit
.. _here: http://bitbucket.org/antocuni/fancycompleter/src/tip/misc/fancycompleterrc.py


Customization
--------------

To customize the configuration of fancycompleter, you need to put a
file named ``.fancycompleterrc.py`` in your home directory.  The file must
contain a class named ``Config`` inheriting from ``DefaultConfig`` and
overridding the desired values.


What is really going on?
-------------------------

The default and preferred way to get colors is to use ``pyrepl``.  However,
there is no way to tell CPython to use ``pyrepl`` instead of the built-in
readline at the interactive prompt: this means that even if we install our
completer inside pyrepl's readline library, the interactive prompt won't see
it.

The issue is simply solved by avoiding to use the built-in prompt: instead, we
use a pure Python replacement based on `code.InteractiveConsole`_.  This
brings us also some niceties, such as the ability to do multi-line editing of
the history.

The console is automatically run by ``fancycompleter.interact()``, followed by
``sys.exit()``: this way, if we execute it from the script in
``PYTHONSTARTUP``, the interpreter exits as soon as we finish the use the
prompt (e.g. by pressing CTRL-D, or by calling ``quit()``).  This way, we
avoid to enter the built-in prompt and we get a behaviour which closely
resembles the default one.  This is why in this configuration lines after
``fancycompleter.interact()`` might not be run.

Note that if we are using ``readline`` instead of ``pyrepl``, the trick is not
needed and thus ``interact()`` will simply returns, letting the built-in
prompt to show up.  The same is true if we are running PyPy, as its built-in
prompt is based on pyrepl anyway.


.. _rlcompleter: http://docs.python.org/library/rlcompleter.html
.. _PYTHONSTARTUP: http://docs.python.org/using/cmdline.html#envvar-PYTHONSTARTUP
.. _`GNU readline`: http://tiswww.case.edu/php/chet/readline/rltop.html
.. _pyrepl: http://codespeak.net/pyrepl/
.. _`SVN repository`: http://codespeak.net/svn/pyrepl/trunk/pyrepl/
.. _`code.InteractiveConsole`: http://docs.python.org/library/code.html#code.InteractiveConsole
.. _pyreadline: https://pypi.python.org/pypi/pyreadline
