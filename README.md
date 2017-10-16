Tuna
====

Tuna is a Tunable Fabry-Perot Interferometer Data Reduction software solution.

It is written in Python. Uses Astropy, Numpy, Scipy, Sympy and ZeroMQ.

The online documentation can be found on:

https://tuna.readthedocs.org

Tuna is a Python library module. It has no GUI, and no interactive text interface. It is meant to be imported and used as a collection of tools and recipes in your own programs.

Installation
------------

Complete installation instructions can be found at:

https://tuna.readthedocs.org/en/stable/installation.html

Tuna is currently tested to run in Linux and OSX. The general procedure to install it is to clone the repo in a directory within your $PYTHONPATH, and then import it in Python, which will probably result in an error, regarding a missing library. Once you install all libraries, Tuna should work.

Fedora 21
---------

This is a recipe to install in Fedora 21.

Inside a directory in your $PYTHONPATH (and preferably inside a virtualenv), run:

$ git clone https://gitlab.com/JulienP82/tuna2.0.git

$ pip install -U pip

$ pip install numpy

$ pip install -U setuptools

$ pip install PySide

$ python tuna/setup.py install

How to use Tuna
---------------

Documentation, including a gallery of examples, is at:

https://tuna.readthedocs.org


BRANCH-IO MODIFICATION notice installation  en cours ...