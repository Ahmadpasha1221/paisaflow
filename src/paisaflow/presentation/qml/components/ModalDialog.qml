import QtQuick 2.15

Rectangle {
    id: root

    property string title: ""
    property bool open: false
    property real contentWidth: 460
    property alias content: bodyContainer.data
    signal closed()

    anchors.fill: parent
    color: Qt.rgba(0, 0, 0, 0.55)
    visible: opacity > 0
    opacity: open ? 1.0 : 0.0

    Behavior on opacity {
        NumberAnimation { duration: 150 }
    }

    // Intercept clicks on backdrop to dismiss
    MouseArea {
        anchors.fill: parent
        onClicked: root.closed()
    }

    // Modal Card
    Rectangle {
        id: card
        width: Math.min(parent.width - 32, root.contentWidth)
        implicitHeight: cardColumn.implicitHeight + 36
        radius: 12
        color: themeEngine.elevatedSurface
        border.color: themeEngine.divider
        border.width: 1
        anchors.centerIn: parent

        // Prevent click propagation through the card
        MouseArea {
            anchors.fill: parent
            onClicked: {}
        }

        Column {
            id: cardColumn
            anchors.fill: parent
            anchors.margins: 20
            spacing: 16

            Row {
                width: parent.width

                Text {
                    text: root.title
                    color: themeEngine.primaryText
                    font.pixelSize: 18
                    font.weight: Font.DemiBold
                    font.family: "Segoe UI, Inter, sans-serif"
                    width: parent.width - closeBtn.width
                    anchors.verticalCenter: parent.verticalCenter
                }

                IconButton {
                    id: closeBtn
                    iconName: "close"
                    iconSize: 16
                    anchors.verticalCenter: parent.verticalCenter
                    onClicked: root.closed()
                }
            }

            Rectangle {
                width: parent.width
                height: 1
                color: themeEngine.divider
            }

            Item {
                id: bodyContainer
                width: parent.width
                implicitHeight: children.length > 0 ? children[0].implicitHeight : 100
                height: implicitHeight
            }
        }
    }

    Keys.onEscapePressed: root.closed()
}
