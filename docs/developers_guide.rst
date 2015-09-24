Developer's guide
=================

Tuna is free software, licensed under the GPL Version 3.

It is hosted on a `github repo <https://github.com/rcbrgs/tuna.git>`_.


Code style
----------

First and foremost, any interaction between developers and public regarding Tuna should follow Python's Code of Conduct, and Astropy's Code of Conduct, which in a nutshell forbid harassment of any sort.

All code to be incorporated into Tuna should follow the same style:

* snake_case for everything, including module and class names,
* every function call has a space before and after each parenthesis. For example: time.sleep ( 5 ), *not* time.sleep(5). When the right parenthesis is the last character in a line, the space to its right can be elided.
* the same rule for parenthesis is applied to brackets and braces.
* the same spacing rule for parenthesis is applied to arithmetical operators. For example: x + y, *not* x+y.
* reStructeredText docstrings,
* Sphinx documentation, and
* unittest'ed functions and methods.

Of course, code which only uses Tuna as a library or framework might differ from this style. But to be merged into Tuna, source should follow these rules, so that the whole code base has a single style.

Documentation style
-------------------

Documentation should be produced writing docstrings within the source code, so that Sphinx can generate the html and pdf versions automatically, from the source code.

Since Sphinx is used to also include more free-form documentation, such as long texts and images, we decided on some styles so additions to the existing documentation are made in a orderly fashion.

* New module's documentations should be created using the automodule extension of Sphinx, in a file with full Python module name resolution with dots substituted for underlines, in the docs/ directory of the source code. For example: if a new module tuna.io.hdfs is introduced, its documentation should be created using autodoc in a file named docs/tuna_io_hdfs.rst.
* Each module should be included in the toctree of its parent package. Following the above example, the toctree in docs/tuna_io.rst should be expanded to include an entry for tuna_io_hdfs.
* New entries in lists of packages, modules, classes and functions should follow alphabetical order.
* Titles and subtitles' are underlined with the same number of characters as the (sub)title itself. For example: fsr is underlined with === in docs/tuna_tools_phase_map_fsr.rst.
  
