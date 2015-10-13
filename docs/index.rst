Documentation
=============

This is the documentation for Tuna |version|. The source for code and documentation can be obtained at `github <https://github.com/rcbrgs/tuna>`_.

Tuna is a Python package for reduction of data cubes produced using Fabry-Pérot interferometers. If you are in doubt whether Tuna would be useful to you, please read our :ref:`overview_label`. You can also browse our :ref:`examples_label`.

The main capabilities of Tuna are to reduce and automatically fit models to Fabry-Pérot data cubes.

Getting started
---------------

.. toctree::
   :maxdepth: 2

   overview
   installation
   examples
   developers_guide

Modules and namespaces
----------------------

Tuna is organized hierarchically into namespaces, each containing several modules. The namespaces don't have useful code in themselves, serving as organizers of the codebase. The modules contain most of Tuna's utilitarian code, and are written with the intent of being small and "to the point" files. As a rule of thumb, if a module is larger than a 100 lines of code, it probably should be split up.

.. toctree::
   :maxdepth: 1

   tuna_console
   tuna_io
   tuna_log
   tuna_models
   tuna_pipelines
   tuna_plugins
   tuna_repo
   tuna_test
   tuna_tools
   tuna_zeromq

Support
-------

Currently, support is offered by direct mailing the author, rborges _at_ hush _dot_ com. Once the project attracts some interested participants, we will create a mailing list.

Also, please do use github's issue tracker and pull request features, so that the bugs also get documented publicly.

External libraries
------------------

Tuna makes extensive use of third-party libraries. The documentation for some of them is listed here:

.. toctree::
   :maxdepth: 2

   external_threading
   external_logging

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
