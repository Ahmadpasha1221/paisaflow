import QtQuick 2.15

Rectangle {
    id: root

    property string title: ""
    property string amount: "₹0.00"
    property string subtitle: ""
    property string iconName: "wallet"
    property color accentColor: themeEngine.primaryAccent
    property color amountColor: themeEngine.primaryText

    implicitHeight: 120
    implicitWidth: 260
    radius: 12
    color: themeEngine.primarySurface
    border.color: themeEngine.divider
    border.width: 1

    Behavior on color {
        ColorAnimation { duration: 150 }
    }

    Column {
        anchors.fill: parent
        anchors.margins: 18
        spacing: 8

        Row {
            width: parent.width
            spacing: 8

            Text {
                text: root.title
                color: themeEngine.secondaryText
                font.pixelSize: 13
                font.weight: Font.Medium
                font.family: "Segoe UI, Inter, sans-serif"
                width: parent.width - iconBox.width - 8
                elide: Text.ElideRight
            }

            Rectangle {
                id: iconBox
                width: 28
                height: 28
                radius: 6
                color: Qt.rgba(root.accentColor.r, root.accentColor.g, root.accentColor.b, 0.15)

                FlowIcon {
                    name: root.iconName
                    size: 16
                    color: root.accentColor
                    anchors.centerIn: parent
                }
            }
        }

        Text {
            text: root.amount
            color: root.amountColor
            font.pixelSize: 22
            font.weight: Font.DemiBold
            font.family: "Segoe UI, Inter, sans-serif"
            font.features: { "tnum": 1 }
        }

        Text {
            text: root.subtitle
            color: themeEngine.secondaryText
            font.pixelSize: 12
            font.family: "Segoe UI, Inter, sans-serif"
            visible: root.subtitle !== ""
        }
    }
}
