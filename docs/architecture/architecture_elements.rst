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

.. mermaid::
   :caption: ARCH_LIGHTING — signal flow through lighting subsystem

   graph LR
       SCCM(["SCCM"]):::ecu
       DRV["DriverCan0"]:::chan
       BCM(["BCM"]):::ecu
       BDY["BodyCan0"]:::chan
       FLCM(["FLCM"]):::ecu
       RLCM(["RLCM"]):::ecu
       LIN["RearLightLIN"]:::chan
       RL(["RL"]):::ecu
       SCCM -->|hazard / turn| DRV
       DRV --> BCM
       BCM -->|light cmds| BDY
       BDY --> FLCM
       BDY --> RLCM
       RLCM -->|LIN frames| LIN --> RL
       classDef ecu fill:#583eff,color:#fff,stroke:#3d2bbf
       classDef chan fill:#f0f0f0,color:#333,stroke:#aaa

.. arch:: Gateway Routing Architecture
   :id: ARCH_GATEWAY
   :status: reviewed
   :source_doc: remotive_car/platform/remotive-car.platform.yaml
   :satisfies: SYSREQ_MULTI_CHANNEL

   The gateway architecture bridges three CAN domains
   (DriverCan0, BodyCan0, ChassisCan0) and one SOME/IP
   domain through the GWM, enabling selective signal
   forwarding across network boundaries.

.. mermaid::
   :caption: ARCH_GATEWAY — multi-domain routing topology

   graph LR
       subgraph CAN["CAN Domains"]
           DRV["DriverCan0"]:::chan
           BDY["BodyCan0"]:::chan
           CHS["ChassisCan0"]:::chan
       end
       GWM(["GWM"]):::ecu
       SIP["SOME/IP"]:::chan
       DRV --> GWM
       BDY --> GWM
       CHS --> GWM
       GWM --> SIP
       classDef ecu fill:#583eff,color:#fff,stroke:#3d2bbf
       classDef chan fill:#f0f0f0,color:#333,stroke:#aaa

.. arch:: Test Harness Architecture
   :id: ARCH_TEST_HARNESS
   :status: reviewed
   :source_doc: remotive_car/tests/tester.instance.yaml
   :satisfies: SYSREQ_TEST_FRAMEWORK

   The test harness instantiates ECU mocks for signal
   injection, connects to the topology via BrokerClient,
   and executes Behave scenarios and pytest cases against
   the running system.

.. mermaid::
   :caption: ARCH_TEST_HARNESS — test framework structure

   graph LR
       TC["pytest / behave"]:::test
       BC(["BrokerClient"]):::comp
       BRK(["Topology Broker"]):::comp
       MOCKS["ECU Mocks"]:::comp
       TC --> BC
       BC -->|subscribe / publish| BRK
       BRK -->|virtual CAN| MOCKS
       classDef test fill:#e4ff3e,color:#000,stroke:#aaa
       classDef comp fill:#583eff,color:#fff,stroke:#3d2bbf

.. arch:: Container Deployment Architecture
   :id: ARCH_CONTAINER_DEPLOY
   :status: reviewed
   :source_doc: getting_started/Dockerfile
   :satisfies: SYSREQ_CONTAINER_ORCH

   Each ECU behavioral model runs in an isolated Docker
   container. The topology generator produces a Docker
   Compose file wiring virtual CAN interfaces between
   containers.

.. mermaid::
   :caption: ARCH_CONTAINER_DEPLOY — container topology

   graph TB
       PLAT["platform.yaml"]:::cfg
       GEN(["Topology Generator"]):::comp
       subgraph NET["Docker Network"]
           BCM_C(["BCM"]):::ctr
           GWM_C(["GWM"]):::ctr
           SCCM_C(["SCCM"]):::ctr
           IHU_C(["IHU"]):::ctr
       end
       PLAT --> GEN --> NET
       classDef cfg fill:#f0f0f0,color:#333,stroke:#aaa
       classDef comp fill:#e4ff3e,color:#000,stroke:#aaa
       classDef ctr fill:#583eff,color:#fff,stroke:#3d2bbf

.. arch:: Platform Signal Pipeline
   :id: ARCH_SIGNAL_PIPELINE
   :status: reviewed
   :source_doc: getting_started/platform/topology.platform.yaml
   :satisfies: SYSREQ_TOPOLOGY_PARSE; SYSREQ_SIGNAL_DB_LOAD

   The signal pipeline architecture covers platform YAML parsing,
   DBC/LDF database loading, and signal namespace resolution.
   Platform definitions declare channels and ECU endpoints; signal
   databases provide encoding and routing metadata.

.. mermaid::
   :caption: ARCH_SIGNAL_PIPELINE — signal ingestion pipeline

   graph LR
       YAML["platform.yaml"]:::src
       DBC["DBC / LDF databases"]:::src
       PARSE(["YAML Parser"]):::stage
       LOAD(["DB Loader"]):::stage
       NS(["Signal Namespace"]):::stage
       BRK(["Topology Broker"]):::stage
       YAML --> PARSE
       DBC --> LOAD
       PARSE --> NS
       LOAD --> NS
       NS --> BRK
       classDef src fill:#f0f0f0,color:#333,stroke:#aaa
       classDef stage fill:#583eff,color:#fff,stroke:#3d2bbf

.. arch:: Behavioral Model Runtime
   :id: ARCH_MODEL_RUNTIME
   :status: reviewed
   :source_doc: remotive_car/models/bcm/python/bcm/__main__.py
   :satisfies: SYSREQ_MODEL_LIFECYCLE

   The model runtime architecture manages broker connection,
   signal subscription registration, callback dispatch, restbus
   publishing, and graceful shutdown for all ECU behavioral
   models.

.. mermaid::
   :caption: ARCH_MODEL_RUNTIME — model lifecycle

   graph LR
       INIT(["1. Connect"]):::stage
       SUB(["2. Subscribe"]):::stage
       RUN(["3. Callback Loop"]):::stage
       PUB(["4. Restbus Publish"]):::stage
       EXIT(["5. Shutdown"]):::stage
       INIT --> SUB --> RUN
       RUN -->|signal received| RUN
       RUN -->|tick| PUB --> RUN
       RUN -->|SIGTERM| EXIT
       classDef stage fill:#583eff,color:#fff,stroke:#3d2bbf

.. arch:: Android IHU Bridge
   :id: ARCH_ANDROID_BRIDGE
   :status: reviewed
   :source_doc: remotive_car/instances/android/main.instance.yaml
   :satisfies: SYSREQ_ANDROID

   The Android bridge architecture connects the IHU behavioral
   model to an Android Automotive OS emulator via SOME/IP,
   enabling infotainment application testing with live vehicle
   signal data.

.. mermaid::
   :caption: ARCH_ANDROID_BRIDGE — IHU to Android emulator

   graph LR
       BRK(["Topology Broker"]):::comp
       IHU(["IHU Model"]):::comp
       SIP["SOME/IP"]:::chan
       EMUL["Android Automotive OS"]:::ext
       BRK -->|vehicle signals| IHU
       IHU -->|SOME/IP services| SIP
       SIP --> EMUL
       classDef comp fill:#583eff,color:#fff,stroke:#3d2bbf
       classDef chan fill:#f0f0f0,color:#333,stroke:#aaa
       classDef ext fill:#fff,color:#555,stroke:#ccc,stroke-dasharray:5

.. arch:: Recording Subsystem
   :id: ARCH_RECORDING
   :status: reviewed
   :source_doc: basic_restbus/recordings/sample_csv.recordingsession.yaml
   :satisfies: SYSREQ_RECORDING

   The recording architecture supports CSV and candump format
   signal sessions. Recording session YAML files define the
   mapping between recording files and topology channels for
   timed playback injection.

.. mermaid::
   :caption: ARCH_RECORDING — recording playback pipeline

   graph LR
       FILES["CSV / candump files"]:::src
       YAML["recordingsession.yaml"]:::src
       PLAYER(["Recording Player"]):::comp
       BRK(["Topology Broker"]):::comp
       CHANS["Topology Channels"]:::chan
       FILES --> PLAYER
       YAML --> PLAYER
       PLAYER -->|timed inject| BRK
       BRK --> CHANS
       classDef src fill:#f0f0f0,color:#333,stroke:#aaa
       classDef comp fill:#583eff,color:#fff,stroke:#3d2bbf
       classDef chan fill:#e4ff3e,color:#000,stroke:#aaa

.. arch:: Monitoring Interface
   :id: ARCH_MONITORING
   :status: reviewed
   :source_doc: remotive_car/common/jupyter/car.ipynb
   :satisfies: SYSREQ_MONITORING

   The monitoring architecture provides a Jupyter notebook
   interface connected to the topology broker for real-time
   signal observation and interactive injection during
   development and demonstration sessions.

.. mermaid::
   :caption: ARCH_MONITORING — live signal observation

   graph LR
       BRK(["Topology Broker"]):::comp
       BC(["BrokerClient"]):::comp
       NB["car.ipynb"]:::comp
       DEV["Developer"]:::ext
       BRK -->|live signals| BC
       BC --> NB
       DEV -->|interactive| NB
       NB -->|inject| BC
       BC -->|publish| BRK
       classDef comp fill:#583eff,color:#fff,stroke:#3d2bbf
       classDef ext fill:#fff,color:#555,stroke:#ccc,stroke-dasharray:5
