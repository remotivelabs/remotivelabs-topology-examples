BCM Component Requirements
==========================

.. comp_req:: Hazard Light Signal Processing
   :id: COMP_REQ_BCM_HAZARD
   :status: approved
   :asil: B
   :verification_method: test
   :source_doc: remotive_car/models/bcm/python/bcm/__main__.py
   :satisfies: SYSREQ_HAZARD_LIGHT_SAFETY
   :refines: MDL_BCM
   :reviewer: safety-engineer
   :approved_by: safety-manager
   :approved_date: 2026-05-10

   The Body Control Module shall activate both left and right turn
   light requests on BodyCan0 when the HazardLightButton signal
   transitions to the active state on DriverCan0.

.. comp_req:: Turn Signal Left Activation
   :id: COMP_REQ_BCM_TURN_LEFT
   :status: approved
   :asil: B
   :verification_method: test
   :source_doc: remotive_car/models/bcm/python/bcm/__main__.py
   :satisfies: SYSREQ_HAZARD_LIGHT_SAFETY
   :refines: MDL_BCM
   :reviewer: safety-engineer
   :approved_by: safety-manager
   :approved_date: 2026-05-10

   The Body Control Module shall maintain the LeftTurnLight output
   on BodyCan0 in the active state when and only when the
   TurnSignalLeft input on DriverCan0 is asserted.

.. comp_req:: Turn Signal Right Activation
   :id: COMP_REQ_BCM_TURN_RIGHT
   :status: approved
   :asil: B
   :verification_method: test
   :source_doc: remotive_car/models/bcm/python/bcm/__main__.py
   :satisfies: SYSREQ_HAZARD_LIGHT_SAFETY
   :refines: MDL_BCM
   :reviewer: safety-engineer
   :approved_by: safety-manager
   :approved_date: 2026-05-10

   The Body Control Module shall maintain the RightTurnLight output
   on BodyCan0 in the active state when and only when the
   TurnSignalRight input on DriverCan0 is asserted.

.. comp_req:: Beam State Management
   :id: COMP_REQ_BCM_BEAMS
   :status: reviewed
   :asil: QM
   :verification_method: test
   :source_doc: remotive_car/models/bcm/python/bcm/state_machines/beams.py
   :satisfies: SYSREQ_MODEL_LIFECYCLE
   :refines: MDL_BCM

   The Body Control Module shall manage headlight beam states
   (off, daytime running lights, low beam) based on the
   LightSwitch input signal, transitioning through valid states
   only.

.. comp_req:: Gear State Tracking
   :id: COMP_REQ_BCM_GEARS
   :status: reviewed
   :asil: QM
   :verification_method: test
   :source_doc: remotive_car/models/bcm/python/bcm/state_machines/gears.py
   :satisfies: SYSREQ_MODEL_LIFECYCLE
   :refines: MDL_BCM

   The Body Control Module shall track the current gear state
   (drive, reverse) and publish the reverse light status on
   BodyCan0 based on the GearPosition input signal.

.. comp_req:: Turn Signal State Machine
   :id: COMP_REQ_BCM_TURN_SM
   :status: approved
   :asil: B
   :verification_method: test
   :source_doc: remotive_car/models/bcm/python/bcm/state_machines/turn_signals.py
   :satisfies: SYSREQ_HAZARD_LIGHT_SAFETY
   :refines: MDL_BCM
   :reviewer: safety-engineer
   :approved_by: safety-manager
   :approved_date: 2026-05-10

   The Body Control Module shall implement a hierarchical state
   machine for turn signal arbitration with four top-level states
   (off, left, right, hazard), each with on/off substates for
   blink cycling at 1.5 Hz nominal (per ISO 4040 §6.1.1).

.. comp_req:: Signal Subscription Setup
   :id: COMP_REQ_BCM_SUBSCRIBE
   :status: reviewed
   :asil: QM
   :verification_method: test
   :source_doc: remotive_car/models/bcm/python/bcm/__main__.py
   :satisfies: SYSREQ_MODEL_LIFECYCLE; SYSREQ_TOPOLOGY_PARSE
   :refines: MDL_BCM

   The Body Control Module shall subscribe to all input signals
   defined in the DriverCan0 namespace and dispatch received
   values to the corresponding handler callbacks.

.. comp_req:: Restbus Behavior
   :id: COMP_REQ_BCM_RESTBUS
   :status: reviewed
   :asil: QM
   :verification_method: test
   :source_doc: remotive_car/models/bcm/python/bcm/__main__.py
   :satisfies: SYSREQ_MODEL_LIFECYCLE
   :refines: MDL_BCM

   The Body Control Module shall maintain a restbus on BodyCan0,
   continuously publishing default signal values for all output
   signals not actively driven by input events.
