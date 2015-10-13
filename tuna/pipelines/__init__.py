"""
This namespace aggregates modules that contain Tuna's pipelines.

The pipeline is a recipe for using the library's tools in a certain way, in order to obtain a desired result. It is expected that the individual tools can be replaced, as long as they result in scientifically equivalent outputs, given the same inputs.

A pipeline can be written using direct references to the tools within the library (for example, a call to tuna.tools.noise_detector) or they can be written using a reference to the "registry" relative to the tools it needs (for example, a call to tuna.plugins.registry ( "Noise detector" ), which by default is tuna.tools.noise_detector).
"""

import tuna.pipelines.calibration_lamp_high_resolution
