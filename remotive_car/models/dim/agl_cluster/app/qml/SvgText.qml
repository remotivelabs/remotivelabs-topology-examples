// SPDX-License-Identifier: Apache-2.0
// Text positioned like an SVG <text> element: ax/ay is the anchor point on the
// baseline (or the vertical centre with central: true), not the top-left corner.
import QtQuick

Text {
    property real ax: 0
    property real ay: 0
    property string anchor: "start"   // start | middle | end
    property bool central: false      // dominant-baseline: central
    property real size: 22            // font pixel size
    property real letterSpacingEm: 0

    x: anchor === "middle" ? ax - width / 2 : anchor === "end" ? ax - width : ax
    y: central ? ay - height / 2 : ay - baselineOffset
    font.pixelSize: size
    font.letterSpacing: size * letterSpacingEm
    color: "#9ca3af"
}
