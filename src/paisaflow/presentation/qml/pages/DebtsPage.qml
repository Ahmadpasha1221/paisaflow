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

        PageHeader {
            title: "Debts & Loans"
            subtitle: "Track money lent to others and loans borrowed with repayment histories."

            actions: [
                PrimaryButton {
                    text: "Record Debt"
                    iconName: "plus"
                    onClicked: appVM.openDialog("debt")
                }
            ]
        }

        EmptyState {
            visible: debtVM.debts.length === 0
            title: "No debts or loans recorded"
            description: "Record money you have lent to others or money borrowed to keep track of dues."
            actionText: "Record First Debt"
            onActionTriggered: appVM.openDialog("debt")
        }

        Flow {
            width: parent.width
            spacing: 16
            visible: debtVM.debts.length > 0

            Repeater {
                model: debtVM.debts

                Rectangle {
                    width: (parent.width - 16) / 2
                    implicitHeight: debtCol.implicitHeight + 36
                    radius: 12
                    color: themeEngine.primarySurface
                    border.color: themeEngine.divider
                    border.width: 1

                    Column {
                        id: debtCol
                        anchors.fill: parent
                        anchors.margins: 18
                        spacing: 12

                        Row {
                            width: parent.width

                            Column {
                                width: parent.width - badge.width - 8
                                spacing: 2

                                Text {
                                    text: modelData.counterparty
                                    color: themeEngine.primaryText
                                    font.pixelSize: 16
                                    font.weight: Font.DemiBold
                                    font.family: "Segoe UI, Inter, sans-serif"
                                    elide: Text.ElideRight
                                    width: parent.width
                                }

                                Text {
                                    text: modelData.debtTypeDisplay + " • " + modelData.personName
                                    color: themeEngine.secondaryText
                                    font.pixelSize: 12
                                    font.family: "Segoe UI, Inter, sans-serif"
                                }
                            }

                            StatusBadge {
                                id: badge
                                text: modelData.isSettled ? "Settled" : (modelData.isLiability ? "You Owe" : "Owed to You")
                                level: modelData.isSettled ? "positive" : (modelData.isLiability ? "negative" : "informational")
                            }
                        }

                        Rectangle {
                            width: parent.width
                            height: 1
                            color: themeEngine.divider
                        }

                        Row {
                            width: parent.width

                            Column {
                                width: parent.width - repayBtn.width - 8
                                spacing: 2

                                Text {
                                    text: "Remaining: " + modelData.remaining + " (Principal: " + modelData.principal + ")"
                                    color: modelData.isLiability ? themeEngine.negative : themeEngine.positive
                                    font.pixelSize: 14
                                    font.weight: Font.DemiBold
                                    font.family: "Segoe UI, Inter, sans-serif"
                                    font.features: { "tnum": 1 }
                                }

                                Text {
                                    text: "Due: " + modelData.dueDate
                                    color: themeEngine.secondaryText
                                    font.pixelSize: 12
                                    font.family: "Segoe UI, Inter, sans-serif"
                                }
                            }

                            SecondaryButton {
                                id: repayBtn
                                text: "Repay"
                                iconName: "plus"
                                visible: !modelData.isSettled
                                anchors.verticalCenter: parent.verticalCenter
                                onClicked: {
                                    debtPaymentDialog.debtId = modelData.id;
                                    debtPaymentDialog.counterparty = modelData.counterparty;
                                    debtPaymentDialog.remaining = modelData.remaining;
                                    debtPaymentDialog.open = true;
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
