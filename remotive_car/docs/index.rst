RemotiveLabs Topology — Sphinx-Needs Traceability
=================================================

ISO 26262-aligned traceability for the RemotiveLabs Topology framework,
powered by `Sphinx-Needs <https://sphinx-needs.readthedocs.io/>`_ and
`useblocks <https://useblocks.com/>`_ tooling.

Overall Traceability
--------------------

The diagram below shows the complete traceability graph across all need objects
— from features through system and component requirements, into architecture,
ECUs, channels, models, test cases, and FMEA entries.

.. needflow::
   :show_link_names:
   :link_types: satisfies, verifies, refines, mitigates, connects_to

.. toctree::
   :maxdepth: 2
   :caption: Contents

   features/index
   requirements/index
   verification/index
   fmea/index
