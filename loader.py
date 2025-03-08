import os
import sys
from PySide2.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QSizePolicy
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QFile, QIODevice
from PySide2.QtGui import QIcon, QPixmap
from PySide2.QtWidgets import QHeaderView
from PySide2.QtCore import Qt

# Get script directory and construct full path to UI file and icon
script_path = os.path.dirname(os.path.realpath(__file__))
ui_path = os.path.join(script_path, "ui", "userUi.ui")
icon_path = os.path.join(script_path, "resource", "profile.png")  # Update with your actual icon path


# Custom stylesheet
stylesheet = """
QWidget {
    background-color: #2e2e2e;
    color: black;
}

QPushButton {
    background-color: #4CAF50;
    color: white;
    border-radius: 5px;
}

QPushButton:hover {
    background-color: #45a049;
}
"""

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = None
        self.load_ui()
        self.add_icon_to_layout()

    def load_ui(self):
        if not os.path.exists(ui_path):
            print(f"Error: UI file not found at {ui_path}")
            sys.exit(1)  # Exit program if UI file is missing

        loader = QUiLoader()
        ui_file = QFile(ui_path)

        if not ui_file.open(QIODevice.ReadOnly):
            print(f"Error: Cannot open {ui_path}")
            return

        self.ui = loader.load(ui_file, self)
        ui_file.close()

        if self.ui:
            self.setCentralWidget(self.ui)
            self.setWindowTitle("Heart Beat")
            self.setWindowIcon(QIcon(icon_path))  # Set application window icon
            self.resize(900, 500)
            self.ui.setStyleSheet(stylesheet)
        else:
            print("Error: Failed to load UI.")

    def add_icon_to_layout(self):
        """Adds an icon inside a QVBoxLayout"""
        if self.ui:
            layout = self.ui.findChild(QVBoxLayout, "verticalLayout")  # Find verticalLayout by object name
            if layout:
                label   = QLabel(self)  # Create a QLabel for the icon
                pixmap  = QPixmap(icon_path)  # Load the icon image
                
                if not pixmap.isNull():
                    label.setPixmap(pixmap.scaled(64, 64, Qt.KeepAspectRatio))  # Resize while maintaining aspect ratio
                    label.setAlignment(Qt.AlignCenter)
                    label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # Allow QLabel to expand
                    layout.addWidget(label)  # Add QLabel to vertical layout
                else:
                    print(f"Error: Failed to load icon from {icon_path}")
            else:
                print("Error: 'verticalLayout' not found in UI.")
            
            # Set initial sizes for the splitter
            # self.ui.splitter_2.setSizes([100, 800])
            self.ui.lineEdit.setAlignment(Qt.AlignCenter)
            self.ui.lineEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # Allow QLineEdit to expand
            header = self.ui.tableWidget.horizontalHeader()
            # add column headers
            self.ui.tableWidget.setColumnCount(6)


            # Ensure table widget columns stretch
            self.ui.tableWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            
            header.setSectionResizeMode(0, QHeaderView.Stretch)  # Stretch the first column
            header.setSectionResizeMode(1, QHeaderView.Stretch)  # Stretch the second column
            header.setSectionResizeMode(2, QHeaderView.Stretch)  # Stretch the third column
            header.setSectionResizeMode(3, QHeaderView.Stretch)  # Stretch the second column
            header.setSectionResizeMode(4, QHeaderView.Stretch)  # Stretch the third column
            header.setSectionResizeMode(5, QHeaderView.Stretch)  # Stretch the third column



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
