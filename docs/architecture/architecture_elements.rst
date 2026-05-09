Architecture Elements
=====================

.. arch:: Lighting Subsystem
   :id: ARCH_LIGHTING
   :status: draft
   :source_doc: remotive_car/platform/remotive-car.platform.yaml
   :satisfies: SYSREQ_HAZARD_LIGHT_SAFETY

   The lighting subsystem comprises the BCM (control logic),
   FLCM (front actuators), RLCM (rear actuators), and RL
   (LIN rear light unit). Signal flow: SCCM → BCM → FLCM/RLCM → RL.

.. arch:: Gateway Routing Architecture
   :id: ARCH_GATEWAY
   :status: draft
   :source_doc: remotive_car/platform/remotive-car.platform.yaml
   :satisfies: SYSREQ_MULTI_CHANNEL

   The gateway architecture bridges three CAN domains
   (DriverCan0, BodyCan0, ChassisCan0) and one SOME/IP
   domain through the GWM, enabling selective signal
   forwarding across network boundaries.

.. arch:: Test Harness Architecture
   :id: ARCH_TEST_HARNESS
   :status: draft
   :source_doc: remotive_car/tests/tester.instance.yaml
   :satisfies: SYSREQ_TEST_FRAMEWORK

   The test harness instantiates ECU mocks for signal
   injection, connects to the topology via BrokerClient,
   and executes Behave scenarios and pytest cases against
   the running system.

.. arch:: Container Deployment Architecture
   :id: ARCH_CONTAINER_DEPLOY
   :status: draft
   :source_doc: getting_started/Dockerfile
   :satisfies: SYSREQ_CONTAINER_ORCH

   Each ECU behavioral model runs in an isolated Docker
   container. The topology generator produces a Docker
   Compose file wiring virtual CAN interfaces between
   containers.
