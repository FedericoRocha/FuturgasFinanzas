from PySide6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLineEdit, 
                               QPushButton, QTableWidget, QTableWidgetItem, 
                               QHeaderView, QMessageBox, QHBoxLayout, 
                               QAbstractItemView, QLabel, QFrame, QToolButton, 
                               QSpacerItem, QStyledItemDelegate)
from PySide6.QtCore import Qt, Signal, QSize, QObject
from PySide6.QtGui import QDoubleValidator, QIcon, QFont, QPalette, QColor, QPixmap

class TechnicianView(QWidget):
    # Señal que se emite cuando se actualiza la lista de técnicos
    technicians_updated = Signal()
    
    # Señal personalizada para mensajes de estado
    status_message = Signal(str)
    
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.selected_technician_id = None
        self.setup_styles()
        self.init_ui()
        self.load_technicians()
        
    def setup_styles(self):
        """Configura los estilos para los widgets de la interfaz con un tema oscuro."""
        # Colores principales
        self.dark_bg = "#1e1e2f"
        self.darker_bg = "#161623"
        self.card_bg = "#27293d"
        self.text_color = "#e9ecef"
        self.accent_color = "#2196F3"  # Azul del logo
        self.accent_hover = "#1976D2"   # Azul más oscuro para hover
        self.secondary_color = "#2196F3"  # Mismo azul para consistencia
        self.border_color = "#2b3553"
        self.highlight_color = "#3a3f5a"
        
        # Estilo para los botones principales
        self.button_style = f"""
            QPushButton {{
                background-color: {self.accent_color};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
                min-width: 100px;
                text-transform: uppercase;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {self.accent_hover};
            }}
            QPushButton:pressed {{
                background-color: #0d47a1;
                padding-top: 9px;
                padding-bottom: 7px;
            }}
            QPushButton:disabled {{
                background-color: #90caf9;
                color: #e3f2fd;
            }}
        """
        
        # Estilo para el botón de cancelar (usamos el mismo estilo que los demás botones)
        self.cancel_button_style = self.button_style
        
        # Estilo para los campos de entrada
        self.input_style = f"""
            QLineEdit, QComboBox, QDateEdit, QCompleter {{
                background-color: {self.card_bg};
                color: {self.text_color};
                padding: 10px 12px;
                border: 1px solid {self.border_color};
                border-radius: 6px;
                min-width: 200px;
                selection-background-color: {self.accent_color};
                selection-color: white;
            }}
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus {{
                border: 1px solid {self.accent_color};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: url(dropdown_arrow.png);
                width: 12px;
                height: 12px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {self.card_bg};
                color: {self.text_color};
                selection-background-color: {self.accent_color};
                selection-color: white;
                outline: none;
                border: 1px solid {self.border_color};
            }}
        """
        
        # Estilo para la tabla
        self.table_style = f"""
            QTableWidget {{
                background-color: {self.card_bg};
                color: {self.text_color};
                border: 1px solid {self.border_color};
                border-radius: 6px;
                gridline-color: {self.border_color};
                outline: 0;
            }}
            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {self.border_color};
            }}
            QHeaderView::section {{
                background-color: {self.darker_bg};
                color: {self.secondary_color};
                padding: 12px 8px;
                border: none;
                font-weight: 600;
                text-transform: uppercase;
                font-size: 11px;
                letter-spacing: 0.5px;
            }}
            QTableWidget::item:selected {{
                background-color: {self.highlight_color};
                color: white;
            }}
            QScrollBar:vertical {{
                background: {self.darker_bg};
                width: 10px;
                margin: 0px 0px 0px 0px;
                border: none;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical {{
                background: {self.accent_color};
                min-height: 20px;
                border-radius: 5px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """
        
        # Estilo para el formulario y grupos
        self.form_style = f"""
            QGroupBox {{
                background-color: {self.card_bg};
                color: {self.text_color};
                border: 1px solid {self.border_color};
                border-radius: 8px;
                margin-top: 15px;
                padding: 15px 15px 20px 15px;
                font-weight: 600;
                font-size: 14px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px;
                color: {self.secondary_color};
            }}
            QLabel {{
                color: {self.text_color};
                font-weight: 500;
                margin-bottom: 3px;
            }}
        """
        
        # Configurar la paleta de colores
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(self.dark_bg))
        palette.setColor(QPalette.WindowText, QColor(self.text_color))
        palette.setColor(QPalette.Base, QColor(self.card_bg))
        palette.setColor(QPalette.AlternateBase, QColor(self.darker_bg))
        palette.setColor(QPalette.ToolTipBase, QColor(self.accent_color))
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, QColor(self.text_color))
        palette.setColor(QPalette.Button, QColor(self.card_bg))
        palette.setColor(QPalette.ButtonText, QColor(self.text_color))
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Highlight, QColor(self.accent_color))
        palette.setColor(QPalette.HighlightedText, Qt.white)
        
        self.setPalette(palette)
        
        # Configurar la fuente
        font = self.font()
        font.setPointSize(10)
        font.setFamily("Segoe UI")
        self.setFont(font)
        
        # Estilo general para la aplicación
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {self.dark_bg};
                color: {self.text_color};
                selection-background-color: {self.accent_color};
                selection-color: white;
            }}
            QTabWidget::pane {{
                border: 1px solid {self.border_color};
                border-radius: 4px;
                padding: 5px;
                background: {self.card_bg};
            }}
            QTabBar::tab {{
                background: {self.darker_bg};
                color: {self.text_color};
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                border: 1px solid {self.border_color};
                border-bottom: none;
            }}
            QTabBar::tab:selected, QTabBar::tab:hover {{
                background: {self.card_bg};
                color: {self.accent_color};
                border-bottom-color: {self.card_bg};
            }}
        """)
    
    def init_ui(self):
        # Layout principal con márgenes y espaciado reducidos
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)  # Reducir márgenes externos
        main_layout.setSpacing(10)  # Reducir espaciado entre widgets
        
        # Aplicar estilo al widget principal
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {self.dark_bg};
                color: {self.text_color};
            }}
            QLabel {{
                color: {self.accent_color};
                font-weight: 500;
                background-color: transparent;
            }}
            QLabel#logoLabel {{
                background-color: transparent;
            }}
            QLineEdit, QComboBox {{
                background-color: {self.darker_bg};
                color: {self.text_color};
                border: 1px solid {self.border_color};
                border-radius: 4px;
                padding: 8px;
                min-height: 36px;
            }}
            QLineEdit:focus, QComboBox:focus {{
                border: 1px solid {self.accent_color};
            }}
            QLineEdit::placeholder {{
                color: #6c757d;
            }}
        """)
        
        # Grupo para el formulario
        form_group = QFrame()
        form_group.setObjectName("formGroup")
        form_group.setFrameShape(QFrame.StyledPanel)
        form_group.setStyleSheet(f"""
            QFrame#formGroup {{
                background-color: {self.card_bg};
                border: 1px solid {self.border_color};
                border-radius: 6px;
                padding: 15px;
            }}
            QLabel {{
                color: {self.accent_color};
                font-weight: 500;
                background-color: transparent;
            }}
            QLineEdit, QComboBox {{
                background-color: {self.darker_bg};
                color: {self.text_color};
                border: 1px solid {self.border_color};
                border-radius: 4px;
                padding: 8px;
            }}
        """)
        
        form_layout = QVBoxLayout(form_group)
        form_layout.setContentsMargins(12, 12, 12, 12)  # Reducir márgenes internos
        form_layout.setSpacing(12)  # Reducir espaciado interno
        
        # Título del formulario
        title_label = QLabel("Gestión de Técnicos")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"""
            color: {self.accent_color};
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 10px;
            background-color: transparent;
        """)
        form_layout.addWidget(title_label)
        
        # Formulario para agregar/editar técnicos
        input_layout = QFormLayout()
        input_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        input_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        input_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)
        input_layout.setLabelAlignment(Qt.AlignLeft)
        
        # Estilo para los campos de entrada
        input_style = f"""
            QLineEdit, QComboBox, QComboBox::drop-down {{
                padding: 8px 12px;
                border: 1px solid {self.border_color};
                border-radius: 6px;
                background-color: {self.darker_bg};
                color: {self.text_color};
                font-size: 13px;
                min-height: 36px;
                selection-background-color: {self.accent_color};
                selection-color: white;
            }}
            QLineEdit:focus, QComboBox:focus, QComboBox::drop-down:focus {{
                border: 1px solid {self.accent_color};
                background-color: {self.darker_bg};
            }}
            QLineEdit::placeholder, QComboBox::placeholder {{
                color: #6c757d;
                font-style: italic;
            }}
            QComboBox::down-arrow {{
                image: url(none);
                width: 0;
                height: 0;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {self.text_color};
                margin-right: 8px;
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid {self.border_color};
                border-top-right-radius: 6px;
                border-bottom-right-radius: 6px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {self.darker_bg};
                color: {self.text_color};
                selection-background-color: {self.accent_color};
                selection-color: white;
                border: 1px solid {self.border_color};
                outline: none;
            }}
        """
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ingrese el nombre del técnico")
        self.name_input.setStyleSheet(input_style)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("ejemplo@email.com")
        self.email_input.setStyleSheet(input_style)
        
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("+54 9 XXX XXX XXXX")
        self.phone_input.setStyleSheet(input_style)
        
        input_layout.addRow("Nombre:", self.name_input)
        input_layout.addRow("Email:", self.email_input)
        input_layout.addRow("Teléfono:", self.phone_input)
        
        form_layout.addLayout(input_layout)
        
        # Botones del formulario
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # Botón Agregar
        self.add_button = QPushButton("➕ Agregar")
        self.add_button.setStyleSheet(self.button_style)
        self.add_button.setCursor(Qt.PointingHandCursor)
        self.add_button.clicked.connect(self.add_technician)
        
        # Botón Actualizar
        self.update_button = QPushButton("🔄 Actualizar")
        self.update_button.setStyleSheet(self.button_style)
        self.update_button.setCursor(Qt.PointingHandCursor)
        self.update_button.clicked.connect(self.update_technician)
        self.update_button.setEnabled(False)
        
        # Botón Cancelar
        self.cancel_button = QPushButton("❌ Cancelar")
        self.cancel_button.setStyleSheet(self.cancel_button_style)
        self.cancel_button.setCursor(Qt.PointingHandCursor)
        self.cancel_button.clicked.connect(self.cancel_edit)
        self.cancel_button.setEnabled(False)
        
        # Espaciador para alinear los botones a la derecha
        button_layout.addStretch()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.cancel_button)
        
        form_layout.addLayout(button_layout)
        
        # Tabla de técnicos
        table_group = QFrame()
        table_group.setObjectName("tableGroup")
        table_group.setFrameShape(QFrame.StyledPanel)
        table_group.setStyleSheet(f"""
            #tableGroup {{
                background-color: {self.card_bg};
                border: 1px solid {self.border_color};
                border-radius: 6px;
                padding: 8px;
                margin-top: 8px;
            }}
            #tableGroup QLabel {{
                color: {self.text_color};
                font-weight: 500;
                font-size: 12px;
            }}
            #tableGroup QTableWidget {{
                background-color: {self.card_bg};
                border: 1px solid {self.border_color};
                border-radius: 6px;
                gridline-color: {self.border_color};
                font-size: 11px;
            }}
            #tableGroup QTableWidget::item {{
                padding: 5px;
                border-bottom: 1px solid {self.border_color};
            }}
            #tableGroup QTableWidget::item:selected {{
                background-color: {self.highlight_color};
                color: white;
            }}
            #tableGroup QHeaderView::section {{
                background-color: {self.darker_bg};
                color: {self.secondary_color};
                padding: 8px;
                border: none;
                font-weight: 600;
                font-size: 11px;
            }}
            #tableGroup QHeaderView::section:first {{
                border-top-left-radius: 5px;
            }}
            #tableGroup QHeaderView::section:last {{
                border-top-right-radius: 5px;
            }}
            /* Estilos para botones en la tabla */
            #tableGroup QPushButton {{
                background-color: {self.accent_color};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
                margin: 1px;
                font-weight: 500;
                min-width: 60px;
            }}
            #tableGroup QPushButton:hover {{
                background-color: {self.accent_hover};
            }}
            #tableGroup QPushButton:pressed {{
                background-color: #0d47a1;
                padding-top: 5px;
                padding-bottom: 3px;
            }}
            #tableGroup QPushButton:disabled {{
                background-color: #90caf9;
                color: #e3f2fd;
                opacity: 0.7;
            }}
        """)
        
        table_layout = QVBoxLayout(table_group)
        
        # Título de la tabla
        table_title = QLabel("Listado de Técnicos")
        table_title.setFont(title_font)
        table_title.setStyleSheet(f"color: {self.accent_color}; margin-bottom: 10px; font-weight: 600;")
        table_layout.addWidget(table_title)
        
        # Crear la tabla
        self.technicians_table = QTableWidget()
        self.technicians_table.setColumnCount(5)
        self.technicians_table.setHorizontalHeaderLabels(["ID", "Nombre", "Email", "Teléfono", "Acciones"])
        
        # Configurar la tabla
        self.technicians_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.technicians_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.technicians_table.setAlternatingRowColors(True)
        self.technicians_table.verticalHeader().setVisible(False)
        self.technicians_table.setShowGrid(False)
        self.technicians_table.verticalHeader().setDefaultSectionSize(28)  # Altura de fila más compacta
        self.technicians_table.horizontalHeader().setStretchLastSection(True)
        
        # Ajustar el ancho de las columnas
        header = self.technicians_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Nombre
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Email
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Teléfono
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Acciones
        
        # Conectar la señal de doble clic para editar
        self.technicians_table.doubleClicked.connect(self.on_table_double_clicked)
        
        table_layout.addWidget(self.technicians_table)
        
        # Agregar widgets al layout principal
        main_layout.addWidget(form_group)
        main_layout.addWidget(table_group, 1)  # El 1 hace que la tabla ocupe el espacio restante
        
        # Ajustar el tamaño de la ventana
        self.setMinimumSize(800, 600)
        
        # Conectar la señal de actualización de técnicos
        self.technicians_updated.connect(self.load_technicians)
        
        self.setLayout(main_layout)
    
    def load_technicians(self):
        """Carga la lista de técnicos en la tabla."""
        try:
            # Mostrar mensaje de carga
            self.status_message.emit("Cargando lista de técnicos...")
            
            # Obtener la lista de técnicos de la base de datos
            technicians = self.db.get_technicians()
            
            # Configurar la tabla
            self.technicians_table.setRowCount(len(technicians))
            
            # Llenar la tabla con los datos
            for row, tech in enumerate(technicians):
                # ID
                id_item = QTableWidgetItem(str(tech['id']))
                id_item.setTextAlignment(Qt.AlignCenter)
                self.technicians_table.setItem(row, 0, id_item)
                
                # Nombre
                name_item = QTableWidgetItem(tech.get('name', ''))
                name_item.setFlags(name_item.flags() ^ Qt.ItemIsEditable)
                self.technicians_table.setItem(row, 1, name_item)
                
                # Email
                email_item = QTableWidgetItem(tech.get('email', ''))
                email_item.setFlags(email_item.flags() ^ Qt.ItemIsEditable)
                self.technicians_table.setItem(row, 2, email_item)
                
                # Teléfono
                phone_item = QTableWidgetItem(tech.get('phone', ''))
                phone_item.setFlags(phone_item.flags() ^ Qt.ItemIsEditable)
                self.technicians_table.setItem(row, 3, phone_item)
                
                # Botones de acciones (editar y eliminar)
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(5, 2, 5, 2)
                actions_layout.setSpacing(5)
                
                # Botón Editar
                edit_btn = QPushButton("✏️ Editar")
                edit_btn.setToolTip("Editar técnico")
                edit_btn.setCursor(Qt.PointingHandCursor)
                edit_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {self.accent_color};
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 4px 8px;
                        margin: 1px;
                        font-size: 11px;
                        min-width: 60px;
                    }}
                    QPushButton:hover {{
                        background-color: {self.accent_hover};
                    }}
                    QPushButton:pressed {{
                        background-color: #0d47a1;
                        padding-top: 5px;
                        padding-bottom: 3px;
                    }}
                """)
                edit_btn.clicked.connect(lambda checked, t=tech: self.edit_technician_data(t))
                
                # Botón Eliminar
                delete_btn = QPushButton("🗑️ Eliminar")
                delete_btn.setToolTip("Eliminar técnico")
                delete_btn.setCursor(Qt.PointingHandCursor)
                delete_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {self.accent_color};
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 4px 8px;
                        margin: 1px;
                        font-size: 11px;
                        min-width: 60px;
                    }}
                    QPushButton:hover {{
                        background-color: {self.accent_hover};
                    }}
                    QPushButton:pressed {{
                        background-color: #0d47a1;
                        padding-top: 5px;
                        padding-bottom: 3px;
                    }}
                """)
                delete_btn.clicked.connect(lambda checked, t=tech['id']: self.delete_technician(t))
                
                actions_layout.addWidget(edit_btn)
                actions_layout.addWidget(delete_btn)
                actions_layout.addStretch()
                
                # Configurar el widget de acciones en la celda
                self.technicians_table.setCellWidget(row, 4, actions_widget)
            
            # Ajustar el alto de las filas
            self.technicians_table.resizeRowsToContents()
            
            # Mostrar mensaje de éxito
            self.status_message.emit(f"Se cargaron {len(technicians)} técnicos correctamente.")
            
        except Exception as e:
            error_msg = f"Error al cargar los técnicos: {str(e)}"
            self.status_message.emit(error_msg)
            QMessageBox.critical(self, "Error", error_msg)
    
    def add_technician(self):
        """Agrega un nuevo técnico a la base de datos."""
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        phone = self.phone_input.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Error", "El nombre del técnico es obligatorio")
            return
            
        try:
            self.db.add_technician(name, email or None, phone or None)
            self.load_technicians()
            self.clear_form()
            self.status_message.emit("Técnico agregado correctamente")
            QMessageBox.information(self, "Éxito", "Técnico agregado correctamente")
        except Exception as e:
            error_msg = f"Error al agregar técnico: {str(e)}"
            self.status_message.emit(error_msg)
            QMessageBox.critical(self, "Error", error_msg)
    
    def edit_technician_data(self, tech_data):
        """Prepara el formulario para editar un técnico existente."""
        try:
            if not tech_data:
                QMessageBox.warning(self, "Advertencia", "No se encontraron datos del técnico.")
                return
                
            self.current_tech_id = tech_data.get('id')
            self.name_input.setText(tech_data.get('name', ''))
            self.email_input.setText(tech_data.get('email', ''))
            self.phone_input.setText(tech_data.get('phone', ''))
            
            # Cambiar al modo de edición
            self.add_button.setEnabled(False)
            self.update_button.setEnabled(True)
            self.cancel_button.setEnabled(True)
            
            # Desplazarse al formulario
            self.name_input.setFocus()
            
            # Mostrar mensaje
            self.status_message.emit(f"Editando técnico: {tech_data.get('name', '')}")
            
        except Exception as e:
            error_msg = f"Error al preparar la edición del técnico: {str(e)}"
            self.status_message.emit(error_msg)
            QMessageBox.critical(self, "Error", error_msg)
    
    def update_technician(self):
        """Actualiza un técnico existente."""
        if not hasattr(self, 'current_tech_id') or not self.current_tech_id:
            QMessageBox.warning(self, "Advertencia", "No hay ningún técnico seleccionado para actualizar.")
            return
            
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        phone = self.phone_input.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Error", "El nombre del técnico es obligatorio")
            return
            
        try:
            # Actualizar en la base de datos
            self.db.update_technician(self.current_tech_id, name, email or None, phone or None)
            
            # Recargar la lista
            self.load_technicians()
            
            # Limpiar el formulario
            self.clear_form()
            
            # Mostrar mensaje de éxito
            self.status_message.emit(f"Técnico actualizado correctamente: {name}")
            QMessageBox.information(self, "Éxito", "Técnico actualizado correctamente")
            
            # Volver al modo de agregar
            self.add_button.setEnabled(True)
            self.update_button.setEnabled(False)
            self.cancel_button.setEnabled(False)
            
        except Exception as e:
            error_msg = f"Error al actualizar el técnico: {str(e)}"
            self.status_message.emit(error_msg)
            QMessageBox.critical(self, "Error", error_msg)
    
    def delete_technician(self, tech_id):
        """Elimina un técnico después de confirmación."""
        try:
            # Confirmar eliminación
            reply = QMessageBox.question(
                self, 
                'Confirmar eliminación',
                '¿Está seguro de que desea eliminar este técnico?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # Eliminar el técnico
                self.db.delete_technician(tech_id)
                
                # Recargar la lista
                self.load_technicians()
                
                # Mostrar mensaje de éxito
                self.status_message.emit("Técnico eliminado correctamente")
                QMessageBox.information(self, "Éxito", "Técnico eliminado correctamente")
                
        except Exception as e:
            error_msg = f"Error al eliminar el técnico: {str(e)}"
            self.status_message.emit(error_msg)
            QMessageBox.critical(self, "Error", error_msg)
    
    def cancel_edit(self):
        """Cancela el modo de edición y limpia el formulario."""
        try:
            self.clear_form()
            
            # Volver al modo de agregar
            self.add_button.setEnabled(True)
            self.update_button.setEnabled(False)
            self.cancel_button.setEnabled(False)
            
            # Desenfocar cualquier elemento seleccionado
            if hasattr(self, 'current_tech_id'):
                delattr(self, 'current_tech_id')
                
            self.status_message.emit("Edición cancelada")
            
        except Exception as e:
            error_msg = f"Error al cancelar la edición: {str(e)}"
            self.status_message.emit(error_msg)
            QMessageBox.critical(self, "Error", error_msg)
    
    def on_table_double_clicked(self, index):
        """Maneja el evento de doble clic en la tabla para editar un técnico."""
        try:
            # Obtener la fila seleccionada
            row = index.row()
            
            # Obtener los datos del técnico de la fila
            tech_id = int(self.technicians_table.item(row, 0).text())
            name = self.technicians_table.item(row, 1).text()
            email = self.technicians_table.item(row, 2).text()
            phone = self.technicians_table.item(row, 3).text()
            
            # Crear un diccionario con los datos del técnico
            tech_data = {
                'id': tech_id,
                'name': name,
                'email': email,
                'phone': phone
            }
            
            # Llamar al método de edición con los datos del técnico
            self.edit_technician_data(tech_data)
            
        except Exception as e:
            error_msg = f"Error al seleccionar el técnico: {str(e)}"
            self.status_message.emit(error_msg)
            QMessageBox.critical(self, "Error", error_msg)
    
    def clear_form(self):
        """Limpia todos los campos del formulario."""
        self.name_input.clear()
        self.email_input.clear()
        self.phone_input.clear()
        self.name_input.setFocus()
