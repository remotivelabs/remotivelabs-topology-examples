FMEA Entries
============

.. fmea:: Hazard Light Failure to Activate
   :id: FMEA_HAZARD_NO_ACTIVATE
   :status: reviewed
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
   :status: reviewed
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
   :status: reviewed
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
   :status: reviewed
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
   :status: reviewed
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

.. fmea:: Turn Signal Left Failure to Activate
   :id: FMEA_TURN_LEFT_NO_ACTIVATE
   :status: reviewed
   :severity: 7
   :occurrence: 2
   :detection: 3
   :rpn: 42
   :mitigates: COMP_REQ_BCM_TURN_LEFT

   **Failure Mode:** Left turn signal does not activate when the
   driver engages the turn stalk.

   **Cause:** Input signal edge detection missed due to callback
   registration failure or signal subscription dropped during
   broker reconnection.

   **Effect:** Left turn intention is not communicated to other
   road users, increasing risk of side collision.

   **Detection:** Test case TC_TURN_LEFT verifies left turn signal
   activation within one processing cycle.

.. fmea:: Turn Signal Right Failure to Activate
   :id: FMEA_TURN_RIGHT_NO_ACTIVATE
   :status: reviewed
   :severity: 7
   :occurrence: 2
   :detection: 3
   :rpn: 42
   :mitigates: COMP_REQ_BCM_TURN_RIGHT

   **Failure Mode:** Right turn signal does not activate when the
   driver engages the turn stalk.

   **Cause:** Input signal edge detection missed due to callback
   registration failure or signal subscription dropped during
   broker reconnection.

   **Effect:** Right turn intention is not communicated to other
   road users, increasing risk of side collision.

   **Detection:** Test case TC_TURN_RIGHT verifies right turn signal
   activation within one processing cycle.

.. fmea:: Brake Light Failure to Activate
   :id: FMEA_BRAKE_LIGHT_NO_ACTIVATE
   :status: reviewed
   :severity: 9
   :occurrence: 2
   :detection: 3
   :rpn: 54
   :mitigates: COMP_REQ_RLCM_CONTROL

   **Failure Mode:** Brake lights do not illuminate when the brake
   pedal is pressed.

   **Cause:** RLCM fails to receive or process the BrakeLight
   command signal on BodyCan0, or the RearLightLIN communication
   is interrupted.

   **Effect:** Following vehicles are not warned of deceleration,
   significantly increasing rear collision risk.

   **Detection:** Test case TC_RLCM verifies brake light signal
   path from BodyCan0 through RLCM to the rear light unit.

.. fmea:: Gear Position Mismatch
   :id: FMEA_GEAR_POSITION_MISMATCH
   :status: reviewed
   :severity: 6
   :occurrence: 2
   :detection: 4
   :rpn: 48
   :mitigates: COMP_REQ_BCM_GEARS

   **Failure Mode:** Published gear position does not match the
   actual gear selector state.

   **Cause:** State machine transition logic error or stale
   GearPosition input signal value due to missed CAN frame.

   **Effect:** Reverse light indicates incorrect direction of
   travel; downstream systems receive wrong gear information.

   **Detection:** Test case TC_GEARS verifies gear state tracking
   and reverse light activation for each gear position.
