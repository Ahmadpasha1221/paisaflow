import QtQuick 2.15
import QtQuick.Controls 2.15
import "../components"

ScrollView {
    id: root

    contentWidth: availableWidth
    clip: true
    padding: 24

    Column {
        width: parent.width
        spacing: 20

        PageHeader {
            title: "Category Budgets"
            subtitle: "Monthly spending limits, thresholds (75%, 90%, 100%), and active utilization."

            actions: [
                PrimaryButton {
                    text: "Create Budget"
                    iconName: "plus"
                    onClicked: appVM.openDialog("budget")
                }
            ]
        }

        EmptyState {
            visible: budgetVM.budgets.length === 0
            title: "No budgets created"
            description: "Set spending limits for categories like Groceries, Dining, or Shopping."
            actionText: "Create First Budget"
            onActionTriggered: appVM.openDialog("budget")
        }

        Flow {
            width: parent.width
            spacing: 16
            visible: budgetVM.budgets.length > 0

            Repeater {
                model: budgetVM.budgets

                BudgetProgress {
                    width: (parent.width - 16) / 2
                    name: modelData.name
                    categoryName: modelData.categoryName
                    personName: modelData.personName
                    limit: modelData.limit
                    spent: modelData.spent
                    remaining: modelData.remaining
                    utilization: modelData.utilization
                    statusLevel: modelData.statusLevel
                }
            }
        }
    }
}
