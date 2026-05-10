Architecture Diagrams
=====================

Real architecture diagrams extracted from source code by Pharaoh diagram agents.
Every diagram is grounded in the actual implementation — no hand-waved boxes.

System Overview
---------------

All ECUs and communication channels of the RemotiveLabs vehicle simulation topology.

.. uml::
   :caption: System Overview — ECUs and Communication Channels
   :align: center

   @startuml RemotiveLabs_System_Overview
   skinparam componentStyle rectangle
   skinparam shadowing false
   skinparam ArrowColor #555555
   skinparam defaultFontSize 11

   package "DriverCan0\nCAN · driver_can.dbc" as DRV #D4E8FF {
     [SCCM\nSteering Column Control] as SCCM
     [BCM\nBody Control Module] as BCM
     [TCU\nTransmission Control] as TCU
   }

   package "BodyCan0\nCAN · body_can.dbc" as BODY #D4FFD4 {
     [BCM\n(subscriber)] as BCM2
     [FLCM\nFront Light Control] as FLCM
     [RLCM\nRear Light Control] as RLCM
     [GWM\nGateway Module] as GWM
     [DIM\nDriver Information] as DIM
     [HVAC] as HVAC
     [PAM\nPark Assist] as PAM
   }

   package "ChassisCan0\nCAN · chassis_can.dbc" as CHASSIS #FFE5CC {
     [ABS\nAnti-lock Brakes] as ABS
     [GWM\n(subscriber)] as GWM2
   }

   package "RearLightLIN\nLIN Bus" as LIN #FFF3CC {
     [RLCM\n(publisher)] as RLCM2
     [RL\nRear Light Unit] as RL
     [DEVS2] as DEVS2
   }

   package "SOME/IP Network" as SOMEIP_NET #EFD4FF {
     [GWM\n(bridge)] as GWM3
     [IHU\nInfotainment Head Unit] as IHU
   }

   @enduml

Lighting Subsystem — BCM Component Structure
---------------------------------------------

Extracted by **pharaoh.feat-component-extract** from
``remotive_car/models/bcm/python/bcm/``.

.. uml::
   :caption: BCM – Body Control Module · Component Diagram (FEAT_STATE_MACHINE)
   :align: center

   @startuml BCM_Component_Diagram

   skinparam componentStyle rectangle
   skinparam shadowing false
   skinparam ArrowColor #444444
   skinparam ComponentBackgroundColor #EDF4FF
   skinparam PackageBackgroundColor #F6F8FA
   skinparam NoteBackgroundColor #FFFDE7
   skinparam defaultFontName Monospaced
   skinparam defaultFontSize 11

   package "BCM-DriverCan0  (input bus)" as BusDrv <<Bus>> {
     [TurnStalk\n.TurnSignal]                       as F_TS
     [HazardLightButton\n.HazardLightButton]         as F_HZ
     [LightStalk\n.LightMode / .HighBeam]            as F_LS
     [BrakePedalPositionSensor\n.BrakePedalPosition] as F_BR
     [AcceleratorPedalPositionSensor\n.AcceleratorPedalPosition] as F_AC
     [GearShiftPaddles\n.GearShiftUp / .GearShiftDown]          as F_GS
     [SteeringAngle\n.SteeringAngle]                as F_SA
   }

   package "BCM-BodyCan0  (output bus)" as BusBody <<Bus>> {
     [TurnLightControl\n.(L+R)TurnLightRequest]                       as O_TL
     [HighBeamLightControl\n.(L+R)HighBeamLightRequest]               as O_HB
     [DaylightRunningLightControl\n.(L+R)DaylightRunningLightRequest] as O_DRL
     [LowBeamLightControl\n.(L+R)LowBeamLightRequest]                as O_LB
     [BrakeLightControl\n.(L+R)BrakeLightRequest]                    as O_BLK
     [AcceleratorPedalInfo\n.AcceleratorPedalPosition]                      as O_AP
     [GearInfo\n.GearLeverPosition]                                         as O_GR
     [SteeringWheelInfo\n.SteeringWheelPosition]                            as O_SW
   }

   package "bcm/  (remotive_car/models/bcm/python/bcm/)" as BCMPkg <<Module>> {

     [__main__.py\n─────────────────\nclass BCM\nBehavioralModel wrapper\nCanNamespace: DriverCan0\nCanNamespace: BodyCan0\nRestbus + E2eSignalsFilter\nOperatingMode {NORMAL, EMERGENCY}] as BCM_Main

     package "state_machines/" as SMs {
       [turn_signals.py\n─────────────────\nTurnSignalsStateMachine\n«HierarchicalMachine»\nstates: off / left / right / hazard\nblink ticker: 1 s interval\nrefs: COMP_REQ_BCM_TURN_SM] as SM_Turn

       [beams.py\n─────────────────\nBeamsStateMachine\n«Machine»\nstates: off | drl | low\nrefs: COMP_REQ_BCM_BEAMS] as SM_Beams

       [gears.py\n─────────────────\nGearsStateMachine\n«Machine»\nstates: drive | reverse\nrefs: COMP_REQ_BCM_GEARS] as SM_Gears
     }
   }

   package "remotivelabs.topology  (platform)" as RTLib <<library>> {
     [BehavioralModel\nCanNamespace / RestbusConfig\nBrokerClient / Frame] as RT_BM
   }

   [transitions\nMachine / HierarchicalMachine] as Lib_Trans <<library>>
   [remotivelabs.topology.time\nasync_ticker (blink clock)]    as Lib_Ticker <<library>>

   BCM_Main .up.> RT_BM      : «import»
   BCM_Main .down.> SM_Turn  : «import»
   BCM_Main .down.> SM_Beams : «import»
   BCM_Main .down.> SM_Gears : «import»

   SM_Turn  ..> Lib_Trans  : «import»
   SM_Beams ..> Lib_Trans  : «import»
   SM_Gears ..> Lib_Trans  : «import»
   SM_Turn  ..> Lib_Ticker : «import»

   F_TS --> BCM_Main : on_turn_stalk()
   F_HZ --> BCM_Main : on_hazard_button()
   F_LS --> BCM_Main : on_light_mode()\non_high_beam()
   F_BR --> BCM_Main : on_brake()
   F_AC --> BCM_Main : on_accelerator()
   F_GS --> BCM_Main : on_gear_up()\non_gear_down()
   F_SA --> BCM_Main : on_steering_angle()

   BCM_Main --> SM_Turn  : set_turn_stalk_position()\nset_hazard_button_pressed()
   BCM_Main --> SM_Beams : set_light_mode_position()
   BCM_Main --> SM_Gears : change_gear_position(Up|Down)

   SM_Turn  --> O_TL  : left / right blink\n(via _set_turn_lights)
   SM_Beams --> O_DRL : daylight_running_lights
   SM_Beams --> O_LB  : low_beams
   SM_Gears --> O_GR  : 0=reverse / 1=drive

   BCM_Main --> O_HB  : HighBeam (direct remap)
   BCM_Main --> O_BLK : brake_light (direct remap)
   BCM_Main --> O_AP  : accelerator_position (direct remap)
   BCM_Main --> O_SW  : steering_angle (direct remap)

   note top of SM_Turn
     Emergency mode bypasses DriverCan0
     and calls set_emergency_mode()
     directly on this state machine.
   end note

   @enduml

BCM Turn Signal State Machine
------------------------------

Extracted by **pharaoh.state-diagram-draft** from
``remotive_car/models/bcm/python/bcm/state_machines/turn_signals.py``.
Implements :need:`COMP_REQ_BCM_TURN_SM`.

.. uml::
   :caption: BCM Turn Signal Hierarchical State Machine (COMP_REQ_BCM_TURN_SM)
   :align: center

   @startuml bcm_turn_signals
   hide empty description

   [*] --> off
   state off

   state hazard {
     hazard : entry / _start_blinking()
     hazard : exit  / _stop_blinking()
     [*] --> hazard_on
     hazard_on --> hazard_off : blink
     hazard_off --> hazard_on : blink
   }

   state left {
     left : entry / _start_blinking()
     left : exit  / _stop_blinking()
     [*] --> left_on
     left_on --> left_off : blink
     left_off --> left_on : blink
   }

   state right {
     right : entry / _start_blinking()
     right : exit  / _stop_blinking()
     [*] --> right_on
     right_on --> right_off : blink
     right_off --> right_on : blink
   }

   off      --> hazard_on : emergency_mode
   left     --> hazard_on : emergency_mode
   right    --> hazard_on : emergency_mode
   hazard   --> hazard_on : emergency_mode

   off       --> hazard_on : hazard_pressed
   left_on   --> hazard_on : hazard_pressed
   left_off  --> hazard_on : hazard_pressed
   right_on  --> hazard_on : hazard_pressed
   right_off --> hazard_on : hazard_pressed

   hazard_on  --> left_on  : hazard_pressed [stalk=left]
   hazard_off --> left_on  : hazard_pressed [stalk=left]
   hazard_on  --> right_on : hazard_pressed [stalk=right]
   hazard_off --> right_on : hazard_pressed [stalk=right]
   hazard_on  --> off      : hazard_pressed [stalk=off]
   hazard_off --> off      : hazard_pressed [stalk=off]

   off       --> left_on  : turn_left
   right_on  --> left_on  : turn_left
   right_off --> left_on  : turn_left

   off      --> right_on : turn_right
   left_on  --> right_on : turn_right
   left_off --> right_on : turn_right

   left_on   --> off : turn_off
   left_off  --> off : turn_off
   right_on  --> off : turn_off
   right_off --> off : turn_off

   @enduml

Hazard Light Activation — Signal Flow
--------------------------------------

Extracted by **pharaoh.feat-flow-extract** tracing the call graph from
``sccm/__main__.py`` → ``bcm/__main__.py`` → ``turn_signals.py`` → BodyCan0 outputs.

.. uml::
   :caption: Hazard Light Activation — End-to-End Signal Flow
   :align: center

   @startuml hazard_light_activation
   skinparam sequenceMessageAlign direction
   skinparam responseMessageBelowArrow true

   participant Driver       as DRV
   participant "SCCM\n(EventLoop / EvdevMapper)" as SCCM
   participant "Topology Broker\n(RemotiveLabs gRPC)" as TB
   participant "BCM\n(on_hazard_button)" as BCM
   participant "TurnSignalSM\n(HierarchicalMachine)" as SM
   participant "FLCM\n(BodyCan0 subscriber)" as FLCM
   participant "RLCM\n(BodyCan0 subscriber)" as RLCM

   == Button Press (SCCM side) ==

   DRV  ->  SCCM : physical hazard button press\n(evdev key event)
   activate SCCM
   SCCM ->  SCCM : EvdevToTopologyMapper.map_event()\n→ Signal("HazardLightButton.HazardLightButton", 1)
   SCCM ->  TB   : restbus.update_signals("HazardLightButton", 1)\n[namespace: SCCM-DriverCan0]
   deactivate SCCM

   == Frame Delivery (Broker → BCM) ==

   TB   ->  BCM  : deliver Frame("HazardLightButton")\n[FrameFilter on BCM-DriverCan0]
   activate BCM
   BCM  ->  BCM  : rising-edge guard:\n_hazard_button_state==0 and signal!=0

   == State Machine Transition ==

   BCM  ->  SM   : set_hazard_button_pressed()
   activate SM
   SM   ->  SM   : trigger("hazard_pressed")\noff → hazard_on
   SM   ->  SM   : on_enter_hazard()\n→ _start_blinking() [asyncio ticker, 1 s]
   SM  -->  BCM  : state = "hazard_on"
   deactivate SM

   BCM  ->  TB   : restbus.update_signals(\n  LeftTurnLightRequest=1,\n  RightTurnLightRequest=1)\n[namespace: BCM-BodyCan0]
   deactivate BCM

   TB   ->  FLCM : TurnLightControl (Left=1, Right=1) [BodyCan0]
   TB   ->  RLCM : TurnLightControl (Left=1, Right=1) [BodyCan0]

   == Blink Loop (asyncio ticker every blink_interval_in_sec) ==

   loop every blink_interval_in_sec
     SM   ->  SM   : on_blink_tick() → trigger("blink")\nhazard_on ↔ hazard_off
     SM   ->  BCM  : _callback(state)
     activate BCM
     BCM  ->  TB   : restbus.update_signals(\n  Left=<toggled>, Right=<toggled>)
     deactivate BCM
     TB   ->  FLCM : TurnLightControl (toggled) [BodyCan0]
     TB   ->  RLCM : TurnLightControl (toggled) [BodyCan0]
   end

   @enduml

Gateway Multi-Domain Routing
-----------------------------

Extracted by **pharaoh.feat-flow-extract** tracing the GWM call graph from
``remotive_car/models/gwm/python/gwm/__main__.py`` and
``remotive_car/platform/someip.platform.yaml``.

.. uml::
   :caption: Gateway Module — CAN-to-SOME/IP Signal Routing
   :align: center

   @startuml gwm_routing
   skinparam sequenceMessageAlign center
   skinparam ParticipantPadding 20

   participant "BodyCan0\n(GWM-BodyCan0)" as BC0
   participant "GWM\n(BehavioralModel)" as GWM
   participant "ChassisCan0\n(GWM-ChassisCan0)" as CC0
   participant "SOMEIPNetwork" as SOMEIP
   participant "IHU\n(172.31.0.12:16000)" as IHU

   == Turn Light Control (BodyCan0 → SOME/IP) ==

   BC0 -> GWM : TurnLightControl frame\n[CAN, FrameFilter on GWM-BodyCan0]
   note right of GWM
     create_input_handler(FrameFilter,
     on_frame) in __init__
   end note
   GWM -> GWM : extract signals:\n  LeftTurnLightRequest\n  RightTurnLightRequest
   GWM -> SOMEIP : SomeIPNamespace.notify(\n  SomeIPEvent(\n    service="TurnlightIndicator",\n    event="TurnlightControlEvent",\n    params={Left, Right}))
   SOMEIP -> IHU : TurnlightIndicator::TurnlightControlEvent\n[UDP, port 16000]

   == Vehicle Speed (ChassisCan0 → SOME/IP) ==

   CC0 -> GWM : UISpeedFrame\n[CAN, FrameFilter on GWM-ChassisCan0]
   GWM -> GWM : extract signals:\n  UISpeedFrame.uispeed
   GWM -> SOMEIP : SomeIPNamespace.notify(\n  SomeIPEvent(\n    service="SpeedService",\n    event="SpeedEvent",\n    params={Speed}))
   SOMEIP -> IHU : SpeedService::SpeedEvent\n[UDP, port 16000]

   @enduml
