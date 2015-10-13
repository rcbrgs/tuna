.. _tuna_plugins_label:

plugins
=======

.. automodule:: tuna.plugins
   :members:

.. toctree::
   :maxdepth: 2

   tuna_plugins_registry

Tuna's plugins system
---------------------

Plugins fulfill two important goals in Tuna:

#. They facilitate extension of Tuna, by providing a mechanism for writing compatible functionality.

#. They allow modification of the framework's default behaviour, by allowing default plugins to be substituted with customized ones.

Technologically, such goals could be fulfilled in many ways. However, since plugins are meant to be the *easiest* way for some functionality to be included in Tuna, the specific system for plugins was designed with simplicity in mind.

It was decided to design the system around Python function calls. This was chosen because it is expected that users would have, at the very least, mastery over structured programming. Therefore, having a plugin system that consists essentially of some limitation on how to write functions would not be a syntatical problem for these users.

This simplistic design has its limitations - for example, previous work on parallelism on Tuna was negated by the refactoring of its tools into plugins. When other designs were considered, the designs they inspired were much more complex and reliant on higher abstractions (classes, APIs, RPCs). In the end, the "function signature" plugin system was chosen because it seems the most likely to be properly understood by the users.

How it works
++++++++++++

Consider the following two functions::

  def function_1 ( argument_1, argument_2 ):
      # ...

  def function_2 ( argument_3, argument_4 ):
      # ...

Since Python does not have type enforcement for its function signatures, there is no way to know if these two functions are equivalent in their signatures: we do not know if argument_1 is an int and argument_3 is a str or something else. We do not know the return types for either function!

However, if we are to create plugins out of functions, and a plugin must be replaceable by an equivalent plugin, we need a form of specifying this equivalency. This is done by adopting Python type hinting, which is a feature introduced in Python 3.5 but which has been in development for a long time, under other names. Essentially, it is a syntax to define the types of the arguments and return values for a function.

These are two functions, including type hinting::

  def function_1 ( argument_1 : int, argument_2 : float ) -> numpy.ndarray:
      # ...

  def function_2 ( argument_3 : float, argument_4 : int ) -> numpy.ndarray:
      # ...

Now, it is possible to decide on the equivalency of two functions - from a purely syntactical point of view. However, since Tuna is a framework focused on a specific domain - reduction of data from Fabry-Pérot spectrometers - the semantic of the function should also be taken in consideration.

This is accomplished in two ways. First, arguments names and ordering must be equal. So that in our example, the two functions would not be considered equivalent. Secondly, functions must be registered as plugins, under a certain key, and pipelines will use the plugin currently associated with a key.

When a new key / function plugin is registered, the user is free to use whatever function he wants, since there is no equivalency to be met. However, to substitute an existing key / function plugin, it is necessary to do so with a function that is equivalent to the one currently registered in the plugin.

The equivalency rules are:

#. Functions must be fully annotated (*all* parameters *and* the function return type must be specified).

#. Arguments names and order of appearance on the function signature must be equal, and obey alphanumerical order.

During development, a user might consult the current function signature associated with a given key by the following command::

  tuna.plugins.registry ( 'key' )

And an output similar to this should be displayed::

  def function ( argument_1 : int ) -> float

With this information, it should be simple for a user to write new or replacement plugins.
