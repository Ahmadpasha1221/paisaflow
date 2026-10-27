import QtQuick 2.15
import QtQuick.Controls 2.15

Button {
    id: root

    property string iconName: ""
    property bool fullWidth: false

    implicitHeight: 40
    implicitWidth: fullWidth ? parent.width : (contentRow.implicitWidth + 28)

    background: Rectangle {
        radius: 8
        color: !root.enabled ? "transparent" : (root.down ? themeEngine.elevatedSurface : (root.hovered ? themeEngine.elevatedSurface : "transparent"))
        border.color: themeEngine.divider
        border.width: 1

        Behavior on color {
            ColorAnimation { duration: 120 }
        }
    }

    contentItem: Row {
        id: contentRow
        spacing: 8
        anchors.centerIn: parent

        FlowIcon {
            name: root.iconName
            size: 16
            color: root.enabled ? themeEngine.primaryText : themeEngine.secondaryText
            visible: root.iconName !== ""
            anchors.verticalCenter: parent.verticalCenter
        }

        Text {
            text: root.text
            color: root.enabled ? themeEngine.primaryText : themeEngine.secondaryText
            font.pixelSize: 14
            font.weight: Font.Medium
            font.family: "Segoe UI, Inter, sans-serif"
            anchors.verticalCenter: parent.verticalCenter
        }
    }
}
