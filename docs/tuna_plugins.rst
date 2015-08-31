.. _plugin_label:

plugins
=======

*Warning*: this is a design document, and therefore it does not correspond (yet) to any version of Tuna.

In a sense, Tuna is both a toolkit and a framework. When used as a library, the tools, models and structural pieces of Tuna can be used by external programs, just like any other Python module. As a framework, however, these different parts are connected in "pipelines", so that specific data processing tasks can be constructed from these independent parts.

It is straightforward to add a new tool to Tuna: it can be encapsulated in a Python module .py file, and placed in the tools/ directory. However, the existing pipelines will not know of this new tool, so a system is needed to take care of that.

An analogous situation motivated the development of [CosmoSIS]_, where benefits and costs of a modular design were considered, regarding their field of cosmological parameter estimation, which is - from computer science point of view - very similar to the field of data reduction of Fabry-Pérot interferometers.

Benefits:

* **replacement**, or the ability to change parts of the code easily;
* **verifiability**, since it is easier to test, read and understand smaller pieces of code;
* **debugging**, since the modular architecture imposes a clear structure on its modules;
* **consistency**, derived physics parameters that are shared through the modular framework, instead of being re-coded in each module;
* **languages**, in the sense that different modules can be written in different programming languages;
* **legacy**, by providing a structure where existing but independent code can be reused in a larger workflow;
* **publishing**, in the sense that innovative code regarding one module can be readily combined with innovative code from other developers, as long as all respect the framework modularization rules;
* **samplers**, which correspond to Tuna's pipelines, can be more easily be substituted - and the feasibility of different approaches to solve the problem at hand can be more readily investigated.

Costs:

* **overheads**, corresponding to the "boilerplate code" that must run to effectively launch the module as a part of the framework.
* **interpolation**, since the data served to a module may not be sampled at the points it would require, because of requirements of another module;
* **speed**, related to the overhead code being run;
* **consistency**, missuse of the code can happen, specially when compared to a monolithic code base, written to specifically implement a scientific solution;
* **temptation**, since it is simple to add steps to a pipeline, this might happen often, although the introduction of uncertainty and errors from the "excessive" module will be its negative consequences;
* **legacy**, since existing code is not yet adapted to the specific modular framework, the development of adapted versions will require some effort.

It is our opinion that the benefits far outweight the costs associated with a modular approach. Also, it our expectation that costs associated with developing the framework, and adapting existing code to it, would become smaller in the future, as new code is already produced modularly, and as the expertise of adapting code is spread to a wider community of developers.
  
.. [CosmoSIS] Zuntz et al, *CosmoSIS: Modular cosmological parameter estimation*. Available at http://arxiv.org/abs/1409.3409. Retrieved on 2015-09-17.

The plugin API
--------------

Tuna's pipelines, instead of calling the tools by its module name, call the module that is registered as the implementation for a given tool. For example: the high resolution data reduction pipeline needs to call *some* tool that detects noise in a raw data cube. Instead of calling directly the module tools/phase_map/noise.py, it calls the module registered under the "high resultion data 3D noise detector" entry in the dictionary tuna.plugins.registrar.

