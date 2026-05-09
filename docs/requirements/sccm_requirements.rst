SCCM Component Requirements
============================

.. comp_req:: Steering Column Input Handling
   :id: COMP_REQ_SCCM_INPUT
   :status: draft
   :asil: QM
   :verification_method: test
   :source_doc: remotive_car/models/sccm/python/sccm/__main__.py
   :satisfies: SYSREQ_MODEL_LIFECYCLE

   The Steering Column Control Module shall receive driver inputs
   (turn signals, hazard light button, wiper controls) and publish
   the corresponding CAN signals on DriverCan0.
