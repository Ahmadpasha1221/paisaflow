import QtQuick 2.15

Rectangle {
    id: root

    property int transactionId: 0
    property string referenceNo: ""
    property string dateStr: ""
    property string txnType: "expense"
    property string description: ""
    property string amountStr: "₹0.00"
    property string personName: ""
    property string categoryName: ""
    property string paymentMethod: ""
    property string status: "completed"
    property bool isVoided: status === "voided"
    // Active rows offer the delete affordance; rows in the History tab do not.
    property bool showDeleteAction: true
    // Extra detail appended to the subtitle, e.g. when the record was deleted.
    property string statusNote: ""

    signal voidRequested(int id)

    implicitHeight: 56
    implicitWidth: parent ? parent.width : 600
    radius: 8
    color: rowHover.hovered ? themeEngine.elevatedSurface : "transparent"
    border.color: themeEngine.divider
    border.width: 1

    Behavior on color {
        ColorAnimation { duration: 120 }
    }

    // A HoverHandler observes the pointer passively, including while it sits on the
    // child delete button. The previous MouseArea lost hover as soon as the button
    // appeared underneath the cursor, so the button hid itself, the row regained
    // hover, and both blinked in a loop.
    HoverHandler {
        id: rowHover
    }

    Row {
        anchors.fill: parent
        anchors.leftMargin: 16
        anchors.rightMargin: 16
        spacing: 14

        // Type Icon Box
        Rectangle {
            width: 34
            height: 34
            radius: 8
            anchors.verticalCenter: parent.verticalCenter
            color: {
                if (root.isVoided) return Qt.rgba(0.5, 0.5, 0.5, 0.15);
                if (root.txnType === "income") return Qt.rgba(themeEngine.positive.r, themeEngine.positive.g, themeEngine.positive.b, 0.15);
                if (root.txnType === "transfer") return Qt.rgba(themeEngine.informational.r, themeEngine.informational.g, themeEngine.informational.b, 0.15);
                return Qt.rgba(themeEngine.negative.r, themeEngine.negative.g, themeEngine.negative.b, 0.15);
            }

            FlowIcon {
                name: {
                    if (root.txnType === "income") return "arrow-down-left";
                    if (root.txnType === "transfer") return "arrow-left-right";
                    return "arrow-up-right";
                }
                size: 16
                color: {
                    if (root.isVoided) return themeEngine.secondaryText;
                    if (root.txnType === "income") return themeEngine.positive;
                    if (root.txnType === "transfer") return themeEngine.informational;
                    return themeEngine.negative;
                }
                anchors.centerIn: parent
            }
        }

        // Details (Description & Category/Person)
        Column {
            width: Math.max(0, parent.width - 34 - 80 - 100 - 32 - 4 * 14)
            anchors.verticalCenter: parent.verticalCenter
            spacing: 2

            Text {
                text: root.description
                color: root.isVoided ? themeEngine.secondaryText : themeEngine.primaryText
                font.pixelSize: 14
                font.weight: Font.Medium
                font.family: "Segoe UI, Inter, sans-serif"
                font.strikeout: root.isVoided
                elide: Text.ElideRight
                width: parent.width
            }

            Text {
                text: (root.categoryName !== "" ? root.categoryName + " • " : "")
                      + root.personName + " • " + root.paymentMethod
                      + (root.statusNote !== "" ? " • " + root.statusNote : "")
                color: themeEngine.secondaryText
                font.pixelSize: 12
                font.family: "Segoe UI, Inter, sans-serif"
                elide: Text.ElideRight
                width: parent.width
            }
        }

        // Date
        Text {
            text: root.dateStr
            color: themeEngine.secondaryText
            font.pixelSize: 12
            font.family: "Segoe UI, Inter, sans-serif"
            font.features: { "tnum": 1 }
            anchors.verticalCenter: parent.verticalCenter
            width: 80
        }

        // Amount
        Text {
            text: (root.txnType === "income" ? "+" : (root.txnType === "expense" ? "-" : "")) + root.amountStr
            color: {
                if (root.isVoided) return themeEngine.secondaryText;
                if (root.txnType === "income") return themeEngine.positive;
                if (root.txnType === "transfer") return themeEngine.informational;
                return themeEngine.negative;
            }
            font.pixelSize: 15
            font.weight: Font.DemiBold
            font.family: "Segoe UI, Inter, sans-serif"
            font.features: { "tnum": 1 }
            font.strikeout: root.isVoided
            horizontalAlignment: Text.AlignRight
            anchors.verticalCenter: parent.verticalCenter
            width: 100
        }

        // Delete action, revealed while the row is hovered.
        Item {
            width: 32
            height: 32
            anchors.verticalCenter: parent.verticalCenter

            IconButton {
                id: deleteButton
                objectName: "deleteTransactionButton"
                iconName: "trash"
                iconSize: 14
                anchors.centerIn: parent
                visible: root.showDeleteAction && (rowHover.hovered || opacity > 0)
                opacity: rowHover.hovered ? 1 : 0
                enabled: rowHover.hovered
                onClicked: root.voidRequested(root.transactionId)

                Behavior on opacity {
                    NumberAnimation { duration: 120; easing.type: Easing.OutQuad }
                }
            }
        }
    }
}
