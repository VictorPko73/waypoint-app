# 🚀 Guía de Deploy en Render - Waypoint App

## 📋 Configuración en Render

### 1️⃣ Crear Web Service

1. Ve a [Render Dashboard](https://dashboard.render.com/)
2. Click en **"New +"** → **"Web Service"**
3. Conecta tu repositorio de GitHub: `VictorPko73/waypoint-app`
4. Configura los siguientes campos:

### 2️⃣ Configuración Básica

| Campo | Valor |
|-------|-------|
| **Name** | `waypoint-app` (o el nombre que prefieras) |
| **Region** | Selecciona la región más cercana |
| **Branch** | `develop` (o `main`) |
| **Runtime** | `Python 3` |
| **Build Command** | `./render_build.sh` |
| **Start Command** | `gunicorn --bind 0.0.0.0:$PORT wsgi:app` |

### 3️⃣ Variables de Entorno

Ve a **Environment** y agrega las siguientes variables:

#### ✅ Variables Obligatorias

```bash
# Database (Render lo genera automáticamente si creas PostgreSQL)
DATABASE_URL=postgresql://...  # Se auto-configura al conectar base de datos

# JWT Secret (genera una clave segura aleatoria)
JWT_SECRET_KEY=tu-clave-secreta-super-segura-de-minimo-32-caracteres

# Python version
PYTHON_VERSION=3.11.9
```

#### ⚙️ Variables Opcionales (pero recomendadas)

```bash
# API Keys
PEXELS_API_KEY=tu_clave_de_pexels

# Email Configuration (para reportes)
REPORT_RECEIVER_EMAIL=tu_email@ejemplo.com
EMAIL_USER=tu_email@ejemplo.com
EMAIL_PASS=tu_password_de_app

# Admin Password (para usuario administrador inicial)
ADMIN_PASSWORD=TuPasswordSeguroDeAdmin2025!

# Frontend
VITE_BACKEND_URL=https://tu-app.onrender.com
```

### 4️⃣ Crear Base de Datos PostgreSQL

1. En Render Dashboard, click **"New +"** → **"PostgreSQL"**
2. Configura:
   - **Name**: `waypoint-db`
   - **Database**: `waypoint`
   - **User**: `waypoint_user`
   - **Region**: Misma que tu Web Service
   - **Plan**: Free (o el que prefieras)

3. Una vez creada, copia la **Internal Database URL**
4. En tu Web Service, agrega como variable de entorno:
   ```bash
   DATABASE_URL=postgresql://...
   ```

### 5️⃣ Deploy

1. Click en **"Create Web Service"**
2. Render automáticamente:
   - Instalará dependencias de Node.js
   - Construirá el frontend
   - Instalará dependencias de Python
   - Ejecutará migraciones
   - **🌱 Cargará datos iniciales automáticamente** (usuarios, rutas, votos)
   - Iniciará la aplicación

### 6️⃣ Verificar Deploy

Una vez completado el deploy:

1. Accede a la URL de tu app: `https://tu-app.onrender.com`
2. Deberías ver la aplicación funcionando con datos precargados

## 🔐 Credenciales por Defecto

Una vez deployado, puedes acceder con:

### Usuario Administrador
- **Email**: `admin@waypoint.com`
- **Password**: El valor de `ADMIN_PASSWORD` (por defecto: `WaypointAdmin2025!`)

### Usuarios Normales
- **Email**: `maria@waypoint.com` | **Password**: `WaypointUser2025!`
- **Email**: `juan@waypoint.com` | **Password**: `WaypointUser2025!`
- **Email**: `ana@waypoint.com` | **Password**: `WaypointUser2025!`
- **Email**: `carlos@waypoint.com` | **Password**: `WaypointUser2025!`

## 📊 Datos Precargados

El script de inicialización crea automáticamente:

- ✅ **5 usuarios** (1 admin + 4 usuarios normales)
- ✅ **25+ rutas turísticas** de ciudades alrededor del mundo:
  - España (Madrid, Barcelona, Sevilla)
  - Francia (París, Lyon)
  - Italia (Roma, Florencia, Venecia)
  - Reino Unido (Londres, Edimburgo)
  - Alemania (Berlín, Múnich)
  - Países Bajos (Ámsterdam)
  - Y muchas más...
- ✅ **Votos aleatorios** para cada ruta (1-3 votos por ruta)

## 🔄 Actualizaciones

Para actualizar la aplicación:

1. Haz push de tus cambios a la rama configurada:
   ```bash
   git push origin develop
   ```

2. Render detectará automáticamente los cambios y hará redeploy

## 🛠️ Troubleshooting

### Error: "DATABASE_URL not found"
- Asegúrate de haber creado la base de datos PostgreSQL
- Verifica que la variable `DATABASE_URL` esté configurada en Environment

### Error: "PyYAML build failed"
- ✅ Ya solucionado - `Pipfile` configurado para Python 3.11
- ✅ `requirements.txt` actualizado con PyYAML 6.0.1

### La app no muestra datos
- Revisa los logs de deploy: busca "🌱 Inicializando datos por defecto"
- Puedes ejecutar manualmente: `flask insert-test-data` desde Render Shell

### Cambiar contraseña de admin
1. Ve a Environment en Render
2. Cambia `ADMIN_PASSWORD`
3. Redeploy (o espera a que se reinicie)

## 📝 Comandos Útiles

### Acceder a Shell en Render
```bash
# En Render Dashboard → Shell
flask shell
```

### Regenerar datos (desde Shell)
```bash
flask insert-test-data
```

### Ver estadísticas de la BD
```bash
flask shell
>>> from api.models import User, Route, Vote
>>> print(f"Usuarios: {User.query.count()}")
>>> print(f"Rutas: {Route.query.count()}")
>>> print(f"Votos: {Vote.query.count()}")
```

## 🔗 Enlaces Importantes

- **Render Dashboard**: https://dashboard.render.com/
- **Documentación Render**: https://render.com/docs
- **GitHub Repo**: https://github.com/VictorPko73/waypoint-app

---

¿Problemas? Revisa los logs en Render Dashboard → tu-app → Logs
