BCM Component Requirements
==========================

.. comp_req:: Hazard Light Signal Processing
   :id: COMP_REQ_BCM_HAZARD
   :status: draft
   :asil: B
   :verification_method: test
   :source_doc: remotive_car/models/bcm/python/bcm/__main__.py
   :satisfies: SYSREQ_HAZARD_LIGHT_SAFETY

   The Body Control Module shall activate both left and right turn
   light requests on BodyCan0 when the HazardLightButton signal
   transitions to the active state on DriverCan0.

.. comp_req:: Turn Signal Left Activation
   :id: COMP_REQ_BCM_TURN_LEFT
   :status: draft
   :asil: A
   :verification_method: test
   :source_doc: remotive_car/models/bcm/python/bcm/__main__.py
   :satisfies: SYSREQ_HAZARD_LIGHT_SAFETY

   The Body Control Module shall activate the left turn light
   request when the TurnSignalLeft input signal transitions to
   the active state, and deactivate it when the signal returns
   to inactive.

.. comp_req:: Turn Signal Right Activation
   :id: COMP_REQ_BCM_TURN_RIGHT
   :status: draft
   :asil: A
   :verification_method: test
   :source_doc: remotive_car/models/bcm/python/bcm/__main__.py
   :satisfies: SYSREQ_HAZARD_LIGHT_SAFETY

   The Body Control Module shall activate the right turn light
   request when the TurnSignalRight input signal transitions to
   the active state, and deactivate it when the signal returns
   to inactive.

.. comp_req:: Beam State Management
   :id: COMP_REQ_BCM_BEAMS
   :status: draft
   :asil: QM
   :verification_method: test
   :source_doc: remotive_car/models/bcm/python/bcm/state_machines/beams.py
   :satisfies: SYSREQ_MODEL_LIFECYCLE

   The Body Control Module shall manage headlight beam states
   (off, daytime running lights, low beam) based on the
   LightSwitch input signal, transitioning through valid states
   only.

.. comp_req:: Gear State Tracking
   :id: COMP_REQ_BCM_GEARS
   :status: draft
   :asil: QM
   :verification_method: test
   :source_doc: remotive_car/models/bcm/python/bcm/state_machines/gears.py
   :satisfies: SYSREQ_MODEL_LIFECYCLE

   The Body Control Module shall track the current gear state
   (drive, reverse) and publish the reverse light status on
   BodyCan0 based on the GearPosition input signal.

.. comp_req:: Turn Signal State Machine
   :id: COMP_REQ_BCM_TURN_SM
   :status: draft
   :asil: B
   :verification_method: test
   :source_doc: remotive_car/models/bcm/python/bcm/state_machines/turn_signals.py
   :satisfies: SYSREQ_HAZARD_LIGHT_SAFETY

   The Body Control Module shall implement a hierarchical state
   machine for turn signal arbitration with four top-level states
   (off, left, right, hazard), each with on/off substates for
   blink cycling.

.. comp_req:: Signal Subscription Setup
   :id: COMP_REQ_BCM_SUBSCRIBE
   :status: draft
   :asil: QM
   :verification_method: test
   :source_doc: remotive_car/models/bcm/python/bcm/__main__.py
   :satisfies: SYSREQ_MODEL_LIFECYCLE; SYSREQ_TOPOLOGY_PARSE

   The Body Control Module shall subscribe to all input signals
   defined in the DriverCan0 namespace and dispatch received
   values to the corresponding handler callbacks.

.. comp_req:: Restbus Behavior
   :id: COMP_REQ_BCM_RESTBUS
   :status: draft
   :asil: QM
   :verification_method: test
   :source_doc: remotive_car/models/bcm/python/bcm/__main__.py
   :satisfies: SYSREQ_MODEL_LIFECYCLE

   The Body Control Module shall maintain a restbus on BodyCan0,
   continuously publishing default signal values for all output
   signals not actively driven by input events.
