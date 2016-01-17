Installation of Tuna
====================

Tuna is built as a Python package, and to have it working in your system, you need:

- The code for Tuna in a directory inside one of the locations listed in your environment's $PYTHONPATH.
   
- The third-party Python modules that are used by Tuna must be installed.

- Optionally, if a MySQL server is installed, Tuna will use it to store cross-references between its numpy arrays' hashes.

In the current version, Tuna is not yet part of PyPI, but this should be corrected in the future. Therefore, the installation procedure consists of cloning the repository and using the setup.py script directly. Also, we have not been able to generalize the directory name for the installation; you *must* clone the repository in a directory named "tuna".

Dependencies
------------

Tuna depends on the following packages, and will install them if they are not yet installed in your system (or virtual environment):

   #. `Astropy <http://www.astropy.org/>`_
     
   #. `Matplotlib <http://matplotlib.org/>`_

   #. `Mpyfit <https://github.com/evertrol/mpyfit>`_
      
   #. `Numpy <http://www.numpy.org/>`_
      
   #. `Psutil <https://github.com/giampaolo/psutil>`_
      
   #. `Pyfits <http://www.stsci.edu/institute/software_hardware/pyfits/>`_
      
   #. `PySide <https://wiki.qt.io/PySide>`_
      
   #. `Scipy <https://www.scipy.org/>`_
      
   #. `Sympy <http://www.sympy.org/en/index.html>`_
      
   #. `ZeroMQ <https://github.com/zeromq/pyzmq>`_

Permissions
-----------

You need read, write and execution permissions on the directories where you intend to install Tuna. This is taken care for you if you use a virtual environment in your $HOME directory in a Linux system. In case you intend to not use virtualenv, an option must be set during installation, and will be noted on the installation recipe, below.
      
Virtualenv
----------

We highly recommend using Python's virtual environments to encapsulate all dependencies of Tuna in a single namespace, and avoid conflicting with other Python software in your system.

To create a virtual environment, the command is::

  virtualenv <path>/<name>

To use a virtual environment, the command is::

  source <path>/<name>/bin/activate

Once activated, the Python interpreter and the modules it uses are loaded from the virtual environment. Also, packages installed using pip are installed inside the virtual environment. In this way, it is very easy to have multiple Python packages installed in the same system, without conflicts, as long as each package is in its own virtual environment.

Also, packages installed by downloading the code from github (such as Mpyfit), work by simply cloning the repo inside the virtualenv directory.

Python versions
---------------

Tuna is only compatible with Python 3. 

Linux installation - with virtualenv
------------------------------------

This is a step-by-step guide to installing Tuna. It uses Python 3 and virtual environments. We install in the directory ~/vtuna, so if you install in another directory, please adjust your commands accordingly.

#. Create the virtual environment that will contain Tuna (this must be run in a directory where you have read, write and execute permissions)::

     ~ $ virtualenv -p python3 vtuna

#. Activate the virtual environment::

     ~ $ cd vtuna
     
     vtuna $ source bin/activate

#. Obtain the source code for Tuna::

     (vtuna)vtuna $ git clone https://github.com/rcbrgs/tuna.git

#. Update pip to its most recent version::

     (vtuna)vtuna $ pip install -U pip

#. (*Debian* and derivatives only) Numpy requires some packages to be installed::

     $ sudo aptitude install python3-dev

#. Install NumPy, which is currently not well-behaved in PyPI (and so must be installed separatedly)::

     (vtuna)vtuna $ pip install numpy

#. Install PySide, which is currently not well supported by readthedocs.org (and therefore must be installed separatedly)::

   (vtuna)vtuna $ pip install PySide

   * In case the installation of PySide fails, you might need the cmake or qmake (or both) to be installed. In Fedora, the following packages must be installed::
  
       (vtuna)vtuna $ sudo yum install cmake qt-devel

#. Install some of the other libraries required by Tuna::

   (vtuna)vtuna $ pip install -r tuna/pip_packages.txt

   * In case the installation of SciPy fails because your system lack lapack or blas, you must install those. On Fedora, the command to install the right packages is::

       (vtuna)vtuna $ sudo yum install openblas-devel lapack-devel 
     
#. Install the package::

     (vtuna)vtuna $ python tuna/setup.py install

   This could take some time to install, since some of the dependencies are large (dozens of MB).

#. Use Tuna::

     (vtuna)vtuna $ ipython
     Python 3.4.1 (default, Nov  3 2014, 14:38:10)
     Type "copyright", "credits" or "license" for more information.

     IPython 4.0.0 -- An enhanced Interactive Python.
     ?         -> Introduction and overview of IPython's features.
     %quickref -> Quick reference.
     help      -> Python's own help system.
     object?   -> Details about 'object', use 'object??' for extra details.

     In [1]: import tuna

     In [2]:

Using Tuna once it has already been installed in a virtual environment
----------------------------------------------------------------------

Once Tuna is installed, you must always load the virtual environment where it resides before using it. The commands are::

  ~ $ cd vtuna
  vtuna $ source bin/activate
  (tuna)tuna $ ipython
  Python 3.4.1 (default, Nov  3 2014, 14:38:10)
  Type "copyright", "credits" or "license" for more information.

  IPython 4.0.0 -- An enhanced Interactive Python.
  ?         -> Introduction and overview of IPython's features.
  %quickref -> Quick reference.
  help      -> Python's own help system.
  object?   -> Details about 'object', use 'object??' for extra details.

  In [1]: import tuna

  In [2]:

Of course, if you created your virtual environment in a directory other than ~/tuna, you should adjust your commands accordingly.

Linux installation - without virtualenv
---------------------------------------

This is a step-by-step guide to installing Tuna in Fedora 21. It uses Python 3.

#. Obtain the source code for Tuna::

     $ git clone https://github.com/rcbrgs/tuna.git

#. Update pip to its most recent version::

     $ pip install -U pip

#. (Debian and derivatives) Numpy requires some packages to be installed::

     $ sudo aptitude install python3-dev
     
#. Install NumPy::

     $ pip install numpy

#. (Only required for Python 2) update setuptools::

     $ pip install -U setuptools

#. Install PySide, which is currently not well supported by readthedocs.org (and therefore must be installed separatedly)::

     $ pip install PySide

#. Install the package, selecting a directory where you have read, write and execute rights::

     $ python tuna/setup.py install --home=~

   This could take some time to install, since some of the packages are large (dozens of MB).

#. Use Tuna::

     $ ipython
     Python 3.4.1 (default, Nov  3 2014, 14:38:10)
     Type "copyright", "credits" or "license" for more information.

     IPython 4.0.0 -- An enhanced Interactive Python.
     ?         -> Introduction and overview of IPython's features.
     %quickref -> Quick reference.
     help      -> Python's own help system.
     object?   -> Details about 'object', use 'object??' for extra details.

     In [1]: import tuna

     In [2]:

Steps necessary to build the documentation locally
--------------------------------------------------

In case you wish to build the documentation yourself, it is necessary to install and configure Sphinx.

#. Supposing you already installed Tuna, enter its virtualenv::

     $ cd vtuna
     vtuna $ source bin/activate

#. Install Sphinx::

     (vtuna)vtuna $ pip install sphinx

#. Create a directory to store your documentation::

     (vtuna)vtuna $ mkdir sphinx
     
#. Build the package, then the documentation. you must re-run this step every time you change the documentation sources::

     (vtuna)vtuna $ python tuna/setup.py install
     (vtuna)vtuna $ sphinx-build -b html tuna/docs/ sphinx
