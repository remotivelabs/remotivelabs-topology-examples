Behavioral Models
=================

.. model:: BCM Behavioral Model
   :id: MDL_BCM
   :status: reviewed
   :source_doc: remotive_car/models/bcm/python/bcm/__main__.py
   :satisfies: SYSREQ_MODEL_LIFECYCLE

   Python behavioral model implementing BCM logic with state
   machines for turn signals, beams, and gears. Subscribes
   to DriverCan0 inputs, publishes to BodyCan0 outputs.

.. mermaid::
   :caption: MDL_BCM — signal flow through BCM state machines

   graph LR
       DRV["DriverCan0"]:::chan
       subgraph BCM["BCM Model"]
           TS(["turn_signals.py"]):::sm
           BM(["beams.py"]):::sm
           GR(["gears.py"]):::sm
       end
       BDY["BodyCan0"]:::chan
       DRV -->|VehicleTurnSignal| TS
       DRV -->|BeamLevel| BM
       DRV -->|GearShift| GR
       TS -->|blink cmds| BDY
       BM -->|beam cmds| BDY
       GR -->|gear state| BDY
       classDef chan fill:#f0f0f0,color:#333,stroke:#aaa
       classDef sm fill:#583eff,color:#fff,stroke:#3d2bbf

.. model:: GWM Behavioral Model
   :id: MDL_GWM
   :status: reviewed
   :source_doc: remotive_car/models/gwm/python/gwm/__main__.py
   :satisfies: SYSREQ_MULTI_CHANNEL

   Python behavioral model implementing gateway signal
   forwarding between CAN and SOME/IP domains.

.. mermaid::
   :caption: MDL_GWM — CAN to SOME/IP signal forwarding

   graph LR
       BDY["BodyCan0"]:::chan
       CHS["ChassisCan0"]:::chan
       subgraph GWM["GWM Model"]
           FWD(["CAN to SOME/IP Forwarder"]):::comp
       end
       SIP["SOME/IP"]:::chan
       BDY -->|body signals| FWD
       CHS -->|chassis signals| FWD
       FWD -->|service events| SIP
       classDef chan fill:#f0f0f0,color:#333,stroke:#aaa
       classDef comp fill:#583eff,color:#fff,stroke:#3d2bbf

.. model:: SCCM Behavioral Model
   :id: MDL_SCCM
   :status: reviewed
   :source_doc: remotive_car/models/sccm/python/sccm/__main__.py
   :satisfies: SYSREQ_MODEL_LIFECYCLE

   Python behavioral model implementing steering column
   input processing and signal publishing on DriverCan0.

.. mermaid::
   :caption: MDL_SCCM — physical input to CAN signal pipeline

   graph LR
       DEV["evdev input device"]:::ext
       subgraph SCCM["SCCM Model"]
           EVL(["event_loop.py"]):::comp
           MAP(["evdev_to_topology_mapper.py"]):::comp
       end
       DRV["DriverCan0"]:::chan
       DEV -->|raw events| EVL
       EVL --> MAP
       MAP -->|driver signals| DRV
       classDef ext fill:#fff,color:#555,stroke:#ccc,stroke-dasharray:5
       classDef comp fill:#583eff,color:#fff,stroke:#3d2bbf
       classDef chan fill:#f0f0f0,color:#333,stroke:#aaa

.. model:: IHU Behavioral Model
   :id: MDL_IHU
   :status: reviewed
   :source_doc: remotive_car/models/ihu/python/ihu/__main__.py
   :satisfies: SYSREQ_MULTI_CHANNEL

   Python behavioral model implementing infotainment head
   unit SOME/IP service consumption and display logic.

.. mermaid::
   :caption: MDL_IHU — SOME/IP service to Android display

   graph LR
       SIP["SOME/IP"]:::chan
       subgraph IHU["IHU Model"]
           BTE(["broker_to_emulator.py"]):::comp
       end
       EMUL["Android Automotive OS"]:::ext
       SIP -->|vehicle services| BTE
       BTE -->|display data| EMUL
       classDef chan fill:#f0f0f0,color:#333,stroke:#aaa
       classDef comp fill:#583eff,color:#fff,stroke:#3d2bbf
       classDef ext fill:#fff,color:#555,stroke:#ccc,stroke-dasharray:5

.. model:: RLCM Behavioral Model
   :id: MDL_RLCM
   :status: reviewed
   :source_doc: remotive_car/models/rlcm/python/rlcm/__main__.py
   :satisfies: SYSREQ_MODEL_LIFECYCLE

   Python behavioral model implementing rear light control
   logic via BodyCan0 input and RearLightLIN output.

.. mermaid::
   :caption: MDL_RLCM — BodyCan0 commands to LIN actuation

   graph LR
       BDY["BodyCan0"]:::chan
       subgraph RLCM["RLCM Model"]
           LOGIC(["Rear Light Control Logic"]):::comp
       end
       LIN["RearLightLIN"]:::chan
       BDY -->|light commands| LOGIC
       LOGIC -->|LIN frames| LIN
       classDef chan fill:#f0f0f0,color:#333,stroke:#aaa
       classDef comp fill:#583eff,color:#fff,stroke:#3d2bbf
