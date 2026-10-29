// SPDX-License-Identifier: Apache-2.0
// Horizontal power / regeneration bar growing from zero: amber for power
// drawn from the battery, green for regeneration.
import QtQuick

Item {
    id: bar

    property real x0: 1120
    property real x1: 1760
    property real barY: 200
    property real barHeight: 26
    property real minValue: -100
    property real maxValue: 200
    property real value: 0
    property bool valid: false
    required property QtObject theme

    readonly property real zeroX: x0 + (x1 - x0) * Math.max(0, Math.min(1, (0 - minValue) / (maxValue - minValue)))
    // Whole kW, so the bar repaints only when the shown value changes
    readonly property real clamped: Math.round(Math.max(minValue, Math.min(maxValue, value)))
    readonly property color valueColor: !valid ? theme.textMuted
                                       : clamped > 0.5 ? theme.accentWarning
                                       : clamped < -0.5 ? theme.accentSuccess
                                       : theme.textMuted
    readonly property real fillWidth: !valid ? 0
                                     : clamped >= 0 ? (x1 - zeroX) * (maxValue > 0 ? clamped / maxValue : 0)
                                     : (zeroX - x0) * (minValue < 0 ? -clamped / -minValue : 0)
    readonly property real fillX: clamped >= 0 ? zeroX : zeroX - fillWidth

    SvgText {
        ax: (bar.x0 + bar.x1) / 2; ay: 148
        anchor: "middle"
        size: 16
        letterSpacingEm: 0.08
        color: bar.theme.textTertiary
        text: "POWER / REGEN"
    }

    Rectangle {
        x: bar.x0; y: bar.barY
        width: bar.x1 - bar.x0; height: bar.barHeight
        radius: 3
        color: bar.theme.surfaceInactive
    }
    Rectangle {
        visible: bar.fillWidth > 0
        x: bar.fillX; y: bar.barY
        width: bar.fillWidth; height: bar.barHeight
        radius: 3
        color: bar.valueColor
    }
    Rectangle {
        x: bar.zeroX - 0.5; y: bar.barY - 9
        width: 1; height: bar.barHeight + 18
        color: bar.theme.surfaceInactive
    }

    SvgText {
        ax: bar.x0; ay: bar.barY - 10
        size: 15
        color: bar.theme.accentSuccess
        text: "- " + Math.abs(bar.minValue) + " kW"
    }
    SvgText {
        ax: bar.x1; ay: bar.barY - 10
        anchor: "end"
        size: 15
        color: bar.theme.accentWarning
        text: "+ " + bar.maxValue + " kW"
    }
    SvgText {
        ax: bar.zeroX; ay: bar.barY + bar.barHeight + 22
        anchor: "middle"
        size: 12
        color: bar.theme.textTertiary
        text: "0"
    }
    SvgText {
        ax: (bar.x0 + bar.x1) / 2; ay: 280
        anchor: "middle"
        size: 24
        color: bar.valueColor
        text: bar.valid ? Math.round(Math.abs(bar.clamped)) + " kW" : "-- kW"
    }
}
