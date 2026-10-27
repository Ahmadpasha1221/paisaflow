import QtQuick 2.15

Column {
    id: root

    property string iconName: "wallet"
    property string title: "No entries yet"
    property string description: "Add your first transaction or account to get started."
    property string actionText: ""
    signal actionTriggered()

    width: parent.width
    spacing: 14
    anchors.centerIn: parent

    Rectangle {
        width: 64
        height: 64
        radius: 32
        color: Qt.rgba(themeEngine.primaryAccent.r, themeEngine.primaryAccent.g, themeEngine.primaryAccent.b, 0.12)
        anchors.horizontalCenter: parent.horizontalCenter

        FlowIcon {
            name: root.iconName
            size: 30
            color: themeEngine.primaryAccent
            anchors.centerIn: parent
        }
    }

    Text {
        text: root.title
        color: themeEngine.primaryText
        font.pixelSize: 18
        font.weight: Font.DemiBold
        font.family: "Segoe UI, Inter, sans-serif"
        anchors.horizontalCenter: parent.horizontalCenter
    }

    Text {
        text: root.description
        color: themeEngine.secondaryText
        font.pixelSize: 13
        font.family: "Segoe UI, Inter, sans-serif"
        anchors.horizontalCenter: parent.horizontalCenter
        horizontalAlignment: Text.AlignHCenter
        width: Math.min(parent.width - 40, 360)
        wrapMode: Text.Wrap
    }

    Item { width: 1; height: 4 }

    PrimaryButton {
        text: root.actionText
        iconName: "plus"
        visible: root.actionText !== ""
        anchors.horizontalCenter: parent.horizontalCenter
        onClicked: root.actionTriggered()
    }
}
