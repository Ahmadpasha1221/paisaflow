import QtQuick 2.15
import QtQuick.Controls 2.15
import "../components"

ModalDialog {
    id: root

    title: "New Savings Goal"
    contentWidth: 440

    content: Column {
        width: parent.width
        spacing: 14

        FormField {
            label: "Goal Name *"
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
                    placeholderText: "e.g. Emergency Fund, New Car, Goa Vacation"
                    background: Item {}
                    selectByMouse: true
                }
            }
        }

        FormField {
            label: "Target Amount *"
            CurrencyInput {
                id: targetInput
                placeholderText: "0.00"
            }
        }

        FormField {
            label: "Goal Owner *"
            SelectField {
                id: personSelect
                model: appVM.people
                textRoleName: "name"
                valueRoleName: "id"
            }
        }

        FormField {
            label: "Target Date (Optional)"
            DateInput {
                id: dateInput
                placeholderText: "YYYY-MM-DD"
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
                text: "Create Goal"
                width: (parent.width - 12) / 2
                onClicked: root.submit()
            }
        }
    }

    function submit() {
        if (!nameInput.text.trim()) {
            appVM.showToast("Goal name cannot be empty.", true);
            return;
        }
        if (!targetInput.text.trim()) {
            appVM.showToast("Target amount cannot be empty.", true);
            return;
        }

        var success = goalVM.createGoal(
            nameInput.text.trim(),
            targetInput.text,
            personSelect.currentValue,
            dateInput.text.trim(),
            ""
        );

        if (success) {
            nameInput.text = "";
            targetInput.text = "";
            dateInput.text = "";
            appVM.notifyDataChanged();
            root.closed();
        }
    }
}
