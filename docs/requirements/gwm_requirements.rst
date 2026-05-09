GWM Component Requirements
==========================

.. comp_req:: Cross-Network Signal Forwarding
   :id: COMP_REQ_GWM_FORWARD
   :status: draft
   :asil: QM
   :verification_method: test
   :source_doc: remotive_car/models/gwm/python/gwm/__main__.py
   :satisfies: SYSREQ_MULTI_CHANNEL

   The Gateway Module shall forward designated signals between
   BodyCan0, ChassisCan0, and the SOME/IP network according to
   the configured routing table.

.. comp_req:: Gateway Protocol Translation
   :id: COMP_REQ_GWM_TRANSLATE
   :status: draft
   :asil: QM
   :verification_method: test
   :source_doc: remotive_car/models/gwm/python/gwm/__main__.py
   :satisfies: SYSREQ_MULTI_CHANNEL; SYSREQ_SIGNAL_DB_LOAD

   The Gateway Module shall translate signal representations
   between CAN frame encoding and SOME/IP service interface
   format when forwarding across protocol boundaries.
