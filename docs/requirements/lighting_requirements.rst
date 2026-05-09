Lighting System Requirements
============================

.. comp_req:: Front Light Control
   :id: COMP_REQ_FLCM_CONTROL
   :status: reviewed
   :asil: B
   :verification_method: test
   :source_doc: getting_started/platform/databases/body_can.dbc
   :satisfies: SYSREQ_HAZARD_LIGHT_SAFETY

   The Front Light Control Module shall activate the front turn
   indicators and headlights based on TurnLightControl and
   HeadlightControl signals received on BodyCan0.

.. comp_req:: Rear Light Control
   :id: COMP_REQ_RLCM_CONTROL
   :status: reviewed
   :asil: B
   :verification_method: test
   :source_doc: remotive_car/platform/remotive-car.platform.yaml
   :satisfies: SYSREQ_HAZARD_LIGHT_SAFETY
   :refines: MDL_RLCM

   The Rear Light Control Module shall activate rear turn
   indicators and brake lights based on signals received on
   BodyCan0 and control the rear light unit via RearLightLIN.
