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
            title: "People & Household"
            subtitle: "Manage household members, profile colors, and individual expense scopes."

            actions: [
                PrimaryButton {
                    text: "Add Member"
                    iconName: "plus"
                    onClicked: appVM.openDialog("person")
                }
            ]
        }

        // Empty state
        EmptyState {
            visible: personVM.people.length === 0
            title: "No people added"
            description: "Add yourself or family members to organize transactions by person."
            actionText: "Add First Member"
            onActionTriggered: appVM.openDialog("person")
        }

        // People Grid
        Flow {
            width: parent.width
            spacing: 16
            visible: personVM.people.length > 0

            Repeater {
                model: personVM.people

                Rectangle {
                    width: (parent.width - 16) / 2
                    height: 90
                    radius: 12
                    color: themeEngine.primarySurface
                    border.color: themeEngine.divider
                    border.width: 1

                    Row {
                        anchors.fill: parent
                        anchors.margins: 18
                        spacing: 16

                        // Avatar Circle
                        Rectangle {
                            width: 48
                            height: 48
                            radius: 24
                            color: modelData.colorCode
                            anchors.verticalCenter: parent.verticalCenter

                            Text {
                                text: modelData.name.length > 0 ? modelData.name.substring(0, 1).toUpperCase() : "?"
                                color: "#17251F"
                                font.pixelSize: 20
                                font.weight: Font.Bold
                                font.family: "Segoe UI, Inter, sans-serif"
                                anchors.centerIn: parent
                            }
                        }

                        Column {
                            anchors.verticalCenter: parent.verticalCenter
                            spacing: 4

                            Text {
                                text: modelData.name
                                color: themeEngine.primaryText
                                font.pixelSize: 16
                                font.weight: Font.DemiBold
                                font.family: "Segoe UI, Inter, sans-serif"
                            }

                            Text {
                                text: "Household Member • Active"
                                color: themeEngine.secondaryText
                                font.pixelSize: 12
                                font.family: "Segoe UI, Inter, sans-serif"
                            }
                        }
                    }
                }
            }
        }
    }
}
