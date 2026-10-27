import QtQuick 2.15
import QtQuick.Controls 2.15
import "../components"

ModalDialog {
    id: root

    property int goalId: 0
    property string goalName: ""

    title: "Contribute to Goal"
    contentWidth: 400

    content: Column {
        width: parent.width
        spacing: 14

        Text {
            text: "Adding allocation to: " + root.goalName
            color: themeEngine.secondaryText
            font.pixelSize: 13
            font.family: "Segoe UI, Inter, sans-serif"
        }

        FormField {
            label: "Contribution Amount *"
            CurrencyInput {
                id: amountInput
                placeholderText: "0.00"
            }
        }

        Item { width: 1; height: 8 }

        Row {
            width: parent.width
            spacing: 12

            SecondaryButton {
                text: "Cancel"
                width: (parent.width - 12) / 2
                onClicked: root.closed()
            }

            PrimaryButton {
                text: "Save Contribution"
                width: (parent.width - 12) / 2
                onClicked: root.submit()
            }
        }
    }

    function submit() {
        if (!amountInput.text.trim()) {
            appVM.showToast("Contribution amount cannot be empty.", true);
            return;
        }

        var success = goalVM.contribute(root.goalId, amountInput.text, "");
        if (success) {
            amountInput.text = "";
            appVM.notifyDataChanged();
            root.closed();
        }
    }
}
