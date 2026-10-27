import QtQuick 2.15
import QtQuick.Controls 2.15
import "../components"

ScrollView {
    id: root

    contentWidth: availableWidth
    clip: true

    Column {
        width: parent.width
        spacing: 20
        padding: 24

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

                // Column Headers
                Row {
                    width: parent.width
                    height: 24
                    anchors.leftMargin: 16
                    anchors.rightMargin: 16

                    Item { width: 34; height: 1 } // icon spacer
                    Item { width: 14; height: 1 }

                    Text {
                        text: "DESCRIPTION & DETAILS"
                        color: themeEngine.secondaryText
                        font.pixelSize: 11
                        font.weight: Font.DemiBold
                        width: parent.width - 34 - 180 - 130 - 32
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

                // Empty state if no transactions
                EmptyState {
                    visible: transactionVM.transactions.length === 0
                    title: "No transactions found"
                    description: "No records match your selected filters or search query."
                    actionText: "Clear Filters"
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
                        onVoidRequested: (id) => {
                            transactionVM.voidTransaction(id);
                            appVM.notifyDataChanged();
                        }
                    }
                }

                // Pagination Controls
                Item {
                    width: parent.width
                    height: 38
                    visible: transactionVM.totalCount > 0

                    Text {
                        text: "Showing " + transactionVM.transactions.length + " of " + transactionVM.totalCount + " transactions"
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
