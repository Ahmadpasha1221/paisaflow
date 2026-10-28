import QtQuick 2.15
import QtQuick.Controls 2.15

ComboBox {
    id: root

    property string textRoleName: "name"
    property string valueRoleName: "id"

    textRole: textRoleName
    valueRole: valueRoleName

    implicitHeight: 42
    implicitWidth: parent ? parent.width : 280

    hoverEnabled: true

    background: Rectangle {
        radius: 8
        color: !root.enabled ? themeEngine.disabledSurface
             : (root.hovered && !root.activeFocus ? themeEngine.inputHoverSurface : themeEngine.inputSurface)
        border.color: root.activeFocus ? themeEngine.primaryAccent : themeEngine.divider
        border.width: root.activeFocus ? 1.5 : 1

        Behavior on border.color {
            ColorAnimation { duration: 120 }
        }
    }

    contentItem: Text {
        leftPadding: 14
        rightPadding: 36
        text: root.displayText
        opacity: root.enabled ? 1 : 0.65
        font.pixelSize: 14
        font.family: "Segoe UI, Inter, sans-serif"
        color: themeEngine.primaryText
        verticalAlignment: Text.AlignVCenter
        elide: Text.ElideRight
    }

    indicator: Item {
        x: root.width - width - 12
        y: (root.height - height) / 2
        width: 12
        height: 12

        Canvas {
            anchors.fill: parent
            onPaint: {
                var ctx = getContext("2d");
                ctx.reset();
                ctx.strokeStyle = themeEngine.secondaryText;
                ctx.lineWidth = 1.5;
                ctx.lineCap = "round";
                ctx.beginPath();
                ctx.moveTo(1, 4); ctx.lineTo(6, 9); ctx.lineTo(11, 4);
                ctx.stroke();
            }
        }
    }

    popup: Popup {
        y: root.height + 4
        width: root.width
        implicitHeight: contentItem.implicitHeight
        padding: 4

        contentItem: ListView {
            clip: true
            implicitHeight: Math.min(contentHeight, 220)
            model: root.popup.visible ? root.delegateModel : null
            currentIndex: root.highlightedIndex

            ScrollIndicator.vertical: ScrollIndicator {}
        }

        background: Rectangle {
            color: themeEngine.elevatedSurface
            radius: 8
            border.color: themeEngine.divider
            border.width: 1
        }
    }

    delegate: ItemDelegate {
        width: root.width - 8
        height: 36

        contentItem: Text {
            // The option models are plain JS arrays of objects, so the entry lives in
            // modelData; ListModel models expose the role through model instead.
            text: {
                var entry = modelData !== undefined && modelData !== null ? modelData : model;
                if (entry === undefined || entry === null)
                    return "";
                var label = entry[root.textRoleName];
                return label === undefined || label === null ? "" : label;
            }
            color: root.enabled ? themeEngine.primaryText : themeEngine.secondaryText
            font.pixelSize: 13
            font.family: "Segoe UI, Inter, sans-serif"
            verticalAlignment: Text.AlignVCenter
            elide: Text.ElideRight
            leftPadding: 8
        }

        background: Rectangle {
            radius: 6
            color: highlighted ? (themeEngine.isDark ? "#385243" : "#EDF1EA") : "transparent"
        }
    }
}
