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
    color: !textField.enabled ? themeEngine.disabledSurface
         : (textField.readOnly ? themeEngine.secondarySurface
         : (textField.hovered && !textField.activeFocus ? themeEngine.inputHoverSurface : themeEngine.inputSurface))
    border.color: hasError ? themeEngine.negative : (textField.activeFocus ? themeEngine.primaryAccent : themeEngine.divider)
    border.width: hasError || textField.activeFocus ? 1.5 : 1

    Behavior on border.color {
        ColorAnimation { duration: 120 }
    }

    Row {
        anchors.fill: parent
        anchors.leftMargin: 12
        anchors.rightMargin: 12
        spacing: 8

        TextInputField {
            id: textField
            width: Math.max(0, parent.width - 24)
            height: parent.height
            anchors.verticalCenter: parent.verticalCenter
            leftPadding: 4
            rightPadding: 8
            placeholderText: "YYYY-MM-DD"
            font.features: { "tnum": 1 }
            background: Item {}
        }
    }
}
