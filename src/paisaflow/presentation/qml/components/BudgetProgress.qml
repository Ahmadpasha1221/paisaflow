import QtQuick 2.15

Rectangle {
    id: root

    property string name: ""
    property string categoryName: ""
    property string personName: ""
    property string limit: "₹0.00"
    property string spent: "₹0.00"
    property string remaining: "₹0.00"
    property real utilization: 0.0
    property string statusLevel: "healthy"

    implicitHeight: 120
    implicitWidth: 340
    radius: 12
    color: themeEngine.primarySurface
    border.color: themeEngine.divider
    border.width: 1

    function getBarColor() {
        if (utilization >= 100) return themeEngine.negative;
        if (utilization >= 90) return themeEngine.negative;
        if (utilization >= 75) return themeEngine.warning;
        return themeEngine.positive;
    }

    Column {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 10

        Row {
            width: parent.width

            Column {
                width: parent.width - badge.width - 8
                spacing: 2

                Text {
                    text: root.name
                    color: themeEngine.primaryText
                    font.pixelSize: 15
                    font.weight: Font.DemiBold
                    font.family: "Segoe UI, Inter, sans-serif"
                    elide: Text.ElideRight
                    width: parent.width
                }

                Text {
                    text: root.categoryName + " • " + root.personName
                    color: themeEngine.secondaryText
                    font.pixelSize: 12
                    font.family: "Segoe UI, Inter, sans-serif"
                }
            }

            StatusBadge {
                id: badge
                text: root.utilization.toFixed(1) + "%"
                level: root.statusLevel
            }
        }

        // Progress Track
        Rectangle {
            width: parent.width
            height: 8
            radius: 4
            color: themeEngine.elevatedSurface

            Rectangle {
                width: Math.min(parent.width, parent.width * (root.utilization / 100.0))
                height: parent.height
                radius: 4
                color: root.getBarColor()

                Behavior on width {
                    NumberAnimation { duration: 250; easing.type: Easing.OutQuad }
                }
            }
        }

        Item {
            width: parent.width
            height: 18

            Text {
                text: "Spent: " + root.spent
                color: themeEngine.secondaryText
                font.pixelSize: 12
                font.family: "Segoe UI, Inter, sans-serif"
                font.features: { "tnum": 1 }
                anchors.left: parent.left
                anchors.verticalCenter: parent.verticalCenter
            }

            Text {
                text: "Limit: " + root.limit
                color: themeEngine.secondaryText
                font.pixelSize: 12
                font.family: "Segoe UI, Inter, sans-serif"
                font.features: { "tnum": 1 }
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
            }
        }
    }
}
