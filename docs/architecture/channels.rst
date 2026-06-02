Communication Channels
======================

.. channel:: Driver CAN Bus
   :id: CH_DRIVER_CAN0
   :status: reviewed
   :channel_name: DriverCan0
   :protocol: CAN
   :signal_database: platform/databases/driver_can.dbc
   :source_doc: remotive_car/platform/remotive-car.platform.yaml
   :connects_to: ECU_BCM; ECU_SCCM; ECU_TCU

   Primary CAN bus carrying driver input signals from the
   steering column to the body control module.

.. mermaid::
   :caption: CH_DRIVER_CAN0 — bus members

   graph TB
       SCCM(["SCCM"]):::pub
       TCU(["TCU"]):::pub
       BUS{{"DriverCan0 / CAN"}}:::bus
       BCM(["BCM"]):::sub
       SCCM -->|driver signals| BUS
       TCU -->|GNSS data| BUS
       BUS -->|turn cmds| BCM
       classDef bus fill:#e4ff3e,color:#000,stroke:#bbb
       classDef pub fill:#583eff,color:#fff,stroke:#3d2bbf
       classDef sub fill:#7a5cff,color:#fff,stroke:#3d2bbf

.. channel:: Body CAN Bus
   :id: CH_BODY_CAN0
   :status: reviewed
   :channel_name: BodyCan0
   :protocol: CAN
   :signal_database: platform/databases/body_can.dbc
   :source_doc: remotive_car/platform/remotive-car.platform.yaml
   :connects_to: ECU_BCM; ECU_FLCM; ECU_RLCM; ECU_DIM; ECU_GWM; ECU_HVAC; ECU_PAM

   CAN bus carrying body electronics signals including
   lighting commands and comfort system status.

.. mermaid::
   :caption: CH_BODY_CAN0 — bus members

   graph TB
       BCM(["BCM"]):::pub
       PAM(["PAM"]):::pub
       BUS{{"BodyCan0 / CAN"}}:::bus
       FLCM(["FLCM"]):::sub
       RLCM(["RLCM"]):::sub
       DIM(["DIM"]):::sub
       GWM(["GWM"]):::sub
       HVAC(["HVAC"]):::sub
       BCM -->|light cmds| BUS
       PAM -->|proximity| BUS
       BUS --> FLCM
       BUS --> RLCM
       BUS --> DIM
       BUS --> GWM
       BUS --> HVAC
       classDef bus fill:#e4ff3e,color:#000,stroke:#bbb
       classDef pub fill:#583eff,color:#fff,stroke:#3d2bbf
       classDef sub fill:#7a5cff,color:#fff,stroke:#3d2bbf

.. channel:: Chassis CAN Bus
   :id: CH_CHASSIS_CAN0
   :status: reviewed
   :channel_name: ChassisCan0
   :protocol: CAN
   :signal_database: platform/databases/chassis_can.dbc
   :source_doc: remotive_car/platform/remotive-car.platform.yaml
   :connects_to: ECU_ABS; ECU_GWM

   CAN bus carrying chassis and powertrain signals
   including vehicle speed and braking data.

.. mermaid::
   :caption: CH_CHASSIS_CAN0 — bus members

   graph TB
       ABS(["ABS"]):::pub
       BUS{{"ChassisCan0 / CAN"}}:::bus
       GWM(["GWM"]):::sub
       ABS -->|speed & brake data| BUS
       BUS -->|chassis signals| GWM
       classDef bus fill:#e4ff3e,color:#000,stroke:#bbb
       classDef pub fill:#583eff,color:#fff,stroke:#3d2bbf
       classDef sub fill:#7a5cff,color:#fff,stroke:#3d2bbf

.. channel:: Rear Light LIN Bus
   :id: CH_REAR_LIGHT_LIN
   :status: reviewed
   :channel_name: RearLightLIN
   :protocol: LIN
   :source_doc: remotive_car/platform/remotive-car.platform.yaml
   :connects_to: ECU_RLCM; ECU_RL; ECU_DEVS2

   LIN bus connecting the rear light control module to
   the physical rear light unit.

.. mermaid::
   :caption: CH_REAR_LIGHT_LIN — bus members

   graph TB
       RLCM(["RLCM (master)"]):::pub
       BUS{{"RearLightLIN / LIN"}}:::bus
       RL(["RL (slave)"]):::sub
       DEVS2(["DEVS2 (monitor)"]):::sub
       RLCM -->|LIN schedules| BUS
       BUS --> RL
       BUS --> DEVS2
       classDef bus fill:#e4ff3e,color:#000,stroke:#bbb
       classDef pub fill:#583eff,color:#fff,stroke:#3d2bbf
       classDef sub fill:#7a5cff,color:#fff,stroke:#3d2bbf

.. channel:: SOME/IP Network
   :id: CH_SOMEIP
   :status: reviewed
   :channel_name: SOMEIP
   :protocol: SOME/IP
   :source_doc: remotive_car/platform/someip.platform.yaml
   :connects_to: ECU_GWM; ECU_IHU

   Service-oriented middleware connecting the gateway
   module to the infotainment head unit.

.. mermaid::
   :caption: CH_SOMEIP — service mesh

   graph LR
       GWM(["GWM (service provider)"]):::pub
       BUS{{"SOME/IP / Ethernet"}}:::bus
       IHU(["IHU (service consumer)"]):::sub
       GWM -->|vehicle services| BUS
       BUS -->|service events| IHU
       classDef bus fill:#e4ff3e,color:#000,stroke:#bbb
       classDef pub fill:#583eff,color:#fff,stroke:#3d2bbf
       classDef sub fill:#7a5cff,color:#fff,stroke:#3d2bbf
