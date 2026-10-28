import QtQuick 2.15

Column {
    id: root

    property string label: ""
    property string errorText: ""
    property alias content: contentPlaceholder.data

    spacing: 6
    width: parent ? parent.width : 280

    Text {
        width: parent.width
        text: root.label
        color: themeEngine.secondaryText
        font.pixelSize: 13
        font.weight: Font.Medium
        font.family: "Segoe UI, Inter, sans-serif"
        elide: Text.ElideRight
        visible: root.label !== ""
    }

    Item {
        id: contentPlaceholder
        width: parent.width
        implicitHeight: children.length > 0 ? children[0].implicitHeight : 42
        height: implicitHeight
    }

    Text {
        width: parent.width
        text: root.errorText
        color: themeEngine.negative
        font.pixelSize: 12
        font.family: "Segoe UI, Inter, sans-serif"
        wrapMode: Text.Wrap
        visible: root.errorText !== ""
    }
}
