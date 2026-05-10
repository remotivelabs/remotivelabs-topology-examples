ECUs
====

.. ecu:: Body Control Module
   :id: ECU_BCM
   :status: reviewed
   :ecu_name: BCM
   :source_doc: remotive_car/platform/remotive-car.platform.yaml
   :satisfies: SYSREQ_MODEL_LIFECYCLE

   Controls vehicle body electronics including lights, locks,
   and turn signal arbitration. Connected to DriverCan0 and BodyCan0.

.. mermaid::
   :caption: ECU_BCM — channel connections

   graph LR
       DRV["DriverCan0 (CAN)"]:::chan
       BCM(["BCM"]):::ecu
       BDY["BodyCan0 (CAN)"]:::chan
       DRV -->|turn cmds| BCM
       BCM -->|light cmds| BDY
       classDef ecu fill:#583eff,color:#fff,stroke:#3d2bbf
       classDef chan fill:#f0f0f0,color:#333,stroke:#aaa

.. ecu:: Steering Column Control Module
   :id: ECU_SCCM
   :status: reviewed
   :ecu_name: SCCM
   :source_doc: remotive_car/platform/remotive-car.platform.yaml
   :satisfies: SYSREQ_MODEL_LIFECYCLE

   Receives input from steering wheel controls, pedals, and
   buttons. Connected to DriverCan0.

.. mermaid::
   :caption: ECU_SCCM — channel connections

   graph LR
       HW["Physical Controls"]:::ext
       SCCM(["SCCM"]):::ecu
       DRV["DriverCan0 (CAN)"]:::chan
       HW -->|buttons / pedals| SCCM
       SCCM -->|driver signals| DRV
       classDef ecu fill:#583eff,color:#fff,stroke:#3d2bbf
       classDef chan fill:#f0f0f0,color:#333,stroke:#aaa
       classDef ext fill:#fff,color:#555,stroke:#ccc,stroke-dasharray:5

.. ecu:: Front Light Control Module
   :id: ECU_FLCM
   :status: reviewed
   :ecu_name: FLCM
   :source_doc: remotive_car/platform/remotive-car.platform.yaml
   :satisfies: SYSREQ_MODEL_LIFECYCLE

   Controls front lighting system including headlights and
   front turn indicators. Connected to BodyCan0.

.. mermaid::
   :caption: ECU_FLCM — channel connections

   graph LR
       BDY["BodyCan0 (CAN)"]:::chan
       FLCM(["FLCM"]):::ecu
       LED["Front Lights"]:::ext
       BDY -->|light commands| FLCM
       FLCM -->|PWM drive| LED
       classDef ecu fill:#583eff,color:#fff,stroke:#3d2bbf
       classDef chan fill:#f0f0f0,color:#333,stroke:#aaa
       classDef ext fill:#fff,color:#555,stroke:#ccc,stroke-dasharray:5

.. ecu:: Rear Light Control Module
   :id: ECU_RLCM
   :status: reviewed
   :ecu_name: RLCM
   :source_doc: remotive_car/platform/remotive-car.platform.yaml
   :satisfies: SYSREQ_MODEL_LIFECYCLE

   Controls rear lighting system including brake lights and
   rear turn indicators. Connected to BodyCan0 and RearLightLIN.

.. mermaid::
   :caption: ECU_RLCM — channel connections

   graph LR
       BDY["BodyCan0 (CAN)"]:::chan
       RLCM(["RLCM"]):::ecu
       LIN["RearLightLIN (LIN)"]:::chan
       BDY -->|light commands| RLCM
       RLCM -->|LIN frames| LIN
       classDef ecu fill:#583eff,color:#fff,stroke:#3d2bbf
       classDef chan fill:#f0f0f0,color:#333,stroke:#aaa

.. ecu:: Gateway Module
   :id: ECU_GWM
   :status: reviewed
   :ecu_name: GWM
   :source_doc: remotive_car/platform/remotive-car.platform.yaml
   :satisfies: SYSREQ_MULTI_CHANNEL

   Routes communication between BodyCan0, ChassisCan0, and
   SOME/IP networks.

.. mermaid::
   :caption: ECU_GWM — multi-domain routing

   graph LR
       BDY["BodyCan0 (CAN)"]:::chan
       CHS["ChassisCan0 (CAN)"]:::chan
       GWM(["GWM"]):::ecu
       SIP["SOME/IP (Ethernet)"]:::chan
       BDY -->|body signals| GWM
       CHS -->|chassis signals| GWM
       GWM -->|service events| SIP
       classDef ecu fill:#583eff,color:#fff,stroke:#3d2bbf
       classDef chan fill:#f0f0f0,color:#333,stroke:#aaa

.. ecu:: Driver Information Module
   :id: ECU_DIM
   :status: reviewed
   :ecu_name: DIM
   :source_doc: remotive_car/platform/remotive-car.platform.yaml
   :satisfies: SYSREQ_MODEL_LIFECYCLE

   Manages instrument cluster and driver displays.
   Connected to BodyCan0.

.. mermaid::
   :caption: ECU_DIM — channel connections

   graph LR
       BDY["BodyCan0 (CAN)"]:::chan
       DIM(["DIM"]):::ecu
       DSP["Instrument Cluster"]:::ext
       BDY -->|vehicle data| DIM
       DIM -->|render| DSP
       classDef ecu fill:#583eff,color:#fff,stroke:#3d2bbf
       classDef chan fill:#f0f0f0,color:#333,stroke:#aaa
       classDef ext fill:#fff,color:#555,stroke:#ccc,stroke-dasharray:5

.. ecu:: Anti-lock Braking System
   :id: ECU_ABS
   :status: reviewed
   :ecu_name: ABS
   :source_doc: remotive_car/platform/remotive-car.platform.yaml
   :satisfies: SYSREQ_MODEL_LIFECYCLE

   Provides vehicle speed data. Connected to ChassisCan0.

.. mermaid::
   :caption: ECU_ABS — channel connections

   graph LR
       SNS["Wheel Speed Sensors"]:::ext
       ABS(["ABS"]):::ecu
       CHS["ChassisCan0 (CAN)"]:::chan
       SNS -->|wheel pulses| ABS
       ABS -->|speed data| CHS
       classDef ecu fill:#583eff,color:#fff,stroke:#3d2bbf
       classDef chan fill:#f0f0f0,color:#333,stroke:#aaa
       classDef ext fill:#fff,color:#555,stroke:#ccc,stroke-dasharray:5

.. ecu:: Infotainment Head Unit
   :id: ECU_IHU
   :status: reviewed
   :ecu_name: IHU
   :source_doc: remotive_car/platform/remotive-car.platform.yaml
   :satisfies: SYSREQ_MULTI_CHANNEL

   Manages infotainment and user interface systems.
   Connected to SOME/IP.

.. mermaid::
   :caption: ECU_IHU — channel connections

   graph LR
       SIP["SOME/IP (Ethernet)"]:::chan
       IHU(["IHU"]):::ecu
       UI["Android AAOS"]:::ext
       SIP -->|vehicle services| IHU
       IHU -->|render| UI
       classDef ecu fill:#583eff,color:#fff,stroke:#3d2bbf
       classDef chan fill:#f0f0f0,color:#333,stroke:#aaa
       classDef ext fill:#fff,color:#555,stroke:#ccc,stroke-dasharray:5

.. ecu:: HVAC Module
   :id: ECU_HVAC
   :status: reviewed
   :ecu_name: HVAC
   :source_doc: remotive_car/platform/remotive-car.platform.yaml
   :satisfies: SYSREQ_MODEL_LIFECYCLE

   Heating, ventilation, and air conditioning control.
   Receives temperature commands from infotainment via BodyCan0.

.. mermaid::
   :caption: ECU_HVAC — channel connections

   graph LR
       BDY["BodyCan0 (CAN)"]:::chan
       HVAC(["HVAC"]):::ecu
       ACT["Fans / Valves"]:::ext
       BDY -->|temp commands| HVAC
       HVAC -->|actuate| ACT
       classDef ecu fill:#583eff,color:#fff,stroke:#3d2bbf
       classDef chan fill:#f0f0f0,color:#333,stroke:#aaa
       classDef ext fill:#fff,color:#555,stroke:#ccc,stroke-dasharray:5

.. ecu:: Parking Assistant Module
   :id: ECU_PAM
   :status: reviewed
   :ecu_name: PAM
   :source_doc: remotive_car/platform/remotive-car.platform.yaml
   :satisfies: SYSREQ_MODEL_LIFECYCLE

   Provides access to proximity sensor values.
   Connected to BodyCan0.

.. mermaid::
   :caption: ECU_PAM — channel connections

   graph LR
       SNS["Ultrasonic Sensors"]:::ext
       PAM(["PAM"]):::ecu
       BDY["BodyCan0 (CAN)"]:::chan
       SNS -->|distance data| PAM
       PAM -->|proximity signals| BDY
       classDef ecu fill:#583eff,color:#fff,stroke:#3d2bbf
       classDef chan fill:#f0f0f0,color:#333,stroke:#aaa
       classDef ext fill:#fff,color:#555,stroke:#ccc,stroke-dasharray:5

.. ecu:: Rear Light Unit
   :id: ECU_RL
   :status: reviewed
   :ecu_name: RL
   :source_doc: remotive_car/platform/remotive-car.platform.yaml
   :satisfies: SYSREQ_MODEL_LIFECYCLE

   Physical rear light actuator. Connected to RearLightLIN.

.. mermaid::
   :caption: ECU_RL — channel connections

   graph LR
       LIN["RearLightLIN (LIN)"]:::chan
       RL(["RL"]):::ecu
       LED["Rear LED Array"]:::ext
       LIN -->|LIN frames| RL
       RL -->|current drive| LED
       classDef ecu fill:#583eff,color:#fff,stroke:#3d2bbf
       classDef chan fill:#f0f0f0,color:#333,stroke:#aaa
       classDef ext fill:#fff,color:#555,stroke:#ccc,stroke-dasharray:5

.. ecu:: DEVS2 Module
   :id: ECU_DEVS2
   :status: reviewed
   :ecu_name: DEVS2
   :source_doc: remotive_car/platform/remotive-car.platform.yaml
   :satisfies: SYSREQ_MODEL_LIFECYCLE

   Development support ECU. Connected to RearLightLIN.

.. mermaid::
   :caption: ECU_DEVS2 — channel connections

   graph LR
       LIN["RearLightLIN (LIN)"]:::chan
       DEV(["DEVS2"]):::ecu
       HOST["Dev Host"]:::ext
       LIN -->|bus traffic| DEV
       DEV -->|inject / debug| HOST
       classDef ecu fill:#583eff,color:#fff,stroke:#3d2bbf
       classDef chan fill:#f0f0f0,color:#333,stroke:#aaa
       classDef ext fill:#fff,color:#555,stroke:#ccc,stroke-dasharray:5

.. ecu:: Telematics Control Unit
   :id: ECU_TCU
   :status: reviewed
   :ecu_name: TCU
   :source_doc: remotive_car/platform/remotive-car.platform.yaml
   :satisfies: SYSREQ_MODEL_LIFECYCLE

   Provides GNSS location data. Connected to DriverCan0.

.. mermaid::
   :caption: ECU_TCU — channel connections

   graph LR
       GNSS["GNSS Receiver"]:::ext
       TCU(["TCU"]):::ecu
       DRV["DriverCan0 (CAN)"]:::chan
       GNSS -->|position fix| TCU
       TCU -->|location data| DRV
       classDef ecu fill:#583eff,color:#fff,stroke:#3d2bbf
       classDef chan fill:#f0f0f0,color:#333,stroke:#aaa
       classDef ext fill:#fff,color:#555,stroke:#ccc,stroke-dasharray:5
