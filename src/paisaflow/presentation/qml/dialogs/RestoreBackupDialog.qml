import QtQuick 2.15
import QtQuick.Controls 2.15
import "../components"

ModalDialog {
    id: root

    property string backupPath: ""
    property string backupName: ""

    title: "Restore from Backup"
    contentWidth: 460

    content: Column {
        width: parent.width
        spacing: 14

        Text {
            text: "This will replace all current records with the contents of the selected backup:"
            color: themeEngine.secondaryText
            font.pixelSize: 13
            font.family: "Segoe UI, Inter, sans-serif"
            wrapMode: Text.WordWrap
            width: parent.width
        }

        Text {
            text: root.backupName
            color: themeEngine.primaryText
            font.pixelSize: 14
            font.weight: Font.DemiBold
            font.family: "Consolas, monospace"
            elide: Text.ElideMiddle
            width: parent.width
        }

        Text {
            text: "A safety copy of your current database is saved first, so this can be undone by restoring that copy."
            color: themeEngine.secondaryText
            font.pixelSize: 12
            font.family: "Segoe UI, Inter, sans-serif"
            wrapMode: Text.WordWrap
            width: parent.width
        }

    }

    footer: Row {
        width: parent.width
        spacing: 12

        SecondaryButton {
            text: "Cancel"
            width: (parent.width - 12) / 2
            onClicked: root.closed()
        }

        DestructiveButton {
            text: "Restore Now"
            width: (parent.width - 12) / 2
            onClicked: root.submit()
        }
    }

    function submit() {
        var restored = settingsVM.restoreBackup(root.backupPath);
        root.closed();
        if (restored) {
            appVM.showToast("Database restored from backup.");
        }
    }
}
