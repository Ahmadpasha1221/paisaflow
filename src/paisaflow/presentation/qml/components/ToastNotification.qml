import QtQuick 2.15

Rectangle {
    id: root

    property string message: ""
    property bool isError: false
    property bool showing: false

    function show(msg, error) {
        message = msg;
        isError = error;
        showing = true;
        dismissTimer.restart();
    }

    function hide() {
        showing = false;
    }

    Timer {
        id: dismissTimer
        interval: 3200
        onTriggered: root.hide()
    }

    width: Math.min(parent ? parent.width - 32 : 360, 420)
    height: 48
    radius: 10
    color: themeEngine.elevatedSurface
    border.color: isError ? themeEngine.negative : themeEngine.primaryAccent
    border.width: 1.5

    y: showing ? 20 : -60
    opacity: showing ? 1.0 : 0.0
    visible: opacity > 0

    Behavior on y {
        NumberAnimation { duration: 200; easing.type: Easing.OutQuad }
    }
    Behavior on opacity {
        NumberAnimation { duration: 200 }
    }

    Row {
        anchors.fill: parent
        anchors.leftMargin: 16
        anchors.rightMargin: 12
        spacing: 12

        FlowIcon {
            name: root.isError ? "alert" : "check"
            size: 18
            color: root.isError ? themeEngine.negative : themeEngine.primaryAccent
            anchors.verticalCenter: parent.verticalCenter
        }

        Text {
            text: root.message
            color: themeEngine.primaryText
            font.pixelSize: 13
            font.family: "Segoe UI, Inter, sans-serif"
            width: parent.width - 48
            elide: Text.ElideRight
            anchors.verticalCenter: parent.verticalCenter
        }

        IconButton {
            iconName: "close"
            iconSize: 14
            implicitWidth: 24
            implicitHeight: 24
            anchors.verticalCenter: parent.verticalCenter
            onClicked: root.hide()
        }
    }
}
