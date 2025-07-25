import sys
import os
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QVBoxLayout, 
                              QWidget, QStatusBar, QLabel, QHBoxLayout, QFrame)
from PySide6.QtGui import QIcon, QFont, QPixmap, QPalette, QColor
from PySide6.QtCore import Qt, QSize
from database import Database
from views.technician_view import TechnicianView
from views.report_view import ReportView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Gestión de Técnicos")
        self.setGeometry(100, 100, 1200, 800)  # Ventana más grande por defecto
        
        # Configurar el ícono de la aplicación
        self.setWindowIcon(QIcon(os.path.join('resources', 'logo.png')))
        
        # Establecer estilos CSS
        self.setup_styles()
        
        # Inicializar la base de datos
        self.db = Database()
        self.db.initialize_database()
        
        # Configurar la interfaz de usuario
        self.setup_ui()
        
        # Mostrar mensaje de bienvenida
        self.show_status_message("Sistema de Gestión de Técnicos - Listo")
    
    def setup_styles(self):
        """Configura los estilos CSS de la aplicación con un tema oscuro global."""
        # Colores principales
        dark_bg = "#1e1e2f"
        darker_bg = "#161623"
        card_bg = "#27293d"
        text_color = "#e9ecef"
        accent_color = "#2196F3"  # Azul del logo
        accent_hover = "#1976D2"  # Azul un poco más oscuro para hover
        secondary_color = "#00f2c3"
        border_color = "#2b3553"
        highlight_color = "#3a3f5a"
        
        # Estilos globales
        style_sheet = f"""
            /* Estilos generales */
            QMainWindow, QDialog, QWidget {{
                background-color: {dark_bg};
                color: {text_color};
                font-family: 'Segoe UI';
                font-size: 10pt;
            }}
            
            /* Barra de menú */
            QMenuBar {{
                background-color: {darker_bg};
                color: {text_color};
                border-bottom: 1px solid {border_color};
            }}
            QMenuBar::item {{
                background: transparent;
                padding: 5px 10px;
            }}
            QMenuBar::item:selected {{
                background: {highlight_color};
                border-radius: 4px;
            }}
            QMenu {{
                background-color: {card_bg};
                border: 1px solid {border_color};
                padding: 5px;
            }}
            QMenu::item:selected {{
                background-color: {highlight_color};
                color: white;
            }}
            
            /* Barra de estado */
            QStatusBar {{
                background-color: {darker_bg};
                color: {text_color};
                border-top: 1px solid {border_color};
            }}
            
            /* Pestañas */
            QTabWidget::pane {{
                border: 1px solid {border_color};
                border-radius: 4px;
                padding: 5px;
                background: {card_bg};
            }}
            QTabBar::tab {{
                background: {darker_bg};
                color: {text_color};
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                border: 1px solid {border_color};
                border-bottom: none;
            }}
            QTabBar::tab:selected, QTabBar::tab:hover {{
                background: {card_bg};
                color: {accent_color};
                border-bottom: 2px solid {accent_color};
                margin-bottom: -1px;  /* Para compensar el borde inferior */
            }}
            
            /* Botones */
            QPushButton {{
                background-color: {accent_color};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {accent_hover};
            }}
            QPushButton:disabled {{
                background-color: #3a3a4a;
                color: #6c757d;
            }}
            
            /* Campos de entrada */
            QLineEdit, QComboBox, QDateEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox {{
                background-color: {card_bg};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 4px;
                padding: 5px 10px;
                min-height: 25px;
            }}
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus {{
                border: 1px solid {accent_color};
            }}
            
            /* Tablas */
            QTableView, QTableWidget {{
                background-color: {card_bg};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 4px;
                gridline-color: {border_color};
            }}
            QHeaderView::section {{
                background-color: {darker_bg};
                color: {secondary_color};
                padding: 8px;
                border: none;
                font-weight: 600;
            }}
            QTableWidget::item:selected, QTableView::item:selected {{
                background-color: {highlight_color};
                color: white;
            }}
            
            /* Barras de desplazamiento */
            QScrollBar:vertical {{
                background: {darker_bg};
                width: 10px;
                margin: 0px;
                border: none;
            }}
            QScrollBar::handle:vertical {{
                background: {accent_color};
                min-height: 20px;
                border-radius: 5px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            
            /* Grupos y marcos */
            QGroupBox {{
                background-color: {card_bg};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 6px;
                margin-top: 15px;
                padding: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: {secondary_color};
            }}
            
            /* Etiquetas */
            QLabel {{
                color: {text_color};
            }}
            
            /* Checkboxes y radio buttons */
            QCheckBox, QRadioButton {{
                color: {text_color};
                spacing: 5px;
            }}
            QCheckBox::indicator, QRadioButton::indicator {{
                width: 16px;
                height: 16px;
                border: 1px solid {border_color};
                border-radius: 3px;
                background: {card_bg};
            }}
            QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
                background-color: {accent_color};
                border-color: {accent_color};
            }}
            
            /* Tooltips */
            QToolTip {{
                background-color: {darker_bg};
                color: {text_color};
                border: 1px solid {border_color};
                padding: 5px;
                border-radius: 4px;
                opacity: 230;
            }}
        """
        
        # Aplicar los estilos
        self.setStyleSheet(style_sheet)
        
        # Configurar la paleta de colores
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(dark_bg))
        palette.setColor(QPalette.WindowText, QColor(text_color))
        palette.setColor(QPalette.Base, QColor(card_bg))
        palette.setColor(QPalette.AlternateBase, QColor(darker_bg))
        palette.setColor(QPalette.ToolTipBase, QColor(accent_color))
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, QColor(text_color))
        palette.setColor(QPalette.Button, QColor(card_bg))
        palette.setColor(QPalette.ButtonText, QColor(text_color))
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Highlight, QColor(accent_color))
        palette.setColor(QPalette.HighlightedText, Qt.white)
        self.setPalette(palette)
        
        # Configurar fuente por defecto
        font = QFont("Segoe UI", 10)
        QApplication.setFont(font)
    
    def setup_ui(self):
        # Crear widget central y layout principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # Crear encabezado
        self.setup_header(main_layout)
        
        # Crear pestañas
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)  # Estilo más moderno para las pestañas
        main_layout.addWidget(self.tab_widget)
        
        # Agregar vistas a las pestañas
        self.technician_view = TechnicianView(self.db)
        self.report_view = ReportView(self.db)
        
        # Personalizar íconos de las pestañas (opcional)
        self.tab_widget.addTab(self.technician_view, "👨‍🔧 Técnicos")
        self.tab_widget.addTab(self.report_view, "📊 Reportes")
        
        # Crear barra de estado
        self.setup_status_bar()
        
        # Conectar señales
        self.technician_view.status_message.connect(self.show_status_message)
        self.report_view.status_message.connect(self.show_status_message)
    
    def setup_header(self, parent_layout):
        """Configura el encabezado de la aplicación."""
        header = QFrame()
        header.setObjectName("header")
        header.setFixedHeight(60)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(15, 5, 15, 5)
        
        # Título de la aplicación
        title_label = QLabel("Sistema de Gestión de Técnicos")
        title_label.setObjectName("appTitle")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        
        # Logo (opcional)
        logo_label = QLabel()
        logo_path = os.path.join('resources', 'logo.png')
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path).scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
        
        # Versión
        version_label = QLabel("v1.0.0")
        version_label.setObjectName("versionLabel")
        
        # Añadir widgets al layout del encabezado
        header_layout.addWidget(logo_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(version_label)
        
        # Aplicar estilo al encabezado
        header.setStyleSheet("""
            #header {
                background-color: #2c3e50;
                color: white;
                border-radius: 4px;
                margin-bottom: 10px;
            }
            #header QLabel {
                background-color: transparent;
            }
            #appTitle {
                color: white;
                margin-left: 10px;
                background-color: transparent;
            }
            #versionLabel {
                color: #bdc3c7;
                font-size: 12px;
                background-color: transparent;
            }
        """)
        
        parent_layout.addWidget(header)
    
    def setup_status_bar(self):
        """Configura la barra de estado."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #f8f9fa;
                color: #2c3e50;
                border-top: 1px solid #dcdde1;
            }
        """)
        
        # Agregar etiqueta de estado
        self.status_label = QLabel()
        self.status_bar.addPermanentWidget(self.status_label)
        
        # Agregar separador
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        self.status_bar.addPermanentWidget(separator)
        
        # Agregar etiqueta de estado de la base de datos
        self.db_status = QLabel("DB: Conectado")
        self.db_status.setToolTip("Estado de la conexión a la base de datos")
        self.status_bar.addPermanentWidget(self.db_status)
    
    def show_status_message(self, message, timeout=5000):
        """Muestra un mensaje en la barra de estado."""
        self.status_bar.showMessage(message, timeout)
        
        # Cambiar el color según el tipo de mensaje
        if "error" in message.lower():
            self.status_bar.setStyleSheet("""
                QStatusBar {
                    background-color: #f8f9fa;
                    color: #e74c3c;
                    border-top: 1px solid #dcdde1;
                }
            """)
        elif "éxito" in message.lower() or "listo" in message.lower():
            self.status_bar.setStyleSheet("""
                QStatusBar {
                    background-color: #f8f9fa;
                    color: #27ae60;
                    border-top: 1px solid #dcdde1;
                }
            """)
        else:
            self.status_bar.setStyleSheet("""
                QStatusBar {
                    background-color: #f8f9fa;
                    color: #2c3e50;
                    border-top: 1px solid #dcdde1;
                }
            """)
    
def main():
    # Configurar la política de redondeo de DPI antes de crear QApplication
    if hasattr(QApplication, 'setHighDpiScaleFactorRoundingPolicy'):
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
