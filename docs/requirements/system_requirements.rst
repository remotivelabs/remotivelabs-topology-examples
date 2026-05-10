System Requirements
===================

.. sysreq:: Platform Topology Parsing
   :id: SYSREQ_TOPOLOGY_PARSE
   :status: reviewed
   :asil: QM
   :verification_method: test
   :satisfies: FEAT_PLATFORM_TOPOLOGY

   The system shall parse platform YAML files conforming to the
   ``remotive-topology-platform`` schema and instantiate all declared
   channels and ECU endpoints.

.. sysreq:: Signal Database Loading
   :id: SYSREQ_SIGNAL_DB_LOAD
   :status: reviewed
   :asil: QM
   :verification_method: test
   :satisfies: FEAT_SIGNAL_DATABASE

   The system shall load DBC and LDF signal database files referenced
   in the platform definition and derive message routing, signal
   encoding, and ECU membership automatically.

.. sysreq:: Multi-Channel Routing
   :id: SYSREQ_MULTI_CHANNEL
   :status: reviewed
   :asil: QM
   :verification_method: test
   :satisfies: FEAT_CAN_ROUTING; FEAT_MULTI_PROTOCOL; FEAT_GATEWAY

   The system shall maintain independent message routing for each
   declared communication channel, preventing cross-channel signal
   leakage.

.. sysreq:: Behavioral Model Lifecycle
   :id: SYSREQ_MODEL_LIFECYCLE
   :status: reviewed
   :asil: QM
   :verification_method: test
   :satisfies: FEAT_BEHAVIORAL_MODEL

   The system shall manage behavioral model lifecycle including
   broker connection, signal subscription, callback dispatch,
   and graceful shutdown.

.. sysreq:: Container Orchestration
   :id: SYSREQ_CONTAINER_ORCH
   :status: reviewed
   :asil: QM
   :verification_method: test
   :satisfies: FEAT_CONTAINER_DEPLOY

   The system shall generate Docker Compose files from topology
   instance YAML that correctly wire CAN channels, mount signal
   databases, and start all declared ECU containers.

.. sysreq:: Test Framework Integration
   :id: SYSREQ_TEST_FRAMEWORK
   :status: reviewed
   :asil: QM
   :verification_method: test
   :satisfies: FEAT_SCENARIO_TESTING; FEAT_INTEGRATION_TESTING

   The system shall support both Behave (Gherkin) and pytest test
   frameworks for executing verification scenarios against a
   running topology instance.

.. sysreq:: Hazard Light Safety
   :id: SYSREQ_HAZARD_LIGHT_SAFETY
   :status: approved
   :asil: B
   :verification_method: test
   :satisfies: FEAT_STATE_MACHINE
   :reviewer: safety-engineer
   :approved_by: safety-manager
   :approved_date: 2026-05-10

   When the hazard light button is activated, the Body Control
   Module shall command simultaneous left and right turn indicator
   activation within one signal processing cycle.

.. sysreq:: Recording Session Management
   :id: SYSREQ_RECORDING
   :status: reviewed
   :asil: QM
   :verification_method: test
   :satisfies: FEAT_RECORDING

   The system shall support playback of recorded signal sessions
   in CSV and candump formats, injecting recorded signals into
   the topology at their original timing.

.. sysreq:: Interactive Monitoring
   :id: SYSREQ_MONITORING
   :status: reviewed
   :asil: QM
   :verification_method: review
   :satisfies: FEAT_JUPYTER

   The system shall provide an interactive notebook interface
   for real-time signal monitoring and input injection during
   a running topology session.

.. sysreq:: Android Integration
   :id: SYSREQ_ANDROID
   :status: reviewed
   :asil: QM
   :verification_method: test
   :satisfies: FEAT_ANDROID

   The system shall support integration with Android Automotive
   OS emulators, enabling infotainment application testing via
   SOME/IP connectivity to the simulated vehicle network.
