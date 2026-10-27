import QtQuick 2.15

// Clean vector-rendered icon supporting Lucide-inspired glyphs
Item {
    id: root

    property string name: "tag"
    property color color: "#B8C6BC"
    property real size: 20

    width: size
    height: size

    Canvas {
        id: canvas
        anchors.fill: parent

        onPaint: {
            var ctx = getContext("2d");
            ctx.reset();
            ctx.clearRect(0, 0, width, height);
            ctx.strokeStyle = root.color;
            ctx.fillStyle = root.color;
            ctx.lineWidth = 1.75;
            ctx.lineCap = "round";
            ctx.lineJoin = "round";

            var w = width;
            var h = height;

            switch(root.name) {
                case "overview":
                case "home":
                    // 4-quadrant grid
                    ctx.strokeRect(w * 0.15, h * 0.15, w * 0.3, h * 0.3);
                    ctx.strokeRect(w * 0.55, h * 0.15, w * 0.3, h * 0.3);
                    ctx.strokeRect(w * 0.15, h * 0.55, w * 0.3, h * 0.3);
                    ctx.strokeRect(w * 0.55, h * 0.55, w * 0.3, h * 0.3);
                    break;

                case "transactions":
                case "list":
                    // Horizontal lines with bullets
                    ctx.beginPath();
                    ctx.arc(w * 0.2, h * 0.28, 1.5, 0, 2 * Math.PI);
                    ctx.arc(w * 0.2, h * 0.5, 1.5, 0, 2 * Math.PI);
                    ctx.arc(w * 0.2, h * 0.72, 1.5, 0, 2 * Math.PI);
                    ctx.fill();

                    ctx.beginPath();
                    ctx.moveTo(w * 0.38, h * 0.28); ctx.lineTo(w * 0.85, h * 0.28);
                    ctx.moveTo(w * 0.38, h * 0.5); ctx.lineTo(w * 0.85, h * 0.5);
                    ctx.moveTo(w * 0.38, h * 0.72); ctx.lineTo(w * 0.85, h * 0.72);
                    ctx.stroke();
                    break;

                case "accounts":
                case "wallet":
                case "credit-card":
                    // Rectangular card
                    ctx.strokeRect(w * 0.15, h * 0.22, w * 0.7, h * 0.56);
                    ctx.beginPath();
                    ctx.moveTo(w * 0.15, h * 0.42); ctx.lineTo(w * 0.85, h * 0.42);
                    ctx.moveTo(w * 0.25, h * 0.62); ctx.lineTo(w * 0.45, h * 0.62);
                    ctx.stroke();
                    break;

                case "people":
                case "users":
                    // User icon
                    ctx.beginPath();
                    ctx.arc(w * 0.5, h * 0.32, w * 0.18, 0, 2 * Math.PI);
                    ctx.stroke();
                    ctx.beginPath();
                    ctx.arc(w * 0.5, h * 0.85, w * 0.32, Math.PI, 2 * Math.PI);
                    ctx.stroke();
                    break;

                case "budgets":
                case "pie-chart":
                    // Circle with slice
                    ctx.beginPath();
                    ctx.arc(w * 0.5, h * 0.5, w * 0.35, 0, 2 * Math.PI);
                    ctx.stroke();
                    ctx.beginPath();
                    ctx.moveTo(w * 0.5, h * 0.5); ctx.lineTo(w * 0.5, h * 0.15);
                    ctx.moveTo(w * 0.5, h * 0.5); ctx.lineTo(w * 0.8, h * 0.65);
                    ctx.stroke();
                    break;

                case "goals":
                case "target":
                    // Target concentric circles
                    ctx.beginPath();
                    ctx.arc(w * 0.5, h * 0.5, w * 0.36, 0, 2 * Math.PI);
                    ctx.stroke();
                    ctx.beginPath();
                    ctx.arc(w * 0.5, h * 0.5, w * 0.18, 0, 2 * Math.PI);
                    ctx.stroke();
                    ctx.beginPath();
                    ctx.arc(w * 0.5, h * 0.5, 1.5, 0, 2 * Math.PI);
                    ctx.fill();
                    break;

                case "debts":
                case "scale":
                case "handshake":
                    // Balance scales
                    ctx.beginPath();
                    ctx.moveTo(w * 0.2, h * 0.35); ctx.lineTo(w * 0.8, h * 0.35);
                    ctx.moveTo(w * 0.5, h * 0.2); ctx.lineTo(w * 0.5, h * 0.8);
                    ctx.moveTo(w * 0.35, h * 0.8); ctx.lineTo(w * 0.65, h * 0.8);
                    ctx.stroke();
                    // Left and right pans
                    ctx.beginPath();
                    ctx.arc(w * 0.25, h * 0.55, w * 0.12, 0, Math.PI);
                    ctx.stroke();
                    ctx.beginPath();
                    ctx.arc(w * 0.75, h * 0.55, w * 0.12, 0, Math.PI);
                    ctx.stroke();
                    break;

                case "reports":
                case "bar-chart":
                    // Bar chart
                    ctx.beginPath();
                    ctx.moveTo(w * 0.15, h * 0.85); ctx.lineTo(w * 0.85, h * 0.85);
                    ctx.stroke();
                    ctx.strokeRect(w * 0.22, h * 0.5, w * 0.14, h * 0.35);
                    ctx.strokeRect(w * 0.43, h * 0.28, w * 0.14, h * 0.57);
                    ctx.strokeRect(w * 0.64, h * 0.4, w * 0.14, h * 0.45);
                    break;

                case "settings":
                    // Gear
                    ctx.beginPath();
                    ctx.arc(w * 0.5, h * 0.5, w * 0.2, 0, 2 * Math.PI);
                    ctx.stroke();
                    ctx.beginPath();
                    ctx.arc(w * 0.5, h * 0.5, w * 0.35, 0, 2 * Math.PI);
                    ctx.stroke();
                    break;

                case "plus":
                    ctx.beginPath();
                    ctx.moveTo(w * 0.5, h * 0.2); ctx.lineTo(w * 0.5, h * 0.8);
                    ctx.moveTo(w * 0.2, h * 0.5); ctx.lineTo(w * 0.8, h * 0.5);
                    ctx.stroke();
                    break;

                case "search":
                    ctx.beginPath();
                    ctx.arc(w * 0.42, h * 0.42, w * 0.24, 0, 2 * Math.PI);
                    ctx.stroke();
                    ctx.beginPath();
                    ctx.moveTo(w * 0.6, h * 0.6); ctx.lineTo(w * 0.82, h * 0.82);
                    ctx.stroke();
                    break;

                case "sun":
                    ctx.beginPath();
                    ctx.arc(w * 0.5, h * 0.5, w * 0.18, 0, 2 * Math.PI);
                    ctx.stroke();
                    // Rays
                    ctx.beginPath();
                    ctx.moveTo(w * 0.5, h * 0.15); ctx.lineTo(w * 0.5, h * 0.25);
                    ctx.moveTo(w * 0.5, h * 0.75); ctx.lineTo(w * 0.5, h * 0.85);
                    ctx.moveTo(w * 0.15, h * 0.5); ctx.lineTo(w * 0.25, h * 0.5);
                    ctx.moveTo(w * 0.75, h * 0.5); ctx.lineTo(w * 0.85, h * 0.5);
                    ctx.stroke();
                    break;

                case "moon":
                    ctx.beginPath();
                    ctx.arc(w * 0.5, h * 0.5, w * 0.3, -Math.PI * 0.3, Math.PI * 0.7);
                    ctx.arc(w * 0.4, h * 0.45, w * 0.24, Math.PI * 0.7, -Math.PI * 0.3, true);
                    ctx.stroke();
                    break;

                case "close":
                case "x":
                    ctx.beginPath();
                    ctx.moveTo(w * 0.25, h * 0.25); ctx.lineTo(w * 0.75, h * 0.75);
                    ctx.moveTo(w * 0.75, h * 0.25); ctx.lineTo(w * 0.25, h * 0.75);
                    ctx.stroke();
                    break;

                case "arrow-down-left":
                case "income":
                    // Diagonal arrow pointing bottom-left
                    ctx.beginPath();
                    ctx.moveTo(w * 0.75, h * 0.25); ctx.lineTo(w * 0.25, h * 0.75);
                    ctx.moveTo(w * 0.55, h * 0.75); ctx.lineTo(w * 0.25, h * 0.75);
                    ctx.lineTo(w * 0.25, h * 0.45);
                    ctx.stroke();
                    break;

                case "arrow-up-right":
                case "expense":
                    // Diagonal arrow pointing top-right
                    ctx.beginPath();
                    ctx.moveTo(w * 0.25, h * 0.75); ctx.lineTo(w * 0.75, h * 0.25);
                    ctx.moveTo(w * 0.45, h * 0.25); ctx.lineTo(w * 0.75, h * 0.25);
                    ctx.lineTo(w * 0.75, h * 0.55);
                    ctx.stroke();
                    break;

                case "arrow-left-right":
                case "transfer":
                    // Bi-directional arrows
                    ctx.beginPath();
                    ctx.moveTo(w * 0.2, h * 0.38); ctx.lineTo(w * 0.8, h * 0.38);
                    ctx.moveTo(w * 0.65, h * 0.25); ctx.lineTo(w * 0.8, h * 0.38); ctx.lineTo(w * 0.65, h * 0.51);
                    ctx.moveTo(w * 0.8, h * 0.62); ctx.lineTo(w * 0.2, h * 0.62);
                    ctx.moveTo(w * 0.35, h * 0.49); ctx.lineTo(w * 0.2, h * 0.62); ctx.lineTo(w * 0.35, h * 0.75);
                    ctx.stroke();
                    break;

                case "trash":
                case "delete":
                    // Waste bin: lid, handle and body
                    ctx.beginPath();
                    ctx.moveTo(w * 0.22, h * 0.3); ctx.lineTo(w * 0.78, h * 0.3);
                    ctx.stroke();
                    ctx.beginPath();
                    ctx.moveTo(w * 0.4, h * 0.3); ctx.lineTo(w * 0.43, h * 0.18);
                    ctx.lineTo(w * 0.57, h * 0.18); ctx.lineTo(w * 0.6, h * 0.3);
                    ctx.stroke();
                    ctx.beginPath();
                    ctx.moveTo(w * 0.31, h * 0.3); ctx.lineTo(w * 0.35, h * 0.82);
                    ctx.lineTo(w * 0.65, h * 0.82); ctx.lineTo(w * 0.69, h * 0.3);
                    ctx.moveTo(w * 0.44, h * 0.42); ctx.lineTo(w * 0.45, h * 0.7);
                    ctx.moveTo(w * 0.56, h * 0.42); ctx.lineTo(w * 0.55, h * 0.7);
                    ctx.stroke();
                    break;

                case "check":
                    ctx.beginPath();
                    ctx.moveTo(w * 0.2, h * 0.52); ctx.lineTo(w * 0.42, h * 0.74); ctx.lineTo(w * 0.82, h * 0.28);
                    ctx.stroke();
                    break;

                case "alert":
                    ctx.beginPath();
                    ctx.moveTo(w * 0.5, h * 0.15); ctx.lineTo(w * 0.88, h * 0.82); ctx.lineTo(w * 0.12, h * 0.82);
                    ctx.closePath();
                    ctx.stroke();
                    ctx.beginPath();
                    ctx.moveTo(w * 0.5, h * 0.4); ctx.lineTo(w * 0.5, h * 0.6);
                    ctx.stroke();
                    ctx.beginPath();
                    ctx.arc(w * 0.5, h * 0.72, 1.5, 0, 2 * Math.PI);
                    ctx.fill();
                    break;

                default:
                    // Generic tag
                    ctx.beginPath();
                    ctx.moveTo(w * 0.2, h * 0.2); ctx.lineTo(w * 0.6, h * 0.2);
                    ctx.lineTo(w * 0.82, h * 0.5); ctx.lineTo(w * 0.5, h * 0.82);
                    ctx.lineTo(w * 0.2, h * 0.5);
                    ctx.closePath();
                    ctx.stroke();
                    ctx.beginPath();
                    ctx.arc(w * 0.38, h * 0.38, 1.5, 0, 2 * Math.PI);
                    ctx.fill();
                    break;
            }
        }
    }

    onColorChanged: canvas.requestPaint()
    onNameChanged: canvas.requestPaint()
    onSizeChanged: canvas.requestPaint()
}
