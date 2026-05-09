RemotiveLabs Topology — Sphinx-Needs Traceability
=================================================

.. raw:: html

   <div style="display: flex; align-items: center; justify-content: center; gap: 2em; margin: 2em 0 1.5em 0; padding: 1.5em; border-radius: 12px; background: var(--color-background-secondary, #f8f8f8);">
     <a href="https://www.remotivelabs.com/" target="_blank" style="text-decoration: none;">
       <img class="only-light" src="_static/remotivelabs-logo-light.svg" alt="RemotiveLabs" style="height: 40px;">
       <img class="only-dark" src="_static/remotivelabs-logo-dark.svg" alt="RemotiveLabs" style="height: 40px;">
     </a>
     <span style="font-size: 1.8em; color: var(--color-foreground-muted, #999); font-weight: 300;">×</span>
     <a href="https://useblocks.com/" target="_blank" style="text-decoration: none;">
       <img class="only-light" src="_static/useblocks-logo-light.svg" alt="useblocks" style="height: 40px;">
       <img class="only-dark" src="_static/useblocks-logo-dark.svg" alt="useblocks" style="height: 40px;">
     </a>
   </div>

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
   architecture/index
   models/index
   verification/index
   fmea/index
