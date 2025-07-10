from PySide6 import QtCore, QtGui
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QDateEdit, 
    QComboBox, QPushButton, QDialogButtonBox, QLabel, QDoubleSpinBox,
    QTextEdit, QMessageBox
)
from PySide6.QtCore import Qt, QDate

class TaskDialog(QDialog):
    def __init__(self, parent=None, task_data=None):
        super().__init__(parent)
        self.setWindowTitle("Agregar/Editar Tarea" if not task_data else "Editar Tarea")
        self.setMinimumWidth(500)
        
        self.task_data = task_data or {}
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Formulario
        form_layout = QFormLayout()
        
        # Campos básicos
        self.technician_combo = QComboBox()
        self.technician_combo.setEnabled(not bool(self.task_data))  # Solo habilitar si es una tarea nueva
        
        # Cargar técnicos disponibles
        if self.parent() and hasattr(self.parent(), 'db'):
            self.parent().db.cursor.execute('SELECT id, name FROM technicians ORDER BY name')
            technicians = self.parent().db.cursor.fetchall()
            for tech_id, name in technicians:
                self.technician_combo.addItem(name, tech_id)
        
        self.client_name_input = QLineEdit()
        self.task_description_input = QTextEdit()
        self.task_date_edit = QDateEdit(calendarPopup=True)
        self.task_date_edit.setDate(QDate.currentDate())
        self.budget_total_input = self.create_currency_input()
        self.labor_cost_input = self.create_currency_input()
        self.material_cost_input = self.create_currency_input()
        self.insurance_payment_input = self.create_currency_input()
        self.cash_payment_input = self.create_currency_input()
        self.material_expense_input = self.create_currency_input()
        self.order_number_input = QLineEdit()
        
        # Tipo de pago
        self.payment_type_combo = QComboBox()
        self.payment_type_combo.addItems(["EFECTIVO", "TRANSFERENCIA", "MERCADO PAGO", "OTRO"])
        
        # Estado
        self.status_combo = QComboBox()
        self.status_combo.addItems(["PENDIENTE", "EN PROCESO", "COMPLETADA", "CANCELADA"])
        
        # Agregar campos al formulario
        form_layout.addRow("Técnico*:", self.technician_combo)
        form_layout.addRow("Cliente*:", self.client_name_input)
        form_layout.addRow("Descripción:", self.task_description_input)
        form_layout.addRow("N° Pedido:", self.order_number_input)
        form_layout.addRow("Fecha Tarea*:", self.task_date_edit)
        form_layout.addRow("Presupuesto Total*:", self.budget_total_input)
        form_layout.addRow("Mano de Obra:", self.labor_cost_input)
        form_layout.addRow("Material:", self.material_cost_input)
        form_layout.addRow("Pago del Seguro:", self.insurance_payment_input)
        form_layout.addRow("Efectivo:", self.cash_payment_input)
        form_layout.addRow("Gasto Material:", self.material_expense_input)
        form_layout.addRow("Tipo de Pago:", self.payment_type_combo)
        form_layout.addRow("Estado:", self.status_combo)
        
        # Campos calculados (solo lectura)
        self.profit_label = QLabel("0.00")
        self.net_profit_label = QLabel("0.00")
        self.technician_share_label = QLabel("0.00")
        self.facu_share_label = QLabel("0.00")
        self.insurance_payment_label = QLabel("0.00")
        self.cash_payment_label = QLabel("0.00")
        self.material_expense_label = QLabel("0.00")
        self.iva_label = QLabel("0.00")
        self.technician_insurance_label = QLabel("0.00")
        
        form_layout.addRow("Ganancia Total:", self.profit_label)
        form_layout.addRow("Ganancia Neta:", self.net_profit_label)
        form_layout.addRow("Técnico (70%):", self.technician_share_label)
        form_layout.addRow("Facu (30%):", self.facu_share_label)
        form_layout.addRow("Pago del Seguro:", self.insurance_payment_label)
        form_layout.addRow("Efectivo:", self.cash_payment_label)
        form_layout.addRow("Gasto Material:", self.material_expense_label)
        form_layout.addRow("IVA (10.5%):", self.iva_label)
        form_layout.addRow("Seguro del Técnico:", self.technician_insurance_label)
        
        layout.addLayout(form_layout)
        
        # Botones
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.on_accept)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
        
        # Conectar señales para cálculos automáticos
        for field in [
            self.budget_total_input, 
            self.labor_cost_input, 
            self.material_cost_input, 
            self.insurance_payment_input, 
            self.cash_payment_input, 
            self.material_expense_input
        ]:
            field.textChanged.connect(self.calculate_derived_fields)
        
        # Forzar el cálculo inicial
        self.calculate_derived_fields()
        
        # Cargar datos si se está editando
        if self.task_data:
            self.load_task_data()
    
    def create_currency_input(self):
        """Crea un campo de entrada numérico con formato de moneda"""
        input_field = QLineEdit()
        input_field.setAlignment(Qt.AlignmentFlag.AlignRight)
        input_field.setPlaceholderText("0.00")
        
        # Validador para solo números y punto decimal
        regex = QtCore.QRegularExpression(r'^\d*\.?\d{0,2}$')
        validator = QtGui.QRegularExpressionValidator(regex)
        input_field.setValidator(validator)
        
        return input_field
    
    def get_currency_value(self, input_field):
        """Obtiene el valor numérico de un campo de moneda"""
        try:
            text = input_field.text().replace('$', '').replace(',', '').strip()
            return float(text) if text else 0.0
        except:
            return 0.0

    def set_currency_value(self, input_field, value):
        """Establece el valor formateado en un campo de moneda"""
        if value is not None and value != 0:
            input_field.setText(f"{value:,.2f}")
        else:
            input_field.clear()

    def clear_calculated_fields(self):
        """Limpia todos los campos calculados"""
        self.profit_label.setText("0.00")
        self.net_profit_label.setText("0.00")
        self.technician_share_label.setText("0.00")  # Técnico (70%)
        self.facu_share_label.setText("0.00")   # Facu (30%)
        self.iva_label.setText("0.00")
        self.technician_insurance_label.setText("0.00")
        
    def calculate_derived_fields(self):
        """Calcula los campos derivados de la tarea según el Excel"""
        try:
            # Obtener valores de los campos
            budget_total = self.get_currency_value(self.budget_total_input) or 0
            insurance_payment = self.get_currency_value(self.insurance_payment_input) or 0
            cash_payment = self.get_currency_value(self.cash_payment_input) or 0
            material_expense = self.get_currency_value(self.material_expense_input) or 0
            
            # Si no hay valores, limpiar todo
            if not any([budget_total, insurance_payment, cash_payment, material_expense]):
                self.clear_calculated_fields()
                return
                
            # Validar que los montos sean consistentes
            if abs((insurance_payment + cash_payment) - budget_total) > 0.01 and (insurance_payment != 0 or cash_payment != 0):
                # No mostramos el error, solo no actualizamos los cálculos
                return
            
            # 1. Calcular IVA (10.5% sobre el presupuesto total)
            iva = budget_total * 0.105
            
            # 2. Calcular ganancia total (presupuesto - gasto material - IVA)
            profit = budget_total - material_expense - iva
            
            # 3. Distribución (70% Técnico, 30% Socio) sobre la ganancia
            technician_share = profit * 0.7
            facu_share = profit * 0.3
            
            # 4. Ganancia neta es igual a la ganancia total en este cálculo
            net_profit = profit
            
            # 5. Calcular el pago del seguro del técnico
            # Si hay pago de seguro, se asigna al técnico
            technician_insurance = insurance_payment
            
            # Actualizar los campos calculados
            self.profit_label.setText(f"${profit:,.2f}")
            self.net_profit_label.setText(f"${net_profit:,.2f}")
            self.technician_share_label.setText(f"${technician_share:,.2f}")
            self.facu_share_label.setText(f"${facu_share:,.2f}")
            self.insurance_payment_label.setText(f"${insurance_payment:,.2f}")
            self.cash_payment_label.setText(f"${cash_payment:,.2f}")
            self.material_expense_label.setText(f"${material_expense:,.2f}")
            self.iva_label.setText(f"${iva:,.2f}")
            self.technician_insurance_label.setText(f"${technician_insurance:,.2f}")
        except:
            pass
    
    def load_task_data(self):
        """Carga los datos de la tarea en el formulario"""
        if not self.task_data:
            return
            
        # Establecer técnico si ya está asignado
        technician_id = self.task_data.get('technician_id')
        if technician_id:
            index = self.technician_combo.findData(technician_id)
            if index >= 0:
                self.technician_combo.setCurrentIndex(index)
            
        self.client_name_input.setText(self.task_data.get('client_name', ''))
        self.task_description_input.setPlainText(self.task_data.get('task_description', ''))
        self.order_number_input.setText(self.task_data.get('order_number', ''))
        
        # Establecer fecha
        task_date = self.task_data.get('task_date')
        if task_date:
            try:
                if isinstance(task_date, str):
                    task_date = datetime.datetime.strptime(task_date, '%Y-%m-%d').date()
                self.task_date_edit.setDate(QDate(task_date.year, task_date.month, task_date.day))
            except:
                pass
        
        # Establecer valores monetarios
        self.set_currency_value(self.budget_total_input, float(self.task_data.get('budget_total', 0)))
        self.set_currency_value(self.labor_cost_input, float(self.task_data.get('labor_cost', 0)))
        self.set_currency_value(self.material_cost_input, float(self.task_data.get('material_cost', 0)))
        self.set_currency_value(self.insurance_payment_input, float(self.task_data.get('insurance_payment', 0)))
        self.set_currency_value(self.cash_payment_input, float(self.task_data.get('cash_payment', 0)))
        self.set_currency_value(self.material_expense_input, float(self.task_data.get('material_expense', 0)))
        
        # Establecer tipo de pago
        payment_type = self.task_data.get('payment_type', '')
        if payment_type:
            index = self.payment_type_combo.findText(payment_type)
            if index >= 0:
                self.payment_type_combo.setCurrentIndex(index)
        
        # Establecer estado
        status = self.task_data.get('status', 'PENDIENTE')
        index = self.status_combo.findText(status)
        if index >= 0:
            self.status_combo.setCurrentIndex(index)
        
        # Actualizar campos calculados
        self.calculate_derived_fields()
    
    def on_accept(self):
        """Maneja el evento de aceptar el diálogo"""
        if self.validate():
            self.accept()
    
    def validate(self):
        """Valida los datos del formulario"""
        if not self.client_name_input.text().strip():
            QMessageBox.warning(self, "Error", "El campo Cliente es obligatorio")
            return False
            
        if not self.task_description_input.toPlainText().strip():
            QMessageBox.warning(self, "Error", "El campo Descripción es obligatorio")
            return False
            
        budget_total = self.get_currency_value(self.budget_total_input)
        if budget_total <= 0:
            QMessageBox.warning(self, "Error", "El Presupuesto Total debe ser mayor a cero")
            return False
            
        # Validar que la suma de seguro + efectivo sea igual al presupuesto total
        insurance = self.get_currency_value(self.insurance_payment_input)
        cash = self.get_currency_value(self.cash_payment_input)
        
        if abs((insurance + cash) - budget_total) > 0.01:  # Permitir pequeñas diferencias de redondeo
            QMessageBox.warning(
                self, 
                "Error", 
                f"La suma del pago del seguro (${insurance:,.2f}) y efectivo (${cash:,.2f}) "
                f"debe ser igual al presupuesto total (${budget_total:,.2f})"
            )
            return False
            
        return True
    
    def get_task_data(self):
        """Devuelve un diccionario con los datos del formulario"""
        return {
            'technician_id': self.technician_combo.currentData(),
            'client_name': self.client_name_input.text().strip(),
            'task_description': self.task_description_input.toPlainText().strip(),
            'order_number': self.order_number_input.text().strip(),
            'task_date': self.task_date_edit.date().toString('yyyy-MM-dd'),
            'budget_total': self.get_currency_value(self.budget_total_input),
            'labor_cost': self.get_currency_value(self.labor_cost_input),
            'material_cost': self.get_currency_value(self.material_cost_input),
            'insurance_payment': self.get_currency_value(self.insurance_payment_input),
            'cash_payment': self.get_currency_value(self.cash_payment_input),
            'material_expense': self.get_currency_value(self.material_expense_input),
            'payment_type': self.payment_type_combo.currentText(),
            'status': self.status_combo.currentText()
        }
