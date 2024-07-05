# Documento de Requisitos del Sistema

## Descripción General

El objetivo de este sistema es monitorear la temperatura de lugares refrigerados y vehículos en movimiento (como furgonetas de carne, pescado o helados). El sistema utilizará dispositivos Arduino para sensar la temperatura y enviarla a la nube para su almacenamiento y análisis. Los datos recolectados se utilizarán para generar gráficos y estadísticas, y se mantendrán almacenados por al menos 48 horas. Además, el sistema enviará alertas a través de Telegram cuando la temperatura esté fuera del rango preestablecido.

## Requisitos Funcionales

### Sensado de Temperatura
1. El sistema debe sensar la temperatura de lugares refrigerados y vehículos en movimiento.
2. El sistema debe utilizar el sensor digital de temperatura DS18b20 conectado a un Arduino con conexión WiFi.
3. Los datos de temperatura deben ser registrados con fecha y hora.

### Transmisión de Datos
4. Los datos de temperatura deben ser enviados a la nube cada minuto.
5. La transmisión debe garantizar que los datos no sean volátiles por al menos 48 horas.

### Almacenamiento y Análisis de Datos
6. Los datos deben ser almacenados en una base de datos en la nube.
7. La aplicación web debe permitir la visualización de gráficos y estadísticas de las temperaturas registradas.
8. La aplicación web debe utilizar Python, Django, Matplotlib, Bootstrap, HTML, CSS y JavaScript para su desarrollo.

### Gestión de Usuarios y Equipos
9. El sistema debe permitir la creación de múltiples usuarios con contraseñas.
10. Cada usuario debe poder gestionar varios equipos de varios clientes.
11. Los usuarios deben poder visualizar los datos de temperatura y las estadísticas de sus equipos.

### Alertas
12. El sistema debe proporcionar alertas a través de Telegram si la temperatura de un equipo está fuera del rango preestablecido.
13. Las alertas deben ser configurables por el usuario.

## Requisitos No Funcionales

### Confiabilidad
1. El sistema debe asegurar la integridad y disponibilidad de los datos por al menos 48 horas.
2. El sistema debe manejar de manera eficiente la conexión intermitente de los equipos en movimiento.

### Rendimiento
3. La transmisión de datos debe realizarse cada minuto sin afectar el rendimiento del sistema.
4. La generación de gráficos y estadísticas debe ser rápida y eficiente.

### Seguridad
5. El sistema debe garantizar la seguridad de los datos mediante autenticación y autorización de usuarios.


### Usabilidad
7. La aplicación web debe ser intuitiva y fácil de usar para usuarios con diferentes niveles de experiencia.

### Mantenimiento
8. El sistema debe ser modular y fácil de mantener y actualizar.
9. Debe ser posible agregar nuevos sensores o tipos de datos en el futuro sin realizar cambios significativos en el sistema.

## Componentes del Sistema

### Hardware
- Arduino con conexión WiFi
- Sensor Digital de Temperatura DS18b20 Cable Sumergible
- Caja de conexión

### Software
- Python
- Django
- Matplotlib
- Bootstrap
- HTML
- CSS
- JavaScript
- Telegram API para alertas

