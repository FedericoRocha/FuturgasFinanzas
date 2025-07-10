import sqlite3
import os
import pandas as pd
from datetime import datetime, timedelta

class Database:
    def __init__(self, db_name='technicians.db'):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        
    def connect(self):
        self.conn = sqlite3.connect(self.db_name)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
    
    def close(self):
        if self.conn:
            self.conn.close()
    
    def _table_exists(self, table_name):
        """Verifica si una tabla existe en la base de datos"""
        self.cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name=?
        """, (table_name,))
        return self.cursor.fetchone() is not None
        
    def _column_exists(self, table_name, column_name):
        """Verifica si una columna existe en una tabla"""
        self.cursor.execute(f'PRAGMA table_info({table_name})')
        columns = [column[1] for column in self.cursor.fetchall()]
        return column_name in columns
    
    def initialize_database(self):
        self.connect()
        
        # Crear tabla de técnicos si no existe
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS technicians (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Crear tabla de tareas si no existe
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            technician_id INTEGER,
            client_name TEXT NOT NULL,
            task_description TEXT,
            task_date TEXT,
            budget_total REAL,
            labor_cost REAL,
            material_cost REAL,
            insurance_payment REAL,
            cash_payment REAL,
            material_expense REAL,
            profit REAL,
            pablo_share REAL,
            facu_share REAL,
            iva REAL,
            payment_type TEXT,
            order_number TEXT,
            status TEXT DEFAULT 'PENDIENTE',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (technician_id) REFERENCES technicians (id)
        )
        ''')
        
        # Verificar y agregar columnas faltantes
        if self._table_exists('tasks'):
            # Lista de columnas que deberían existir
            required_columns = [
                'insurance_payment', 'cash_payment', 'material_expense',
                'profit', 'pablo_share', 'facu_share', 'iva', 'order_number'
            ]
            
            for column in required_columns:
                if not self._column_exists('tasks', column):
                    try:
                        self.cursor.execute(f'ALTER TABLE tasks ADD COLUMN {column} REAL')
                    except sqlite3.OperationalError:
                        # Si la columna es de tipo texto
                        if column in ['payment_type', 'order_number', 'status']:
                            self.cursor.execute(f'ALTER TABLE tasks ADD COLUMN {column} TEXT')
        
        self.conn.commit()
    
    # Métodos para técnicos
    def add_technician(self, name, email=None, phone=None):
        self.cursor.execute('''
        INSERT INTO technicians (name, email, phone)
        VALUES (?, ?, ?)
        ''', (name, email, phone))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_technicians(self):
        self.cursor.execute('SELECT * FROM technicians ORDER BY name')
        return [dict(row) for row in self.cursor.fetchall()]
    
    # Métodos para tareas
    def add_task(self, task_data):
        """Agrega una nueva tarea a la base de datos"""
        query = '''
        INSERT INTO tasks (
            technician_id, client_name, task_description, task_date,
            budget_total, labor_cost, material_cost, insurance_payment,
            cash_payment, material_expense, profit, pablo_share,
            facu_share, iva, payment_type, order_number, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        # Calcular campos derivados
        task_data = self._calculate_derived_fields(task_data)
        
        values = (
            task_data.get('technician_id'),
            task_data.get('client_name'),
            task_data.get('task_description'),
            task_data.get('task_date'),
            task_data.get('budget_total', 0),
            task_data.get('labor_cost', 0),
            task_data.get('material_cost', 0),
            task_data.get('insurance_payment', 0),
            task_data.get('cash_payment', 0),
            task_data.get('material_expense', 0),
            task_data.get('profit', 0),
            task_data.get('pablo_share', 0),
            task_data.get('facu_share', 0),
            task_data.get('iva', 0),
            task_data.get('payment_type', 'EFECTIVO'),
            task_data.get('order_number', ''),
            task_data.get('status', 'PENDIENTE')
        )
        
        self.cursor.execute(query, values)
        self.conn.commit()
        return self.cursor.lastrowid
        
    def _calculate_derived_fields(self, task_data):
        """Calcula los campos derivados de la tarea"""
        print("\n--- Calculando campos derivados ---")
        print("Datos de entrada:", task_data)
        
        try:
            # Convertir a float, manejando valores None o vacíos
            def to_float(value):
                if value is None or value == '':
                    return 0.0
                try:
                    return float(value)
                except (ValueError, TypeError):
                    return 0.0
            
            # Obtener valores y convertir a float
            budget_total = to_float(task_data.get('budget_total'))
            labor_cost = to_float(task_data.get('labor_cost'))
            material_cost = to_float(task_data.get('material_cost'))
            insurance_payment = to_float(task_data.get('insurance_payment'))
            cash_payment = to_float(task_data.get('cash_payment'))
            material_expense = to_float(task_data.get('material_expense'))
            
            print(f"Valores numéricos: budget_total={budget_total}, labor_cost={labor_cost}, material_cost={material_cost}")
            print(f"insurance_payment={insurance_payment}, cash_payment={cash_payment}, material_expense={material_expense}")
            
            # Si el pago total no coincide con la suma de seguro + efectivo, ajustar el efectivo
            total_payment = insurance_payment + cash_payment
            if abs(total_payment - budget_total) > 0.01:
                print(f"Ajustando pagos: total_payment({total_payment}) != budget_total({budget_total})")
                cash_payment = budget_total - insurance_payment
                print(f"Nuevo cash_payment: {cash_payment}")
            
            # Calcular IVA (10.5% sobre el presupuesto total)
            iva = budget_total * 0.105
            
            # Calcular ganancia total (presupuesto - gasto material - IVA)
            profit = budget_total - material_expense - iva
            
            print(f"Cálculo de ganancia: {budget_total} (presupuesto) - {material_expense} (material) - {iva} (IVA) = {profit} (ganancia)")
            
            # Calcular distribución (70% Técnico, 30% Socio) sobre la ganancia
            technician_share = profit * 0.7
            partner_share = profit * 0.3
            
            # Calcular el seguro neto (pago del seguro - IVA - porcentaje del socio)
            insurance_net = max(0, insurance_payment - iva - partner_share)
            
            print(f"Distribución: Técnico={technician_share}, Socio={partner_share}, IVA={iva}")
            print(f"Pago del seguro: {insurance_payment}, IVA: {iva}, Porcentaje socio: {partner_share}, Seguro neto: {insurance_net}")
            
            # Actualizar el diccionario con los campos calculados
            result = {
                'profit': round(profit, 2),
                'pablo_share': round(technician_share, 2),  # Mantener compatibilidad con el código existente
                'facu_share': round(partner_share, 2),     # Mantener compatibilidad con el código existente
                'technician_share': round(technician_share, 2),
                'partner_share': round(partner_share, 2),
                'insurance_net': round(insurance_net, 2),
                'iva': round(iva, 2),
                'insurance_payment': round(insurance_net, 2),  # Actualizar con el valor neto
                'cash_payment': round(cash_payment, 2),
                'material_expense': round(material_expense, 2),
                'budget_total': round(budget_total, 2),
                'labor_cost': round(labor_cost, 2),
                'material_cost': round(material_cost, 2)
            }
            
            print("Resultados calculados:", result)
            task_data.update(result)
            
        except Exception as e:
            print(f"Error en cálculos: {e}")
            import traceback
            traceback.print_exc()
            
            # Establecer valores por defecto en caso de error
            defaults = {
                'profit': 0,
                'pablo_share': 0,
                'facu_share': 0,
                'iva': 0,
                'insurance_payment': 0,
                'cash_payment': 0,
                'material_expense': 0,
                'budget_total': 0,
                'labor_cost': 0,
                'material_cost': 0
            }
            task_data.update(defaults)
        
        print("Datos de salida:", task_data)
        return task_data
    
    def get_technician_tasks(self, technician_id, start_date=None, end_date=None):
        print(f"\n--- Buscando tareas para técnico ID: {technician_id} ---")
        print(f"Fecha inicio: {start_date}, Fecha fin: {end_date}")
        
        query = 'SELECT * FROM tasks WHERE technician_id = ?'
        params = [technician_id]
        
        if start_date:
            query += ' AND task_date >= ?'
            params.append(start_date)
        if end_date:
            query += ' AND task_date <= ?'
            params.append(end_date)
            
        query += ' ORDER BY task_date DESC'
        
        print(f"Ejecutando consulta: {query}")
        print(f"Parámetros: {params}")
        
        self.cursor.execute(query, tuple(params))
        tasks = [dict(row) for row in self.cursor.fetchall()]
        
        print(f"Tareas encontradas: {len(tasks)}")
        if tasks:
            print("Primera tarea:", {k: v for k, v in tasks[0].items() if k != 'task_description'})
        
        return tasks
        
    def get_task(self, task_id):
        """Obtiene una tarea por su ID"""
        self.cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
        result = self.cursor.fetchone()
        return dict(result) if result else None
        
    def update_task(self, task_id, task_data):
        """Actualiza una tarea existente"""
        print(f"\n--- Actualizando tarea ID: {task_id} ---")
        print("Datos de entrada:", task_data)
        
        # Calcular campos derivados
        task_data = self._calculate_derived_fields(task_data)
        
        query = """
        UPDATE tasks SET
            technician_id = ?,
            client_name = ?,
            task_description = ?,
            task_date = ?,
            budget_total = ?,
            labor_cost = ?,
            material_cost = ?,
            insurance_payment = ?,
            cash_payment = ?,
            material_expense = ?,
            profit = ?,
            pablo_share = ?,
            facu_share = ?,
            iva = ?,
            payment_type = ?,
            order_number = ?,
            status = ?
        WHERE id = ?
        """
        
        values = (
            task_data.get('technician_id'),
            task_data.get('client_name'),
            task_data.get('task_description'),
            task_data.get('task_date'),
            task_data.get('budget_total', 0),
            task_data.get('labor_cost', 0),
            task_data.get('material_cost', 0),
            task_data.get('insurance_payment', 0),
            task_data.get('cash_payment', 0),
            task_data.get('material_expense', 0),
            task_data.get('profit', 0),
            task_data.get('pablo_share', 0),
            task_data.get('facu_share', 0),
            task_data.get('iva', 0),
            task_data.get('payment_type', 'EFECTIVO'),
            task_data.get('order_number', ''),
            task_data.get('status', 'PENDIENTE'),
            task_id
        )
        
        try:
            self.cursor.execute(query, values)
            self.conn.commit()
            print("Tarea actualizada exitosamente")
            return True
        except Exception as e:
            print(f"Error al actualizar la tarea: {e}")
            return False
            
    def delete_task(self, task_id):
        """Elimina una tarea por su ID"""
        try:
            self.cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error al eliminar la tarea: {e}")
            return False
    
    def generate_report(self, technician_id, start_date=None, end_date=None):
        tasks = self.get_technician_tasks(technician_id, start_date, end_date)
        
        if not tasks:
            return None
            
        # Calcular totales
        total_tasks = len(tasks)
        total_income = sum(task['budget_total'] or 0 for task in tasks)
        total_labor = sum(task['labor_cost'] or 0 for task in tasks)
        total_material = sum(task['material_cost'] or 0 for task in tasks)
        total_insurance = sum(task['insurance_payment'] or 0 for task in tasks)
        total_cash = sum(task['cash_payment'] or 0 for task in tasks)
        total_material_expense = sum(task['material_expense'] or 0 for task in tasks)
        total_profit = sum(task['profit'] or 0 for task in tasks)
        total_iva = sum(task['iva'] or 0 for task in tasks)
        total_pablo = sum(task['pablo_share'] or 0 for task in tasks)
        total_facu = sum(task['facu_share'] or 0 for task in tasks)
        
        # Calcular totales por semana y mes
        weekly_totals = self._calculate_weekly_totals(tasks)
        monthly_totals = self._calculate_monthly_totals(tasks)
        
        # Crear resumen con todos los totales
        summary = {
            'total_tasks': total_tasks,
            'total_income': total_income,
            'total_labor': total_labor,
            'total_material': total_material,
            'total_insurance_payment': total_insurance,
            'total_cash_payment': total_cash,
            'total_material_expense': total_material_expense,
            'total_profit': total_profit,
            'total_iva': total_iva,
            'pablo_share': total_pablo,
            'facu_share': total_facu,
            'weekly_totals': weekly_totals,
            'monthly_totals': monthly_totals
        }
        
        report = {
            'technician': self.get_technician(technician_id),
            'tasks': tasks,
            'summary': summary,  # Usar el resumen completo
            'period': {
                'start': start_date,
                'end': end_date or datetime.now().strftime('%Y-%m-%d')
            }
        }
        
        return report
        
    def _calculate_weekly_totals(self, tasks):
        """Agrupa las tareas por semana y calcula totales"""
        weekly_data = {}
        for task in tasks:
            if not task['task_date']:
                continue
                
            # Obtener año y número de semana
            task_date = datetime.strptime(task['task_date'], '%Y-%m-%d')
            year_week = f"{task_date.year}-W{task_date.strftime('%U')}"
            
            if year_week not in weekly_data:
                weekly_data[year_week] = {
                    'week_start': task_date - timedelta(days=task_date.weekday()),
                    'income': 0,
                    'profit': 0,
                    'tasks': 0
                }
                
            weekly_data[year_week]['income'] += task['budget_total'] or 0
            weekly_data[year_week]['profit'] += task['profit'] or 0
            weekly_data[year_week]['tasks'] += 1
            
        return weekly_data
        
    def _calculate_monthly_totals(self, tasks):
        """Agrupa las tareas por mes y calcula totales"""
        monthly_data = {}
        for task in tasks:
            if not task['task_date']:
                continue
                
            # Obtener año y mes
            task_date = datetime.strptime(task['task_date'], '%Y-%m-%d')
            year_month = task_date.strftime('%Y-%m')
            
            if year_month not in monthly_data:
                monthly_data[year_month] = {
                    'month': task_date.replace(day=1),
                    'income': 0,
                    'profit': 0,
                    'tasks': 0
                }
                
            monthly_data[year_month]['income'] += task['budget_total'] or 0
            monthly_data[year_month]['profit'] += task['profit'] or 0
            monthly_data[year_month]['tasks'] += 1
            
        return monthly_data
        
    def get_technician(self, technician_id):
        self.cursor.execute('SELECT * FROM technicians WHERE id = ?', (technician_id,))
        result = self.cursor.fetchone()
        return dict(result) if result else None
        
    def export_to_excel(self, file_path):
        """
        Exporta todos los datos a un archivo Excel con dos hojas:
        - Una con los técnicos
        - Otra con las tareas
        """
        try:
            # Obtener todos los técnicos
            self.cursor.execute('SELECT * FROM technicians')
            technicians = [dict(row) for row in self.cursor.fetchall()]
            
            # Obtener todas las tareas con el nombre del técnico
            query = """
            SELECT t.*, tech.name as technician_name 
            FROM tasks t
            LEFT JOIN technicians tech ON t.technician_id = tech.id
            """
            self.cursor.execute(query)
            tasks = [dict(row) for row in self.cursor.fetchall()]
            
            # Crear un escritor de pandas Excel
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                # Exportar técnicos
                if technicians:
                    pd.DataFrame(technicians).to_excel(
                        writer, 
                        sheet_name='Tecnicos', 
                        index=False,
                        columns=['id', 'name', 'email', 'phone']
                    )
                
                # Exportar tareas
                if tasks:
                    # Definir el orden de las columnas
                    task_columns = [
                        'id', 'technician_id', 'technician_name', 'client_name', 'task_description',
                        'task_date', 'budget_total', 'labor_cost', 'material_cost',
                        'insurance_payment', 'cash_payment', 'material_expense',
                        'payment_type', 'order_number', 'status', 'created_at'
                    ]
                    
                    # Crear DataFrame y exportar
                    df_tasks = pd.DataFrame(tasks)
                    df_tasks = df_tasks[task_columns]  # Reordenar columnas
                    df_tasks.to_excel(writer, sheet_name='Tareas', index=False)
            
            return True, "Exportación exitosa"
            
        except Exception as e:
            return False, f"Error al exportar a Excel: {str(e)}"
    
    def import_from_excel(self, file_path):
        """
        Importa datos desde un archivo Excel con dos hojas:
        - Una con los técnicos
        - Otra con las tareas
        """
        try:
            # Leer el archivo Excel
            xls = pd.ExcelFile(file_path)
            
            # Importar técnicos si existe la hoja
            if 'Tecnicos' in xls.sheet_names:
                df_tech = pd.read_excel(xls, sheet_name='Tecnicos')
                for _, row in df_tech.iterrows():
                    # Verificar si el técnico ya existe
                    self.cursor.execute('SELECT id FROM technicians WHERE id = ?', (row['id'],))
                    if not self.cursor.fetchone():
                        self.cursor.execute(
                            'INSERT INTO technicians (id, name, email, phone) VALUES (?, ?, ?, ?)',
                            (row['id'], row['name'], row.get('email', ''), row.get('phone', ''))
                        )
            
            # Importar tareas si existe la hoja
            if 'Tareas' in xls.sheet_names:
                df_tasks = pd.read_excel(xls, sheet_name='Tareas')
                for _, row in df_tasks.iterrows():
                    # Verificar si la tarea ya existe
                    self.cursor.execute('SELECT id FROM tasks WHERE id = ?', (row['id'],))
                    if not self.cursor.fetchone():
                        # Crear diccionario con los datos de la tarea
                        task_data = {
                            'technician_id': row['technician_id'],
                            'client_name': row['client_name'],
                            'task_description': row['task_description'],
                            'task_date': row['task_date'].strftime('%Y-%m-%d') if not pd.isna(row['task_date']) else None,
                            'budget_total': float(row['budget_total']) if pd.notna(row['budget_total']) else 0,
                            'labor_cost': float(row['labor_cost']) if pd.notna(row['labor_cost']) else 0,
                            'material_cost': float(row['material_cost']) if pd.notna(row['material_cost']) else 0,
                            'insurance_payment': float(row['insurance_payment']) if pd.notna(row['insurance_payment']) else 0,
                            'cash_payment': float(row['cash_payment']) if pd.notna(row['cash_payment']) else 0,
                            'material_expense': float(row['material_expense']) if pd.notna(row['material_expense']) else 0,
                            'payment_type': row.get('payment_type', 'EFECTIVO'),
                            'order_number': str(row.get('order_number', '')),
                            'status': row.get('status', 'PENDIENTE')
                        }
                        
                        # Calcular campos derivados
                        task_data = self._calculate_derived_fields(task_data)
                        
                        # Insertar la tarea
                        self.add_task(task_data)
            
            self.conn.commit()
            return True, "Importación exitosa"
            
        except Exception as e:
            self.conn.rollback()
            return False, f"Error al importar desde Excel: {str(e)}"
