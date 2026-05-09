Test Cases
==========

Hazard Light Tests
------------------

.. tc:: Hazard Light Activation
   :id: TC_HAZARD_ACTIVATE
   :status: reviewed
   :verification_method: test
   :source_doc: remotive_car/tests/behave/features/hazard_light.feature
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
   :verification_method: test
   :source_doc: remotive_car/tests/behave/features/hazard_light.feature
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
   :verification_method: test
   :source_doc: remotive_car/tests/behave/features/blink_left.feature
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
   :verification_method: test
   :source_doc: remotive_car/tests/behave/features/blink_left.feature
   :verifies: COMP_REQ_BCM_TURN_RIGHT

   **Preconditions:** Topology running, no active turn signals.

   **Steps:**

   1. Send TurnSignalRight = 1 on DriverCan0
   2. Wait one processing cycle
   3. Read RightTurnLightRequest on BodyCan0

   **Expected:** RightTurnLightRequest shall be active.
   LeftTurnLightRequest shall remain inactive.

Beam Control Tests
------------------

.. tc:: Beam State Transitions
   :id: TC_BEAMS
   :status: reviewed
   :verification_method: test
   :source_doc: remotive_car/models/bcm/python/tests
   :verifies: COMP_REQ_BCM_BEAMS

   **Preconditions:** BCM model active, beams in off state.

   **Steps:**

   1. Send LightSwitch = DRL on DriverCan0
   2. Verify beam state transitions to daytime running lights
   3. Send LightSwitch = LOW on DriverCan0
   4. Verify beam state transitions to low beam

   **Expected:** Each input produces exactly one valid state transition.

.. tc:: Gear State Tracking Verification
   :id: TC_GEARS
   :status: reviewed
   :verification_method: test
   :source_doc: remotive_car/models/bcm/python/tests
   :verifies: COMP_REQ_BCM_GEARS

   **Preconditions:** BCM model active, gear in drive state.

   **Steps:**

   1. Send GearPosition = reverse on DriverCan0
   2. Read ReverseLight on BodyCan0

   **Expected:** ReverseLight shall be active when gear is in reverse.

State Machine Tests
-------------------

.. tc:: Turn Signal State Machine Arbitration
   :id: TC_TURN_SM
   :status: reviewed
   :verification_method: test
   :source_doc: remotive_car/models/bcm/python/bcm/state_machines/turn_signals.py
   :verifies: COMP_REQ_BCM_TURN_SM

   **Preconditions:** BCM model active, turn signal state machine in off state.

   **Steps:**

   1. Activate left turn signal — verify state = left
   2. While left active, activate hazard — verify state = hazard (priority)
   3. Deactivate hazard — verify state returns to left
   4. Deactivate left — verify state = off

   **Expected:** Hazard takes priority over directional signals.
   State transitions follow the hierarchical state machine graph.

.. tc:: Turn Signal Blink Timing
   :id: TC_BLINK_TIMING
   :status: reviewed
   :verification_method: test
   :source_doc: remotive_car/models/bcm/python/bcm/state_machines/turn_signals.py
   :verifies: COMP_REQ_BCM_TURN_SM

   **Preconditions:** BCM model active, turn signal state machine in off state.

   **Steps:**

   1. Activate left turn signal
   2. Measure timing of on/off transitions over 10 blink cycles
   3. Verify blink frequency is within the specified cadence
   4. Deactivate turn signal and verify blinking stops

   **Expected:** Blink on/off timing shall be consistent across cycles
   with frequency within the configured cadence tolerance.

Integration Tests
-----------------

.. tc:: End-to-End Signal Chain
   :id: TC_E2E_SIGNAL
   :status: reviewed
   :verification_method: test
   :source_doc: remotive_car/tests/pytest/test_simulate_driver.py
   :verifies: COMP_REQ_BCM_SUBSCRIBE

   **Preconditions:** Full topology running with all ECU models.

   **Steps:**

   1. Inject driver inputs via SCCM mock on DriverCan0
   2. Wait for BCM processing
   3. Verify output signals appear on BodyCan0

   **Expected:** Input signals are routed through BCM and produce
   correct output signals within the specified processing window.

.. tc:: Restbus Default Values
   :id: TC_RESTBUS
   :status: reviewed
   :verification_method: test
   :source_doc: remotive_car/models/bcm/python/bcm/__main__.py
   :verifies: COMP_REQ_BCM_RESTBUS

   **Preconditions:** BCM model active, no input signals received.

   **Steps:**

   1. Start BCM model
   2. Read all output signals on BodyCan0

   **Expected:** All output signals shall have their default values
   published by the restbus.

.. tc:: Gateway Signal Forwarding
   :id: TC_GWM_FORWARD
   :status: reviewed
   :verification_method: test
   :source_doc: remotive_car/models/gwm/python/gwm/__main__.py
   :verifies: COMP_REQ_GWM_FORWARD

   **Preconditions:** Topology running with GWM model active.

   **Steps:**

   1. Send a signal on BodyCan0
   2. Verify the signal appears on ChassisCan0 via GWM forwarding

   **Expected:** Designated signals are forwarded between CAN domains
   according to the routing configuration.

.. tc:: Front Light Control Verification
   :id: TC_FLCM
   :status: reviewed
   :verification_method: test
   :source_doc: getting_started/tests/test_hazard_light.py
   :verifies: COMP_REQ_FLCM_CONTROL

   **Preconditions:** Topology running with FLCM connected to BodyCan0.

   **Steps:**

   1. Send TurnLightControl with LeftTurnLightRequest = 1 on BodyCan0
   2. Verify FLCM receives and processes the command

   **Expected:** FLCM activates the front left turn indicator.

.. tc:: Rear Light Control Verification
   :id: TC_RLCM
   :status: reviewed
   :verification_method: test
   :source_doc: remotive_car/platform/remotive-car.platform.yaml
   :verifies: COMP_REQ_RLCM_CONTROL

   **Preconditions:** Topology running with RLCM connected to BodyCan0
   and RearLightLIN.

   **Steps:**

   1. Send rear turn signal command on BodyCan0
   2. Verify signal reaches rear light unit via RearLightLIN

   **Expected:** RLCM forwards the lighting command to the rear
   light unit over the LIN bus.

.. tc:: Gateway Protocol Translation Verification
   :id: TC_GWM_TRANSLATE
   :status: reviewed
   :verification_method: test
   :source_doc: remotive_car/models/gwm/python/gwm/__main__.py
   :verifies: COMP_REQ_GWM_TRANSLATE

   **Preconditions:** Topology running with GWM bridging CAN and SOME/IP.

   **Steps:**

   1. Send a CAN-encoded signal on BodyCan0
   2. Verify the signal appears on the SOME/IP interface in the
      correct service representation

   **Expected:** Signal representation is correctly translated between
   CAN frame encoding and SOME/IP service interface format.

.. tc:: IHU SOME/IP Consumption
   :id: TC_IHU_SOMEIP
   :status: reviewed
   :verification_method: test
   :source_doc: remotive_car/models/ihu/python/ihu/__main__.py
   :verifies: COMP_REQ_IHU_SOMEIP

   **Preconditions:** Topology running with IHU and GWM active.

   **Steps:**

   1. Send vehicle signals through the GWM to the SOME/IP network
   2. Verify IHU receives and processes the signals

   **Expected:** IHU successfully consumes vehicle signals via the
   SOME/IP service interface.

.. tc:: SCCM Input Processing
   :id: TC_SCCM_INPUT
   :status: reviewed
   :verification_method: test
   :source_doc: remotive_car/models/sccm/python/sccm/__main__.py
   :verifies: COMP_REQ_SCCM_INPUT

   **Preconditions:** Topology running with SCCM model active.

   **Steps:**

   1. Inject driver input (turn signal, hazard button) to SCCM
   2. Verify corresponding CAN signals appear on DriverCan0

   **Expected:** SCCM publishes correct CAN signals for each
   driver input event.
