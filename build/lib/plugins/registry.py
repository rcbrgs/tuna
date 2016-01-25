"""
This module's scope are the operation related to Tuna's plugin system's registry.

In very brief terms, a function may be registered as a Tuna plugin as long as it only uses keyworded arguments, and if it replaces an existing plugin, it must have the same number, name and type of arguments.

Tuna's pipelines, instead of calling the tools by its module name, call the module that is registered as the implementation for a given "tool". For example: the high resolution data reduction pipeline needs to call *some* tool that detects noise in a raw data cube. Instead of calling directly the module tools/noise.py, it calls the module registered under the "Noise detector" entry in the registry.

This is how to list the plugins currently registered in Tuna::

  >>> import tuna
  >>> tuna.plugins.registry ( )
  The following plugins are registered in Tuna:
  * "Airy fit" : tuna.models.airy.fit_airy
  * "Apply wavelength calibration" : tuna.tools.wavelength.wavelength_calibration.wavelength_calibrator
  * "B-ratio estimation" : tuna.tools.estimate_b_ratio.estimate_b_ratio
  * "Barycenter algorithm" : tuna.tools.barycenter.barycenter_geometry
  * "Continuum detector" : tuna.tools.continuum.continuum_detector
  * "FSR mapper" : tuna.tools.fsr.fsr_mapper
  * "Find the ring borders" : tuna.tools.phase_map.ring_borders.ring_border_detector
  * "Noise detector" : tuna.tools.noise.detect_noise
  * "Overscan" : tuna.tools.overscan.no_overscan
  * "Parabola fit" : tuna.models.parabola.parabolic_fitter
  * "Ring center finder" : tuna.tools.find_rings.find_rings

And how to list the parameters and return types for a given plugin::

  >>> tuna.plugins.registry ( "Noise detector" )
  def detect_noise ( data : tuna.io.can.can, noise_mask_radius : int, noise_threshold : float, wrapped : tuna.io.can.can ) -> tuna.io.can.can

In this output, notice the annotations regarding the type of each parameters, and the annotation regarding the return value. This annotation format is compatible with Python's `type hint system <https://docs.python.org/3.5/library/typing.html>`_. In very brief terms, after each variable name, a colon ( ":" ) is added, and the type of that variable is specified. If there is a default value, that is specified after the type. After the closing parenthesis, an arrow ( "->" ) is added, and after that, the type of the return value.

If some value (for instance, the return value) is a tuple of several types, it must be fully described, like so::

  def function ( variable: type ) -> ( int, float, str, list )
    
The pipelines in Tuna are recipes that step through the workflow by calling the module associated with the corresponding step, in the registry. This call is made like this::

  # (We are inside a function that runs the pipeline from raw data to wavelength calibration. The raw data is in a numpy.ndarray named "raw").

  noise = tuna.plugins.run ( "Noise detector" ) ( noise_mask_radius = 1, noise_threshold = 1, raw = raw_can, wrapped = barycenter_can )

  # (We now have the noise array loaded in the "noise" variable).
    
Now let's suppose you need a different noise calculation - for instance, the current one does not work in your dataset. However, you do not want to re-write the pipeline for high-resolution data reduction. What you want is to change the current noise calculation.

What you need to do is:

#. Create a function with the same signature as defined for that plugin type, on the registry.

#. Register this new function in the registry, under the name specified as the plugin type.

A worked-out example follows::

  >>> import numpy
  >>> def my_super_complicated_noise_function ( data: tuna.io.can, noise_mask_radius: int, noise_threshold : float, wrapped : tuna.io.can ) -> tuna.io.can:
  ...     final_noise_array = numpy.copy ( original )
  ...     # Lots of math go here
  ...     return final_noise_array
  >>> tuna.plugins.registry ( "Noise detector", my_super_complicated_noise_function )
  Plugin for "Noise detector" set to my_super_complicated_noise_function.
  >>> tuna.plugins.registry ( )
  The following plugins are registered in Tuna:
  * "Airy fit" : tuna.models.airy.fit_airy
  * "Apply wavelength calibration" : tuna.tools.wavelength.wavelength_calibration.wavelength_calibrator
  * "B-ratio estimation" : tuna.tools.estimate_b_ratio.estimate_b_ratio
  * "Barycenter algorithm" : tuna.tools.barycenter.barycenter_geometry
  * "Continuum detector" : tuna.tools.continuum.continuum_detector
  * "FSR mapper" : tuna.tools.fsr.fsr_mapper
  * "Find the ring borders" : tuna.tools.phase_map.ring_borders.ring_border_detector
  * "Noise detector" : my_super_complicated_noise_function
  * "Overscan" : tuna.tools.overscan.no_overscan
  * "Parabola fit" : tuna.models.parabola.parabolic_fitter
  * "Ring center finder" : tuna.tools.find_rings.find_rings
  >>> tuna.plugins.registry ( "Noise detector" )
  def my_super_complicated_noise_function ( data : tuna.io.can.can, noise_mask_radius : int, noise_threshold : float, wrapped : tuna.io.can.can ) -> tuna.io.can.can

Some remarks: the numpy.copy function is not a requirement; as long as the return value of the function obeys the signature, it will be accepted as a valid plugin.
Notice that in the worked-out example, the function signature does not change, as expected.
At the end of this plugin setup, any pipeline can be called, and they will then use the newly set noise detector.
It is possible to "break" the pipeline, for instance the shape and axis order of the numpy arrays is not checked at all, and it is expected that the plugins will do "the right thing". In this example, the plugin will receive a 3D numpy array, and return a 2D numpy array, with the same number of columns and rows as the input.

Finally, if you want to add a plugin that has no signature yet, the syntax is identical to the one to modify a plugin:

  >>> tuna.plugins.registry ( "Something new", my_super_complicated_noise_function )
  Added my_super_complicated_noise_function to the plugin registry.
  >>> tuna.plugins.registry ( )
  The following plugins are registered in Tuna:
  * "Airy fit" : tuna.models.airy.fit_airy
  * "Apply wavelength calibration" : tuna.tools.wavelength.wavelength_calibration.wavelength_calibrator
  * "B-ratio estimation" : tuna.tools.estimate_b_ratio.estimate_b_ratio
  * "Barycenter algorithm" : tuna.tools.barycenter.barycenter_geometry
  * "Continuum detector" : tuna.tools.continuum.continuum_detector
  * "FSR mapper" : tuna.tools.fsr.fsr_mapper
  * "Find the ring borders" : tuna.tools.phase_map.ring_borders.ring_border_detector
  * "Noise detector" : my_super_complicated_noise_function
  * "Overscan" : tuna.tools.overscan.no_overscan
  * "Parabola fit" : tuna.models.parabola.parabolic_fitter
  * "Ring center finder" : tuna.tools.find_rings.find_rings
  * "Something new" : my_super_complicated_noise_function
"""

__version__ = "0.1.0"
__changelog__ = {
    "0.1.0" : { "Tuna" : "0.15.0", "Change" : "Added plugin 'Overscan' with default tuna.tools.overscan.no_overscan. Refactored examples to account for Overscan plugin, airy fit plugin." }
    }

import tuna

__registry = {
    "Airy fit" : tuna.models.airy.fit_airy,
    "Apply wavelength calibration" : tuna.tools.wavelength.wavelength_calibration.wavelength_calibrator,
    "B-ratio estimation" : tuna.tools.estimate_b_ratio,
    "Barycenter algorithm" : tuna.tools.barycenter_geometry,
    "Continuum detector" : tuna.tools.continuum_detector,
    "Find the ring borders" : tuna.tools.phase_map.ring_borders.ring_border_detector,
    "FSR mapper" : tuna.tools.fsr.fsr_mapper,
    "Noise detector" : tuna.tools.noise.detect_noise,
    "Overscan" : tuna.tools.overscan.no_overscan,
    "Parabola fit" : tuna.models.parabola.parabolic_fitter,
    "Ring center finder" : tuna.tools.find_rings
    }

def get_full_module_path ( reference : object ) -> str:
    """
    This function's goal is to return a standardized string version of the full module path and function name, when given a reference to a function as input.

    Parameters:

    * reference : object

    Returns:

    * str
    """
    ignorable_module_names = [ "__main__",
                               "builtins",
                               "registry" ]
    
    if reference.__module__ in ignorable_module_names:
        return reference.__name__
    else:
        return reference.__module__ + "." + reference.__name__

def registry ( step_name : str = "",
               callable_reference : object = None ):
    """
    This function's goal is to be an user interface to the registry.

    If called with no step_name parameter, it will print the current registry to stdout.

    If called with only the step_name parameter, it will check that argument is a key in the registry's dictionary, and print the signature associated with that key if so.

    If called with two parameters, it will attempt to add or modify the dictionary so that the second parameter is the entry with the key contained in the first parameter.

    Parameters:

    * step_name : str : ""
        The name of the workflow "step" this plugin refers to.

    * callable_reference : object : None
        reference to a Python callable object.
    """
    global __registry

    # List all entries
    if step_name == "":
        print ( "The following plugins are registered in Tuna:" )
        for key in sorted ( list ( __registry.keys ( ) ) ):
            print ( "* \"{}\" : {}".format ( key, get_full_module_path ( __registry [ key ] ) ) )
        return

    # Describe a specific entry
    if callable_reference is None:
        try:
            entry = __registry [ step_name ]
        except KeyError:
            print ( "The registry does not have a \"{}\" key.".format ( step_name ) )
            return
        function_name = entry.__name__
        signature = "def {} ( ".format ( function_name )
        for parameter in sorted ( list ( entry.__annotations__.keys ( ) ) ):
            if parameter != "return":
                try:
                    parameters_string += ", " + parameter + " : " + get_full_module_path (
                        entry.__annotations__ [ parameter ] )
                except UnboundLocalError:
                    parameters_string = parameter + " : " + get_full_module_path (
                        entry.__annotations__ [ parameter ] )
        try:
            parameters_string += " ) -> "
        except UnboundLocalError:
            parameters_string = ") -> "
        signature += parameters_string
        signature += get_full_module_path ( entry.__annotations__ [ "return" ] )
        print ( signature )
        return

    # Add an entry
    if step_name not in list ( __registry.keys ( ) ):
        __registry [ step_name ] = callable_reference
        print ( "Added {} to the plugin registry.".format ( get_full_module_path ( callable_reference ) ) )
        return

    # Change an entry
    current_annotation = __registry [ step_name ].__annotations__
    future_annotation = callable_reference.__annotations__
    similar = True
    for key in current_annotation.keys ( ):
        try:
            if future_annotation [ key ] != current_annotation [ key ]:
                similar = False
                break
        except:
            print ( "Aborted registry change, new plugin signature differs from previous one for \"{}\".".format (
                key ) )
            return
        
    if similar:
        __registry [ step_name ] = callable_reference
        print ( "Plugin for \"{}\" set to {}.".format (
            step_name,
            get_full_module_path ( callable_reference ) ) )

def run ( step_name : str ) -> object:
    """
    This function's goal is to return a reference to the callable object associated with the registry key given as input.
    """
    try:
        return __registry [ step_name ]
    except:
        print ( "Unable to find a reference to {}.".format ( step_name ) )
