import QtQuick 2.15
import QtQuick.Controls 2.15

TextField {
    id: root

    property bool hasError: false

    implicitHeight: 42
    implicitWidth: parent ? parent.width : 280
    leftPadding: 12
    rightPadding: 12
    topPadding: 4
    bottomPadding: 4
    verticalAlignment: TextInput.AlignVCenter
    selectByMouse: true
    hoverEnabled: true
    activeFocusOnTab: activeFocus
    color: enabled ? themeEngine.primaryText : themeEngine.secondaryText
    placeholderTextColor: themeEngine.secondaryText
    selectionColor: themeEngine.primaryAccent
    selectedTextColor: themeEngine.accentButtonText
    cursorDelegate: Rectangle {
        width: 1
        color: themeEngine.primaryAccent
    }
    font.pixelSize: 14
    font.family: "Segoe UI, Inter, sans-serif"

    background: Rectangle {
        radius: 8
        color: !root.enabled ? themeEngine.disabledSurface
             : (root.readOnly ? themeEngine.secondarySurface
             : (root.hovered && !root.activeFocus ? themeEngine.inputHoverSurface : themeEngine.inputSurface))
        border.color: root.hasError ? themeEngine.negative
                    : (root.activeFocus ? themeEngine.primaryAccent : themeEngine.divider)
        border.width: root.hasError || root.activeFocus ? 1.5 : 1

        Behavior on border.color { ColorAnimation { duration: 120 } }
        Behavior on color { ColorAnimation { duration: 120 } }
    }
}
