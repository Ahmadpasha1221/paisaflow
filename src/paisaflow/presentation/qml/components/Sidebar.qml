import QtQuick 2.15

Rectangle {
    id: root

    property bool collapsed: false

    width: collapsed ? 68 : 230
    color: themeEngine.sidebarBackground
    border.color: themeEngine.divider
    border.width: 1

    Behavior on width {
        NumberAnimation { duration: 160; easing.type: Easing.OutQuad }
    }

    Column {
        anchors.fill: parent
        anchors.margins: 12
        spacing: 16

        // Brand & Collapse Header
        Row {
            width: parent.width
            height: 44

            Item {
                width: parent.width - toggleBtn.width
                height: parent.height
                visible: !root.collapsed

                Column {
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: 2

                    Text {
                        text: "PaisaFlow"
                        color: themeEngine.primaryText
                        font.pixelSize: 18
                        font.weight: Font.Bold
                        font.family: "Segoe UI, Inter, sans-serif"
                    }

                    Text {
                        text: "Personal finance, made clear."
                        color: themeEngine.secondaryText
                        font.pixelSize: 10
                        font.family: "Segoe UI, Inter, sans-serif"
                    }
                }
            }

            IconButton {
                id: toggleBtn
                iconName: root.collapsed ? "overview" : "arrow-left-right"
                iconSize: 16
                anchors.verticalCenter: parent.verticalCenter
                anchors.right: parent.right
                onClicked: root.collapsed = !root.collapsed
            }
        }

        Rectangle {
            width: parent.width
            height: 1
            color: themeEngine.divider
        }

        // Navigation Menu Items
        Column {
            width: parent.width
            spacing: 4

            SidebarItem {
                pageId: "overview"
                label: "Overview"
                iconName: "overview"
                isActive: appVM.activePage === "overview"
                collapsed: root.collapsed
                onClicked: appVM.navigateTo("overview")
            }

            SidebarItem {
                pageId: "transactions"
                label: "Transactions"
                iconName: "transactions"
                isActive: appVM.activePage === "transactions"
                collapsed: root.collapsed
                onClicked: appVM.navigateTo("transactions")
            }

            SidebarItem {
                pageId: "accounts"
                label: "Accounts"
                iconName: "accounts"
                isActive: appVM.activePage === "accounts"
                collapsed: root.collapsed
                onClicked: appVM.navigateTo("accounts")
            }

            SidebarItem {
                pageId: "people"
                label: "People & Household"
                iconName: "people"
                isActive: appVM.activePage === "people"
                collapsed: root.collapsed
                onClicked: appVM.navigateTo("people")
            }

            SidebarItem {
                pageId: "budgets"
                label: "Budgets"
                iconName: "budgets"
                isActive: appVM.activePage === "budgets"
                collapsed: root.collapsed
                onClicked: appVM.navigateTo("budgets")
            }

            SidebarItem {
                pageId: "goals"
                label: "Savings Goals"
                iconName: "goals"
                isActive: appVM.activePage === "goals"
                collapsed: root.collapsed
                onClicked: appVM.navigateTo("goals")
            }

            SidebarItem {
                pageId: "debts"
                label: "Debts & Loans"
                iconName: "debts"
                isActive: appVM.activePage === "debts"
                collapsed: root.collapsed
                onClicked: appVM.navigateTo("debts")
            }

            SidebarItem {
                pageId: "reports"
                label: "Reports"
                iconName: "reports"
                isActive: appVM.activePage === "reports"
                collapsed: root.collapsed
                onClicked: appVM.navigateTo("reports")
            }
        }
    }

    // Bottom Settings anchored to bottom
    Column {
        width: parent.width - 24
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 12
        anchors.horizontalCenter: parent.horizontalCenter
        spacing: 8

        Rectangle {
            width: parent.width
            height: 1
            color: themeEngine.divider
        }

        SidebarItem {
            pageId: "settings"
            label: "Settings"
            iconName: "settings"
            isActive: appVM.activePage === "settings"
            collapsed: root.collapsed
            onClicked: appVM.navigateTo("settings")
        }
    }
}
