FMEA Entries
============

.. fmea:: Hazard Light Failure to Activate
   :id: FMEA_HAZARD_NO_ACTIVATE
   :status: reviewed
   :asil: B
   :severity: 8
   :occurrence: 3
   :detection: 4
   :rpn: 96
   :mitigates: COMP_REQ_BCM_HAZARD

   **Failure Mode:** Hazard light button press does not activate
   both turn indicators simultaneously.

   **Cause:** The HazardLightButton input is corrupted on DriverCan0
   (harness fault or stuck-low contact); the BCM hazard-button handler
   fails to evaluate the input; or the BCM fails to drive both
   ``LeftTurnLightRequest`` and ``RightTurnLightRequest`` on BodyCan0
   within one signal-processing cycle.

   **Effect:** Other road users are not warned of emergency situation,
   increasing collision risk.

   **Detection:** End-to-end test TC_HAZARD_ACTIVATE verifies correct
   activation within one processing cycle.

.. fmea:: Turn Signal Stuck Active
   :id: FMEA_TURN_STUCK
   :status: reviewed
   :asil: B
   :severity: 6
   :occurrence: 2
   :detection: 3
   :rpn: 36
   :mitigates: COMP_REQ_BCM_TURN_SM

   **Failure Mode:** Turn signal remains active after deactivation
   command is sent.

   **Cause:** The deactivation transition of the turn-signal state
   machine fails to fire because the off-state stalk edge is missed on
   DriverCan0 (intermittent contact or single-frame loss) or because
   the BCM continues to drive the turn-indicator output even though the
   internal state has reached the off state.

   **Effect:** Misleading indication to other road users about
   intended vehicle direction.

   **Detection:** State machine unit tests verify all state
   transitions including deactivation paths.

.. fmea:: Front Light No Response
   :id: FMEA_FLCM_NO_RESPONSE
   :status: reviewed
   :asil: B
   :severity: 7
   :occurrence: 2
   :detection: 4
   :rpn: 56
   :mitigates: COMP_REQ_FLCM_CONTROL

   **Failure Mode:** Front Light Control Module does not activate
   turn indicators when commanded.

   **Cause:** The ``TurnLightControl`` frame is lost or corrupted on
   BodyCan0 between BCM and FLCM (harness fault or bus error); or the
   FLCM does not actuate the front-indicator lamp driver despite a
   valid frame.

   **Effect:** Front turn indicators do not illuminate, reducing
   visibility of turn intention to oncoming traffic.

   **Detection:** Test case TC_FLCM verifies signal reception
   and actuation response.

.. fmea:: Rear Light Turn Indicator LIN Communication Failure
   :id: FMEA_RLCM_LIN_FAIL
   :status: reviewed
   :asil: B
   :severity: 7
   :occurrence: 2
   :detection: 5
   :rpn: 70
   :mitigates: COMP_REQ_RLCM_CONTROL

   **Failure Mode:** Rear Light Control Module fails to forward
   commands to the rear light unit over RearLightLIN.

   **Cause:** LIN bus communication error or timing violation
   in the RLCM-to-RL protocol exchange.

   **Effect:** Rear turn indicators do not respond to commands,
   reducing visibility of turn intention to following vehicles.

   **Detection:** Test case TC_RLCM verifies end-to-end signal
   path from BodyCan0 through RearLightLIN to RL.

.. fmea:: Turn Signal Left Failure to Activate
   :id: FMEA_TURN_LEFT_NO_ACTIVATE
   :status: reviewed
   :asil: B
   :severity: 7
   :occurrence: 2
   :detection: 3
   :rpn: 42
   :mitigates: COMP_REQ_BCM_TURN_LEFT

   **Failure Mode:** Left turn signal does not activate when the
   driver engages the turn stalk.

   **Cause:** The left turn-stalk input is stuck low on DriverCan0
   (harness fault or stuck-at-zero sensor); the BCM turn-signal state
   machine fails to transition to the left-active state due to missed
   CAN frame; or the BCM fails to drive the ``LeftTurnLightRequest``
   output on BodyCan0.

   **Effect:** Left turn intention is not communicated to other
   road users, increasing risk of side collision.

   **Detection:** Test case TC_TURN_LEFT verifies left turn signal
   activation within one processing cycle.

.. fmea:: Turn Signal Right Failure to Activate
   :id: FMEA_TURN_RIGHT_NO_ACTIVATE
   :status: reviewed
   :asil: B
   :severity: 7
   :occurrence: 2
   :detection: 3
   :rpn: 42
   :mitigates: COMP_REQ_BCM_TURN_RIGHT

   **Failure Mode:** Right turn signal does not activate when the
   driver engages the turn stalk.

   **Cause:** The right turn-stalk input is stuck low on DriverCan0
   (harness fault or stuck-at-zero sensor); the BCM turn-signal state
   machine fails to transition to the right-active state due to missed
   CAN frame; or the BCM fails to drive the ``RightTurnLightRequest``
   output on BodyCan0.

   **Effect:** Right turn intention is not communicated to other
   road users, increasing risk of side collision.

   **Detection:** Test case TC_TURN_RIGHT verifies right turn signal
   activation within one processing cycle.
