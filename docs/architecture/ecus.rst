ECUs
====

.. ecu:: Body Control Module
   :id: ECU_BCM
   :status: draft
   :ecu_name: BCM
   :source_doc: remotive_car/platform/remotive-car.platform.yaml
   :satisfies: SYSREQ_MODEL_LIFECYCLE

   Controls vehicle body electronics including lights, locks,
   and turn signal arbitration. Connected to DriverCan0 and BodyCan0.

.. ecu:: Steering Column Control Module
   :id: ECU_SCCM
   :status: draft
   :ecu_name: SCCM
   :source_doc: remotive_car/platform/remotive-car.platform.yaml
   :satisfies: SYSREQ_MODEL_LIFECYCLE

   Receives input from steering wheel controls, pedals, and
   buttons. Connected to DriverCan0.

.. ecu:: Front Light Control Module
   :id: ECU_FLCM
   :status: draft
   :ecu_name: FLCM
   :source_doc: remotive_car/platform/remotive-car.platform.yaml
   :satisfies: SYSREQ_MODEL_LIFECYCLE

   Controls front lighting system including headlights and
   front turn indicators. Connected to BodyCan0.

.. ecu:: Rear Light Control Module
   :id: ECU_RLCM
   :status: draft
   :ecu_name: RLCM
   :source_doc: remotive_car/platform/remotive-car.platform.yaml
   :satisfies: SYSREQ_MODEL_LIFECYCLE

   Controls rear lighting system including brake lights and
   rear turn indicators. Connected to BodyCan0 and RearLightLIN.

.. ecu:: Gateway Module
   :id: ECU_GWM
   :status: draft
   :ecu_name: GWM
   :source_doc: remotive_car/platform/remotive-car.platform.yaml
   :satisfies: SYSREQ_MULTI_CHANNEL

   Routes communication between BodyCan0, ChassisCan0, and
   SOME/IP networks.

.. ecu:: Driver Information Module
   :id: ECU_DIM
   :status: draft
   :ecu_name: DIM
   :source_doc: remotive_car/platform/remotive-car.platform.yaml
   :satisfies: SYSREQ_MODEL_LIFECYCLE

   Manages instrument cluster and driver displays.
   Connected to BodyCan0.

.. ecu:: Anti-lock Braking System
   :id: ECU_ABS
   :status: draft
   :ecu_name: ABS
   :source_doc: remotive_car/platform/remotive-car.platform.yaml
   :satisfies: SYSREQ_MODEL_LIFECYCLE

   Provides vehicle speed data. Connected to ChassisCan0.

.. ecu:: Infotainment Head Unit
   :id: ECU_IHU
   :status: draft
   :ecu_name: IHU
   :source_doc: remotive_car/platform/remotive-car.platform.yaml
   :satisfies: SYSREQ_MULTI_CHANNEL

   Manages infotainment and user interface systems.
   Connected to SOME/IP.

.. ecu:: HVAC Module
   :id: ECU_HVAC
   :status: draft
   :ecu_name: HVAC
   :source_doc: remotive_car/platform/remotive-car.platform.yaml
   :satisfies: SYSREQ_MODEL_LIFECYCLE

   Heating, ventilation, and air conditioning control.
   Receives temperature commands from infotainment via BodyCan0.

.. ecu:: Parking Assistant Module
   :id: ECU_PAM
   :status: draft
   :ecu_name: PAM
   :source_doc: remotive_car/platform/remotive-car.platform.yaml
   :satisfies: SYSREQ_MODEL_LIFECYCLE

   Provides access to proximity sensor values.
   Connected to BodyCan0.

.. ecu:: Rear Light Unit
   :id: ECU_RL
   :status: draft
   :ecu_name: RL
   :source_doc: remotive_car/platform/remotive-car.platform.yaml
   :satisfies: SYSREQ_MODEL_LIFECYCLE

   Physical rear light actuator. Connected to RearLightLIN.

.. ecu:: DEVS2 Module
   :id: ECU_DEVS2
   :status: draft
   :ecu_name: DEVS2
   :source_doc: remotive_car/platform/remotive-car.platform.yaml
   :satisfies: SYSREQ_MODEL_LIFECYCLE

   Development support ECU. Connected to RearLightLIN.

.. ecu:: Telematics Control Unit
   :id: ECU_TCU
   :status: draft
   :ecu_name: TCU
   :source_doc: remotive_car/platform/remotive-car.platform.yaml
   :satisfies: SYSREQ_MODEL_LIFECYCLE

   Provides GNSS location data. Connected to DriverCan0.
