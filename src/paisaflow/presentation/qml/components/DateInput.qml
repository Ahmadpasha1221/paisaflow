import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    id: root

    property alias text: textField.text
    property alias placeholderText: textField.placeholderText

    implicitHeight: 42
    implicitWidth: parent ? parent.width : 280
    radius: 8
    color: themeEngine.isDark ? "#1F2E26" : "#FFFFFF"
    border.color: textField.activeFocus ? themeEngine.primaryAccent : themeEngine.divider
    border.width: textField.activeFocus ? 1.5 : 1

    Behavior on border.color {
        ColorAnimation { duration: 120 }
    }

    Row {
        anchors.fill: parent
        anchors.leftMargin: 12
        anchors.rightMargin: 12
        spacing: 8

        TextField {
            id: textField
            width: parent.width - 24
            height: parent.height
            anchors.verticalCenter: parent.verticalCenter
            verticalAlignment: TextInput.AlignVCenter
            color: themeEngine.primaryText
            placeholderTextColor: themeEngine.secondaryText
            placeholderText: "YYYY-MM-DD"
            font.pixelSize: 14
            font.family: "Segoe UI, Inter, sans-serif"
            font.features: { "tnum": 1 }
            background: Item {}
            selectByMouse: true
        }
    }
}
