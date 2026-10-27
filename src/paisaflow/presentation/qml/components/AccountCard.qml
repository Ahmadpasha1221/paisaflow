import QtQuick 2.15

Rectangle {
    id: root

    property int accountId: 0
    property string name: ""
    property string accountType: ""
    property string accountTypeDisplay: ""
    property string ownerName: ""
    property string balance: "₹0.00"
    property bool isLiability: false
    property string notes: ""

    signal archiveRequested(int id)

    implicitHeight: 140
    implicitWidth: 320
    radius: 12
    color: themeEngine.primarySurface
    border.color: themeEngine.divider
    border.width: 1

    Behavior on color {
        ColorAnimation { duration: 150 }
    }

    Column {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 12

        Row {
            width: parent.width

            Column {
                width: parent.width - badge.width - 8
                spacing: 2

                Text {
                    text: root.name
                    color: themeEngine.primaryText
                    font.pixelSize: 16
                    font.weight: Font.DemiBold
                    font.family: "Segoe UI, Inter, sans-serif"
                    elide: Text.ElideRight
                    width: parent.width
                }

                Text {
                    text: "Owner: " + root.ownerName
                    color: themeEngine.secondaryText
                    font.pixelSize: 12
                    font.family: "Segoe UI, Inter, sans-serif"
                }
            }

            StatusBadge {
                id: badge
                text: root.accountTypeDisplay
                level: root.isLiability ? "warning" : "informational"
            }
        }

        Item { width: 1; height: 12 }

        Row {
            width: parent.width

            Column {
                width: parent.width - archiveBtn.width - 8
                spacing: 2

                Text {
                    text: root.isLiability ? "Outstanding Balance" : "Current Balance"
                    color: themeEngine.secondaryText
                    font.pixelSize: 11
                    font.family: "Segoe UI, Inter, sans-serif"
                }

                Text {
                    text: root.balance
                    color: root.isLiability ? themeEngine.negative : themeEngine.positive
                    font.pixelSize: 20
                    font.weight: Font.DemiBold
                    font.family: "Segoe UI, Inter, sans-serif"
                    font.features: { "tnum": 1 }
                }
            }

            IconButton {
                id: archiveBtn
                iconName: "close"
                iconSize: 14
                anchors.verticalCenter: parent.verticalCenter
                onClicked: root.archiveRequested(root.accountId)
            }
        }
    }
}
