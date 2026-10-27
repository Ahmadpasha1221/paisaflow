import QtQuick 2.15
import QtQuick.Controls 2.15

Button {
    id: root

    property string iconName: "plus"
    property real iconSize: 18
    property color iconColor: root.hovered ? themeEngine.primaryAccent : themeEngine.primaryText
    property color hoverColor: themeEngine.elevatedSurface

    implicitWidth: 36
    implicitHeight: 36

    background: Rectangle {
        radius: 8
        color: root.down ? themeEngine.elevatedSurface : (root.hovered ? root.hoverColor : "transparent")
        border.color: root.hovered ? themeEngine.divider : "transparent"
        border.width: 1

        Behavior on color {
            ColorAnimation { duration: 120 }
        }
    }

    contentItem: Item {
        FlowIcon {
            name: root.iconName
            size: root.iconSize
            color: root.iconColor
            anchors.centerIn: parent
        }
    }
}
