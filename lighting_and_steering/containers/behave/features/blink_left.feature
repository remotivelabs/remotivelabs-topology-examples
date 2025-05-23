Feature: Turn Signal Behavior

    Scenario Outline: Validate turn signal behavior
        Given the system is running
        When the SCCM indicates a <turn_direction> turn
        Then the left turn light <left_light_behavior>
        And the right turn light <right_light_behavior>

        Examples:
            | turn_direction | left_light_behavior | right_light_behavior |
            | left           | blinks              | remains off          |
            | right          | remains off         | blinks               |
            | none           | remains off         | remains off          |


    Scenario: Validate the left turn signal behavior
        Given the system is running
        When the SCCM indicates a left turn
        Then the left turn light blinks
        And the right turn light remains off

    Scenario: Validate the right turn signal behavior
        Given the system is running
        When the SCCM indicates a right turn
        Then the right turn light blinks
        And the left turn light remains off

    Scenario: Validate no signal is sent
        Given the system is running
        When the SCCM indicates a none turn
        Then the left turn light remains off
        And the right turn light remains off
