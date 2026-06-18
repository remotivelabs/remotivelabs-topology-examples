BCM Component Requirements
==========================

.. comp_req:: Hazard Light Signal Processing
   :id: COMP_REQ_BCM_HAZARD
   :status: approved
   :asil: B
   :verification_method: test
   :source_doc: models/bcm/python/bcm/__main__.py
   :satisfies: SYSREQ_HAZARD_LIGHT_SAFETY
   :reviewer: Max Pabinger
   :approved_by: Bartosz Burda
   :approved_date: 2026-05-10

   The Body Control Module shall activate both left and right turn
   light requests on BodyCan0 when the HazardLightButton signal
   transitions to the active state on DriverCan0.

.. comp_req:: Turn Signal Left Activation
   :id: COMP_REQ_BCM_TURN_LEFT
   :status: approved
   :asil: B
   :verification_method: test
   :source_doc: models/bcm/python/bcm/__main__.py
   :satisfies: SYSREQ_TURN_SIGNAL_SIGNALING
   :reviewer: Max Pabinger
   :approved_by: Bartosz Burda
   :approved_date: 2026-05-13

   The Body Control Module shall maintain the LeftTurnLight output on
   BodyCan0 in the active state within one signal-processing cycle
   when and only when the TurnSignalLeft input on DriverCan0 is
   asserted.

.. comp_req:: Turn Signal Right Activation
   :id: COMP_REQ_BCM_TURN_RIGHT
   :status: approved
   :asil: B
   :verification_method: test
   :source_doc: models/bcm/python/bcm/__main__.py
   :satisfies: SYSREQ_TURN_SIGNAL_SIGNALING
   :reviewer: Max Pabinger
   :approved_by: Bartosz Burda
   :approved_date: 2026-05-13

   The Body Control Module shall maintain the RightTurnLight output on
   BodyCan0 in the active state within one signal-processing cycle
   when and only when the TurnSignalRight input on DriverCan0 is
   asserted.

.. comp_req:: Turn Signal Hazard Priority
   :id: COMP_REQ_BCM_TURN_SM
   :status: approved
   :asil: B
   :verification_method: test
   :source_doc: models/bcm/python/bcm/state_machines/turn_signals.py
   :satisfies: SYSREQ_HAZARD_LIGHT_SAFETY; SYSREQ_TURN_SIGNAL_SIGNALING
   :reviewer: Max Pabinger
   :approved_by: Bartosz Burda
   :approved_date: 2026-05-13

   The Body Control Module shall command the turn indicator outputs
   such that when the hazard state is active both indicator outputs
   are commanded irrespective of the directional inputs, and when the
   hazard state is inactive only the indicator on the side of the
   active directional input is commanded.

.. comp_req:: Turn Signal Blink Cadence
   :id: COMP_REQ_BCM_TURN_BLINK
   :status: approved
   :asil: B
   :verification_method: test
   :source_doc: models/bcm/python/bcm/state_machines/turn_signals.py
   :satisfies: SYSREQ_TURN_SIGNAL_SIGNALING
   :reviewer: Max Pabinger
   :approved_by: Bartosz Burda
   :approved_date: 2026-05-13

   While a turn indicator output is commanded active, the Body Control
   Module shall toggle that output between the active and inactive
   states at a frequency of 1.5 Hz with a tolerance of plus or minus
   0.5 Hz, keeping the cycle within the regulatory range of 60 to 120
   cycles per minute defined by UNECE Regulation No. 48 for direction
   indicator lamps.
