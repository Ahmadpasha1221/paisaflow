import QtQuick 2.15
import QtQuick.Controls 2.15
import "../components"

ScrollView {
    id: root

    contentWidth: availableWidth
    clip: true

    Column {
        width: parent.width
        spacing: 24
        padding: 24

        PageHeader {
            title: "Financial Reports & Trends"
            subtitle: "Historical monthly income versus expenses and lifetime category expenditure."
        }

        // Monthly Comparison Trend Table
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

        // Lifetime Category Breakdown
        Rectangle {
            width: parent.width
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

                Rectangle {
                    width: parent.width
                    height: 1
                    color: themeEngine.divider
                }

                Text {
                    text: "No expenses recorded to calculate distribution."
                    color: themeEngine.secondaryText
                    font.pixelSize: 13
                    visible: reportsVM.categoryShares.length === 0
                }

                Repeater {
                    model: reportsVM.categoryShares

                    Column {
                        width: parent.width
                        spacing: 4

                        Row {
                            width: parent.width

                            Rectangle {
                                width: 10
                                height: 10
                                radius: 5
                                color: modelData.color
                                anchors.verticalCenter: parent.verticalCenter
                            }

                            Item { width: 8; height: 1 }

                            Text {
                                text: modelData.category
                                color: themeEngine.primaryText
                                font.pixelSize: 13
                                font.weight: Font.Medium
                                width: parent.width - shareText.width - 20
                                elide: Text.ElideRight
                                anchors.verticalCenter: parent.verticalCenter
                            }

                            Text {
                                id: shareText
                                text: modelData.amount + " (" + modelData.percentage.toFixed(1) + "%)"
                                color: themeEngine.secondaryText
                                font.pixelSize: 12
                                font.features: { "tnum": 1 }
                                anchors.verticalCenter: parent.verticalCenter
                            }
                        }

                        Rectangle {
                            width: parent.width
                            height: 6
                            radius: 3
                            color: themeEngine.elevatedSurface

                            Rectangle {
                                width: Math.min(parent.width, parent.width * (modelData.percentage / 100.0))
                                height: parent.height
                                radius: 3
                                color: modelData.color
                            }
                        }
                    }
                }
            }
        }
    }
}
