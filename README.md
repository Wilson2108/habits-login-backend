# HABITS LOGIN BACKEND

## 🧩 Backend

### Tecnologías

- Python 3.11
- FastAPI
- Uvicorn
- Mongo

### Funcionalidad

El backend funciona en conjunto con el frontend de la app de habits, para dar acceso a los usuarios de la app

- Registrar usuarios
- Logear usuarios

### Instalación

```bash
pip install -r requirements.txt
```

### Ejecución

```bash
uvicorn main:app --reload
```

El backend quedará disponible en:

```text
http://localhost:8000
```

---

## 📡 Endpoints principales

- `POST /login`
- `POST /register`

---

## 🚀 Flujo de ejecución

1. Iniciar el backend (FastAPI)
2. Iniciar el frontend (React)
3. El usuario interactúa con el frontend
4. El frontend llama a la API-LOGIN
5. El backend da acceso al usuario
