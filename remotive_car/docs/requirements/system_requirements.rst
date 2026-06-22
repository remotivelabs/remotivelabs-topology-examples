System Requirements
===================

.. sysreq:: Hazard Light Safety
   :id: SYSREQ_HAZARD_LIGHT_SAFETY
   :status: approved
   :asil: B
   :verification_method: test
   :reviewer: Max Pabinger
   :approved_by: Bartosz Burda
   :approved_date: 2026-05-10
   :satisfies: FEAT_LIGHTING_STATES

   When the hazard light button is activated, the Body Control
   Module shall command simultaneous left and right turn indicator
   activation within one signal processing cycle.

.. sysreq:: Turn Signal Indication
   :id: SYSREQ_TURN_SIGNAL_SIGNALING
   :status: approved
   :asil: B
   :verification_method: test
   :reviewer: Max Pabinger
   :approved_by: Bartosz Burda
   :approved_date: 2026-05-13
   :satisfies: FEAT_LIGHTING_STATES

   When the driver asserts a left or right turn intention, the system
   shall illuminate only the front and rear turn indicator lamps on
   the side matching the active turn input.

