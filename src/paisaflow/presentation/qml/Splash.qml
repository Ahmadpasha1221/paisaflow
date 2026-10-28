import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Window 2.15

Window {
    id: splash

    width: 360
    height: 320
    visible: true
    color: "#17251F"
    flags: Qt.SplashScreen | Qt.FramelessWindowHint
    modality: Qt.NonModal
    title: "Preparing your workspace"

    Rectangle {
        anchors.fill: parent
        color: "#17251F"
        border.color: "#34483C"
        border.width: 1
        radius: 16

        Column {
            anchors.centerIn: parent
            width: parent.width - 48
            spacing: 18

            Rectangle {
                objectName: "brandImage"
                width: 104
                height: 104
                anchors.horizontalCenter: parent.horizontalCenter
                radius: 8
                color: "#17251F"
                readonly property int status: img.status
                readonly property url source: img.source
                Image {
                    id: img
                    anchors.fill: parent
                    source: brandIconUrl
                    fillMode: Image.PreserveAspectFit
                    smooth: true
                    mipmap: true
                }
            }

            Text {
                text: "Ready"
                visible: true
                color: "#F5F6F2"
                font.pixelSize: 12
                font.family: "Segoe UI, Inter, sans-serif"
                horizontalAlignment: Text.AlignHCenter
            }

            Text {
                width: parent.width
                text: startupState ? startupState.message : ""
                color: "#F5F6F2"
                font.pixelSize: 15
                font.family: "Segoe UI, Inter, sans-serif"
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.Wrap
                visible: !!startupState && startupState.errorMessage === ""
            }

            Text {
                objectName: "startupError"
                width: parent.width
                text: "Unable to open your workspace\n" + (startupState ? startupState.errorMessage : "")
                color: "#FFB4A9"
                font.pixelSize: 12
                font.family: "Segoe UI, Inter, sans-serif"
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.Wrap
                visible: !!startupState && startupState.errorMessage !== ""
            }

            BusyIndicator {
                width: 28
                height: 28
                anchors.horizontalCenter: parent.horizontalCenter
                running: !!startupState && startupState.errorMessage === ""
                visible: running
            }

            Button {
                text: "Close"
                anchors.horizontalCenter: parent.horizontalCenter
                visible: !!startupState && startupState.errorMessage !== ""
                onClicked: Qt.quit()
            }
        }
    }

    Component.onCompleted: splash.centerOnScreen()

    function centerOnScreen() {
        const scr = splash.screen;
        if (scr && scr.availableGeometry) {
            splash.x = scr.availableGeometry.x + (scr.availableGeometry.width - splash.width) / 2;
            splash.y = scr.availableGeometry.y + (scr.availableGeometry.height - splash.height) / 2;
        }
    }
}
