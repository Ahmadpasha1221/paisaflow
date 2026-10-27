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

        PageHeader {
            title: "Savings Goals"
            subtitle: "Track targets, emergency reserves, vacation funds, and progress."

            actions: [
                PrimaryButton {
                    text: "New Goal"
                    iconName: "plus"
                    onClicked: appVM.openDialog("goal")
                }
            ]
        }

        EmptyState {
            visible: goalVM.goals.length === 0
            title: "No savings goals created"
            description: "Set financial goals to build emergency funds, prepare for purchases, or invest."
            actionText: "Create First Goal"
            onActionTriggered: appVM.openDialog("goal")
        }

        Flow {
            width: parent.width
            spacing: 16
            visible: goalVM.goals.length > 0

            Repeater {
                model: goalVM.goals

                Rectangle {
                    width: (parent.width - 16) / 2
                    implicitHeight: goalCol.implicitHeight + 36
                    radius: 12
                    color: themeEngine.primarySurface
                    border.color: themeEngine.divider
                    border.width: 1

                    Column {
                        id: goalCol
                        anchors.fill: parent
                        anchors.margins: 18
                        spacing: 12

                        Row {
                            width: parent.width

                            Column {
                                width: parent.width - badge.width - 8
                                spacing: 2

                                Text {
                                    text: modelData.name
                                    color: themeEngine.primaryText
                                    font.pixelSize: 16
                                    font.weight: Font.DemiBold
                                    font.family: "Segoe UI, Inter, sans-serif"
                                    elide: Text.ElideRight
                                    width: parent.width
                                }

                                Text {
                                    text: "Owner: " + modelData.personName + " • Target Date: " + modelData.targetDate
                                    color: themeEngine.secondaryText
                                    font.pixelSize: 12
                                    font.family: "Segoe UI, Inter, sans-serif"
                                }
                            }

                            StatusBadge {
                                id: badge
                                text: modelData.isAchieved ? "Achieved" : (modelData.progress.toFixed(1) + "%")
                                level: modelData.isAchieved ? "positive" : "informational"
                            }
                        }

                        // Progress Bar
                        Rectangle {
                            width: parent.width
                            height: 8
                            radius: 4
                            color: themeEngine.elevatedSurface

                            Rectangle {
                                width: Math.min(parent.width, parent.width * (modelData.progress / 100.0))
                                height: parent.height
                                radius: 4
                                color: themeEngine.positive
                            }
                        }

                        Item {
                            width: parent.width
                            height: 38

                            Text {
                                text: "Saved: " + modelData.current + " of " + modelData.target
                                color: themeEngine.secondaryText
                                font.pixelSize: 12
                                font.family: "Segoe UI, Inter, sans-serif"
                                font.features: { "tnum": 1 }
                                anchors.left: parent.left
                                anchors.verticalCenter: parent.verticalCenter
                            }

                            SecondaryButton {
                                text: "Contribute"
                                iconName: "plus"
                                anchors.right: parent.right
                                anchors.verticalCenter: parent.verticalCenter
                                onClicked: {
                                    contributeDialog.goalId = modelData.id;
                                    contributeDialog.goalName = modelData.name;
                                    contributeDialog.open = true;
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
