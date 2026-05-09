Platform Definition
===================

.. feat:: Platform Topology Definition
   :id: FEAT_PLATFORM_TOPOLOGY
   :status: reviewed
   :source_doc: remotive_car/platform/remotive-car.platform.yaml

   The system shall allow users to define a vehicle platform topology
   consisting of ECUs, communication channels, and signal databases
   in a declarative YAML format, enabling automatic discovery of
   ECU connectivity from DBC files.

.. feat:: Multi-Protocol Communication
   :id: FEAT_MULTI_PROTOCOL
   :status: reviewed
   :source_doc: remotive_car/platform/remotive-car.platform.yaml

   The platform shall support multiple communication protocols
   including CAN, LIN, and SOME/IP within a single topology
   definition, allowing heterogeneous vehicle network simulation.

.. feat:: Signal Database Integration
   :id: FEAT_SIGNAL_DATABASE
   :status: reviewed
   :source_doc: getting_started/platform/databases/driver_can.dbc

   The system shall parse signal database files (DBC, LDF) to
   automatically derive ECU endpoints, signal definitions, and
   message routing without manual configuration.
