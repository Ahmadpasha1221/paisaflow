import QtQuick 2.15
import QtQuick.Controls 2.15
import "../components"

ModalDialog {
    id: root

    title: "New Transaction"
    contentWidth: 500

    property string activeTab: "expense" // 'expense', 'income', 'transfer'

    content: Column {
        width: parent.width
        spacing: 14

        // Segmented Type Selector
        Rectangle {
            width: parent.width
            height: 38
            radius: 8
            color: themeEngine.isDark ? "#1A2821" : "#E4ECE0"
            border.color: themeEngine.divider
            border.width: 1

            Row {
                anchors.fill: parent
                anchors.margins: 3
                spacing: 4

                // Expense Tab
                Rectangle {
                    width: (parent.width - 8) / 3
                    height: parent.height
                    radius: 6
                    color: root.activeTab === "expense" ? themeEngine.elevatedSurface : "transparent"
                    border.color: root.activeTab === "expense" ? themeEngine.negative : "transparent"
                    border.width: 1

                    Text {
                        text: "Expense"
                        color: root.activeTab === "expense" ? themeEngine.negative : themeEngine.secondaryText
                        font.pixelSize: 13
                        font.weight: Font.DemiBold
                        anchors.centerIn: parent
                    }

                    MouseArea {
                        anchors.fill: parent
                        onClicked: root.activeTab = "expense"
                    }
                }

                // Income Tab
                Rectangle {
                    width: (parent.width - 8) / 3
                    height: parent.height
                    radius: 6
                    color: root.activeTab === "income" ? themeEngine.elevatedSurface : "transparent"
                    border.color: root.activeTab === "income" ? themeEngine.positive : "transparent"
                    border.width: 1

                    Text {
                        text: "Income"
                        color: root.activeTab === "income" ? themeEngine.positive : themeEngine.secondaryText
                        font.pixelSize: 13
                        font.weight: Font.DemiBold
                        anchors.centerIn: parent
                    }

                    MouseArea {
                        anchors.fill: parent
                        onClicked: root.activeTab = "income"
                    }
                }

                // Transfer Tab
                Rectangle {
                    width: (parent.width - 8) / 3
                    height: parent.height
                    radius: 6
                    color: root.activeTab === "transfer" ? themeEngine.elevatedSurface : "transparent"
                    border.color: root.activeTab === "transfer" ? themeEngine.informational : "transparent"
                    border.width: 1

                    Text {
                        text: "Transfer"
                        color: root.activeTab === "transfer" ? themeEngine.informational : themeEngine.secondaryText
                        font.pixelSize: 13
                        font.weight: Font.DemiBold
                        anchors.centerIn: parent
                    }

                    MouseArea {
                        anchors.fill: parent
                        onClicked: root.activeTab = "transfer"
                    }
                }
            }
        }

        // Amount & Date
        Row {
            width: parent.width
            spacing: 12

            FormField {
                label: "Amount *"
                width: (parent.width - 12) * 0.6
                CurrencyInput {
                    id: amountInput
                    placeholderText: "0.00"
                }
            }

            FormField {
                label: "Date"
                width: (parent.width - 12) * 0.4
                DateInput {
                    id: dateInput
                    text: new Date().toISOString().substring(0, 10)
                }
            }
        }

        // Description
        FormField {
            label: "Description *"
            Rectangle {
                width: parent.width
                height: 42
                radius: 8
                color: themeEngine.isDark ? "#1F2E26" : "#FFFFFF"
                border.color: descInput.activeFocus ? themeEngine.primaryAccent : themeEngine.divider
                border.width: descInput.activeFocus ? 1.5 : 1

                TextField {
                    id: descInput
                    anchors.fill: parent
                    anchors.margins: 10
                    color: themeEngine.primaryText
                    placeholderTextColor: themeEngine.secondaryText
                    placeholderText: "e.g. Grocery shopping, Salary deposit"
                    background: Item {}
                    selectByMouse: true
                }
            }
        }

        // Account selectors (Conditional based on activeTab)
        Row {
            width: parent.width
            spacing: 12

            FormField {
                label: root.activeTab === "transfer" ? "From Account *" : "Account *"
                width: root.activeTab === "transfer" ? (parent.width - 12) / 2 : parent.width
                SelectField {
                    id: accountSelect
                    model: transactionVM.accountOptions
                    textRoleName: "name"
                    valueRoleName: "id"
                }
            }

            FormField {
                label: "To Account *"
                width: (parent.width - 12) / 2
                visible: root.activeTab === "transfer"
                SelectField {
                    id: destAccountSelect
                    model: transactionVM.accountOptions
                    textRoleName: "name"
                    valueRoleName: "id"
                }
            }
        }

        // Category & Person (Hidden for transfer)
        Row {
            width: parent.width
            spacing: 12
            visible: root.activeTab !== "transfer"

            FormField {
                label: "Category *"
                width: (parent.width - 12) / 2
                SelectField {
                    id: categorySelect
                    model: root.activeTab === "income" ? transactionVM.incomeCategoryOptions : transactionVM.expenseCategoryOptions
                    textRoleName: "name"
                    valueRoleName: "id"
                }
            }

            FormField {
                label: "Person *"
                width: (parent.width - 12) / 2
                SelectField {
                    id: personSelect
                    model: appVM.people
                    textRoleName: "name"
                    valueRoleName: "id"
                }
            }
        }

        // Person selector for Transfer
        FormField {
            label: "Person Responsible *"
            visible: root.activeTab === "transfer"
            SelectField {
                id: transferPersonSelect
                model: appVM.people
                textRoleName: "name"
                valueRoleName: "id"
            }
        }

        // Payment Method
        FormField {
            label: "Payment Method"
            SelectField {
                id: paymentMethodSelect
                model: [
                    { id: "upi", name: "UPI" },
                    { id: "credit_card", name: "Credit Card" },
                    { id: "debit_card", name: "Debit Card" },
                    { id: "bank_transfer", name: "Bank Transfer" },
                    { id: "cash", name: "Cash" },
                    { id: "other", name: "Other" }
                ]
                textRoleName: "name"
                valueRoleName: "id"
            }
        }

    }

    // Action buttons stay pinned below the scrolling form.
    footer: Row {
        width: parent.width
        spacing: 12

        SecondaryButton {
            text: "Cancel"
            width: (parent.width - 12) / 2
            onClicked: root.closed()
        }

        PrimaryButton {
            text: "Save Transaction"
            width: (parent.width - 12) / 2
            onClicked: root.submit()
        }
    }

    function submit() {
        var success = false;
        var pId = root.activeTab === "transfer" ? transferPersonSelect.currentValue : personSelect.currentValue;
        var method = paymentMethodSelect.currentValue ? paymentMethodSelect.currentValue : "upi";

        if (!amountInput.text.trim()) {
            appVM.showToast("Please enter an amount.", true);
            return;
        }
        if (!descInput.text.trim()) {
            appVM.showToast("Please enter a description.", true);
            return;
        }

        if (root.activeTab === "income") {
            success = transactionVM.addIncome(
                dateInput.text,
                descInput.text,
                amountInput.text,
                accountSelect.currentValue,
                pId,
                categorySelect.currentValue,
                method,
                ""
            );
        } else if (root.activeTab === "expense") {
            success = transactionVM.addExpense(
                dateInput.text,
                descInput.text,
                amountInput.text,
                accountSelect.currentValue,
                pId,
                categorySelect.currentValue,
                method,
                ""
            );
        } else if (root.activeTab === "transfer") {
            success = transactionVM.addTransfer(
                dateInput.text,
                descInput.text,
                amountInput.text,
                accountSelect.currentValue,
                destAccountSelect.currentValue,
                pId,
                method,
                ""
            );
        }

        if (success) {
            // transactionVM.dataChanged already refreshed the rest of the shell.
            amountInput.text = "";
            descInput.text = "";
            root.closed();
        }
    }
}
