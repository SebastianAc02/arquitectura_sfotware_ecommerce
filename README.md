# Kibo — E-commerce de mascotas

Proyecto académico construido con **Django + PostgreSQL + Docker**.

Este README está orientado a evitar el problema de "solo funciona en mi PC" y asegurar que cualquier persona del equipo pueda levantar el sistema con el mismo comportamiento.

---

## 1) Stack tecnológico

- Python 3.11 (dentro del contenedor)
- Django 4.2
- PostgreSQL 15
- Docker + Docker Compose

La ejecución recomendada es **siempre con Docker**.

---

## 2) Requisitos previos (máquina host)

Instalar en tu computador:

1. **Docker Desktop** (incluye Docker Compose)
2. **Git**

Validar instalación:

```bash
docker --version
docker compose version
git --version
```

---

## 3) Clonar y entrar al proyecto

```bash
git clone https://github.com/SebastianAc02/arquitectura_sfotware_ecommerce.git
cd arquitectura_sfotware_ecommerce
```

---

## 4) Variables de entorno

El proyecto usa archivo `.env` en la raíz.

Si no existe, créalo con este contenido mínimo:

```env
SECRET_KEY=django-insecure-kibo-dev-key-change-in-prod
DEBUG=True
DB_NAME=kibo_db
DB_USER=kibo_user
DB_PASSWORD=kibo_pass
DB_HOST=db
DB_PORT=5432
```

Notas importantes:
- `DB_HOST=db` es correcto cuando corres con Docker Compose (nombre del servicio).
- No subir `.env` al repositorio.

---

## 5) Levantar proyecto con Docker (flujo recomendado)

### Paso 1: construir imágenes y levantar contenedores

```bash
docker compose up -d --build
```

### Paso 2: ejecutar migraciones

```bash
docker compose exec -T web python manage.py migrate
```

### Paso 3: cargar data demo (recomendado para pruebas funcionales)

```bash
docker compose exec -T web python manage.py seed_demo_data
```

### Paso 4: abrir aplicación

- App: http://localhost:8000
- (opcional) PostgreSQL expuesto en host: `localhost:5432`

---

## 6) Credenciales de prueba

Después de ejecutar `seed_demo_data`:

- Admin de dominio y Django Admin:
  - usuario: `kibo_admin`
  - contraseña: `kibo12345`
  - permisos: `is_staff=True`, `is_superuser=True`
- Clientes demo:
  - usuarios: `cliente1` a `cliente5`
  - contraseña: `kibo12345`

---

## 7) Rutas principales

- Home: `/`
- Catálogo: `/catalogo/`
- Detalle de producto: `/producto/<slug>/`
- Carrito: `/carrito/`
- Checkout: `/checkout/`
- Mis órdenes: `/mis-ordenes/`
- Login: `/accounts/login/`
- Registro: `/accounts/register/`
- Perfil: `/accounts/profile/`
- Panel admin custom: `/panel/`
- Django admin built-in: `/django-admin/`

---

## 8) Comandos útiles de operación

### Ver logs

```bash
docker compose logs -f web
docker compose logs -f db
```

### Reiniciar servicios

```bash
docker compose restart web
docker compose restart db
```

### Entrar a shell de Django

```bash
docker compose exec -T web python manage.py shell
```

### Verificar estado de Django

```bash
docker compose exec -T web python manage.py check
```

### Bajar contenedores

```bash
docker compose down
```

### Bajar contenedores y borrar volúmenes (reset total de BD)

```bash
docker compose down -v
```

---

## 9) Guía anti "solo funciona en mi PC"

Seguir estas reglas en el equipo:

1. **Usar Docker siempre** para ejecutar backend y DB.
2. No depender de paquetes instalados en Python local.
3. Versionar cambios de modelo con `makemigrations` y `migrate`.
4. Mantener `.env` con las mismas claves requeridas.
5. Levantar desde cero al menos una vez por rama:
   ```bash
   docker compose down -v
   docker compose up -d --build
   docker compose exec -T web python manage.py migrate
   ```
6. Verificar antes de hacer PR:
   ```bash
   docker compose exec -T web python manage.py check
   ```

---

## 10) Solución de problemas comunes

### Error: puerto 8000 ocupado

```bash
lsof -i :8000
```
Cerrar el proceso o cambiar mapeo de puerto en `docker-compose.yml`.

### Error: puerto 5432 ocupado

```bash
lsof -i :5432
```
Cerrar PostgreSQL local o cambiar puerto host del servicio `db`.

### Error de conexión a PostgreSQL

- Si estás en Docker, validar que `.env` use `DB_HOST=db`.
- Revisar logs:
  ```bash
  docker compose logs -f db
  docker compose logs -f web
  ```

### Django Admin: "autenticado pero no autorizado"

Si aparece el mensaje de que estás autenticado como otro usuario (por ejemplo, un cliente) pero no autorizado:

1. Cierra sesión en `/accounts/logout/`.
2. Abre una ventana incógnito y entra a `/django-admin/`.
3. Re-ejecuta seed para reforzar permisos del admin demo:
   ```bash
   docker compose exec -T web python manage.py seed_demo_data
   ```
4. Ingresa con:
   - usuario: `kibo_admin`
   - contraseña: `kibo12345`

### Error de dependencias tipo `psycopg2`

Si corres sin Docker puede ocurrir. Solución recomendada: ejecutar por Docker.

### Cambios no reflejados

```bash
docker compose up -d --build
```
Si persiste, reconstruir sin caché:

```bash
docker compose build --no-cache web
docker compose up -d
```

---

## 11) Ejecución local sin Docker (no recomendada)

Solo para casos puntuales:

1. Crear y activar entorno virtual
2. `pip install -r requirements.txt`
3. Levantar PostgreSQL local
4. Cambiar `.env` a `DB_HOST=localhost`
5. `python manage.py migrate`
6. `python manage.py runserver 8000`

La ruta oficial del proyecto sigue siendo Docker para asegurar reproducibilidad.
