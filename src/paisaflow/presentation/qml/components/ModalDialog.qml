import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    id: root

    property string title: ""
    property bool open: false
    property real contentWidth: 460
    property alias content: bodyColumn.data
    property alias footer: footerContainer.data
    signal closed()

    // Fixed chrome around the scrollable body:
    // top margin (20) + header (36) + gap (16) + divider (1) + gap (16) + bottom margin (20).
    readonly property real chromeHeight: 109
    readonly property real maxCardHeight: (parent ? parent.height : 600) - 32
    readonly property bool hasFooter: footerContainer.children.length > 0
    readonly property real footerHeight: hasFooter ? footerContainer.implicitHeight + 16 : 0

    anchors.fill: parent
    color: Qt.rgba(0, 0, 0, 0.55)
    visible: opacity > 0
    opacity: open ? 1.0 : 0.0
    z: 1000

    // Every close path (buttons, backdrop, Escape) ends here, so the dialog always hides itself.
    onClosed: root.open = false

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
        width: Math.min((parent ? parent.width : 800) - 32, root.contentWidth)
        height: Math.min(
                    root.chromeHeight + bodyColumn.implicitHeight + root.footerHeight,
                    root.maxCardHeight)
        radius: 12
        color: themeEngine.elevatedSurface
        border.color: themeEngine.divider
        border.width: 1
        anchors.centerIn: parent

        // Prevent click propagation through the card
        MouseArea {
            anchors.fill: parent
        }

        Item {
            id: header
            anchors.top: parent.top
            anchors.topMargin: 20
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.leftMargin: 20
            anchors.rightMargin: 20
            height: 36

            Text {
                text: root.title
                color: themeEngine.primaryText
                font.pixelSize: 18
                font.weight: Font.DemiBold
                font.family: "Segoe UI, Inter, sans-serif"
                elide: Text.ElideRight
                anchors.left: parent.left
                anchors.right: closeBtn.left
                anchors.rightMargin: 12
                anchors.verticalCenter: parent.verticalCenter
            }

            IconButton {
                id: closeBtn
                iconName: "close"
                iconSize: 16
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
                onClicked: root.closed()
            }
        }

        Rectangle {
            id: divider
            anchors.top: header.bottom
            anchors.topMargin: 16
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.leftMargin: 20
            anchors.rightMargin: 20
            height: 1
            color: themeEngine.divider
        }

        // Scrollable body. The action buttons live in the footer so they stay reachable
        // even when the form is taller than the window.
        Flickable {
            id: scroller
            anchors.top: divider.bottom
            anchors.topMargin: 16
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            anchors.leftMargin: 20
            anchors.rightMargin: 20
            anchors.bottomMargin: 20 + (root.hasFooter ? root.footerHeight : 0)
            contentWidth: width
            contentHeight: bodyColumn.implicitHeight
            clip: true
            boundsBehavior: Flickable.StopAtBounds

            ScrollBar.vertical: ScrollBar {
                policy: scroller.contentHeight > scroller.height ? ScrollBar.AsNeeded : ScrollBar.AlwaysOff
            }

            Column {
                id: bodyColumn
                width: scroller.width
                spacing: 14
            }
        }

        Item {
            id: footerContainer
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            anchors.leftMargin: 20
            anchors.rightMargin: 20
            anchors.bottomMargin: 20
            implicitHeight: children.length > 0 ? children[0].implicitHeight : 0
            height: implicitHeight
        }
    }

    Keys.onEscapePressed: root.closed()
}
