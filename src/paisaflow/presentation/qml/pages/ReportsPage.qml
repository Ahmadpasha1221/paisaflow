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

        PageHeader {
            title: "Financial Reports & Trends"
            subtitle: "Historical monthly income versus expenses and lifetime category expenditure."
        }

        // Monthly income vs expenses chart
        Rectangle {
            width: parent.width
            implicitHeight: chartCol.implicitHeight + 36
            radius: 12
            color: themeEngine.primarySurface
            border.color: themeEngine.divider
            border.width: 1

            Column {
                id: chartCol
                anchors.fill: parent
                anchors.margins: 18
                spacing: 14

                Text {
                    text: "Monthly Cash Flow (Last 6 Months)"
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

                GroupedBarChart {
                    objectName: "monthlyBarChart"
                    width: parent.width
                    plotHeight: 190
                    bars: reportsVM.monthlyTrends
                    visible: reportsVM.monthlyTrends.length > 0
                }

                Text {
                    text: "No monthly activity recorded yet."
                    color: themeEngine.secondaryText
                    font.pixelSize: 13
                    font.family: "Segoe UI, Inter, sans-serif"
                    visible: reportsVM.monthlyTrends.length === 0
                }
            }
        }

        // Smooth monthly net cash-flow series complements the income/expense bars above.
        Rectangle {
            width: parent.width
            implicitHeight: netTrendCol.implicitHeight + 36
            radius: 12
            color: themeEngine.primarySurface
            border.color: themeEngine.divider
            border.width: 1

            Column {
                id: netTrendCol
                anchors.fill: parent
                anchors.margins: 18
                spacing: 14

                Text {
                    text: "Net Cash Flow Trend"
                    color: themeEngine.primaryText
                    font.pixelSize: 16
                    font.weight: Font.DemiBold
                    font.family: "Segoe UI, Inter, sans-serif"
                }

                SmoothAreaLineChart {
                    objectName: "reportsNetCashFlowChart"
                    width: parent.width
                    height: 220
                    points: reportsVM.monthlyTrends
                    valueRole: "netPaise"
                    formattedValueRole: "net"
                    seriesLabel: "Net cash flow"
                }
            }
        }

        // Monthly comparison figures
        Rectangle {
            width: parent.width
            implicitHeight: trendCol.implicitHeight + 36
            radius: 12
            color: themeEngine.primarySurface
            border.color: themeEngine.divider
            border.width: 1

            Column {
                id: trendCol
                anchors.fill: parent
                anchors.margins: 18
                spacing: 14

                Text {
                    text: "Monthly Trajectory (Last 6 Months)"
                    color: themeEngine.primaryText
                    font.pixelSize: 16
                    font.weight: Font.DemiBold
                    font.family: "Segoe UI, Inter, sans-serif"
                }

                // Header Row
                Row {
                    width: parent.width
                    height: 24

                    Text {
                        text: "MONTH"
                        color: themeEngine.secondaryText
                        font.pixelSize: 11
                        font.weight: Font.DemiBold
                        width: parent.width * 0.25
                    }

                    Text {
                        text: "INCOME"
                        color: themeEngine.secondaryText
                        font.pixelSize: 11
                        font.weight: Font.DemiBold
                        horizontalAlignment: Text.AlignRight
                        width: parent.width * 0.25
                    }

                    Text {
                        text: "EXPENSES"
                        color: themeEngine.secondaryText
                        font.pixelSize: 11
                        font.weight: Font.DemiBold
                        horizontalAlignment: Text.AlignRight
                        width: parent.width * 0.25
                    }

                    Text {
                        text: "NET CASH FLOW"
                        color: themeEngine.secondaryText
                        font.pixelSize: 11
                        font.weight: Font.DemiBold
                        horizontalAlignment: Text.AlignRight
                        width: parent.width * 0.25
                    }
                }

                Rectangle {
                    width: parent.width
                    height: 1
                    color: themeEngine.divider
                }

                Repeater {
                    model: reportsVM.monthlyTrends

                    Row {
                        width: parent.width
                        height: 38

                        Text {
                            text: modelData.month
                            color: themeEngine.primaryText
                            font.pixelSize: 13
                            font.weight: Font.Medium
                            font.family: "Segoe UI, Inter, sans-serif"
                            anchors.verticalCenter: parent.verticalCenter
                            width: parent.width * 0.25
                        }

                        Text {
                            text: modelData.income
                            color: themeEngine.positive
                            font.pixelSize: 13
                            font.family: "Segoe UI, Inter, sans-serif"
                            font.features: { "tnum": 1 }
                            horizontalAlignment: Text.AlignRight
                            anchors.verticalCenter: parent.verticalCenter
                            width: parent.width * 0.25
                        }

                        Text {
                            text: modelData.expenses
                            color: themeEngine.negative
                            font.pixelSize: 13
                            font.family: "Segoe UI, Inter, sans-serif"
                            font.features: { "tnum": 1 }
                            horizontalAlignment: Text.AlignRight
                            anchors.verticalCenter: parent.verticalCenter
                            width: parent.width * 0.25
                        }

                        Text {
                            text: modelData.net
                            color: modelData.netPaise >= 0 ? themeEngine.positive : themeEngine.negative
                            font.pixelSize: 13
                            font.weight: Font.DemiBold
                            font.family: "Segoe UI, Inter, sans-serif"
                            font.features: { "tnum": 1 }
                            horizontalAlignment: Text.AlignRight
                            anchors.verticalCenter: parent.verticalCenter
                            width: parent.width * 0.25
                        }
                    }
                }
            }
        }

        // Lifetime category and per-person breakdowns
        Row {
            width: parent.width
            spacing: 20

            Rectangle {
                width: (parent.width - 20) / 2
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
                        text: "Category Expense Distribution"
                        color: themeEngine.primaryText
                        font.pixelSize: 16
                        font.weight: Font.DemiBold
                        font.family: "Segoe UI, Inter, sans-serif"
                    }

                    Text {
                        text: "Lifetime total " + reportsVM.totalExpenses
                        color: themeEngine.secondaryText
                        font.pixelSize: 12
                        font.family: "Segoe UI, Inter, sans-serif"
                    }

                    Rectangle {
                        width: parent.width
                        height: 1
                        color: themeEngine.divider
                    }

                    Text {
                        text: "No expenses recorded to calculate distribution."
                        color: themeEngine.secondaryText
                        font.pixelSize: 13
                        font.family: "Segoe UI, Inter, sans-serif"
                        visible: reportsVM.categoryShares.length === 0
                    }

                    RankedBarList {
                        objectName: "categorySpendingChart"
                        width: parent.width
                        items: reportsVM.categoryShares
                    }
                }
            }

            Rectangle {
                width: (parent.width - 20) / 2
                implicitHeight: peopleCol.implicitHeight + 36
                radius: 12
                color: themeEngine.primarySurface
                border.color: themeEngine.divider
                border.width: 1

                Column {
                    id: peopleCol
                    anchors.fill: parent
                    anchors.margins: 18
                    spacing: 14

                    Text {
                        text: "Spending by Person"
                        color: themeEngine.primaryText
                        font.pixelSize: 16
                        font.weight: Font.DemiBold
                        font.family: "Segoe UI, Inter, sans-serif"
                    }

                    Text {
                        text: "How much each household member has used"
                        color: themeEngine.secondaryText
                        font.pixelSize: 12
                        font.family: "Segoe UI, Inter, sans-serif"
                    }

                    Rectangle {
                        width: parent.width
                        height: 1
                        color: themeEngine.divider
                    }

                    Text {
                        text: "No member spending recorded yet."
                        color: themeEngine.secondaryText
                        font.pixelSize: 13
                        font.family: "Segoe UI, Inter, sans-serif"
                        visible: reportsVM.personSpending.length === 0
                    }

                    RankedBarList {
                        objectName: "personSpendingChart"
                        width: parent.width
                        items: reportsVM.personSpending
                    }
                }
            }
        }
    }
}
