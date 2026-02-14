from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton, QMessageBox
from PySide6.QtCore import Signal


class ConnectionWidget(QWidget):
    on_connection_attempt = Signal(str)
    def __init__(self, parent=None):
        super(ConnectionWidget, self).__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 0, 10, 0)
        self.layout.setSpacing(10)

        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("IP Adresa")

        connect_btn = QPushButton("Připojit")
        connect_btn.clicked.connect(self.on_button_clicked)

        self.layout.addWidget(self.ip_input)
        self.layout.addWidget(connect_btn)

    def on_button_clicked(self):
        ip = self.ip_input.text()

        # Ověření vstupu
        # Je-li nalezen problém, vykresli chybu a ukonči funkci předčasně
        split = ip.split(".")
        if len(split) == 4:
            for i in split:
                if not i.isnumeric():
                    QMessageBox.critical(self, "Error", "IP adresa se skládá ze 4 čísel od 0 do 255")
                    return
                else:
                    val = int(i)
                    if val < 0 or val > 255:
                        QMessageBox.critical(self, "Error", "IP adresa obsahuje pouze čísla od 0 do 255")
                        return

        else:
            QMessageBox.critical(self, "Error", "Neplatná IP adresa.")

        self.on_connection_attempt.emit(ip)

