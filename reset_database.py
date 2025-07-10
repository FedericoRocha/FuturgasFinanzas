import sqlite3

def reset_database():
    # Conectar a la base de datos
    conn = sqlite3.connect('technicians.db')
    cursor = conn.cursor()
    
    try:
        # Eliminar todas las tareas
        cursor.execute("DELETE FROM tasks")
        
        # Reiniciar el contador de autoincremento
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='tasks'")
        
        # Confirmar los cambios
        conn.commit()
        print("Base de datos limpiada correctamente. Se eliminaron todas las tareas.")
        
    except sqlite3.Error as e:
        print(f"Error al limpiar la base de datos: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    reset_database()
