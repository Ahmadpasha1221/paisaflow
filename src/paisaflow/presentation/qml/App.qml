import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Window 2.15
import "components"
import "pages"
import "dialogs"

ApplicationWindow {
    id: window

    title: "PaisaFlow — Personal finance, made clear."
    visible: true
    width: 1200
    height: 750
    minimumWidth: 960
    minimumHeight: 600

    color: themeEngine.appBackground

    // Main Shell Layout
    Row {
        anchors.fill: parent

        // Left Navigation Sidebar
        Sidebar {
            id: mainSidebar
            height: parent.height
        }

        // Main Workspace Area
        Column {
            width: parent.width - mainSidebar.width
            height: parent.height

            TopBar {
                id: topBar
                width: parent.width
            }

            // Page Content Stack
            Item {
                width: parent.width
                height: parent.height - topBar.height
                clip: true

                OverviewPage {
                    anchors.fill: parent
                    visible: appVM.activePage === "overview"
                }

                TransactionsPage {
                    anchors.fill: parent
                    visible: appVM.activePage === "transactions"
                }

                AccountsPage {
                    anchors.fill: parent
                    visible: appVM.activePage === "accounts"
                }

                PeoplePage {
                    anchors.fill: parent
                    visible: appVM.activePage === "people"
                }

                BudgetsPage {
                    anchors.fill: parent
                    visible: appVM.activePage === "budgets"
                }

                GoalsPage {
                    anchors.fill: parent
                    visible: appVM.activePage === "goals"
                }

                DebtsPage {
                    anchors.fill: parent
                    visible: appVM.activePage === "debts"
                }

                ReportsPage {
                    anchors.fill: parent
                    visible: appVM.activePage === "reports"
                }

                SettingsPage {
                    anchors.fill: parent
                    visible: appVM.activePage === "settings"
                }
            }
        }
    }

    // Modal Dialogs
    TransactionDialog {
        id: transactionDialog
        anchors.fill: parent
    }

    AccountDialog {
        id: accountDialog
        anchors.fill: parent
    }

    PersonDialog {
        id: personDialog
        anchors.fill: parent
    }

    BudgetDialog {
        id: budgetDialog
        anchors.fill: parent
    }

    GoalDialog {
        id: goalDialog
        anchors.fill: parent
    }

    GoalContributeDialog {
        id: contributeDialog
        anchors.fill: parent
    }

    DebtDialog {
        id: debtDialog
        anchors.fill: parent
    }

    DebtPaymentDialog {
        id: debtPaymentDialog
        anchors.fill: parent
    }

    RestoreBackupDialog {
        id: restoreBackupDialog
        anchors.fill: parent
    }

    ConfirmDialog {
        id: deleteTransactionDialog
        title: "Delete Transaction"

        onConfirmed: transactionVM.voidTransaction(transactionId)
    }

    // Floating Toast Notification
    ToastNotification {
        id: toast
        anchors.top: parent.top
        anchors.horizontalCenter: parent.horizontalCenter
    }

    // Connections to ViewModel Signals
    Connections {
        target: appVM

        function onToastRequested(message, isError) {
            toast.show(message, isError);
        }

        function onDialogRequested(dialogType) {
            switch(dialogType) {
                case "transaction":
                    transactionDialog.open = true;
                    break;
                case "account":
                    accountDialog.open = true;
                    break;
                case "person":
                    personDialog.open = true;
                    break;
                case "budget":
                    budgetDialog.open = true;
                    break;
                case "goal":
                    goalDialog.open = true;
                    break;
                case "debt":
                    debtDialog.open = true;
                    break;
            }
        }

        function onTransactionDeleteRequested(transactionId, description) {
            deleteTransactionDialog.transactionId = transactionId;
            deleteTransactionDialog.message = "Delete \"" + description + "\"? It will be removed from the ledger and kept in History for your records. Balances, budgets and reports are recalculated.";
            deleteTransactionDialog.open = true;
        }

        function onRestoreRequested(backupPath, backupName) {
            restoreBackupDialog.backupPath = backupPath;
            restoreBackupDialog.backupName = backupName;
            restoreBackupDialog.open = true;
        }

        function onHouseholdContextChanged() {
            overviewVM.setPersonFilter(appVM.selectedPersonId);
            transactionVM.setPersonFilter(appVM.selectedPersonId);
            accountVM.setPersonFilter(appVM.selectedPersonId);
            budgetVM.setPersonFilter(appVM.selectedPersonId);
            goalVM.setPersonFilter(appVM.selectedPersonId);
            debtVM.setPersonFilter(appVM.selectedPersonId);
            reportsVM.setPersonFilter(appVM.selectedPersonId);
        }

        function onDataRefreshed() {
            overviewVM.refresh();
            transactionVM.refresh();
            accountVM.refresh();
            budgetVM.refresh();
            goalVM.refresh();
            debtVM.refresh();
            reportsVM.refresh();
        }
    }

    // Transaction actions (delete, failed save) report back through the toast, and every
    // ledger mutation refreshes the dashboards, budgets and reports in one place.
    Connections {
        target: transactionVM

        function onDataChanged() {
            appVM.notifyDataChanged();
        }

        function onOperationSuccess(message) {
            toast.show(message, false);
        }

        function onOperationError(message) {
            toast.show(message, true);
        }
    }

    // Settings: surface restore errors and refresh the shell after a restore.
    Connections {
        target: settingsVM

        function onOperationError(message) {
            toast.show(message, true);
        }

        function onDatabaseRestored() {
            themeEngine.reloadTheme();
            appVM.notifyDataChanged();
        }
    }

    // Keyboard Shortcuts
    Shortcut {
        sequence: "Ctrl+N"
        onActivated: appVM.openDialog("transaction")
    }

    Shortcut {
        sequence: "Ctrl+1"
        onActivated: appVM.navigateTo("overview")
    }

    Shortcut {
        sequence: "Ctrl+2"
        onActivated: appVM.navigateTo("transactions")
    }

    Shortcut {
        sequence: "Ctrl+3"
        onActivated: appVM.navigateTo("accounts")
    }

    Shortcut {
        sequence: "Ctrl+4"
        onActivated: appVM.navigateTo("people")
    }

    Shortcut {
        sequence: "Ctrl+5"
        onActivated: appVM.navigateTo("budgets")
    }

    Shortcut {
        sequence: "Ctrl+6"
        onActivated: appVM.navigateTo("goals")
    }

    Shortcut {
        sequence: "Ctrl+7"
        onActivated: appVM.navigateTo("debts")
    }

    Shortcut {
        sequence: "Ctrl+8"
        onActivated: appVM.navigateTo("reports")
    }

    Shortcut {
        sequence: "Ctrl+9"
        onActivated: appVM.navigateTo("settings")
    }
}
