Testing
=======

.. feat:: Scenario-Based Testing
   :id: FEAT_SCENARIO_TESTING
   :status: reviewed
   :source_doc: remotive_car/tests/behave/features/hazard_light.feature

   The system shall support scenario-based testing using Gherkin
   feature files executed by Behave, enabling natural-language
   specification of vehicle behavior verification scenarios.

.. feat:: Automated Integration Testing
   :id: FEAT_INTEGRATION_TESTING
   :status: reviewed
   :source_doc: remotive_car/tests/pytest/test_simulate_driver.py

   The system shall support automated integration tests using
   pytest that exercise full signal chains across ECU models
   within a running topology instance.
