import astropy
if astropy.__version__ == '1.0.2':
    from .airy     import ( airy_fitter )
    from .parabola import ( parabolic_fitter )
else:
    from .airy_legacy import ( airy, fit_airy )
    from .parabola_legacy import fit_parabolic_model_by_Polynomial2D
