import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    id: root

    property alias text: textField.text
    property alias placeholderText: textField.placeholderText
    property alias readOnly: textField.readOnly
    signal searchSubmitted(string query)

    implicitHeight: 42
    implicitWidth: 260
    radius: 8
    color: !textField.enabled ? themeEngine.disabledSurface
         : (textField.readOnly ? themeEngine.secondarySurface
         : (textField.hovered && !textField.activeFocus ? themeEngine.inputHoverSurface : themeEngine.inputSurface))
    border.color: textField.activeFocus ? themeEngine.primaryAccent : themeEngine.divider
    border.width: textField.activeFocus ? 1.5 : 1

    Behavior on border.color {
        ColorAnimation { duration: 120 }
    }

    Row {
        anchors.fill: parent
        anchors.leftMargin: 10
        anchors.rightMargin: 10
        spacing: 8

        FlowIcon {
            name: "search"
            size: 16
            color: themeEngine.secondaryText
            anchors.verticalCenter: parent.verticalCenter
        }

        TextInputField {
            id: textField
            width: Math.max(0, parent.width - 48)
            height: parent.height
            anchors.verticalCenter: parent.verticalCenter
            leftPadding: 2
            rightPadding: 4
            placeholderText: "Search transactions..."
            font.pixelSize: 13
            background: Item {}
            onAccepted: root.searchSubmitted(textField.text)
        }

        IconButton {
            iconName: "close"
            iconSize: 14
            implicitWidth: 20
            implicitHeight: 20
            anchors.verticalCenter: parent.verticalCenter
            visible: textField.text !== ""
            onClicked: {
                textField.text = "";
                root.searchSubmitted("");
            }
        }
    }
}
