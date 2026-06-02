Lighting System Requirements
============================

.. comp_req:: Front Turn Indicator Control
   :id: COMP_REQ_FLCM_CONTROL
   :status: approved
   :asil: B
   :verification_method: test
   :source_doc: remotive_car/platform/remotive-car.platform.yaml
   :satisfies: SYSREQ_TURN_SIGNAL_SIGNALING
   :refines: MDL_FLCM
   :reviewer: Max Pabinger
   :approved_by: Bartosz Burda
   :approved_date: 2026-05-13

   The Front Light Control Module shall activate the front turn
   indicator on the side corresponding to the active TurnLightControl
   signal received on BodyCan0 within one bus cycle of signal change.

.. comp_req:: Rear Turn Indicator Control
   :id: COMP_REQ_RLCM_CONTROL
   :status: approved
   :asil: B
   :verification_method: test
   :source_doc: remotive_car/models/rlcm/python/rlcm/__main__.py
   :satisfies: SYSREQ_TURN_SIGNAL_SIGNALING
   :refines: MDL_RLCM
   :reviewer: Max Pabinger
   :approved_by: Bartosz Burda
   :approved_date: 2026-05-13

   The Rear Light Control Module shall translate rear turn indicator
   commands received on BodyCan0 into corresponding LIN frames on
   RearLightLIN within one bus cycle so the rear light unit
   illuminates the indicator on the requested side.
