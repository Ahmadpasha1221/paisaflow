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
        spacing: 24

        // Page Header
        PageHeader {
            title: "Financial Overview"
            subtitle: "Real-time consolidated balances, net worth, and monthly cash flow."
        }

        // Empty state if brand new setup
        EmptyState {
            visible: !overviewVM.hasData
            title: "Welcome to PaisaFlow"
            description: "No financial records found. Record your first transaction or add an account to begin tracking your finances."
            actionText: "Record First Transaction"
            onActionTriggered: appVM.openDialog("transaction")
        }

        // Active Overview Content
        Column {
            width: parent.width
            spacing: 24
            visible: overviewVM.hasData

            // Key Metrics Row: Net Worth, Assets, Liabilities
            Flow {
                width: parent.width
                spacing: 16

                FinancialSummaryCard {
                    width: (parent.width - 32) / 3
                    title: "Net Worth"
                    amount: overviewVM.netWorth
                    amountColor: overviewVM.netWorthPaise >= 0 ? themeEngine.primaryAccent : themeEngine.negative
                    iconName: "scale"
                    accentColor: themeEngine.primaryAccent
                    subtitle: "Total Assets minus Total Liabilities"
                }

                FinancialSummaryCard {
                    width: (parent.width - 32) / 3
                    title: "Total Assets"
                    amount: overviewVM.totalAssets
                    amountColor: themeEngine.positive
                    iconName: "wallet"
                    accentColor: themeEngine.positive
                    subtitle: "Cash, Bank, Savings & Receivables"
                }

                FinancialSummaryCard {
                    width: (parent.width - 32) / 3
                    title: "Total Liabilities"
                    amount: overviewVM.totalLiabilities
                    amountColor: themeEngine.negative
                    iconName: "credit-card"
                    accentColor: themeEngine.negative
                    subtitle: "Credit Cards & Active Borrowings"
                }
            }

            // Monthly Cash Flow Row: Income, Expenses, Net Cash Flow
            Flow {
                width: parent.width
                spacing: 16

                FinancialSummaryCard {
                    width: (parent.width - 32) / 3
                    title: "Income (This Month)"
                    amount: overviewVM.incomeMonth
                    amountColor: themeEngine.positive
                    iconName: "arrow-down-left"
                    accentColor: themeEngine.positive
                }

                FinancialSummaryCard {
                    width: (parent.width - 32) / 3
                    title: "Expenses (This Month)"
                    amount: overviewVM.expensesMonth
                    amountColor: themeEngine.negative
                    iconName: "arrow-up-right"
                    accentColor: themeEngine.negative
                }

                FinancialSummaryCard {
                    width: (parent.width - 32) / 3
                    title: "Net Cash Flow (This Month)"
                    amount: overviewVM.netCashFlow
                    amountColor: overviewVM.netCashFlowPaise >= 0 ? themeEngine.positive : themeEngine.negative
                    iconName: "arrow-left-right"
                    accentColor: overviewVM.netCashFlowPaise >= 0 ? themeEngine.positive : themeEngine.negative
                    subtitle: "Surplus cash generated this month"
                }
            }

            // Shared six-month net cash-flow trend, matching the selected household filter.
            Rectangle {
                width: parent.width
                implicitHeight: trendColumn.implicitHeight + 36
                radius: 12
                color: themeEngine.primarySurface
                border.color: themeEngine.divider
                border.width: 1

                Column {
                    id: trendColumn
                    anchors.fill: parent
                    anchors.margins: 18
                    spacing: 12

                    Text {
                        text: "Cash Flow Trend (Last 6 Months)"
                        color: themeEngine.primaryText
                        font.pixelSize: 16
                        font.weight: Font.DemiBold
                        font.family: "Segoe UI, Inter, sans-serif"
                    }

                    SmoothAreaLineChart {
                        objectName: "overviewCashFlowChart"
                        width: parent.width
                        height: 220
                        points: reportsVM.monthlyTrends
                        valueRole: "netPaise"
                        formattedValueRole: "net"
                        seriesLabel: "Net cash flow"
                    }
                }
            }

            // Two-column layout: Recent Transactions (60%) & Category Breakdown (40%)
            Row {
                width: parent.width
                spacing: 20

                // Recent Transactions Panel
                Rectangle {
                    width: (parent.width - 20) * 0.6
                    implicitHeight: recentCol.implicitHeight + 36
                    radius: 12
                    color: themeEngine.primarySurface
                    border.color: themeEngine.divider
                    border.width: 1

                    Column {
                        id: recentCol
                        anchors.fill: parent
                        anchors.margins: 18
                        spacing: 14

                        Row {
                            width: parent.width

                            Text {
                                text: "Recent Transactions"
                                color: themeEngine.primaryText
                                font.pixelSize: 16
                                font.weight: Font.DemiBold
                                font.family: "Segoe UI, Inter, sans-serif"
                                width: parent.width - viewAllBtn.width
                                anchors.verticalCenter: parent.verticalCenter
                            }

                            SecondaryButton {
                                id: viewAllBtn
                                text: "View All"
                                anchors.verticalCenter: parent.verticalCenter
                                onClicked: appVM.navigateTo("transactions")
                            }
                        }

                        Rectangle {
                            width: parent.width
                            height: 1
                            color: themeEngine.divider
                        }

                        Repeater {
                            model: overviewVM.recentTransactions

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
                                onVoidRequested: (id) => appVM.requestTransactionDelete(id, modelData.description)
                            }
                        }
                    }
                }

                // Category Spending Breakdown Panel
                Rectangle {
                    width: (parent.width - 20) * 0.4
                    implicitHeight: catCol.implicitHeight + 36
                    radius: 12
                    color: themeEngine.primarySurface
                    border.color: themeEngine.divider
                    border.width: 1

                    Column {
                        id: catCol
                        anchors.fill: parent
                        anchors.margins: 18
                        spacing: 14

                        Text {
                            text: "Spending Breakdown (This Month)"
                            color: themeEngine.primaryText
                            font.pixelSize: 16
                            font.weight: Font.DemiBold
                            font.family: "Segoe UI, Inter, sans-serif"
                        }

                        Rectangle {
                            width: parent.width
                            height: 1
                            color: themeEngine.divider
                        }

                        Text {
                            text: "No expenses recorded this month."
                            color: themeEngine.secondaryText
                            font.pixelSize: 13
                            visible: overviewVM.categorySpending.length === 0
                        }

                        RankedBarList {
                            width: parent.width
                            items: overviewVM.categorySpending
                            maxRows: 6
                        }
                    }
                }
            }
        }
    }
}
