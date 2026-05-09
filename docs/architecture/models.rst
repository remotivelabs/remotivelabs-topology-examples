Behavioral Models
=================

.. model:: BCM Behavioral Model
   :id: MDL_BCM
   :status: draft
   :source_doc: remotive_car/models/bcm/python/bcm/__main__.py
   :satisfies: SYSREQ_MODEL_LIFECYCLE

   Python behavioral model implementing BCM logic with state
   machines for turn signals, beams, and gears. Subscribes
   to DriverCan0 inputs, publishes to BodyCan0 outputs.

.. model:: GWM Behavioral Model
   :id: MDL_GWM
   :status: draft
   :source_doc: remotive_car/models/gwm/python/gwm/__main__.py
   :satisfies: SYSREQ_MULTI_CHANNEL

   Python behavioral model implementing gateway signal
   forwarding between CAN and SOME/IP domains.

.. model:: SCCM Behavioral Model
   :id: MDL_SCCM
   :status: draft
   :source_doc: remotive_car/models/sccm/python/sccm/__main__.py
   :satisfies: SYSREQ_MODEL_LIFECYCLE

   Python behavioral model implementing steering column
   input processing and signal publishing on DriverCan0.

.. model:: IHU Behavioral Model
   :id: MDL_IHU
   :status: draft
   :source_doc: remotive_car/models/ihu/python/ihu/__main__.py
   :satisfies: SYSREQ_MULTI_CHANNEL

   Python behavioral model implementing infotainment head
   unit SOME/IP service consumption and display logic.

.. model:: RLCM Behavioral Model
   :id: MDL_RLCM
   :status: draft
   :source_doc: remotive_car/models/rlcm/python/rlcm/__main__.py
   :satisfies: SYSREQ_MODEL_LIFECYCLE

   Python behavioral model implementing rear light control
   logic via BodyCan0 input and RearLightLIN output.
