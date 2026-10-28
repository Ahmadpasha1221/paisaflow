import QtQuick 2.15
import QtQuick.Controls 2.15
import "../../src/paisaflow/presentation/qml/components"

ApplicationWindow {
    visible: true
    width: 640
    height: 420
    color: themeEngine.appBackground

    Column {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 12

        TextInputField {
            objectName: "inputField"
            width: parent.width
            placeholderText: "Enter a value"
        }

        CurrencyInput {
            objectName: "currencyField"
            width: parent.width
            text: "123.45"
        }

        DateInput {
            objectName: "dateField"
            width: parent.width
            text: "2026-10-28"
        }

        SearchField {
            objectName: "searchField"
            width: parent.width
            placeholderText: "Search"
        }

        MultilineInputField {
            objectName: "notesField"
            width: parent.width
            placeholderText: "Notes"
        }
    }
}
