Test Cases
==========

Hazard Light Tests
------------------

.. tc:: Hazard Light Activation
   :id: TC_HAZARD_ACTIVATE
   :status: reviewed
   :asil: B
   :verification_method: test
   :source_doc: tests/behave/features/hazard_light.feature
   :verifies: COMP_REQ_BCM_HAZARD

   **Preconditions:** Topology running with BCM model active.
   Turn signals in off state.

   **Steps:**

   1. Send HazardLightButton = 1 on DriverCan0
   2. Wait one processing cycle
   3. Read LeftTurnLightRequest and RightTurnLightRequest on BodyCan0

   **Expected:** Both LeftTurnLightRequest and RightTurnLightRequest
   shall be active (value = 1).

.. tc:: Hazard Light Deactivation
   :id: TC_HAZARD_DEACTIVATE
   :status: reviewed
   :asil: B
   :verification_method: test
   :source_doc: tests/behave/features/hazard_light.feature
   :verifies: COMP_REQ_BCM_HAZARD

   **Preconditions:** Hazard lights currently active.

   **Steps:**

   1. Send HazardLightButton = 0 on DriverCan0
   2. Wait one processing cycle
   3. Read LeftTurnLightRequest and RightTurnLightRequest on BodyCan0

   **Expected:** Both turn light requests shall be inactive (value = 0).

Turn Signal Tests
-----------------

.. tc:: Left Turn Signal Activation
   :id: TC_TURN_LEFT
   :status: reviewed
   :asil: B
   :verification_method: test
   :source_doc: tests/behave/features/blink_left.feature
   :verifies: COMP_REQ_BCM_TURN_LEFT

   **Preconditions:** Topology running, no active turn signals.

   **Steps:**

   1. Send TurnSignalLeft = 1 on DriverCan0
   2. Wait one processing cycle
   3. Read LeftTurnLightRequest on BodyCan0

   **Expected:** LeftTurnLightRequest shall be active.
   RightTurnLightRequest shall remain inactive.

.. tc:: Right Turn Signal Activation
   :id: TC_TURN_RIGHT
   :status: reviewed
   :asil: B
   :verification_method: test
   :source_doc: tests/behave/features/blink_left.feature
   :verifies: COMP_REQ_BCM_TURN_RIGHT

   **Preconditions:** Topology running, no active turn signals.

   The ``blink_left.feature`` file contains scenarios for both left and
   right turn directions; the right-turn scenario rows in the example
   table cover this test case.

   **Steps:**

   1. Send TurnSignalRight = 1 on DriverCan0
   2. Wait one processing cycle
   3. Read RightTurnLightRequest on BodyCan0

   **Expected:** RightTurnLightRequest shall be active.
   LeftTurnLightRequest shall remain inactive.

State Machine Tests
-------------------

.. tc:: Turn Signal Hazard Priority
   :id: TC_TURN_SM
   :status: reviewed
   :asil: B
   :verification_method: test
   :source_doc: models/bcm/python/tests/test_turn_signals_state_machine.py
   :verifies: COMP_REQ_BCM_TURN_SM

   **Preconditions:** BCM model active, turn signal state machine in off state.

   **Steps:**

   1. Trigger the left turn signal — verify state machine reports
      ``state == "left_on"`` or equivalent.
   2. While left is active, trigger hazard — verify state machine
      reports the hazard-active state.
   3. Trigger hazard deactivation — verify state machine returns to
      the left-only state.
   4. Trigger left deactivation — verify state machine reports the
      off state.

   **Expected:** The state machine transitions between off / left /
   hazard states as triggered. The hazard state takes priority over
   directional states. No transition occurs that is not represented
   in the state-machine graph.

.. tc:: Turn Signal Blink Cadence Measurement
   :id: TC_BLINK_TIMING
   :status: draft
   :asil: B
   :verification_method: test
   :source_doc: models/bcm/python/tests/test_turn_signals_state_machine.py
   :verifies: COMP_REQ_BCM_TURN_BLINK

   **Preconditions:** BCM model active, turn signal state machine in
   off state.

   **Steps:**

   1. Activate left turn signal.
   2. Record the timestamp of every rising and falling edge of the
      LeftTurnLightRequest signal for at least 10 blink cycles.
   3. Compute the mean blink frequency from the inter-edge intervals
      and the duty cycle (active time over period).
   4. Deactivate the turn signal and confirm no further edges occur
      within the next 2 seconds.

   **Expected:** The measured blink frequency is in the range
   1.0 Hz to 2.0 Hz with a mean of 1.5 Hz plus or minus 0.5 Hz; the
   active-state duty cycle is between 40 percent and 60 percent; no
   edges occur after deactivation.

   **Note:** Status is ``draft`` because the cited test currently
   exercises state-machine transitions only. Numerical cadence
   measurement (frequency, duty cycle) needs to be added before this
   TC can move to ``reviewed``.

.. tc:: Turn Signal Hazard Priority — CAN Output Verification
   :id: TC_TURN_SM_OUTPUTS
   :status: draft
   :asil: B
   :verification_method: test
   :source_doc: tests/pytest/test_simulate_driver.py
   :verifies: COMP_REQ_BCM_TURN_SM

   **Preconditions:** Full topology running with BCM model active;
   ``LeftTurnLightRequest`` and ``RightTurnLightRequest`` on BodyCan0
   both inactive.

   **Steps:**

   1. Publish ``TurnSignalLeft`` = 1 on DriverCan0.
   2. Within one signal-processing cycle, sample
      ``LeftTurnLightRequest`` and ``RightTurnLightRequest`` on
      BodyCan0.
   3. While ``TurnSignalLeft`` is asserted, publish
      ``HazardLightButton`` = 1 on DriverCan0.
   4. Within one signal-processing cycle, sample both outputs again.
   5. Publish ``HazardLightButton`` = 0.
   6. Within one signal-processing cycle, sample both outputs.

   **Expected:** After step 2 only ``LeftTurnLightRequest`` is active.
   After step 4 both indicator outputs are active. After step 6 only
   ``LeftTurnLightRequest`` is active. State-name verification is
   covered by ``TC_TURN_SM``; this TC covers the state-to-CAN-output
   emission mapping.

   **Note:** Status is ``draft`` because the integration scenario
   for hazard-priority CAN-output observation is not yet present in
   ``test_simulate_driver.py``. The ``source_doc`` path is the
   intended home.

Integration Tests
-----------------

.. tc:: Front Turn Indicator Verification
   :id: TC_FLCM
   :status: reviewed
   :asil: B
   :verification_method: test
   :source_doc: getting_started/tests/test_hazard_light.py
   :verifies: COMP_REQ_FLCM_CONTROL

   **Preconditions:** Topology running with FLCM connected to BodyCan0.

   **Steps:**

   1. Send HazardLightButton = 1 on DriverCan0.
   2. Within one bus cycle, sample the FLCM front turn indicator
      outputs for both left and right sides.

   **Expected:** FLCM activates both front turn indicators (left and
   right) within one bus cycle of hazard activation, exercising the
   FLCM side-selection logic in the symmetric (hazard) case. Isolated
   single-side stimuli (left-only or right-only) are not covered by
   the cited test and remain to be exercised separately.

.. tc:: Rear Turn Indicator Verification
   :id: TC_RLCM
   :status: reviewed
   :asil: B
   :verification_method: test
   :source_doc: tests/pytest/test_simulate_driver.py
   :verifies: COMP_REQ_RLCM_CONTROL

   **Preconditions:** Topology running with RLCM connected to BodyCan0
   and RearLightLIN.

   **Steps:**

   1. Send rear turn signal command on BodyCan0
   2. Verify signal reaches rear light unit via RearLightLIN

   **Expected:** RLCM forwards the lighting command to the rear
   light unit over the LIN bus.

