// SPDX-License-Identifier: Apache-2.0
// Battery symbol with five bars, state of charge in percent and the
// estimated range next to it.
import QtQuick

Item {
    id: battery

    property real bx: 1120
    property real by: 424
    property real soc: 0            // percent
    property bool valid: false
    property real kmPerPercent: 5.5
    required property QtObject theme

    readonly property real level: valid ? Math.max(0, Math.min(100, soc)) : 0
    readonly property color textColor: valid ? theme.textPrimary : theme.textMuted

    Rectangle {
        x: battery.bx; y: battery.by
        width: 150; height: 68
        radius: 5
        color: "transparent"
        border.color: battery.theme.textMuted
        border.width: 1
    }
    Rectangle {
        x: battery.bx + 150; y: battery.by + 16
        width: 10; height: 38
        color: battery.theme.textMuted
    }
    Repeater {
        model: 5
        Rectangle {
            required property int index
            x: battery.bx + 6 + index * 28; y: battery.by + 6
            width: 26; height: 56
            radius: 2
            color: battery.valid && battery.level >= (index + 1) * 20 - 10
                   ? (battery.level <= 15 ? battery.theme.accentDanger
                      : battery.level <= 30 ? battery.theme.accentWarning
                      : battery.theme.accentSuccess)
                   : battery.theme.surfaceInactive
        }
    }

    SvgText {
        ax: battery.bx + 170; ay: battery.by + 34
        central: true
        size: 48
        color: battery.textColor
        text: battery.valid ? Math.round(battery.level) + " %" : "-- %"
    }

    Rectangle {
        x: battery.bx + 310; y: battery.by + 6
        width: 1; height: 56
        color: battery.theme.surfaceInactive
    }
    SvgText {
        ax: battery.bx + 335; ay: battery.by + 6
        central: true
        size: 16
        letterSpacingEm: 0.08
        color: battery.theme.textTertiary
        text: "RANGE"
    }
    SvgText {
        ax: battery.bx + 335; ay: battery.by + 34
        central: true
        size: 40
        color: battery.textColor
        text: battery.valid ? Math.round(battery.level * battery.kmPerPercent) : "---"
    }
    SvgText {
        ax: battery.bx + 450; ay: battery.by + 34
        central: true
        size: 20
        color: battery.theme.textSecondary
        text: "km"
    }
}
