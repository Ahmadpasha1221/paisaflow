import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Dialogs
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
            title: "Settings & System Management"
            subtitle: "Theme preferences, offline storage configuration, backups, and CSV data export."
        }

        // Appearance & Localization
        Rectangle {
            width: parent.width
            implicitHeight: appCol.implicitHeight + 36
            radius: 12
            color: themeEngine.primarySurface
            border.color: themeEngine.divider
            border.width: 1

            Column {
                id: appCol
                anchors.fill: parent
                anchors.margins: 18
                spacing: 14

                Text {
                    text: "Appearance & Localization"
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

                Row {
                    width: parent.width

                    Column {
                        width: parent.width - themeToggleBtn.width
                        spacing: 2
                        anchors.verticalCenter: parent.verticalCenter

                        Text {
                            text: "Interface Theme"
                            color: themeEngine.primaryText
                            font.pixelSize: 14
                            font.weight: Font.Medium
                        }

                        Text {
                            text: "Toggle between Flowline Dark (default) and Light theme."
                            color: themeEngine.secondaryText
                            font.pixelSize: 12
                        }
                    }

                    SecondaryButton {
                        id: themeToggleBtn
                        text: themeEngine.isDark ? "Dark Theme" : "Light Theme"
                        iconName: themeEngine.isDark ? "moon" : "sun"
                        anchors.verticalCenter: parent.verticalCenter
                        onClicked: themeEngine.toggleTheme()
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
                        width: parent.width * 0.5
                        spacing: 2

                        Text {
                            text: "Primary Currency"
                            color: themeEngine.primaryText
                            font.pixelSize: 14
                            font.weight: Font.Medium
                        }

                        Text {
                            text: settingsVM.currency
                            color: themeEngine.primaryAccent
                            font.pixelSize: 13
                            font.weight: Font.DemiBold
                        }
                    }

                    Column {
                        width: parent.width * 0.5
                        spacing: 2

                        Text {
                            text: "Locale & Numbering"
                            color: themeEngine.primaryText
                            font.pixelSize: 14
                            font.weight: Font.Medium
                        }

                        Text {
                            text: settingsVM.locale + " (Lakhs & Crores Tabular)"
                            color: themeEngine.secondaryText
                            font.pixelSize: 13
                        }
                    }
                }
            }
        }

        // Data Storage & Security Info
        Rectangle {
            width: parent.width
            implicitHeight: storageCol.implicitHeight + 36
            radius: 12
            color: themeEngine.primarySurface
            border.color: themeEngine.divider
            border.width: 1

            Column {
                id: storageCol
                anchors.fill: parent
                anchors.margins: 18
                spacing: 14

                Text {
                    text: "Local Storage & Privacy"
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

                Column {
                    width: parent.width
                    spacing: 4

                    Text {
                        text: "Database File Location:"
                        color: themeEngine.secondaryText
                        font.pixelSize: 12
                    }

                    Text {
                        text: settingsVM.databasePath
                        color: themeEngine.primaryText
                        font.pixelSize: 13
                        font.family: "Consolas, monospace"
                        font.weight: Font.Medium
                        elide: Text.ElideMiddle
                        width: parent.width
                    }
                }

                Column {
                    width: parent.width
                    spacing: 4

                    Text {
                        text: "Backup Storage Directory:"
                        color: themeEngine.secondaryText
                        font.pixelSize: 12
                    }

                    Text {
                        text: settingsVM.backupDirectory
                        color: themeEngine.primaryText
                        font.pixelSize: 13
                        font.family: "Consolas, monospace"
                        font.weight: Font.Medium
                        elide: Text.ElideMiddle
                        width: parent.width
                    }
                }
            }
        }

        // Backup, Restore & Export Actions
        Rectangle {
            width: parent.width
            implicitHeight: actionCol.implicitHeight + 36
            radius: 12
            color: themeEngine.primarySurface
            border.color: themeEngine.divider
            border.width: 1

            Column {
                id: actionCol
                anchors.fill: parent
                anchors.margins: 18
                spacing: 16

                Text {
                    text: "Backup & Export Tools"
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

                Row {
                    width: parent.width
                    spacing: 16

                    PrimaryButton {
                        text: "Create Backup Now"
                        iconName: "overview"
                        onClicked: {
                            var path = settingsVM.createBackup();
                            if (path) {
                                appVM.showToast("Backup created in backup folder.");
                            }
                        }
                    }

                    SecondaryButton {
                        text: "Export Transactions to CSV"
                        iconName: "transactions"
                        onClicked: {
                            var path = settingsVM.exportTransactionsCsv("");
                            if (path) {
                                appVM.showToast("Exported to CSV successfully.");
                            }
                        }
                    }
                }
            }
        }

        // About Box
        Rectangle {
            width: parent.width
            implicitHeight: aboutCol.implicitHeight + 28
            radius: 12
            color: themeEngine.isDark ? "#1B2A22" : "#EDF1EA"
            border.color: themeEngine.divider
            border.width: 1

            Column {
                id: aboutCol
                anchors.fill: parent
                anchors.margins: 16
                spacing: 4

                Text {
                    text: "PaisaFlow v" + settingsVM.appVersion
                    color: themeEngine.primaryText
                    font.pixelSize: 14
                    font.weight: Font.DemiBold
                }

                Text {
                    text: "100% Offline-first personal and household finance manager.\nNo telemetry, no external accounts, no cloud sync. All records reside securely on your local disk."
                    color: themeEngine.secondaryText
                    font.pixelSize: 12
                    lineHeight: 1.3
                }
            }
        }
    }
}
