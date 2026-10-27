import QtQuick 2.15

// Animated grouped bar chart (two series per category), used for monthly
// income vs expenses. Bars grow on first paint and re-animate whenever the
// underlying data changes, e.g. after a transaction is deleted.
Item {
    id: root

    // Named bars rather than "data": Item.data is the default child list.
    property var bars: []
    property string labelRole: "shortMonth"
    property string titleRole: "month"
    property string primaryPaiseRole: "incomePaise"
    property string primaryTextRole: "income"
    property string secondaryPaiseRole: "expensesPaise"
    property string secondaryTextRole: "expenses"
    property string primaryLabel: "Income"
    property string secondaryLabel: "Expenses"
    property color primaryColor: themeEngine.positive
    property color secondaryColor: themeEngine.negative
    property real plotHeight: 180

    readonly property real gutter: 56
    readonly property real plotWidth: Math.max(0, width - gutter - 4)
    readonly property real plotTop: 30
    property int hovered: -1
    property bool ready: false

    implicitHeight: plotTop + plotHeight + 24

    function valueOf(entry, role) {
        if (!entry)
            return 0;
        var value = entry[role];
        return typeof value === "number" ? value : 0;
    }

    function maxPaise() {
        var max = 0;
        for (var i = 0; i < bars.length; i++) {
            max = Math.max(max,
                           valueOf(bars[i], primaryPaiseRole),
                           valueOf(bars[i], secondaryPaiseRole));
        }
        return max;
    }

    function niceMax(value) {
        if (!(value > 0))
            return 100;
        var pow = Math.pow(10, Math.floor(Math.log(value) / Math.LN10));
        var n = value / pow;
        var step = n <= 1 ? 1 : n <= 2 ? 2 : n <= 5 ? 5 : 10;
        return step * pow;
    }

    function compact(paise) {
        var value = paise / 100;
        if (value >= 10000000) return "₹" + (value / 10000000).toFixed(1) + "Cr";
        if (value >= 100000) return "₹" + (value / 100000).toFixed(1) + "L";
        if (value >= 1000) return "₹" + (value / 1000).toFixed(1) + "k";
        return "₹" + Math.round(value);
    }

    readonly property real maxValue: niceMax(maxPaise())

    // Kick the grow-in animation one frame after the first layout so the bars
    // animate from zero instead of appearing already full height.
    Timer {
        interval: 60
        running: true
        onTriggered: root.ready = true
    }

    // Legend
    Row {
        id: legend
        anchors.left: parent.left
        anchors.top: parent.top
        height: 20
        spacing: 16

        Row {
            spacing: 6
            anchors.verticalCenter: parent.verticalCenter

            Rectangle {
                width: 9
                height: 9
                radius: 2
                color: root.primaryColor
                anchors.verticalCenter: parent.verticalCenter
            }

            Text {
                text: root.primaryLabel
                color: themeEngine.secondaryText
                font.pixelSize: 11
                font.family: "Segoe UI, Inter, sans-serif"
                anchors.verticalCenter: parent.verticalCenter
            }
        }

        Row {
            spacing: 6
            anchors.verticalCenter: parent.verticalCenter

            Rectangle {
                width: 9
                height: 9
                radius: 2
                color: root.secondaryColor
                anchors.verticalCenter: parent.verticalCenter
            }

            Text {
                text: root.secondaryLabel
                color: themeEngine.secondaryText
                font.pixelSize: 11
                font.family: "Segoe UI, Inter, sans-serif"
                anchors.verticalCenter: parent.verticalCenter
            }
        }
    }

    // Hover readout for exact figures
    Text {
        id: readout
        anchors.right: parent.right
        anchors.verticalCenter: legend.verticalCenter
        text: {
            var entry = root.hovered >= 0 ? root.bars[root.hovered] : null;
            if (!entry)
                return "Hover a month for exact figures";
            return entry[root.titleRole] + "  ·  "
                   + root.primaryLabel + " " + entry[root.primaryTextRole] + "  ·  "
                   + root.secondaryLabel + " " + entry[root.secondaryTextRole];
        }
        color: themeEngine.secondaryText
        font.pixelSize: 11
        font.weight: root.hovered >= 0 ? Font.Medium : Font.Normal
        font.family: "Segoe UI, Inter, sans-serif"
    }

    // Horizontal grid lines with compact axis labels
    Repeater {
        model: 5

        Item {
            width: root.width
            height: 1
            y: root.plotTop + root.plotHeight * index / 4

            Rectangle {
                x: root.gutter
                width: root.plotWidth
                height: 1
                color: themeEngine.divider
                opacity: index === 4 ? 0.9 : 0.5
            }

            Text {
                x: 0
                y: -7
                width: root.gutter - 10
                horizontalAlignment: Text.AlignRight
                text: root.compact(root.maxValue * (4 - index) / 4)
                color: themeEngine.secondaryText
                font.pixelSize: 10
                font.features: { "tnum": 1 }
                font.family: "Segoe UI, Inter, sans-serif"
            }
        }
    }

    Row {
        id: barRow
        x: root.gutter
        y: root.plotTop
        width: root.plotWidth
        height: root.plotHeight + 22

        Repeater {
            model: root.bars

            Item {
                id: column
                width: barRow.width / Math.max(1, root.bars.length)
                height: barRow.height

                property int columnIndex: index
                property var entry: modelData

                HoverHandler {
                    id: hover
                    onHoveredChanged: {
                        if (hovered)
                            root.hovered = column.columnIndex;
                        else if (root.hovered === column.columnIndex)
                            root.hovered = -1;
                    }
                }

                // Highlight band behind the hovered month
                Rectangle {
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.leftMargin: 4
                    anchors.rightMargin: 4
                    anchors.bottom: parent.bottom
                    anchors.bottomMargin: 22
                    height: parent.height - 22
                    radius: 6
                    color: hover.hovered ? Qt.rgba(1, 1, 1, themeEngine.isDark ? 0.05 : 0.5) : "transparent"

                    Behavior on color {
                        ColorAnimation { duration: 120 }
                    }
                }

                Rectangle {
                    width: Math.min(24, Math.max(6, column.width * 0.18))
                    height: root.valueOf(column.entry, root.primaryPaiseRole)
                            / root.maxValue * root.plotHeight * (root.ready ? 1 : 0)
                    x: column.width / 2 - width - 3
                    anchors.bottom: parent.bottom
                    anchors.bottomMargin: 22
                    radius: 4
                    color: root.primaryColor
                    opacity: root.hovered === -1 || root.hovered === column.columnIndex ? 1.0 : 0.45

                    Behavior on height {
                        NumberAnimation { duration: 480; easing.type: Easing.OutCubic }
                    }
                    Behavior on opacity {
                        NumberAnimation { duration: 140 }
                    }
                }

                Rectangle {
                    width: Math.min(24, Math.max(6, column.width * 0.18))
                    height: root.valueOf(column.entry, root.secondaryPaiseRole)
                            / root.maxValue * root.plotHeight * (root.ready ? 1 : 0)
                    x: column.width / 2 + 3
                    anchors.bottom: parent.bottom
                    anchors.bottomMargin: 22
                    radius: 4
                    color: root.secondaryColor
                    opacity: root.hovered === -1 || root.hovered === column.columnIndex ? 1.0 : 0.45

                    Behavior on height {
                        NumberAnimation { duration: 480; easing.type: Easing.OutCubic }
                    }
                    Behavior on opacity {
                        NumberAnimation { duration: 140 }
                    }
                }

                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.bottom: parent.bottom
                    text: column.entry ? column.entry[root.labelRole] : ""
                    color: root.hovered === column.columnIndex ? themeEngine.primaryText : themeEngine.secondaryText
                    font.pixelSize: 11
                    font.weight: root.hovered === column.columnIndex ? Font.DemiBold : Font.Normal
                    font.family: "Segoe UI, Inter, sans-serif"
                }
            }
        }
    }
}
