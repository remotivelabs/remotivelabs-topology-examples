// SPDX-License-Identifier: Apache-2.0
// Turn indicator arrow, lit green while the turn light is requested.
import QtQuick
import QtQuick.Shapes

Shape {
    id: arrow

    property real cx: 760
    property real cy: 140
    property real arrowWidth: 55
    property real arrowHeight: 30
    property bool pointsLeft: true
    property bool on: false
    required property QtObject theme

    readonly property real a: pointsLeft ? -1 : 1
    readonly property real o: arrowWidth / 2
    readonly property real s: arrowHeight / 2
    readonly property real c: arrowHeight * 0.22
    readonly property real l: arrowWidth * 0.35

    ShapePath {
        strokeColor: "transparent"
        fillColor: arrow.on ? arrow.theme.accentSuccess : arrow.theme.textMuted
        startX: arrow.cx + arrow.a * arrow.o; startY: arrow.cy
        PathLine { x: arrow.cx; y: arrow.cy - arrow.s }
        PathLine { x: arrow.cx; y: arrow.cy - arrow.c }
        PathLine { x: arrow.cx - arrow.a * arrow.l; y: arrow.cy - arrow.c }
        PathLine { x: arrow.cx - arrow.a * arrow.l; y: arrow.cy + arrow.c }
        PathLine { x: arrow.cx; y: arrow.cy + arrow.c }
        PathLine { x: arrow.cx; y: arrow.cy + arrow.s }
        PathLine { x: arrow.cx + arrow.a * arrow.o; y: arrow.cy }
    }
}
