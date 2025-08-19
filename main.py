import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QTableWidget, 
                               QTableWidgetItem, QVBoxLayout, QHBoxLayout, 
                               QWidget, QLineEdit, QPushButton, QComboBox, 
                               QLabel, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QColor
from database import get_all_stakeholders, get_all_tables, get_table_data, test_connection

class AdminApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Crown Emirates Safety Induction Database")
        self.resize(1000, 700)
        
        # Test database connection first
        if not test_connection():
            QMessageBox.critical(self, "Database Error", 
                               "Failed to connect to database. Please check your .env file.")
            sys.exit(1)

        # Central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Add logo at the top
        self.add_logo()

        # Top controls
        self.create_top_controls()

        # Table
        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        # Status label
        self.status_label = QLabel("Ready")
        self.layout.addWidget(self.status_label)

        self.load_data()

    def add_logo(self):
        """Add company logo at the top of the application"""
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Try to load the logo from public/img/logo.webp
        logo_path = os.path.join("public", "img", "107338.webp")
        
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            if not pixmap.isNull():
                # Scale the logo to a reasonable size (max height 80px, maintain aspect ratio)
                scaled_pixmap = pixmap.scaledToHeight(60, Qt.TransformationMode.SmoothTransformation)
                logo_label.setPixmap(scaled_pixmap)
            else:
                logo_label.setText("Crown Emirates")
                logo_label.setStyleSheet("font-size: 24px; font-weight: bold; padding: 20px;")
        else:
            # Fallback text if logo not found
            logo_label.setText("Crown Emirates")
            logo_label.setStyleSheet("font-size: 24px; font-weight: bold; padding: 20px;")
        
        logo_label.setMargin(10)
        self.layout.addWidget(logo_label)

    def create_top_controls(self):
        """Create the top control panel"""
        top_layout = QHBoxLayout()
        
        # Table selector
        top_layout.addWidget(QLabel("Table:"))
        self.table_combo = QComboBox()
        self.populate_table_combo()
        self.table_combo.currentTextChanged.connect(self.on_table_changed)
        top_layout.addWidget(self.table_combo)
        
        # Refresh button
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.load_data)
        top_layout.addWidget(self.refresh_btn)
        
        # Search box
        top_layout.addWidget(QLabel("Search:"))
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search...")
        self.search_box.textChanged.connect(self.search)
        top_layout.addWidget(self.search_box)
        
        # Add stretch to push everything to the left
        top_layout.addStretch()
        
        # Create widget to hold the layout
        top_widget = QWidget()
        top_widget.setLayout(top_layout)
        self.layout.addWidget(top_widget)

    def populate_table_combo(self):
        """Populate the table selector combo box"""
        self.table_combo.clear()
        tables = get_all_tables()
        
        if not tables:
            self.table_combo.addItem("No tables found")
            return
            
        # Add stakeholders first if it exists
        if 'stakeholders' in tables:
            self.table_combo.addItem('stakeholders')
            tables.remove('stakeholders')
        
        # Add remaining tables
        for table in tables:
            self.table_combo.addItem(table)

    def on_table_changed(self, table_name):
        """Handle table selection change"""
        if table_name and table_name != "No tables found":
            self.load_data()

    def load_data(self):
        """Load data from the selected table"""
        current_table = self.table_combo.currentText()
        
        if not current_table or current_table == "No tables found":
            self.status_label.setText("No table selected")
            return

        self.status_label.setText("Loading data...")
        
        # Get data based on selected table
        if current_table == 'stakeholders':
            data = get_all_stakeholders()
        else:
            data = get_table_data(current_table)
        
        if not data:
            self.table.setRowCount(0)
            self.table.setColumnCount(0)
            self.status_label.setText(f"No data found in table '{current_table}'")
            return

        # Set up table
        self.table.setRowCount(len(data))
        self.table.setColumnCount(len(data[0]))
        
        # Set headers (column names)
        headers = list(data[0].keys())
        self.table.setHorizontalHeaderLabels(headers)

        # Fill table with data
        for row_idx, row_data in enumerate(data):
            for col_idx, (key, value) in enumerate(row_data.items()):
                item = QTableWidgetItem(str(value) if value is not None else "")
                
                # Special formatting for boolean values in 'passed' field
                if key.lower() == 'passed' and value is not None:
                    if str(value).lower() in ['true', '1', 't', 'yes']:
                        
                        item.setText("✓ Passed")
                    elif str(value).lower() in ['false', '0', 'f', 'no']:
                        
                        item.setText("✗ Failed")
                
                self.table.setItem(row_idx, col_idx, item)
        
        # Auto-resize columns to fit content
        self.table.resizeColumnsToContents()
        
        self.status_label.setText(f"Loaded {len(data)} records from '{current_table}'")

    def search(self, text):
        """Filter table rows based on search text"""
        if not text:
            # Show all rows if search is empty
            for row in range(self.table.rowCount()):
                self.table.setRowHidden(row, False)
            return
        
        text = text.lower()
        for row in range(self.table.rowCount()):
            match = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and text in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(row, not match)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Crown Emirates Admin")
    app.setApplicationVersion("1.0")
    
    try:
        window = AdminApp()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"Application error: {e}")
        sys.exit(1)