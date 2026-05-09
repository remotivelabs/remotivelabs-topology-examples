System Integration Tests
========================

System-level verification covering sysreq-level requirements.

Hazard Light System Test
------------------------

.. tc:: System-Level Hazard Light Safety
   :id: TC_SYS_HAZARD_SAFETY
   :status: reviewed
   :verification_method: test
   :source_doc: remotive_car/tests/behave/features/hazard_light.feature
   :verifies: SYSREQ_HAZARD_LIGHT_SAFETY

   **Preconditions:** Full topology running with SCCM, BCM, FLCM, and RLCM
   models active and connected.

   **Steps:**

   1. Inject HazardLightButton press via SCCM on DriverCan0
   2. Wait one processing cycle for BCM to process
   3. Verify BCM commands both turn indicators on BodyCan0
   4. Verify FLCM activates front left and right indicators
   5. Verify RLCM activates rear left and right indicators

   **Expected:** All four turn indicators (front-left, front-right,
   rear-left, rear-right) shall activate within one processing cycle
   of the hazard button press.

Platform and Routing Tests
--------------------------

.. tc:: System-Level Topology Parsing
   :id: TC_SYS_TOPOLOGY_PARSE
   :status: reviewed
   :verification_method: test
   :source_doc: getting_started/platform/topology.platform.yaml
   :verifies: SYSREQ_TOPOLOGY_PARSE

   **Preconditions:** Valid platform YAML file available.

   **Steps:**

   1. Load the platform YAML file
   2. Verify all declared channels are instantiated
   3. Verify all ECU endpoints are created
   4. Start the topology and confirm broker connectivity

   **Expected:** Platform parser creates correct channel and ECU
   topology matching the YAML definition.

.. tc:: System-Level Signal Database Loading
   :id: TC_SYS_SIGNAL_DB
   :status: reviewed
   :verification_method: test
   :source_doc: getting_started/platform/databases/driver_can.dbc
   :verifies: SYSREQ_SIGNAL_DB_LOAD

   **Preconditions:** Platform with DBC references available.

   **Steps:**

   1. Load the platform definition with DBC database references
   2. Verify signal definitions are available for all channels
   3. Send a raw CAN frame and verify signal decoding

   **Expected:** Signal names, scaling, offsets, and byte ordering
   match the DBC file definitions.

.. tc:: System-Level Multi-Channel Routing
   :id: TC_SYS_MULTI_CHANNEL
   :status: reviewed
   :verification_method: test
   :source_doc: remotive_car/models/gwm/python/gwm/__main__.py
   :verifies: SYSREQ_MULTI_CHANNEL

   **Preconditions:** Topology running with DriverCan0, BodyCan0,
   ChassisCan0, and SOME/IP channels.

   **Steps:**

   1. Send a signal on DriverCan0
   2. Verify it does NOT leak to BodyCan0 unless routed via GWM
   3. Send a signal designated for cross-channel forwarding
   4. Verify it appears on the target channel via GWM

   **Expected:** Channels are isolated; only explicitly routed signals
   cross network boundaries.

Lifecycle and Infrastructure Tests
-----------------------------------

.. tc:: System-Level Model Lifecycle
   :id: TC_SYS_MODEL_LIFECYCLE
   :status: reviewed
   :verification_method: test
   :source_doc: remotive_car/models/bcm/python/bcm/__main__.py
   :verifies: SYSREQ_MODEL_LIFECYCLE

   **Preconditions:** BCM model container available.

   **Steps:**

   1. Start the BCM model container
   2. Verify broker connection is established
   3. Verify signal subscriptions are registered
   4. Send an input signal and verify callback dispatch
   5. Stop the model and verify graceful shutdown

   **Expected:** Model follows the full lifecycle: connect → subscribe →
   dispatch → shutdown without errors.

.. tc:: System-Level Container Orchestration
   :id: TC_SYS_CONTAINER_ORCH
   :status: reviewed
   :verification_method: test
   :source_doc: getting_started/Dockerfile
   :verifies: SYSREQ_CONTAINER_ORCH

   **Preconditions:** Docker Compose file generated from instance YAML.

   **Steps:**

   1. Run ``docker compose up`` on the generated file
   2. Verify all ECU containers start successfully
   3. Verify CAN interfaces are wired between containers
   4. Send a signal and verify cross-container routing

   **Expected:** All containers start, connect to the broker, and
   exchange signals over virtual CAN interfaces.

.. tc:: System-Level Test Framework
   :id: TC_SYS_TEST_FRAMEWORK
   :status: reviewed
   :verification_method: test
   :source_doc: remotive_car/tests/tester.instance.yaml
   :verifies: SYSREQ_TEST_FRAMEWORK

   **Preconditions:** Topology running with tester instance.

   **Steps:**

   1. Run Behave test suite against the running topology
   2. Run pytest test suite against the running topology
   3. Verify both frameworks can inject signals and assert outputs

   **Expected:** Both Behave and pytest execute successfully and
   report pass/fail results for all verification scenarios.

.. tc:: System-Level Recording Playback
   :id: TC_SYS_RECORDING
   :status: reviewed
   :verification_method: test
   :source_doc: basic_restbus/recordings/sample_csv.recordingsession.yaml
   :verifies: SYSREQ_RECORDING

   **Preconditions:** Topology running with a recording session file.

   **Steps:**

   1. Load the CSV recording session
   2. Start playback into the topology
   3. Verify signals appear on the bus at the correct timestamps

   **Expected:** Recorded signals are injected with timing matching
   the original recording session.

.. tc:: System-Level Interactive Monitoring
   :id: TC_SYS_MONITORING
   :status: reviewed
   :verification_method: review
   :source_doc: remotive_car/common/jupyter/car.ipynb
   :verifies: SYSREQ_MONITORING

   **Preconditions:** Topology running with Jupyter notebook server.

   **Steps:**

   1. Open the car.ipynb notebook
   2. Execute cells to connect to the broker
   3. Verify real-time signal values are displayed
   4. Inject a signal via notebook and verify it appears on the bus

   **Expected:** Notebook provides bidirectional signal interaction
   with the running topology.

.. tc:: System-Level Android Integration
   :id: TC_SYS_ANDROID
   :status: reviewed
   :verification_method: test
   :source_doc: remotive_car/instances/android/main.instance.yaml
   :verifies: SYSREQ_ANDROID

   **Preconditions:** Topology running with IHU model and Android
   emulator instance.

   **Steps:**

   1. Start the Android emulator with IHU bridge active
   2. Send vehicle signals through the topology
   3. Verify signals reach the Android emulator via SOME/IP bridge

   **Expected:** Vehicle signals are visible in the Android Automotive
   OS application via the IHU SOME/IP bridge.
