import QtQuick 2.15
import QtQuick.Controls 2.15
import "../components"

ScrollView {
    id: root

    contentWidth: availableWidth
    clip: true

    Column {
        width: parent.width
        spacing: 20
        padding: 24

        PageHeader {
            title: "Accounts & Balances"
            subtitle: "Cash wallets, bank accounts, credit cards, and tracked balances."

            actions: [
                PrimaryButton {
                    text: "Add Account"
                    iconName: "plus"
                    onClicked: appVM.openDialog("account")
                }
            ]
        }

        // Empty state
        EmptyState {
            visible: accountVM.accounts.length === 0
            title: "No accounts configured"
            description: "Add a bank account, cash wallet, or credit card to begin tracking balances."
            actionText: "Add First Account"
            onActionTriggered: appVM.openDialog("account")
        }

        // Accounts Grid
        Flow {
            width: parent.width
            spacing: 16
            visible: accountVM.accounts.length > 0

            Repeater {
                model: accountVM.accounts

                AccountCard {
                    width: (parent.width - 16) / 2
                    accountId: modelData.id
                    name: modelData.name
                    accountType: modelData.accountType
                    accountTypeDisplay: modelData.accountTypeDisplay
                    ownerName: modelData.ownerName
                    balance: modelData.balance
                    isLiability: modelData.isLiability
                    notes: modelData.notes
                    onArchiveRequested: (id) => {
                        accountVM.archiveAccount(id);
                        appVM.notifyDataChanged();
                    }
                }
            }
        }
    }
}
