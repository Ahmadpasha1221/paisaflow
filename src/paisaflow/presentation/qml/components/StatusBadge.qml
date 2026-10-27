import QtQuick 2.15

Rectangle {
    id: root

    property string text: ""
    property string level: "neutral" // positive, negative, warning, informational, neutral

    function getTextColor() {
        switch(level.toLowerCase()) {
            case "positive":
            case "income":
            case "healthy":
                return themeEngine.positive;
            case "negative":
            case "expense":
            case "critical":
            case "exceeded":
                return themeEngine.negative;
            case "warning":
                return themeEngine.warning;
            case "informational":
            case "transfer":
                return themeEngine.informational;
            default:
                return themeEngine.secondaryText;
        }
    }

    implicitHeight: 24
    implicitWidth: label.implicitWidth + 16
    radius: 6
    color: {
        var c = getTextColor();
        return Qt.rgba(c.r, c.g, c.b, 0.12);
    }
    border.color: {
        var c = getTextColor();
        return Qt.rgba(c.r, c.g, c.b, 0.3);
    }
    border.width: 1

    Text {
        id: label
        text: root.text
        color: root.getTextColor()
        font.pixelSize: 11
        font.weight: Font.DemiBold
        font.family: "Segoe UI, Inter, sans-serif"
        anchors.centerIn: parent
    }
}
