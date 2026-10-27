import QtQuick 2.15

Column {
    id: root

    property string label: ""
    property string errorText: ""
    property alias content: contentPlaceholder.data

    spacing: 6
    width: parent ? parent.width : 280

    Text {
        text: root.label
        color: themeEngine.secondaryText
        font.pixelSize: 13
        font.weight: Font.Medium
        font.family: "Segoe UI, Inter, sans-serif"
        visible: root.label !== ""
    }

    Item {
        id: contentPlaceholder
        width: parent.width
        implicitHeight: children.length > 0 ? children[0].implicitHeight : 40
        height: implicitHeight
    }

    Text {
        text: root.errorText
        color: themeEngine.negative
        font.pixelSize: 12
        font.family: "Segoe UI, Inter, sans-serif"
        visible: root.errorText !== ""
    }
}
