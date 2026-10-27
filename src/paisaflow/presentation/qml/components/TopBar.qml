import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    id: root

    height: 60
    color: themeEngine.appBackground
    border.color: themeEngine.divider
    border.width: 1

    function getPageTitle() {
        switch(appVM.activePage) {
            case "overview": return "Overview Dashboard";
            case "transactions": return "Transaction Ledger";
            case "accounts": return "Accounts & Balances";
            case "people": return "People & Household";
            case "budgets": return "Category Budgets";
            case "goals": return "Savings Goals";
            case "debts": return "Debts & Loans";
            case "reports": return "Financial Reports";
            case "settings": return "Settings & Data Management";
            default: return "PaisaFlow";
        }
    }

    Item {
        anchors.fill: parent
        anchors.leftMargin: 24
        anchors.rightMargin: 24

        // Current Page Title on Left
        Text {
            text: root.getPageTitle()
            color: themeEngine.primaryText
            font.pixelSize: 18
            font.weight: Font.DemiBold
            font.family: "Segoe UI, Inter, sans-serif"
            anchors.left: parent.left
            anchors.verticalCenter: parent.verticalCenter
        }

        // Actions on Right
        Row {
            anchors.right: parent.right
            anchors.verticalCenter: parent.verticalCenter
            spacing: 16

            // Household / Person Context Filter
            Rectangle {
                height: 38
                width: personRow.implicitWidth + 24
                radius: 8
                color: themeEngine.primarySurface
                border.color: themeEngine.divider
                border.width: 1
                anchors.verticalCenter: parent.verticalCenter

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: personContextMenu.open()
                }

                Row {
                    id: personRow
                    anchors.centerIn: parent
                    spacing: 8

                    FlowIcon {
                        name: "people"
                        size: 15
                        color: themeEngine.primaryAccent
                        anchors.verticalCenter: parent.verticalCenter
                    }

                    Text {
                        text: appVM.selectedPersonName
                        color: themeEngine.primaryText
                        font.pixelSize: 13
                        font.weight: Font.Medium
                        font.family: "Segoe UI, Inter, sans-serif"
                        anchors.verticalCenter: parent.verticalCenter
                    }
                }

                Menu {
                    id: personContextMenu
                    y: parent.height + 4

                    MenuItem {
                        text: "Household (All)"
                        onTriggered: appVM.setHouseholdContext(0, "Household (All)")
                    }

                    MenuSeparator {}

                    Instantiator {
                        model: appVM.people
                        MenuItem {
                            text: modelData.name
                            onTriggered: appVM.setHouseholdContext(modelData.id, modelData.name)
                        }
                        onObjectAdded: (index, object) => personContextMenu.insertItem(index + 2, object)
                        onObjectRemoved: (index, object) => personContextMenu.removeItem(object)
                    }
                }
            }

            // Theme Toggle (Moon / Sun)
            IconButton {
                iconName: themeEngine.isDark ? "sun" : "moon"
                iconSize: 18
                anchors.verticalCenter: parent.verticalCenter
                onClicked: themeEngine.toggleTheme()
            }

            // Global Add Transaction CTA
            PrimaryButton {
                text: "Add Transaction"
                iconName: "plus"
                anchors.verticalCenter: parent.verticalCenter
                onClicked: appVM.openDialog("transaction")
            }
        }
    }
}
