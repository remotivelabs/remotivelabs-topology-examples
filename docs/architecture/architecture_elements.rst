Architecture Elements
=====================

.. arch:: Lighting Subsystem
   :id: ARCH_LIGHTING
   :status: reviewed
   :source_doc: remotive_car/platform/remotive-car.platform.yaml
   :satisfies: SYSREQ_HAZARD_LIGHT_SAFETY

   The lighting subsystem comprises the BCM (control logic),
   FLCM (front actuators), RLCM (rear actuators), and RL
   (LIN rear light unit). Signal flow: SCCM → BCM → FLCM/RLCM → RL.

.. arch:: Gateway Routing Architecture
   :id: ARCH_GATEWAY
   :status: reviewed
   :source_doc: remotive_car/platform/remotive-car.platform.yaml
   :satisfies: SYSREQ_MULTI_CHANNEL

   The gateway architecture bridges three CAN domains
   (DriverCan0, BodyCan0, ChassisCan0) and one SOME/IP
   domain through the GWM, enabling selective signal
   forwarding across network boundaries.

.. arch:: Test Harness Architecture
   :id: ARCH_TEST_HARNESS
   :status: reviewed
   :source_doc: remotive_car/tests/tester.instance.yaml
   :satisfies: SYSREQ_TEST_FRAMEWORK

   The test harness instantiates ECU mocks for signal
   injection, connects to the topology via BrokerClient,
   and executes Behave scenarios and pytest cases against
   the running system.

.. arch:: Container Deployment Architecture
   :id: ARCH_CONTAINER_DEPLOY
   :status: reviewed
   :source_doc: getting_started/Dockerfile
   :satisfies: SYSREQ_CONTAINER_ORCH

   Each ECU behavioral model runs in an isolated Docker
   container. The topology generator produces a Docker
   Compose file wiring virtual CAN interfaces between
   containers.

.. arch:: Platform Signal Pipeline
   :id: ARCH_SIGNAL_PIPELINE
   :status: reviewed
   :source_doc: getting_started/platform/topology.platform.yaml
   :satisfies: SYSREQ_TOPOLOGY_PARSE; SYSREQ_SIGNAL_DB_LOAD

   The signal pipeline architecture covers platform YAML parsing,
   DBC/LDF database loading, and signal namespace resolution.
   Platform definitions declare channels and ECU endpoints; signal
   databases provide encoding and routing metadata.

.. arch:: Behavioral Model Runtime
   :id: ARCH_MODEL_RUNTIME
   :status: reviewed
   :source_doc: remotive_car/models/bcm/python/bcm/__main__.py
   :satisfies: SYSREQ_MODEL_LIFECYCLE

   The model runtime architecture manages broker connection,
   signal subscription registration, callback dispatch, restbus
   publishing, and graceful shutdown for all ECU behavioral
   models.

.. arch:: Android IHU Bridge
   :id: ARCH_ANDROID_BRIDGE
   :status: reviewed
   :source_doc: remotive_car/instances/android/main.instance.yaml
   :satisfies: SYSREQ_ANDROID

   The Android bridge architecture connects the IHU behavioral
   model to an Android Automotive OS emulator via SOME/IP,
   enabling infotainment application testing with live vehicle
   signal data.

.. arch:: Recording Subsystem
   :id: ARCH_RECORDING
   :status: reviewed
   :source_doc: basic_restbus/recordings/sample_csv.recordingsession.yaml
   :satisfies: SYSREQ_RECORDING

   The recording architecture supports CSV and candump format
   signal sessions. Recording session YAML files define the
   mapping between recording files and topology channels for
   timed playback injection.

.. arch:: Monitoring Interface
   :id: ARCH_MONITORING
   :status: reviewed
   :source_doc: remotive_car/common/jupyter/car.ipynb
   :satisfies: SYSREQ_MONITORING

   The monitoring architecture provides a Jupyter notebook
   interface connected to the topology broker for real-time
   signal observation and interactive injection during
   development and demonstration sessions.
