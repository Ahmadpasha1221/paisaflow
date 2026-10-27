import QtQuick 2.15

// Ranked horizontal bars with a label, amount and share. Used for category and
// per-person spending. Bars animate in on first paint and whenever the values
// change (for example after deleting a transaction).
Item {
    id: root

    // Each entry: { label, color, amount, amountPaise, percentage }
    property var items: []
    property int maxRows: 0 // 0 renders every entry
    property bool ready: false

    implicitHeight: contentColumn.implicitHeight
    width: parent ? parent.width : 0

    readonly property real maxValue: {
        var max = 0;
        for (var i = 0; i < items.length; i++)
            max = Math.max(max, items[i].amountPaise || 0);
        return max;
    }

    Timer {
        interval: 60
        running: true
        onTriggered: root.ready = true
    }

    Column {
        id: contentColumn
        width: parent.width
        spacing: 12

        Repeater {
            model: root.maxRows > 0 ? root.items.slice(0, root.maxRows) : root.items

            Item {
                id: row
                width: contentColumn.width
                height: contentRow.implicitHeight + track.height + 5

                Column {
                    id: contentRow
                    width: parent.width
                    spacing: 5

                    Row {
                        width: parent.width
                        spacing: 10

                        Rectangle {
                            id: dot
                            width: 10
                            height: 10
                            radius: 5
                            color: modelData.color
                            anchors.verticalCenter: parent.verticalCenter
                        }

                        Text {
                            text: modelData.label
                            color: themeEngine.primaryText
                            font.pixelSize: 13
                            font.weight: Font.Medium
                            font.family: "Segoe UI, Inter, sans-serif"
                            elide: Text.ElideRight
                            width: Math.max(0, parent.width - dot.width - amountText.width - 2 * parent.spacing)
                            anchors.verticalCenter: parent.verticalCenter
                        }

                        Text {
                            id: amountText
                            text: modelData.amount + "  ·  " + modelData.percentage.toFixed(1) + "%"
                            color: themeEngine.secondaryText
                            font.pixelSize: 12
                            font.features: { "tnum": 1 }
                            font.family: "Segoe UI, Inter, sans-serif"
                            anchors.verticalCenter: parent.verticalCenter
                        }
                    }
                }

                Rectangle {
                    id: track
                    width: parent.width
                    height: 8
                    radius: 4
                    y: contentRow.height + 5
                    color: themeEngine.secondarySurface

                    Rectangle {
                        width: root.maxValue > 0
                               ? track.width * (modelData.amountPaise / root.maxValue) * (root.ready ? 1 : 0)
                               : 0
                        height: parent.height
                        radius: 4
                        color: modelData.color

                        Behavior on width {
                            NumberAnimation { duration: 520; easing.type: Easing.OutCubic }
                        }
                    }
                }
            }
        }
    }
}
