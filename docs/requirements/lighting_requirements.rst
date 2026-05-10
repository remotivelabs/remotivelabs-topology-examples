Lighting System Requirements
============================

.. comp_req:: Front Light Control
   :id: COMP_REQ_FLCM_CONTROL
   :status: approved
   :asil: B
   :verification_method: test
   :source_doc: remotive_car/platform/remotive-car.platform.yaml
   :satisfies: SYSREQ_HAZARD_LIGHT_SAFETY
   :reviewer: safety-engineer
   :approved_by: safety-manager
   :approved_date: 2026-05-10

   The Front Light Control Module shall activate the front turn
   indicators and headlights based on TurnLightControl and
   HeadlightControl signals received on BodyCan0.

.. comp_req:: Rear Light Control
   :id: COMP_REQ_RLCM_CONTROL
   :status: approved
   :asil: B
   :verification_method: test
   :source_doc: remotive_car/models/rlcm/python/rlcm/__main__.py
   :satisfies: SYSREQ_HAZARD_LIGHT_SAFETY
   :refines: MDL_RLCM
   :reviewer: safety-engineer
   :approved_by: safety-manager
   :approved_date: 2026-05-10

   The Rear Light Control Module shall translate rear turn indicator
   and brake light commands received on BodyCan0 to corresponding
   LIN frames on RearLightLIN, propagating signal state changes to
   the physical rear light unit within one bus cycle.
