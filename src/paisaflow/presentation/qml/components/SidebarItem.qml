import QtQuick 2.15

Rectangle {
    id: root

    property string pageId: ""
    property string label: ""
    property string iconName: "home"
    property bool isActive: false
    property bool collapsed: false
    signal clicked()

    width: parent.width
    height: 40
    radius: 8
    color: isActive ? (themeEngine.isDark ? "#283C31" : "#DDE5D9") : (mouseArea.containsMouse ? (themeEngine.isDark ? "#23332A" : "#E4ECE0") : "transparent")

    Behavior on color {
        ColorAnimation { duration: 100 }
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: root.clicked()
    }

    Row {
        anchors.fill: parent
        anchors.leftMargin: root.collapsed ? 0 : 12
        spacing: 12

        // Icon
        Item {
            width: root.collapsed ? parent.width : 20
            height: parent.height

            FlowIcon {
                name: root.iconName
                size: 18
                color: root.isActive ? themeEngine.primaryAccent : (mouseArea.containsMouse ? themeEngine.primaryText : themeEngine.secondaryText)
                anchors.centerIn: parent
            }
        }

        // Label
        Text {
            text: root.label
            color: root.isActive ? themeEngine.primaryText : (mouseArea.containsMouse ? themeEngine.primaryText : themeEngine.secondaryText)
            font.pixelSize: 13
            font.weight: root.isActive ? Font.DemiBold : Font.Medium
            font.family: "Segoe UI, Inter, sans-serif"
            anchors.verticalCenter: parent.verticalCenter
            visible: !root.collapsed
        }
    }

    // Active accent indicator pill
    Rectangle {
        width: 3
        height: 18
        radius: 1.5
        color: themeEngine.primaryAccent
        anchors.left: parent.left
        anchors.leftMargin: 2
        anchors.verticalCenter: parent.verticalCenter
        visible: root.isActive && !root.collapsed
    }
}
