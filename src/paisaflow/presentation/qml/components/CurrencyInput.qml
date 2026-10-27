import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    id: root

    property alias text: textField.text
    property alias placeholderText: textField.placeholderText
    property alias readOnly: textField.readOnly
    property bool hasError: false

    implicitHeight: 42
    implicitWidth: parent ? parent.width : 280
    radius: 8
    color: themeEngine.isDark ? "#1F2E26" : "#FFFFFF"
    border.color: hasError ? themeEngine.negative : (textField.activeFocus ? themeEngine.primaryAccent : themeEngine.divider)
    border.width: textField.activeFocus ? 1.5 : 1

    Behavior on border.color {
        ColorAnimation { duration: 120 }
    }

    Row {
        anchors.fill: parent
        anchors.leftMargin: 12
        anchors.rightMargin: 12
        spacing: 8

        Text {
            text: "₹"
            color: themeEngine.primaryAccent
            font.pixelSize: 16
            font.weight: Font.DemiBold
            anchors.verticalCenter: parent.verticalCenter
        }

        TextField {
            id: textField
            width: parent.width - 24
            height: parent.height
            anchors.verticalCenter: parent.verticalCenter
            verticalAlignment: TextInput.AlignVCenter
            color: themeEngine.primaryText
            placeholderTextColor: themeEngine.secondaryText
            font.pixelSize: 15
            font.family: "Segoe UI, Inter, sans-serif"
            font.features: { "tnum": 1 }
            inputMethodHints: Qt.ImhFormattedNumbersOnly
            background: Item {}
            selectByMouse: true
        }
    }
}
