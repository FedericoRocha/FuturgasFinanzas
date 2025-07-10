# Sistema de Gestión de Técnicos

Aplicación de escritorio desarrollada en Python con PySide6 para la gestión de tareas y reportes de técnicos.

## Características Principales

- Gestión de técnicos (altas, bajas, modificaciones)
- Registro de tareas con seguimiento de costos y ganancias
- Generación de reportes detallados
- Cálculos automáticos de ganancias y porcentajes
- Interfaz intuitiva con tema oscuro
- Base de datos local SQLite
- Exportación de datos a diferentes formatos

## Requisitos del Sistema

- Python 3.8 o superior
- PySide6
- SQLite3
- Otras dependencias listadas en requirements.txt

## Instalación

### Opción 1: Instalación con Docker (Recomendado)

1. Asegúrate de tener [Docker](https://www.docker.com/get-started) instalado en tu sistema.

2. Clonar el repositorio:
   ```bash
   git clone [URL_DEL_REPOSITORIO]
   cd AnalisisExcel
   ```

3. Construir y ejecutar el contenedor:
   ```bash
   # Crear directorio para datos persistentes
   mkdir -p data
   
   # Construir y ejecutar con Docker Compose
   docker-compose up --build
   ```

   La aplicación debería iniciarse automáticamente.

### Opción 2: Instalación Manual

1. Clonar el repositorio:
   ```bash
   git clone [URL_DEL_REPOSITORIO]
   cd AnalisisExcel
   ```

2. Crear un entorno virtual (recomendado):
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Estructura del Proyecto

```
AnalisisExcel/
├── database/
│   └── database.py      # Clase para manejo de la base de datos
├── views/
│   ├── __init__.py
│   ├── technician_view.py  # Vista de gestión de técnicos
│   └── report_view.py      # Vista de reportes y tareas
├── resources/           # Recursos (imágenes, iconos, etc.)
├── main.py              # Punto de entrada de la aplicación
├── requirements.txt     # Dependencias del proyecto
└── README.md            # Este archivo
```

## Uso

1. Iniciar la aplicación:
   ```bash
   python main.py
   ```

2. **Gestión de Técnicos**:
   - Agregar nuevos técnicos con sus datos personales
   - Editar información existente
   - Dar de baja técnicos (lógica)

3. **Registro de Tareas**:
   - Registrar nuevas tareas con descripción y costo
   - Asignar tareas a técnicos
   - Registrar pagos y gastos asociados

4. **Reportes**:
   - Generar reportes por técnico o generales
   - Filtrar por fechas
   - Exportar reportes a diferentes formatos

## Base de Datos

La aplicación utiliza SQLite como base de datos local. 

- **Con Docker**: Los datos se almacenan en el directorio `./data/technicians.db` en tu sistema anfitrión.
- **Sin Docker**: Los datos se almacenan en el archivo `technicians.db` en el directorio raíz del proyecto.

### Respaldo de Datos

Para hacer una copia de seguridad de tus datos, simplemente copia el archivo `technicians.db` a una ubicación segura.

### Estructura de la Base de Datos

- **technicians**: Almacena información de los técnicos
- **tasks**: Registro de tareas realizadas

## Exportación de Datos

La aplicación permite exportar datos en diferentes formatos:
- Plantilla Excel para importación
- Reportes completos en formato de texto
- Datos para análisis en formato CSV

## Personalización

### Tema y Estilos

Los estilos se definen en `main.py` en el método `setup_styles()`. Se puede personalizar:
- Colores principales
- Fuentes
- Tamaños de elementos

### Configuración

Para modificar la configuración de la base de datos, editar el archivo `database/database.py`.

## Solución de Problemas

### Problemas con Docker

#### La interfaz gráfica no se muestra
- **Windows**: Asegúrate de tener instalado un servidor X como VcXsrv o Xming.
- **Linux/macOS**: Ejecuta `xhost +` en la terminal antes de iniciar el contenedor.

#### Problemas de permisos con la base de datos
Si ves errores de permisos con la base de datos, asegúrate de que el directorio `data` tenga los permisos correctos:
```bash
chmod -R 777 data/
```

### Problemas Comunes


### Error de Escalado en Pantallas de Alta Resolución

Si experimentas problemas de visualización en pantallas de alta resolución, la aplicación ya incluye configuraciones para manejar el escalado. Si persisten los problemas, verifica que tu sistema operativo tenga configurado correctamente el escalado para aplicaciones de escritorio.

### Problemas con la Base de Datos

Si la base de datos se corrompe o necesita ser reiniciada:
1. Hacer una copia de seguridad del archivo `technicians.db`
2. Eliminar el archivo `technicians.db`
3. Reiniciar la aplicación (se creará una nueva base de datos vacía)

## Contribución

1. Hacer fork del repositorio
2. Crear una rama para tu característica (`git checkout -b feature/nueva-funcionalidad`)
3. Hacer commit de tus cambios (`git commit -am 'Añadir nueva funcionalidad'`)
4. Hacer push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abrir un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## Contacto

Para consultas o soporte, contactar al desarrollador.

---

*Última actualización: Julio 2025*
