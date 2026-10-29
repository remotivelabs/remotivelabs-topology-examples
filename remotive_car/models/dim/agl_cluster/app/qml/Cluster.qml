// SPDX-License-Identifier: Apache-2.0
//
// RemotiveCar instrument cluster. Same layout and palette as the instrument
// cluster of the RemotiveLabs 3D car, driven by the CanSignals context
// property ("Can") that reads the vehicle buses over SocketCAN.
import QtQuick
import QtQuick.Shapes

Window {
    id: root
    width: 1920
    height: 720
    visible: true
    flags: Qt.FramelessWindowHint
    color: theme.bg

    // The Qt VNC platform plugin sends its native BGRX pixels to every client
    // regardless of the pixel format the client asked for (qvncclient.cpp,
    // pixelConversionNeeded() does no conversion for 32 bpp screens), while
    // noVNC reads RGBX. Paint with red and blue swapped on that platform so the
    // browser shows the intended colours.
    readonly property bool swapRedBlue: Qt.platform.pluginName === "vnc"
    function c(hex) {
        const col = Qt.color(hex)
        return swapRedBlue ? Qt.rgba(col.b, col.g, col.r, col.a) : col
    }

    readonly property QtObject theme: QtObject {
        readonly property color bg: root.c("#0a0a0a")
        readonly property color surfaceInactive: root.c("#1f2937")
        readonly property color textPrimary: root.c("#ffffff")
        readonly property color textSecondary: root.c("#9ca3af")
        readonly property color textTertiary: root.c("#6b7280")
        readonly property color textMuted: root.c("#4b5563")
        readonly property color tickColor: root.c("#2a3341")
        readonly property color accentSuccess: root.c("#22c55e")
        readonly property color accentWarning: root.c("#f59e0b")
        readonly property color accentDanger: root.c("#ef4444")
        readonly property color accentUnavailable: root.c("#c9a227")
        readonly property color accentError: root.c("#c0392b")
    }

    // CanSignals.State
    readonly property int stateOk: 0
    readonly property int stateSna: 2
    readonly property int stateError: 3

    // Clock, top left
    SvgText {
        id: clock
        ax: 30; ay: 38
        color: theme.textSecondary
        text: Qt.formatTime(new Date(), "HH:mm")
        Timer {
            interval: 30000; running: true; repeat: true
            onTriggered: clock.text = Qt.formatTime(new Date(), "HH:mm")
        }
    }

    // Outside temperature, top right (no sender on the buses yet)
    SvgText {
        ax: 1890; ay: 38
        anchor: "end"
        color: theme.textSecondary
        text: "-- °C"
    }

    // Cruise control, top centre
    Rectangle {
        x: 920; y: 8
        width: 80; height: 44
        radius: 22
        color: "transparent"
        border.color: theme.textMuted
        border.width: 1
    }
    SvgText {
        ax: 960; ay: 36
        anchor: "middle"
        size: 18
        letterSpacingEm: 0.08
        color: theme.textMuted
        text: "SET"
    }

    TurnArrow { cx: 760; cy: 140; pointsLeft: true; on: Can.leftTurn; theme: root.theme }
    TurnArrow { cx: 1160; cy: 140; pointsLeft: false; on: Can.rightTurn; theme: root.theme }

    SpeedGauge {
        anchors.fill: parent
        theme: root.theme
        value: Can.speedKph
        valid: Can.speedState === stateOk
    }

    // Gear strip
    Repeater {
        model: ["P", "R", "N", "D"]
        SvgText {
            required property int index
            required property string modelData
            readonly property bool current: modelData === Can.gear
            ax: 960 + (index - 1.5) * 40; ay: 290
            anchor: "middle"
            size: 34
            font.weight: current ? Font.Medium : Font.Normal
            color: current ? theme.textPrimary : theme.textMuted
            text: modelData
        }
    }

    // Engine lamp: gold while a signal reports SNA, red while one reports Error
    Shape {
        visible: Can.lampState !== stateOk
        x: 960 - 16 * 1.9; y: 345
        width: 32; height: 24
        scale: 1.9
        transformOrigin: Item.TopLeft
        ShapePath {
            strokeColor: "transparent"
            fillColor: Can.lampState === stateError ? theme.accentError : theme.accentUnavailable
            PathSvg { path: "M 11 2 H 19 V 5 H 22 L 25 8 H 28 V 6 H 31 V 18 H 28 V 16 H 25 L 22 19 H 19 V 22 H 13 V 19 H 9 L 6 16 H 3 V 9 H 6 L 9 6 H 11 Z" }
        }
    }

    PowerBar {
        anchors.fill: parent
        theme: root.theme
        value: Can.motorPowerKw
        valid: Can.motorPowerState === stateOk
    }

    BatteryGauge {
        anchors.fill: parent
        theme: root.theme
        soc: Can.stateOfCharge
        valid: Can.stateOfChargeState === stateOk
    }

    // Bottom row
    SvgText {
        ax: 480; ay: 680
        anchor: "middle"
        color: theme.textMuted
        text: "IGN OFF"
    }
    Repeater {
        model: ["LOW", "BELT", "ABS", "P", "AIR", "TPMS", "FOG"]
        SvgText {
            required property int index
            required property string modelData
            ax: 960 + (index - 3) * 120; ay: 685
            anchor: "middle"
            size: 13
            color: theme.textMuted
            text: modelData
        }
    }
}
