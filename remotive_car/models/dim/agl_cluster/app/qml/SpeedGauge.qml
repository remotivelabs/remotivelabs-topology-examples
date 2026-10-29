// SPDX-License-Identifier: Apache-2.0
// Half-circle speed gauge: a thin arc that fills from the left with the speed,
// tick marks with labels, and the speed as a large number in the centre.
import QtQuick
import QtQuick.Shapes

Item {
    id: gauge

    property real cx: 480
    property real cy: 410
    property real radius: 290
    property real maxValue: 240
    property var ticks: [0, 40, 80, 120, 160, 200, 240]
    property real value: 0
    property bool valid: false
    property string unit: "km/h"
    required property QtObject theme

    // Shown speed in whole km/h. The arc follows it in the same steps, so the
    // gauge repaints only when the displayed number changes: with software
    // rendering over VNC every repaint is a frame the viewer has to decode.
    readonly property int shown: valid ? Math.round(Math.max(0, Math.min(maxValue, value))) : 0
    readonly property real fraction: shown / maxValue

    // Arc endpoint for a fraction, going clockwise over the top from the left
    function arcX(f) { return cx - radius * Math.cos(Math.PI * f) }
    function arcY(f) { return cy - radius * Math.sin(Math.PI * f) }

    Shape {
        anchors.fill: parent
        ShapePath {
            strokeColor: gauge.theme.surfaceInactive
            strokeWidth: 6
            fillColor: "transparent"
            capStyle: ShapePath.RoundCap
            startX: gauge.cx - gauge.radius; startY: gauge.cy
            PathArc {
                x: gauge.cx + gauge.radius; y: gauge.cy
                radiusX: gauge.radius; radiusY: gauge.radius
                direction: PathArc.Clockwise
            }
        }
    }

    Shape {
        anchors.fill: parent
        visible: gauge.fraction > 0.002
        opacity: 0.95
        ShapePath {
            strokeColor: gauge.theme.textPrimary
            strokeWidth: 8
            fillColor: "transparent"
            capStyle: ShapePath.RoundCap
            startX: gauge.cx - gauge.radius; startY: gauge.cy
            PathArc {
                x: gauge.arcX(gauge.fraction); y: gauge.arcY(gauge.fraction)
                radiusX: gauge.radius; radiusY: gauge.radius
                direction: PathArc.Clockwise
            }
        }
    }

    Repeater {
        model: gauge.ticks
        Item {
            required property int index
            required property var modelData
            readonly property real angle: 180 - modelData / gauge.maxValue * 180
            readonly property real rad: angle * Math.PI / 180

            Item {
                x: gauge.cx; y: gauge.cy
                width: 0; height: 0
                rotation: -parent.angle
                Rectangle {
                    x: gauge.radius - 12; y: -1
                    width: 30; height: 2
                    radius: 1
                    color: gauge.theme.tickColor
                }
            }
            SvgText {
                ax: gauge.cx + (gauge.radius + 38) * Math.cos(parent.rad)
                ay: gauge.cy - (gauge.radius + 38) * Math.sin(parent.rad) + 6.3
                anchor: "middle"
                size: 18
                color: gauge.theme.textMuted
                text: parent.modelData
            }
        }
    }

    SvgText {
        ax: gauge.cx; ay: gauge.cy - 60
        anchor: "middle"; central: true
        size: 220
        letterSpacingEm: -0.03
        color: gauge.theme.textPrimary
        text: gauge.valid ? gauge.shown : "--"
    }
    SvgText {
        ax: gauge.cx; ay: gauge.cy + 70
        anchor: "middle"; central: true
        size: 22
        letterSpacingEm: 0.08
        color: gauge.theme.textSecondary
        text: gauge.unit
    }
}
