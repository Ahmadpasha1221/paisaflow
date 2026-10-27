import QtQuick 2.15
import QtQuick.Controls 2.15
import "../components"

ModalDialog {
    id: root

    title: "New Account"
    contentWidth: 440

    content: Column {
        width: parent.width
        spacing: 14

        FormField {
            label: "Account Name *"
            Rectangle {
                width: parent.width
                height: 42
                radius: 8
                color: themeEngine.isDark ? "#1F2E26" : "#FFFFFF"
                border.color: nameInput.activeFocus ? themeEngine.primaryAccent : themeEngine.divider
                border.width: nameInput.activeFocus ? 1.5 : 1

                TextField {
                    id: nameInput
                    anchors.fill: parent
                    anchors.margins: 10
                    color: themeEngine.primaryText
                    placeholderTextColor: themeEngine.secondaryText
                    placeholderText: "e.g. HDFC Salary, Wallet Cash, Axis Card"
                    background: Item {}
                    selectByMouse: true
                }
            }
        }

        FormField {
            label: "Account Type *"
            SelectField {
                id: typeSelect
                model: [
                    { id: "bank", name: "Bank Account" },
                    { id: "savings", name: "Savings Account" },
                    { id: "cash", name: "Cash Wallet" },
                    { id: "credit_card", name: "Credit Card (Liability)" },
                    { id: "other", name: "Other Account" }
                ]
                textRoleName: "name"
                valueRoleName: "id"
            }
        }

        FormField {
            label: "Account Owner *"
            SelectField {
                id: ownerSelect
                model: appVM.people
                textRoleName: "name"
                valueRoleName: "id"
            }
        }

        FormField {
            label: "Opening Balance"
            CurrencyInput {
                id: openingBalanceInput
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
            text: "Create Account"
            width: (parent.width - 12) / 2
            onClicked: root.submit()
        }
    }

    function submit() {
        if (!nameInput.text.trim()) {
            appVM.showToast("Account name cannot be empty.", true);
            return;
        }

        var success = accountVM.createAccount(
            nameInput.text.trim(),
            typeSelect.currentValue,
            ownerSelect.currentValue,
            openingBalanceInput.text,
            ""
        );

        if (success) {
            nameInput.text = "";
            openingBalanceInput.text = "";
            appVM.notifyDataChanged();
            root.closed();
        }
    }
}
