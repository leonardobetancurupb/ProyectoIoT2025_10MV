# Landing Page - Dashboard de Sensores IoT

Este proyecto implementa una landing page con dashboard para visualizar datos de sensores IoT, utilizando Streamlit como framework web.

## Características

- Página de inicio con información del proyecto
- Sistema de login y registro de usuarios
- Dashboard interactivo para visualización de datos
- Roles de usuario (admin y usuario normal)
- Gestión de datos según el rol del usuario

## Requisitos

- Docker
- Git

## Instalación y Ejecución

1. Clonar el repositorio:
```bash
git clone <url-del-repositorio>
cd landing_page
```

2. Construir la imagen Docker:
```bash
docker build -t landing-page .
```

3. Ejecutar el contenedor:
```bash
docker run -d -p 8501:8501 landing-page
```

4. Acceder a la aplicación:
- Abrir el navegador y visitar: http://localhost:8501

## Credenciales por defecto

- **Administrador**:
  - Usuario: admin
  - Contraseña: admin

## Estructura del Proyecto

```
landing_page/
├── .dockerignore
├── Dockerfile
├── README.md
├── requirements.txt
└── app.py
```

## Desarrollo

Para desarrollo local sin Docker:

1. Crear un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Ejecutar la aplicación:
```bash
streamlit run app.py
``` 