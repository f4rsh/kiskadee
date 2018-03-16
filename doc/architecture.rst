Architecture
=====================

kiskadee architecture aims to decouple source code analysis from release
monitoring. To accomplish that, we have separated the module responsible to
fetch package versions and source code, and the module responsible to run
the analyses. The communication between them is done through queues, as shown
in the Figure below.

For the current architecture, we use three queues. The *packages_queue* is used
by the fetchers to enqueue the packages that should be analyzed. This queue is
consumed by the monitor module, to check if the enqueued package was already
analyzed. The second queue, called *analysis_queue*, is consumed by the runner
module, in order to receive packages that must be analyzed, which are queued by
the monitor module.  If a dequeued package does not exist in the database, the
monitor module enqueues it for analysis in the *analysis_queue*.  When an
analysis is performed, the runner module sends the analysis report to the
monitor module, by enqueing it in the *results_queue*. The package (and the
analysis) are saved in the database by the monitor module.  Currently, kiskadee
only generates analysis for projects written in C/C++. This was a scope
decision made by the kiskadee authors.

.. figure:: _static/kiskadee_arch.png
        :align: center

..

*Figure One: kiskadee architecture.*

Monitor - Module to manage kiskadee analysis
--------------------------------------------

The Monitor class is responsible for dequeuing packages from the
`packages_queue` and for checking what packages need to be analyzed.

The class defines the following public behaviors:


.. autoclass:: kiskadee.monitor.Monitor()
    :members:

Runner - Module to run static analysis
--------------------------------------

This module is responsible for running several static analyzers on
on a given project source code.

The module defines the following public behaviors:


.. automodule:: kiskadee.runner
   :members:


