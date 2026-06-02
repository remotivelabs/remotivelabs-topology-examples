Infrastructure Requirements
===========================

.. comp_req:: Container Topology Generation
   :id: COMP_REQ_CONTAINER_GEN
   :status: reviewed
   :asil: QM
   :verification_method: test
   :source_doc: getting_started/Dockerfile
   :satisfies: SYSREQ_CONTAINER_ORCH

   The topology generator shall produce a Docker Compose file from
   instance YAML definitions that correctly maps virtual CAN interfaces,
   mounts signal databases, and starts all declared ECU containers
   with the appropriate network configuration.

.. comp_req:: Test Framework Execution
   :id: COMP_REQ_TEST_EXEC
   :status: reviewed
   :asil: QM
   :verification_method: test
   :source_doc: remotive_car/tests/tester.instance.yaml
   :satisfies: SYSREQ_TEST_FRAMEWORK

   The test infrastructure shall support execution of both Behave
   (Gherkin) scenarios and pytest test cases against a running topology
   instance, providing signal injection and assertion helpers via the
   BrokerClient API.

.. comp_req:: Recording Playback
   :id: COMP_REQ_RECORDING_PLAY
   :status: reviewed
   :asil: QM
   :verification_method: test
   :source_doc: basic_restbus/recordings/sample_csv.recordingsession.yaml
   :satisfies: SYSREQ_RECORDING

   The recording subsystem shall load signal recordings in CSV and
   candump formats as defined in recording session YAML files and
   replay the recorded signals into the topology at their original
   timestamps.

.. comp_req:: Jupyter Monitoring Interface
   :id: COMP_REQ_JUPYTER_MONITOR
   :status: reviewed
   :asil: QM
   :verification_method: review
   :source_doc: remotive_car/common/jupyter/car.ipynb
   :satisfies: SYSREQ_MONITORING

   The monitoring subsystem shall provide a Jupyter notebook interface
   that connects to a running topology broker, enables real-time signal
   observation, and supports interactive signal injection for debugging
   and demonstration purposes.
