System Integration Tests
========================

System-level verification covering sysreq-level requirements.

Hazard Light System Test
------------------------

.. tc:: System-Level Hazard Light Safety
   :id: TC_SYS_HAZARD_SAFETY
   :status: reviewed
   :asil: B
   :verification_method: test
   :source_doc: tests/behave/features/hazard_light.feature
   :verifies: SYSREQ_HAZARD_LIGHT_SAFETY

   **Preconditions:** Full topology running with SCCM, BCM, FLCM, and RLCM
   models active and connected.

   **Steps:**

   1. Inject HazardLightButton press via SCCM on DriverCan0
   2. Wait one processing cycle for BCM to process
   3. Verify BCM commands both turn indicators on BodyCan0
   4. Verify FLCM activates front left and right indicators
   5. Verify RLCM activates rear left and right indicators

   **Expected:** All four turn indicators (front-left, front-right,
   rear-left, rear-right) shall activate within one processing cycle
   of the hazard button press.

.. tc:: System-Level Turn Signal Indication
   :id: TC_SYS_TURN_SIGNAL
   :status: reviewed
   :asil: B
   :verification_method: test
   :source_doc: tests/behave/features/blink_left.feature
   :verifies: SYSREQ_TURN_SIGNAL_SIGNALING

   **Preconditions:** Full topology running with SCCM, BCM, FLCM, and
   RLCM models active.

   **Steps:**

   1. Drive the scenario outline with ``<turn_direction>`` = ``left``
      via the SCCM behave step (which asserts the corresponding CAN
      signal on DriverCan0).
   2. Within one processing cycle, observe the front-left, rear-left,
      front-right, and rear-right indicator outputs.
   3. Repeat for ``<turn_direction>`` = ``right``.
   4. Repeat for ``<turn_direction>`` = ``none``.

   **Expected:** For each scenario row the indicator outputs on the
   side matching ``<turn_direction>`` illuminate within one processing
   cycle; the indicator outputs on the opposite side remain off. For
   ``none`` no indicator is illuminated.

