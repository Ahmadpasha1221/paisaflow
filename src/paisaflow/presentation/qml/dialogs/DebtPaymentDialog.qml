import QtQuick 2.15
import QtQuick.Controls 2.15
import "../components"

ModalDialog {
    id: root

    property int debtId: 0
    property string counterparty: ""
    property string remaining: ""

    title: "Record Repayment"
    contentWidth: 400

    content: Column {
        width: parent.width
        spacing: 14

        Text {
            text: "Recording repayment for: " + root.counterparty + "\nRemaining: " + root.remaining
            color: themeEngine.secondaryText
            font.pixelSize: 13
            font.family: "Segoe UI, Inter, sans-serif"
            lineHeight: 1.3
        }

        FormField {
            label: "Repayment Amount *"
            CurrencyInput {
                id: amountInput
                placeholderText: "0.00"
            }
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

        PrimaryButton {
            text: "Save Repayment"
            width: (parent.width - 12) / 2
            onClicked: root.submit()
        }
    }

    function submit() {
        if (!amountInput.text.trim()) {
            appVM.showToast("Repayment amount cannot be empty.", true);
            return;
        }

        var success = debtVM.recordPayment(root.debtId, amountInput.text, "");
        if (success) {
            amountInput.text = "";
            appVM.notifyDataChanged();
            root.closed();
        }
    }
}
