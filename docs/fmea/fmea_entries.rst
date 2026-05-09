FMEA Entries
============

.. fmea:: Hazard Light Failure to Activate
   :id: FMEA_HAZARD_NO_ACTIVATE
   :status: draft
   :severity: 8
   :occurrence: 3
   :detection: 4
   :rpn: 96
   :mitigates: COMP_REQ_BCM_HAZARD

   **Failure Mode:** Hazard light button press does not activate
   both turn indicators simultaneously.

   **Cause:** State machine fails to transition to hazard state due
   to corrupted input signal or race condition in callback dispatch.

   **Effect:** Other road users are not warned of emergency situation,
   increasing collision risk.

   **Detection:** End-to-end test TC_HAZARD_ACTIVATE verifies correct
   activation within one processing cycle.

.. fmea:: Turn Signal Stuck Active
   :id: FMEA_TURN_STUCK
   :status: draft
   :severity: 6
   :occurrence: 2
   :detection: 3
   :rpn: 36
   :mitigates: COMP_REQ_BCM_TURN_SM

   **Failure Mode:** Turn signal remains active after deactivation
   command is sent.

   **Cause:** State machine transition from active to off state is
   not triggered due to missed signal edge or stale callback state.

   **Effect:** Misleading indication to other road users about
   intended vehicle direction.

   **Detection:** State machine unit tests verify all state
   transitions including deactivation paths.

.. fmea:: Gateway Signal Loss
   :id: FMEA_GWM_LOSS
   :status: draft
   :severity: 5
   :occurrence: 3
   :detection: 5
   :rpn: 75
   :mitigates: COMP_REQ_GWM_FORWARD

   **Failure Mode:** Gateway module drops signals during cross-network
   forwarding.

   **Cause:** Buffer overflow or protocol translation error when
   converting between CAN and SOME/IP representations.

   **Effect:** Vehicle subsystems on isolated networks do not receive
   required status updates.

   **Detection:** Integration test TC_GWM_FORWARD verifies end-to-end
   signal forwarding across network boundaries.

.. fmea:: Front Light No Response
   :id: FMEA_FLCM_NO_RESPONSE
   :status: draft
   :severity: 7
   :occurrence: 2
   :detection: 4
   :rpn: 56
   :mitigates: COMP_REQ_FLCM_CONTROL

   **Failure Mode:** Front Light Control Module does not activate
   turn indicators when commanded.

   **Cause:** BodyCan0 message lost or FLCM signal subscription
   fails during initialization.

   **Effect:** Front turn indicators do not illuminate, reducing
   visibility of turn intention to oncoming traffic.

   **Detection:** Test case TC_FLCM verifies signal reception
   and actuation response.

.. fmea:: Rear Light LIN Communication Failure
   :id: FMEA_RLCM_LIN_FAIL
   :status: draft
   :severity: 7
   :occurrence: 2
   :detection: 5
   :rpn: 70
   :mitigates: COMP_REQ_RLCM_CONTROL

   **Failure Mode:** Rear Light Control Module fails to forward
   commands to the rear light unit over RearLightLIN.

   **Cause:** LIN bus communication error or timing violation
   in the RLCM-to-RL protocol exchange.

   **Effect:** Rear lights do not respond to turn or brake
   commands, reducing visibility to following vehicles.

   **Detection:** Test case TC_RLCM verifies end-to-end signal
   path from BodyCan0 through RearLightLIN to RL.
