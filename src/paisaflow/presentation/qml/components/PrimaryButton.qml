import QtQuick 2.15
import QtQuick.Controls 2.15

Button {
    id: root

    property string iconName: ""
    property bool fullWidth: false

    implicitHeight: 40
    implicitWidth: fullWidth ? parent.width : (contentRow.implicitWidth + 32)

    background: Rectangle {
        radius: 8
        color: !root.enabled ? "#55665D" : (root.down ? themeEngine.primaryAccent : (root.hovered ? themeEngine.accentHover : themeEngine.primaryAccent))
        border.color: "transparent"

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
            color: themeEngine.accentButtonText
            visible: root.iconName !== ""
            anchors.verticalCenter: parent.verticalCenter
        }

        Text {
            text: root.text
            color: themeEngine.accentButtonText
            font.pixelSize: 14
            font.weight: Font.DemiBold
            font.family: "Segoe UI, Inter, sans-serif"
            anchors.verticalCenter: parent.verticalCenter
        }
    }
}
