Feature: Hazard light Behavior

    Scenario: Hazard light overrides turn stalk
        Given the system is running

        When the turn stalk is turned left
        Then the left turn light blinks

        When the hazard light button is on
        Then both left and right turn light blinks

        When the turn stalk is reset
        Then both left and right turn light blinks

        When the hazard light button is off
        Then neither left nor right turn light blinks
