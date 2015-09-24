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
* Python packages, such as Tuna, can contain modules and packages. Therefore, it is possible to build infinitely "deep" hierarchies of packages. In Tuna, we intend to restrain the code structure in the following layers:
  
  - *repository*: several files must be present on the root of the source tree, such as setup.py, .travis.yml, .gitignore, etc. These constraints come from the specific technologies adopted (PyPI, Travis, git, etc).
  - *package*: the directory named "tuna" on the root of the repository is the Tuna package itself. In this sense, the meaning of "package" in Python and in Tuna is the same.
  - *namespaces* : each directory immediately below the directory of the package "tuna" is meant as a collection of conceptually related modules and packages, such as "tools", "models", etc. 
  - *module*: individual Python modules or packages that reside under a Tuna namespace. Although this naming scheme does not correspond perfectly to Python usage, we adopt it because we feel that naming the modules in a modular framework as "modules" is more important than being 100% Pythonic in this regard.
    
  These layers are the hierarchical structure which comprises the modular design of Tuna. This should allow module developers to not have to study all the systems coded in Tuna in order to extend it with a custom module. It should suffice to obey constraints imposed by the Tuna package and by the specific namespace where the module resides.

* Each namespace has its __init__.py file, which must contain a docstring specifying the concepts that relate the modules contained in that namespace.
* Each module must have a docstring on the top of the file, describing the scope of tasks performed by the module.
* Each module should be included in the toctree of its parent package. Following the above example, the toctree in docs/tuna_io.rst should be expanded to include an entry for tuna_io_hdfs.
* Each class must have a docstring describing the responsibility of this class.
* New entries in lists of packages, modules, classes and functions should follow alphabetical order.
* Titles and subtitles' are underlined with the same number of characters as the (sub)title itself. For example: fsr is underlined with === in docs/tuna_tools_phase_map_fsr.rst.
* A function docstring that has at least one parameter (besides self, for methods) must list its parameters like this::

    Parameters:

    \* variable_name : variable type[, defaults to <default value>]
        Description of the variable.

* A function that has a return value must document this return like this::

    Returns:

    \* variable_name : variable type
        Description of the variable.
	
* A function docstring should contain example code of its usage.
