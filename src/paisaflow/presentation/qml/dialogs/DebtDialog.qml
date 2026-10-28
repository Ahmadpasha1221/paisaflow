import QtQuick 2.15
import QtQuick.Controls 2.15
import "../components"

ModalDialog {
    id: root

    title: "Record Debt / Loan"
    contentWidth: 440

    property string debtType: "lent" // 'lent' or 'borrowed'

    content: Column {
        width: parent.width
        spacing: 14

        // Lent vs Borrowed selector
        Row {
            width: parent.width
            spacing: 12

            Rectangle {
                width: (parent.width - 12) / 2
                height: 38
                radius: 8
                color: root.debtType === "lent" ? themeEngine.elevatedSurface : "transparent"
                border.color: root.debtType === "lent" ? themeEngine.positive : themeEngine.divider
                border.width: 1

                Text {
                    text: "Money Lent (Receivable)"
                    color: root.debtType === "lent" ? themeEngine.positive : themeEngine.secondaryText
                    font.pixelSize: 12
                    font.weight: Font.DemiBold
                    anchors.centerIn: parent
                }

                MouseArea {
                    anchors.fill: parent
                    onClicked: root.debtType = "lent"
                }
            }

            Rectangle {
                width: (parent.width - 12) / 2
                height: 38
                radius: 8
                color: root.debtType === "borrowed" ? themeEngine.elevatedSurface : "transparent"
                border.color: root.debtType === "borrowed" ? themeEngine.negative : themeEngine.divider
                border.width: 1

                Text {
                    text: "Money Borrowed (Payable)"
                    color: root.debtType === "borrowed" ? themeEngine.negative : themeEngine.secondaryText
                    font.pixelSize: 12
                    font.weight: Font.DemiBold
                    anchors.centerIn: parent
                }

                MouseArea {
                    anchors.fill: parent
                    onClicked: root.debtType = "borrowed"
                }
            }
        }

        FormField {
            label: "Counterparty (Person / Entity) *"
            Rectangle {
                width: parent.width
                height: 42
                radius: 8
                color: "transparent"
                border.color: "transparent"

                TextInputField {
                    id: counterpartyInput
                    anchors.fill: parent
                    placeholderText: "e.g. Ramesh, Personal Loan Co."
                }
            }
        }

        FormField {
            label: "Principal Amount *"
            CurrencyInput {
                id: principalInput
                placeholderText: "0.00"
            }
        }

        FormField {
            label: "Member *"
            SelectField {
                id: personSelect
                model: appVM.people
                textRoleName: "name"
                valueRoleName: "id"
            }
        }

        FormField {
            label: "Due Date (Optional)"
            DateInput {
                id: dateInput
                placeholderText: "YYYY-MM-DD"
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
            text: "Record Debt"
            width: (parent.width - 12) / 2
            onClicked: root.submit()
        }
    }

    function submit() {
        if (!counterpartyInput.text.trim()) {
            appVM.showToast("Counterparty cannot be empty.", true);
            return;
        }
        if (!principalInput.text.trim()) {
            appVM.showToast("Principal amount cannot be empty.", true);
            return;
        }

        var success = debtVM.recordDebt(
            root.debtType,
            personSelect.currentValue,
            counterpartyInput.text.trim(),
            principalInput.text,
            dateInput.text.trim(),
            ""
        );

        if (success) {
            counterpartyInput.text = "";
            principalInput.text = "";
            dateInput.text = "";
            appVM.notifyDataChanged();
            root.closed();
        }
    }
}
