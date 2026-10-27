import QtQuick 2.15

Row {
    id: root

    property string title: ""
    property string subtitle: ""
    property alias actions: actionContainer.data

    width: parent.width
    spacing: 16

    Column {
        width: parent.width - actionContainer.width - root.spacing
        spacing: 4

        Text {
            text: root.title
            color: themeEngine.primaryText
            font.pixelSize: 24
            font.weight: Font.DemiBold
            font.family: "Segoe UI, Inter, sans-serif"
        }

        Text {
            text: root.subtitle
            color: themeEngine.secondaryText
            font.pixelSize: 13
            font.family: "Segoe UI, Inter, sans-serif"
            visible: root.subtitle !== ""
        }
    }

    Row {
        id: actionContainer
        spacing: 12
        anchors.verticalCenter: parent.verticalCenter
    }
}
