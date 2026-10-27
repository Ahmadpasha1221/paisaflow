import QtQuick 2.15
import QtQuick.Controls 2.15
import "../components"

ScrollView {
    id: root

    contentWidth: availableWidth
    clip: true
    padding: 24

    Column {
        width: parent.width
        spacing: 20

        // Header with global add action
        PageHeader {
            title: "Transaction Ledger"
            subtitle: "Search, filter, and audit every double-entry transaction record."

            actions: [
                PrimaryButton {
                    text: "New Transaction"
                    iconName: "plus"
                    onClicked: appVM.openDialog("transaction")
                }
            ]
        }

        // Filter and Search Toolbar
        Rectangle {
            width: parent.width
            implicitHeight: filterRow.implicitHeight + 24
            radius: 12
            color: themeEngine.primarySurface
            border.color: themeEngine.divider
            border.width: 1

            Row {
                id: filterRow
                anchors.fill: parent
                anchors.margins: 12
                spacing: 12

                // Search Box
                SearchField {
                    id: searchBox
                    width: 260
                    onSearchSubmitted: (q) => transactionVM.setSearchText(q)
                }

                // Type Filter Pills
                Row {
                    spacing: 6
                    anchors.verticalCenter: parent.verticalCenter

                    Repeater {
                        model: [
                            { id: "all", name: "All Types" },
                            { id: "expense", name: "Expenses" },
                            { id: "income", name: "Income" },
                            { id: "transfer", name: "Transfers" }
                        ]

                        Rectangle {
                            width: label.implicitWidth + 20
                            height: 34
                            radius: 6
                            color: transactionVM.typeFilter === modelData.id ? themeEngine.elevatedSurface : "transparent"
                            border.color: transactionVM.typeFilter === modelData.id ? themeEngine.primaryAccent : themeEngine.divider
                            border.width: 1

                            Text {
                                id: label
                                text: modelData.name
                                color: transactionVM.typeFilter === modelData.id ? themeEngine.primaryAccent : themeEngine.secondaryText
                                font.pixelSize: 12
                                font.weight: Font.Medium
                                anchors.centerIn: parent
                            }

                            MouseArea {
                                anchors.fill: parent
                                onClicked: transactionVM.setTypeFilter(modelData.id)
                            }
                        }
                    }
                }
            }
        }

        // Ledger views: live records versus deleted records kept for audit
        Row {
            id: ledgerTabs
            objectName: "ledgerTabs"
            width: parent.width
            spacing: 8

            Repeater {
                model: [
                    { mode: "active", label: "Active" },
                    { mode: "history", label: "History" }
                ]

                Rectangle {
                    id: ledgerTab
                    objectName: "ledgerTab_" + modelData.mode
                    readonly property bool selected: transactionVM.viewMode === modelData.mode
                    readonly property int count: modelData.mode === "history" ? transactionVM.historyCount : transactionVM.activeCount

                    width: tabRow.implicitWidth + 26
                    height: 36
                    radius: 8
                    color: selected ? themeEngine.elevatedSurface : "transparent"
                    border.color: selected ? themeEngine.primaryAccent : themeEngine.divider
                    border.width: 1

                    Behavior on color {
                        ColorAnimation { duration: 120 }
                    }

                    Row {
                        id: tabRow
                        anchors.centerIn: parent
                        spacing: 8

                        Text {
                            text: modelData.label
                            color: ledgerTab.selected ? themeEngine.primaryText : themeEngine.secondaryText
                            font.pixelSize: 13
                            font.weight: ledgerTab.selected ? Font.DemiBold : Font.Medium
                            font.family: "Segoe UI, Inter, sans-serif"
                            anchors.verticalCenter: parent.verticalCenter
                        }

                        Rectangle {
                            width: countLabel.implicitWidth + 12
                            height: 20
                            radius: 10
                            color: ledgerTab.selected
                                   ? Qt.rgba(themeEngine.primaryAccent.r, themeEngine.primaryAccent.g, themeEngine.primaryAccent.b, 0.18)
                                   : themeEngine.elevatedSurface
                            anchors.verticalCenter: parent.verticalCenter

                            Text {
                                id: countLabel
                                text: ledgerTab.count
                                color: ledgerTab.selected ? themeEngine.primaryAccent : themeEngine.secondaryText
                                font.pixelSize: 11
                                font.weight: Font.DemiBold
                                font.features: { "tnum": 1 }
                                anchors.centerIn: parent
                            }
                        }
                    }

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        onClicked: transactionVM.setViewMode(modelData.mode)
                    }
                }
            }
        }

        // Ledger List Container
        Rectangle {
            width: parent.width
            implicitHeight: ledgerCol.implicitHeight + 36
            radius: 12
            color: themeEngine.primarySurface
            border.color: themeEngine.divider
            border.width: 1

            Column {
                id: ledgerCol
                anchors.fill: parent
                anchors.margins: 18
                spacing: 12

                // Column Headers (same column widths as TransactionRow)
                Row {
                    width: parent.width - 32
                    x: 16
                    height: 24
                    spacing: 14

                    Item { width: 34; height: 1 } // icon spacer

                    Text {
                        text: "DESCRIPTION & DETAILS"
                        color: themeEngine.secondaryText
                        font.pixelSize: 11
                        font.weight: Font.DemiBold
                        width: parent.width - 34 - 80 - 100 - 32 - 4 * 14
                    }

                    Text {
                        text: "DATE"
                        color: themeEngine.secondaryText
                        font.pixelSize: 11
                        font.weight: Font.DemiBold
                        width: 80
                    }

                    Text {
                        text: "AMOUNT"
                        color: themeEngine.secondaryText
                        font.pixelSize: 11
                        font.weight: Font.DemiBold
                        horizontalAlignment: Text.AlignRight
                        width: 100
                    }

                    Item { width: 32; height: 1 } // action spacer
                }

                Rectangle {
                    width: parent.width
                    height: 1
                    color: themeEngine.divider
                }

                // Empty state
                EmptyState {
                    visible: transactionVM.transactions.length === 0
                    title: transactionVM.viewMode === "history" ? "History is empty" : "No transactions found"
                    description: transactionVM.viewMode === "history"
                                 ? "Deleted transactions are kept here for audit. They no longer count towards balances, budgets or reports."
                                 : "No records match your selected filters or search query."
                    actionText: transactionVM.viewMode === "history" ? "" : "Clear Filters"
                    onActionTriggered: {
                        searchBox.text = "";
                        transactionVM.setSearchText("");
                        transactionVM.setTypeFilter("all");
                    }
                }

                // Transactions List
                Repeater {
                    model: transactionVM.transactions

                    TransactionRow {
                        transactionId: modelData.id
                        referenceNo: modelData.referenceNo
                        dateStr: modelData.date
                        txnType: modelData.type
                        description: modelData.description
                        amountStr: modelData.amount
                        personName: modelData.personName
                        categoryName: modelData.categoryName
                        paymentMethod: modelData.paymentMethod
                        status: modelData.status
                        showDeleteAction: transactionVM.viewMode === "active"
                        statusNote: transactionVM.viewMode === "history" ? "Deleted " + modelData.voidedAt : ""
                        onVoidRequested: (id) => appVM.requestTransactionDelete(id, modelData.description)
                    }
                }

                // Pagination Controls
                Item {
                    width: parent.width
                    height: 38
                    visible: transactionVM.totalCount > 0

                    Text {
                        text: "Showing " + transactionVM.transactions.length + " of " + transactionVM.totalCount
                              + (transactionVM.viewMode === "history" ? " deleted transactions" : " transactions")
                        color: themeEngine.secondaryText
                        font.pixelSize: 12
                        anchors.left: parent.left
                        anchors.verticalCenter: parent.verticalCenter
                    }

                    Row {
                        spacing: 8
                        anchors.right: parent.right
                        anchors.verticalCenter: parent.verticalCenter

                        SecondaryButton {
                            text: "Previous"
                            enabled: transactionVM.currentPage > 0
                            onClicked: transactionVM.setPage(transactionVM.currentPage - 1)
                        }

                        Rectangle {
                            height: 38
                            width: pageNumText.implicitWidth + 24
                            radius: 8
                            color: themeEngine.elevatedSurface
                            border.color: themeEngine.divider
                            border.width: 1

                            Text {
                                id: pageNumText
                                text: (transactionVM.currentPage + 1) + " / " + transactionVM.totalPages
                                color: themeEngine.primaryText
                                font.pixelSize: 12
                                font.features: { "tnum": 1 }
                                anchors.centerIn: parent
                            }
                        }

                        SecondaryButton {
                            text: "Next"
                            enabled: transactionVM.currentPage < (transactionVM.totalPages - 1)
                            onClicked: transactionVM.setPage(transactionVM.currentPage + 1)
                        }
                    }
                }
            }
        }
    }
}
