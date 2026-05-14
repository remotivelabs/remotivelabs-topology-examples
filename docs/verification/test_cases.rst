Test Cases
==========

Hazard Light Tests
------------------

.. tc:: Hazard Light Activation
   :id: TC_HAZARD_ACTIVATE
   :status: reviewed
   :asil: B
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
   :asil: B
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
   :asil: B
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
   :asil: B
   :verification_method: test
   :source_doc: remotive_car/tests/behave/features/blink_left.feature
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

Beam Control Tests
------------------

.. tc:: Beam State Transitions
   :id: TC_BEAMS
   :status: reviewed
   :verification_method: test
   :source_doc: remotive_car/models/bcm/python/tests/test_beams_state_machine.py
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
   :source_doc: remotive_car/models/bcm/python/tests/test_gears_state_machine.py
   :verifies: COMP_REQ_BCM_GEARS

   **Preconditions:** BCM model active, gear in drive state.

   **Steps:**

   1. Send GearPosition = reverse on DriverCan0
   2. Read ReverseLight on BodyCan0

   **Expected:** ReverseLight shall be active when gear is in reverse.

State Machine Tests
-------------------

.. tc:: Turn Signal Hazard Priority
   :id: TC_TURN_SM
   :status: reviewed
   :asil: B
   :verification_method: test
   :source_doc: remotive_car/models/bcm/python/tests/test_turn_signals_state_machine.py
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
   :source_doc: remotive_car/models/bcm/python/tests/test_turn_signals_state_machine.py
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
   :source_doc: remotive_car/tests/pytest/test_simulate_driver.py
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
   :source_doc: remotive_car/tests/pytest/test_simulate_driver.py
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
   :source_doc: remotive_car/tests/pytest/test_simulate_driver.py
   :verifies: COMP_REQ_GWM_FORWARD

   **Preconditions:** Topology running with GWM model active.

   **Steps:**

   1. Send a signal on BodyCan0
   2. Verify the signal appears on ChassisCan0 via GWM forwarding

   **Expected:** Designated signals are forwarded between CAN domains
   according to the routing configuration.

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
   :source_doc: remotive_car/tests/pytest/test_simulate_driver.py
   :verifies: COMP_REQ_RLCM_CONTROL

   **Preconditions:** Topology running with RLCM connected to BodyCan0
   and RearLightLIN.

   **Steps:**

   1. Send rear turn signal command on BodyCan0
   2. Verify signal reaches rear light unit via RearLightLIN

   **Expected:** RLCM forwards the lighting command to the rear
   light unit over the LIN bus.

.. tc:: Brake Light Signal Publication
   :id: TC_BRAKE_LIGHT
   :status: draft
   :asil: C
   :verification_method: test
   :source_doc: remotive_car/models/bcm/python/tests/test_brake_signals.py
   :verifies: COMP_REQ_BCM_BRAKE_LIGHT

   **Preconditions:** Topology running with BCM model active;
   ``BrakeLightControl.LeftBrakeLightRequest`` and
   ``BrakeLightControl.RightBrakeLightRequest`` both inactive on
   BodyCan0.

   **Steps:**

   1. Publish ``BrakePedalPositionSensor.BrakePedalPosition`` = 50
      (non-zero) on DriverCan0.
   2. Within one signal-processing cycle, sample both
      ``BrakeLightControl.LeftBrakeLightRequest`` and
      ``BrakeLightControl.RightBrakeLightRequest`` on BodyCan0.
   3. Publish ``BrakePedalPositionSensor.BrakePedalPosition`` = 0
      on DriverCan0.
   4. Within one signal-processing cycle, sample both signals again.

   **Expected:** Both brake-light request signals report active
   (value = 1) within one cycle of brake-pedal assertion and inactive
   (value = 0) within one cycle of brake-pedal release.

   **Note:** Status is ``draft`` because the test implementation for
   the brake-pedal stimulus is not yet present in
   ``test_simulate_driver.py``; the source_doc path is the intended
   home for the test.

.. tc:: Gateway Protocol Translation Verification
   :id: TC_GWM_TRANSLATE
   :status: reviewed
   :verification_method: test
   :source_doc: remotive_car/tests/pytest/android/test_hvac.py
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
   :source_doc: remotive_car/tests/pytest/android/test_hvac.py
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
   :source_doc: remotive_car/models/sccm/python/tests/test_device.py
   :verifies: COMP_REQ_SCCM_INPUT

   **Preconditions:** Topology running with SCCM model active.

   **Steps:**

   1. Inject driver input (turn signal, hazard button) to SCCM
   2. Verify corresponding CAN signals appear on DriverCan0

   **Expected:** SCCM publishes correct CAN signals for each
   driver input event.

Infrastructure Tests
--------------------

.. tc:: Container Topology Generation
   :id: TC_CONTAINER_GEN
   :status: reviewed
   :verification_method: test
   :source_doc: getting_started/Dockerfile
   :verifies: COMP_REQ_CONTAINER_GEN

   **Preconditions:** Instance YAML files available; Docker daemon running.

   **Steps:**

   1. Run the topology generator against the instance YAML
   2. Inspect the produced Docker Compose file
   3. Verify all declared ECUs appear as services
   4. Verify virtual CAN interface mounts match channel definitions
   5. Verify signal database volume mounts are present

   **Expected:** Docker Compose file is syntactically valid and structurally
   matches the instance YAML topology declaration.

.. tc:: Recording Session Playback
   :id: TC_RECORDING_PLAY
   :status: reviewed
   :verification_method: test
   :source_doc: basic_restbus/recordings/sample_csv.recordingsession.yaml
   :verifies: COMP_REQ_RECORDING_PLAY

   **Preconditions:** Topology running; CSV recording session YAML available.

   **Steps:**

   1. Load the CSV recording session file
   2. Start playback into the running topology
   3. Capture signal values on the target channel during playback
   4. Compare captured timestamps against recording timestamps

   **Expected:** Recorded signals appear on the topology bus within
   the timing tolerance specified in the session YAML.

.. tc:: Test Framework Execution
   :id: TC_TEST_EXEC
   :status: reviewed
   :verification_method: test
   :source_doc: remotive_car/tests/tester.instance.yaml
   :verifies: COMP_REQ_TEST_EXEC

   **Preconditions:** Topology running with tester instance connected;
   Behave and pytest dependencies installed.

   **Steps:**

   1. Run ``behave`` against the feature files with the topology active
   2. Run ``pytest`` against the test modules with the topology active
   3. Verify both runners complete without import or connectivity errors
   4. Verify the BrokerClient API supports signal injection and assertion

   **Expected:** Both Behave and pytest execute successfully; BrokerClient
   signal helpers function correctly in both test contexts.

.. tc:: Jupyter Monitoring Interface
   :id: TC_JUPYTER_MONITOR
   :status: reviewed
   :verification_method: review
   :source_doc: remotive_car/common/jupyter/car.ipynb
   :verifies: COMP_REQ_JUPYTER_MONITOR

   **Verification method rationale:** The Jupyter notebook interface is
   interactive and session-scoped; automated test execution is not
   applicable. Review of the executed notebook output constitutes
   the verification evidence per ISO 26262-8 §9.4.

   **Review criteria:**

   1. Notebook cells execute without errors against a running topology
   2. Real-time signal values are displayed in notebook output
   3. Signal injection cell publishes a value confirmed on the bus
   4. BrokerClient connection cell establishes and closes cleanly

   **Expected:** Executed notebook snapshot demonstrates bidirectional
   signal interaction with the topology broker.

.. tc:: IHU Android Emulator Bridge
   :id: TC_IHU_ANDROID
   :status: reviewed
   :verification_method: test
   :source_doc: remotive_car/tests/pytest/android/test_location.py
   :verifies: COMP_REQ_IHU_ANDROID

   **Preconditions:** Topology running with IHU model; Android Automotive
   OS emulator started with SOME/IP bridge configured.

   **Steps:**

   1. Start the IHU behavioral model with Android emulator bridge enabled
   2. Send a vehicle signal through the topology
   3. Verify the signal reaches the GWM SOME/IP output
   4. Verify the IHU model forwards the signal to the Android emulator

   **Expected:** Vehicle signals delivered via broker reach the Android
   Automotive OS emulator display layer via the IHU SOME/IP bridge.
