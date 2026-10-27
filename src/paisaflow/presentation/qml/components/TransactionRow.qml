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

    signal voidRequested(int id)

    implicitHeight: 56
    implicitWidth: parent ? parent.width : 600
    radius: 8
    color: mouseArea.containsMouse ? themeEngine.elevatedSurface : "transparent"
    border.color: themeEngine.divider
    border.width: 1

    Behavior on color {
        ColorAnimation { duration: 100 }
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
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
            width: parent.width - 34 - 180 - (root.isVoided ? 90 : 130)
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
                text: (root.categoryName !== "" ? root.categoryName + " • " : "") + root.personName + " • " + root.paymentMethod
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

        // Action / Status
        Item {
            width: 32
            height: 32
            anchors.verticalCenter: parent.verticalCenter

            StatusBadge {
                text: "VOID"
                level: "neutral"
                visible: root.isVoided
                anchors.centerIn: parent
            }

            IconButton {
                iconName: "close"
                iconSize: 14
                visible: !root.isVoided && mouseArea.containsMouse
                anchors.centerIn: parent
                onClicked: root.voidRequested(root.transactionId)
            }
        }
    }
}
