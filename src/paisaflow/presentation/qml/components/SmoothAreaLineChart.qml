import QtQuick 2.15

// Reusable single-series trend chart. Financial values and formatted text come
// from Python; this component only maps those values to pixels for drawing.
Item {
    id: root

    // Each point supplies { month, shortMonth, netPaise, net } from the ViewModel.
    // null/missing values create gaps instead of drawing a misleading bridge.
    property var points: []
    property string valueRole: "netPaise"
    property string labelRole: "shortMonth"
    property string titleRole: "month"
    property string formattedValueRole: "net"
    property string seriesLabel: "Net cash flow"
    property color lineColor: themeEngine.primaryAccent
    property color surfaceColor: themeEngine.primarySurface
    property int selectedIndex: -1
    property bool keyboardSelection: false
    property int geometryRevision: 0

    readonly property real plotLeft: 62
    readonly property real plotRight: 14
    readonly property real plotTop: 38
    readonly property real plotBottom: 34
    readonly property real plotWidth: Math.max(0, width - plotLeft - plotRight)
    readonly property real plotHeight: Math.max(0, height - plotTop - plotBottom)
    readonly property real dataMinimumPaise: dataRange().minimum
    readonly property real dataMaximumPaise: dataRange().maximum
    readonly property real domainMinimumPaise: domainRange().minimum
    readonly property real domainMaximumPaise: domainRange().maximum
    readonly property int curveSegmentCount: countCurveSegments()
    readonly property var mappedPoints: makeMappedPoints()
    readonly property string selectedText: {
        if (selectedIndex < 0 || selectedIndex >= points.length || !isValidPoint(selectedIndex))
            return "Hover, select, or focus a month to inspect its value";
        var entry = points[selectedIndex];
        return entry[titleRole] + "  ·  " + seriesLabel + "  " + entry[formattedValueRole];
    }
    readonly property string accessibleSummary: {
        if (selectedIndex >= 0 && selectedIndex < points.length && isValidPoint(selectedIndex))
            return selectedText;
        return seriesLabel + ", " + points.length + " monthly points. " + selectedText;
    }

    implicitHeight: 220
    clip: true
    activeFocusOnTab: true
    Accessible.name: accessibleSummary
    Accessible.description: "Use the left and right arrow keys to inspect actual monthly values."

    function valueAt(index) {
        if (index < 0 || index >= points.length || !points[index])
            return null;
        var value = points[index][valueRole];
        return typeof value === "number" && isFinite(value) ? value : null;
    }

    function isValidPoint(index) {
        return valueAt(index) !== null;
    }

    function dataRange() {
        var minimum = 0;
        var maximum = 0;
        var found = false;
        for (var i = 0; i < points.length; i++) {
            var value = valueAt(i);
            if (value === null)
                continue;
            if (!found) {
                minimum = value;
                maximum = value;
                found = true;
            } else {
                minimum = Math.min(minimum, value);
                maximum = Math.max(maximum, value);
            }
        }
        return { minimum: found ? minimum : 0, maximum: found ? maximum : 0 };
    }

    // Include zero so positive and negative cash flow share a truthful baseline.
    function domainRange() {
        var data = dataRange();
        var minimum = Math.min(0, data.minimum);
        var maximum = Math.max(0, data.maximum);
        var span = maximum - minimum;
        if (span === 0)
            return { minimum: 0, maximum: 10000 }; // Empty/all-zero axis: ₹0 to ₹100.
        var padding = span * 0.08;
        return {
            minimum: minimum < 0 ? minimum - padding : 0,
            maximum: maximum > 0 ? maximum + padding : 0
        };
    }

    function pointX(index) {
        if (points.length <= 1)
            return plotLeft + plotWidth / 2;
        return plotLeft + plotWidth * index / (points.length - 1);
    }

    function pointY(valuePaise) {
        var domain = domainRange();
        var range = domain.maximum - domain.minimum;
        if (range <= 0 || plotHeight <= 0)
            return plotTop + plotHeight;
        return plotTop + (domain.maximum - valuePaise) / range * plotHeight;
    }

    function makeMappedPoints() {
        var result = [];
        for (var i = 0; i < points.length; i++) {
            var value = valueAt(i);
            if (value === null)
                continue;
            result.push({ index: i, x: pointX(i), y: pointY(value), valuePaise: value });
        }
        return result;
    }

    function countCurveSegments() {
        var count = 0;
        var previousValid = false;
        for (var i = 0; i < points.length; i++) {
            var valid = isValidPoint(i);
            if (valid && previousValid)
                count++;
            previousValid = valid;
        }
        return count;
    }

    function contiguousSegments() {
        var segments = [];
        var current = [];
        for (var i = 0; i < points.length; i++) {
            var value = valueAt(i);
            if (value === null) {
                if (current.length)
                    segments.push(current);
                current = [];
                continue;
            }
            current.push({ x: pointX(i), y: pointY(value), value: value });
        }
        if (current.length)
            segments.push(current);
        return segments;
    }

    // Fritsch-Carlson monotone cubic tangents avoid overshooting real values.
    function monotoneTangents(segment) {
        var n = segment.length;
        var slopes = [];
        var tangents = [];
        if (n < 2)
            return tangents;
        for (var i = 0; i < n - 1; i++) {
            var dx = segment[i + 1].x - segment[i].x;
            slopes.push(dx > 0 ? (segment[i + 1].y - segment[i].y) / dx : 0);
        }
        tangents[0] = slopes[0];
        tangents[n - 1] = slopes[n - 2];
        for (var j = 1; j < n - 1; j++) {
            if (slopes[j - 1] * slopes[j] <= 0) {
                tangents[j] = 0;
            } else {
                var leftWidth = segment[j].x - segment[j - 1].x;
                var rightWidth = segment[j + 1].x - segment[j].x;
                var w1 = 2 * rightWidth + leftWidth;
                var w2 = rightWidth + 2 * leftWidth;
                tangents[j] = (w1 + w2) / (w1 / slopes[j - 1] + w2 / slopes[j]);
            }
        }
        for (var k = 0; k < n - 1; k++) {
            if (slopes[k] === 0) {
                tangents[k] = 0;
                tangents[k + 1] = 0;
            } else {
                var a = tangents[k] / slopes[k];
                var b = tangents[k + 1] / slopes[k];
                var magnitude = a * a + b * b;
                if (magnitude > 9) {
                    var scale = 3 / Math.sqrt(magnitude);
                    tangents[k] = scale * a * slopes[k];
                    tangents[k + 1] = scale * b * slopes[k];
                }
            }
        }
        return tangents;
    }

    function areaGradient(ctx, segment) {
        var baseline = pointY(0);
        var minimumY = segment[0].y;
        var maximumY = segment[0].y;
        for (var i = 1; i < segment.length; i++) {
            minimumY = Math.min(minimumY, segment[i].y);
            maximumY = Math.max(maximumY, segment[i].y);
        }

        var gradient;
        if (minimumY < baseline && maximumY > baseline) {
            // Net cash flow crosses zero: fade toward the zero line from either side.
            gradient = ctx.createLinearGradient(0, minimumY, 0, maximumY);
            var baselinePosition = (baseline - minimumY) / (maximumY - minimumY);
            gradient.addColorStop(0, Qt.rgba(lineColor.r, lineColor.g, lineColor.b, 0.18));
            gradient.addColorStop(baselinePosition, Qt.rgba(lineColor.r, lineColor.g, lineColor.b, 0.015));
            gradient.addColorStop(1, Qt.rgba(lineColor.r, lineColor.g, lineColor.b, 0.18));
        } else {
            // For one-sign segments, put the strongest fill at the line and fade to zero.
            var lineEdge = maximumY < baseline ? maximumY : minimumY;
            gradient = ctx.createLinearGradient(0, lineEdge, 0, baseline);
            gradient.addColorStop(0, Qt.rgba(lineColor.r, lineColor.g, lineColor.b, 0.18));
            gradient.addColorStop(1, Qt.rgba(lineColor.r, lineColor.g, lineColor.b, 0.015));
        }
        return gradient;
    }

    function drawCurve(ctx, segment, closeToBaseline) {
        if (!segment.length)
            return;
        var tangents = monotoneTangents(segment);
        ctx.moveTo(segment[0].x, segment[0].y);
        for (var i = 0; i < segment.length - 1; i++) {
            var dx = segment[i + 1].x - segment[i].x;
            ctx.bezierCurveTo(
                segment[i].x + dx / 3,
                segment[i].y + tangents[i] * dx / 3,
                segment[i + 1].x - dx / 3,
                segment[i + 1].y - tangents[i + 1] * dx / 3,
                segment[i + 1].x,
                segment[i + 1].y
            );
        }
        if (closeToBaseline) {
            var baseline = pointY(0);
            ctx.lineTo(segment[segment.length - 1].x, baseline);
            ctx.lineTo(segment[0].x, baseline);
            ctx.closePath();
        }
    }

    function compactCurrency(paise) {
        var value = paise / 100;
        var sign = value < 0 ? "-" : "";
        value = Math.abs(value);
        if (value >= 10000000) return sign + "₹" + (value / 10000000).toFixed(1) + "Cr";
        if (value >= 100000) return sign + "₹" + (value / 100000).toFixed(1) + "L";
        if (value >= 1000) return sign + "₹" + (value / 1000).toFixed(1) + "k";
        return sign + "₹" + Math.round(value);
    }

    function selectAt(x) {
        if (!points.length || plotWidth <= 0) {
            selectedIndex = -1;
            return;
        }
        selectedIndex = Math.max(0, Math.min(points.length - 1,
                                             Math.round((x - plotLeft) / plotWidth * (points.length - 1))));
        keyboardSelection = false;
    }

    onPointsChanged: {
        if (selectedIndex >= points.length)
            selectedIndex = -1;
        canvas.requestPaint();
    }
    onWidthChanged: canvas.requestPaint()
    onHeightChanged: canvas.requestPaint()
    onLineColorChanged: canvas.requestPaint()
    onPlotHeightChanged: canvas.requestPaint()
    onPlotWidthChanged: canvas.requestPaint()
    onPlotLeftChanged: canvas.requestPaint()
    onPlotTopChanged: canvas.requestPaint()
    onPlotRightChanged: canvas.requestPaint()
    onPlotBottomChanged: canvas.requestPaint()

    // Keep a selection while the pointer moves from the plot onto the readout,
    // month labels, or markers; only clear it after leaving the whole chart.
    HoverHandler {
        id: chartHover
        onHoveredChanged: {
            if (!hovered && !root.keyboardSelection)
                root.selectedIndex = -1;
        }
    }

    Keys.onLeftPressed: function(event) {
        keyboardSelection = true;
        if (points.length > 0)
            selectedIndex = Math.max(0, selectedIndex < 0 ? points.length - 1 : selectedIndex - 1);
        event.accepted = true;
    }
    Keys.onRightPressed: function(event) {
        keyboardSelection = true;
        if (points.length > 0)
            selectedIndex = Math.min(points.length - 1, selectedIndex < 0 ? 0 : selectedIndex + 1);
        event.accepted = true;
    }
    Keys.onEscapePressed: function(event) {
        keyboardSelection = false;
        selectedIndex = -1;
        event.accepted = true;
    }

    Canvas {
        id: canvas
        anchors.fill: parent
        renderTarget: Canvas.Image
        renderStrategy: Canvas.Immediate

        onPaint: {
            var ctx = getContext("2d");
            ctx.clearRect(0, 0, width, height);
            if (root.plotWidth <= 0 || root.plotHeight <= 0)
                return;

            // Currency grid and zero baseline.
            var domain = root.domainRange();
            for (var tick = 0; tick <= 4; tick++) {
                var y = root.plotTop + root.plotHeight * tick / 4;
                ctx.beginPath();
                ctx.moveTo(root.plotLeft, y);
                ctx.lineTo(root.width - root.plotRight, y);
                ctx.lineWidth = 1;
                ctx.strokeStyle = themeEngine.divider;
                ctx.globalAlpha = 0.65;
                ctx.stroke();
                ctx.globalAlpha = 1;
            }

            var zeroY = root.pointY(0);
            ctx.beginPath();
            ctx.moveTo(root.plotLeft, zeroY);
            ctx.lineTo(root.width - root.plotRight, zeroY);
            ctx.lineWidth = 1.4;
            ctx.strokeStyle = themeEngine.secondaryText;
            ctx.globalAlpha = 0.55;
            ctx.stroke();
            ctx.globalAlpha = 1;

            var segments = root.contiguousSegments();

            // Close each continuous segment to zero; null points create visible gaps.
            for (var s = 0; s < segments.length; s++) {
                if (segments[s].length < 2)
                    continue;
                ctx.beginPath();
                root.drawCurve(ctx, segments[s], true);
                ctx.fillStyle = root.areaGradient(ctx, segments[s]);
                ctx.fill();
            }

            for (var line = 0; line < segments.length; line++) {
                if (segments[line].length < 2)
                    continue;
                ctx.beginPath();
                root.drawCurve(ctx, segments[line], false);
                ctx.lineWidth = 5;
                ctx.lineCap = "round";
                ctx.lineJoin = "round";
                ctx.strokeStyle = Qt.rgba(root.lineColor.r, root.lineColor.g, root.lineColor.b, 0.14);
                ctx.shadowColor = Qt.rgba(root.lineColor.r, root.lineColor.g, root.lineColor.b, 0.16);
                ctx.shadowBlur = 7;
                ctx.shadowOffsetY = 2;
                ctx.stroke();
                ctx.shadowBlur = 0;
                ctx.shadowOffsetY = 0;
                ctx.beginPath();
                root.drawCurve(ctx, segments[line], false);
                ctx.lineWidth = 2.5;
                ctx.strokeStyle = root.lineColor;
                ctx.stroke();
            }
        }
    }

    Repeater {
        model: 5
        Text {
            x: 0
            y: root.plotTop + root.plotHeight * index / 4 - height / 2
            width: root.plotLeft - 8
            horizontalAlignment: Text.AlignRight
            text: root.compactCurrency(root.domainMaximumPaise
                                       - (root.domainMaximumPaise - root.domainMinimumPaise) * index / 4)
            color: themeEngine.secondaryText
            font.pixelSize: 10
            font.features: { "tnum": 1 }
            font.family: "Segoe UI, Inter, sans-serif"
        }
    }

    Repeater {
        model: root.points
        delegate: Item {
            id: pointDelegate
            property int pointIndex: index
            property var entry: modelData
            property real pointValue: root.valueAt(pointIndex)
            property bool valid: root.isValidPoint(pointIndex)
            x: root.pointX(pointIndex) - marker.width / 2
            y: root.pointY(pointValue) - marker.height / 2
            width: marker.width
            height: marker.height
            visible: valid
            z: 2

            Rectangle {
                id: marker
                width: root.selectedIndex === pointDelegate.pointIndex ? 12 : 8
                height: width
                radius: width / 2
                color: root.surfaceColor
                border.color: root.lineColor
                border.width: root.selectedIndex === pointDelegate.pointIndex ? 2.5 : 2
            }
        }
    }

    Repeater {
        model: root.points.length
        Text {
            property real labelWidth: Math.max(42, Math.min(58, root.plotWidth / Math.max(1, root.points.length)))
            width: labelWidth
            x: Math.max(root.plotLeft, Math.min(root.width - root.plotRight - width,
                                                root.pointX(index) - width / 2))
            y: root.plotTop + root.plotHeight + 8
            horizontalAlignment: Text.AlignHCenter
            text: root.points[index] ? root.points[index][root.labelRole] : ""
            color: root.selectedIndex === index ? themeEngine.primaryText : themeEngine.secondaryText
            font.pixelSize: 10
            font.weight: root.selectedIndex === index ? Font.DemiBold : Font.Normal
            font.family: "Segoe UI, Inter, sans-serif"
            elide: Text.ElideRight
        }
    }

    Text {
        x: root.plotLeft
        y: 2
        width: Math.max(0, root.width - root.plotLeft - root.plotRight)
        text: root.selectedText
        color: root.selectedIndex >= 0 ? themeEngine.primaryText : themeEngine.secondaryText
        font.pixelSize: 11
        font.weight: root.selectedIndex >= 0 ? Font.DemiBold : Font.Normal
        font.family: "Segoe UI, Inter, sans-serif"
        elide: Text.ElideRight
        horizontalAlignment: Text.AlignRight
    }

    MouseArea {
        x: root.plotLeft
        y: root.plotTop
        width: root.plotWidth
        height: root.plotHeight
        hoverEnabled: true
        acceptedButtons: Qt.LeftButton
        z: 3
        onEntered: root.selectAt(mouseX + root.plotLeft)
        onPositionChanged: root.selectAt(mouseX + root.plotLeft)
        onClicked: {
            root.selectAt(mouseX + root.plotLeft);
            root.keyboardSelection = true;
            root.forceActiveFocus();
        }
    }

    Connections {
        target: themeEngine
        function onThemeChanged() { canvas.requestPaint(); }
    }
}
