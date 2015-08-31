Tuna
====

Tuna is a Tunable Fabry-Perot Interferometer Data Reduction software solution.

It is written in Python. Uses Astropy, Numpy, Scipy, Sympy and ZeroMQ.

The online documentation can be found on:

https://tuna.readthedocs.org

Installation
------------

Tuna is currently tested to run in Linux and OSX. The general procedure to install it is to clone the repo in a directory within your $PYTHONPATH, and then import it in Python, which will probably result in an error, regarding a missing library. Once you install all libraries, Tuna should work.

Fedora 21
---------

These is a recipe to install in Fedora 21.

Inside a directory in your $PYTHONPATH (and preferrably inside a virtualenv), run:

$ git clone https://github.com/rcbrgs/tuna.git tuna

$ pip install -r tuna/pip_packages.txt

$ pip install scipy

$ git clone https://github.com/evertrol/mpyfit.git mpyfit

How to use Tuna
---------------

Documentation, including a gallery of examples, is at:

https://tuna.readthedocs.org
