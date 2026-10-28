import QtQuick 2.15
import QtQuick.Controls 2.15
import "../components"

ModalDialog {
    id: root

    title: "Add Household Member"
    contentWidth: 400

    property string selectedColor: "#B8F28B"

    content: Column {
        width: parent.width
        spacing: 14

        FormField {
            label: "Person Name *"
            Rectangle {
                width: parent.width
                height: 42
                radius: 8
                color: "transparent"
                border.color: "transparent"

                TextInputField {
                    id: nameInput
                    anchors.fill: parent
                    placeholderText: "e.g. Aarav, Priya, Rohan"
                }
            }
        }

        // Color Swatches
        FormField {
            label: "Profile Accent Color"
            Row {
                spacing: 10

                Repeater {
                    model: ["#B8F28B", "#82C9D4", "#FFB4A9", "#E9BE76", "#CE93D8", "#80CBC4"]

                    Rectangle {
                        width: 32
                        height: 32
                        radius: 16
                        color: modelData
                        border.color: root.selectedColor === modelData ? themeEngine.primaryText : "transparent"
                        border.width: 2

                        MouseArea {
                            anchors.fill: parent
                            onClicked: root.selectedColor = modelData
                        }
                    }
                }
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
            text: "Add Member"
            width: (parent.width - 12) / 2
            onClicked: root.submit()
        }
    }

    function submit() {
        if (!nameInput.text.trim()) {
            appVM.showToast("Person name cannot be empty.", true);
            return;
        }

        var success = personVM.createPerson(nameInput.text.trim(), root.selectedColor);
        if (success) {
            nameInput.text = "";
            appVM.notifyDataChanged();
            root.closed();
        }
    }
}
