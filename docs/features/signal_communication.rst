Signal Communication
====================

.. feat:: CAN Signal Routing
   :id: FEAT_CAN_ROUTING
   :status: draft
   :source_doc: remotive_car/platform/remotive-car.platform.yaml

   The system shall route CAN signals between ECUs connected to
   the same CAN channel, supporting multiple concurrent channels
   (DriverCan0, BodyCan0, ChassisCan0) within a single topology.

.. feat:: Gateway Message Forwarding
   :id: FEAT_GATEWAY
   :status: draft
   :source_doc: remotive_car/models/gwm/python/gwm/__main__.py

   The Gateway Module (GWM) shall forward messages between
   different vehicle networks (CAN, SOME/IP), enabling
   cross-network signal routing with configurable mapping.
