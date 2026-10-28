import QtQuick 2.15
import QtQuick.Controls 2.15
import "../components"

ModalDialog {
    id: root

    title: "Create Budget"
    contentWidth: 440

    content: Column {
        width: parent.width
        spacing: 14

        FormField {
            label: "Budget Name *"
            Rectangle {
                width: parent.width
                height: 42
                radius: 8
                color: "transparent"
                border.color: "transparent"

                TextInputField {
                    id: nameInput
                    anchors.fill: parent
                    placeholderText: "e.g. October Groceries, Dining Out"
                }
            }
        }

        FormField {
            label: "Category (Optional)"
            SelectField {
                id: categorySelect
                model: [{ id: 0, name: "All Categories (Global)" }].concat(transactionVM.expenseCategoryOptions)
                textRoleName: "name"
                valueRoleName: "id"
            }
        }

        FormField {
            label: "Member (Optional)"
            SelectField {
                id: personSelect
                model: [{ id: 0, name: "Household (All Members)" }].concat(appVM.people)
                textRoleName: "name"
                valueRoleName: "id"
            }
        }

        FormField {
            label: "Monthly Limit Amount *"
            CurrencyInput {
                id: limitInput
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
            text: "Create Budget"
            width: (parent.width - 12) / 2
            onClicked: root.submit()
        }
    }

    function submit() {
        if (!nameInput.text.trim()) {
            appVM.showToast("Budget name cannot be empty.", true);
            return;
        }
        if (!limitInput.text.trim()) {
            appVM.showToast("Limit amount cannot be empty.", true);
            return;
        }

        var today = new Date();
        var start = new Date(today.getFullYear(), today.getMonth(), 1).toISOString().substring(0, 10);
        var end = new Date(today.getFullYear(), today.getMonth() + 1, 0).toISOString().substring(0, 10);

        var success = budgetVM.createBudget(
            nameInput.text.trim(),
            categorySelect.currentValue,
            personSelect.currentValue,
            "monthly",
            start,
            end,
            limitInput.text
        );

        if (success) {
            nameInput.text = "";
            limitInput.text = "";
            appVM.notifyDataChanged();
            root.closed();
        }
    }
}
