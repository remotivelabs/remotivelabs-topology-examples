Behavioral Modeling
===================

.. feat:: ECU Behavioral Modeling
   :id: FEAT_BEHAVIORAL_MODEL
   :status: reviewed
   :source_doc: remotive_car/models/bcm/python/bcm/__main__.py

   The system shall enable users to implement ECU behavioral models
   in Python that subscribe to input signals, execute domain logic
   (including state machines), and publish output signals via the
   BrokerClient API.

.. feat:: State Machine Logic
   :id: FEAT_STATE_MACHINE
   :status: reviewed
   :source_doc: remotive_car/models/bcm/python/bcm/state_machines/turn_signals.py

   Behavioral models shall support hierarchical state machines
   for managing complex signal-processing logic such as turn signal
   arbitration, beam control, and gear state tracking.
