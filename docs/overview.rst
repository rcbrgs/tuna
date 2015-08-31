.. _overview_label:

Overview and features
=====================

Tuna is a Python package containing several tools related to the reduction of data cubes produced by Fabry-Pérot interferometers. Tuna is a professionally written Python package, meant to be a future replacement for the plethora of "obscure" programs used in this field. To fulfill this role, Tuna must offer substantial advantages over the existing software. These are the features present in Tuna, and the corresponding problems we aim to solve with them:

* Free software: scientific results must be reproducible and auditable. The use of proprietary software does not preclude either characteristic, but it hampers both.
* Modularity: the specific computational tasks performed to process astrophysical images are in evolution, and therefore the ability to isolate and replace modules that become obsolete is an imperative.
* Multi-instrument: there is a clear opportunity for methods that are common to several instruments' reduction pipelines to be reused, and improved communaly. In a darwinistic fashion, we hope that common code be improved towards its most precise, fastest and best-documented versions.
* Low learning curve: scientists are not required to be professional programmers. On the other hand, to complete many "difficult" computational tasks (such as parallel execution, VO integration, or large dataset processing), more sophisticated infrastructural code is required. Tuna is intended to mediate this by having the more sophisticated code behind simpler "interfaces", which the "module developers" can then use as a black box.

Regarding this last point, it is important to stress that we welcome contributions to all parts of Tuna, including any "infrastructure" code or design!

Current features
----------------

Tuna version |version| has the following capabilities:

* it produces wavelength-calibrated phase maps,
  
  * wraps raw calibration data finding the spectral barycenter for each pixel,
  * finds rings' center and radius using geometrical properties of the curves in the data;
    
* it can fit models to data,
  
  * either a parabolic model,
  * or an Airy function model;
    
* it reads and writes FITS files, and
* it reads ADHOC ADA, AD2, AD3 and ADT files.

Renato Borges produced a 15 minutes video to highlight the features in this version of Tuna, available at `youtube <https://www.youtube.com/watch?v=Z4adUESjiMs>`_.

Planned features
----------------

The two major features planned for the next version of Tuna are:

* finishing the first draft of documentation, and

* begin to develop a :ref:`plugin_label` to facilitate extensions.

History and supporters
----------------------

The development of Tuna began as a collaborative project between IAG/USP (Brazil) and LAM/AMU (France). The project leads are Claudia Mendes de Oliveira from IAG and Philippe Amram from LAM. 

The major goals at the beginning of the project were:

* to develop a free, high-quality software solution for reducing Fabry-Pérot data,
* be able to reduce data from multiple instruments / interferometers, and
* leverage legacy code integrating it into Tuna.

This led to the request and approval of a grant by FAPESP, to Renato Callado Borges, under supervision of Claudia. This one year grant corresponds to the development of Tuna up to version 0.11. Of invaluable importance were the guidance from other researchers from both institutions: Bruno Quint from IAG, Benoît Epinat, Christian Surace, and Henri Plana from LAM. Also, many thanks are owed to the administrative staff both at IAG and at LAM for their role in enabling this phase of the project!
