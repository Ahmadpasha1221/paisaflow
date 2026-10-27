import QtQuick 2.15
import QtQuick.Controls 2.15
import "../components"

// Reusable destructive confirmation prompt (used when deleting a transaction).
ModalDialog {
    id: root

    property string message: ""
    property string confirmText: "Delete"
    property string cancelText: "Cancel"
    property int transactionId: 0

    signal confirmed()

    contentWidth: 440

    content: Text {
        width: parent.width
        text: root.message
        color: themeEngine.secondaryText
        font.pixelSize: 13
        font.family: "Segoe UI, Inter, sans-serif"
        wrapMode: Text.WordWrap
        lineHeight: 1.35
    }

    footer: Row {
        width: parent.width
        spacing: 12

        SecondaryButton {
            text: root.cancelText
            width: (parent.width - 12) / 2
            onClicked: root.closed()
        }

        DestructiveButton {
            text: root.confirmText
            iconName: "trash"
            width: (parent.width - 12) / 2
            onClicked: {
                root.confirmed();
                root.closed();
            }
        }
    }
}
