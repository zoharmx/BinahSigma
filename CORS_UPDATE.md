# ✅ CORS Configurado para Producción

## 🔧 Cambios Realizados

### 1. Backend - CORS Actualizado

**Archivos modificados:**
- ✅ `backend/main_v2.py` (línea 34)
- ✅ `backend/main.py` (línea 16)

**Configuración aplicada:**
```python
allow_origins=[
    "https://binahsigma.onrender.com",  # Production frontend
    "http://localhost:3000",            # Local development
    "http://localhost:8000",            # Local development
    "http://127.0.0.1:3000",            # Local development
    "http://127.0.0.1:8000",            # Local development
]
```

### 2. Frontend - URLs Actualizadas

**Archivos modificados:**
- ✅ `frontend/index_v2.html` (línea 467-468)
- ✅ `frontend/index.html` (línea 232)

**URLs actualizadas:**
```javascript
// Production
const API_URL_V1 = 'https://binahsigma.onrender.com/binah-sigma/analyze';
const API_URL_V2 = 'https://binahsigma.onrender.com/v2/analyze';
```

---

## 📋 Pasos para Deploy

### 1. Commit y Push los Cambios

```bash
# Agregar archivos modificados
git add backend/main.py backend/main_v2.py frontend/index.html frontend/index_v2.html

# Commit
git commit -m "Update CORS for production and frontend URLs"

# Push
git push origin main
```

### 2. Render Re-deployrá Automáticamente

Render detectará los cambios en tu repo y re-deployrá automáticamente.

Monitorea el deployment en: https://dashboard.render.com

---

## 🧪 Verificar el Deployment

### Test 1: Health Check

```bash
curl https://binahsigma.onrender.com/health
```

**Respuesta esperada:**
```json
{
  "status": "healthy",
  "version": "2.0.0"
}
```

### Test 2: CORS Headers (desde navegador)

Abre la consola del navegador en tu frontend y ejecuta:

```javascript
fetch('https://binahsigma.onrender.com/health')
  .then(r => r.json())
  .then(console.log)
  .catch(console.error)
```

**Si CORS funciona:** Verás el JSON de respuesta
**Si CORS falla:** Verás error "blocked by CORS policy"

### Test 3: API v1 (sin autenticación)

```bash
curl -X POST https://binahsigma.onrender.com/binah-sigma/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "context": "Test CORS",
    "decision_question": "¿Funciona CORS?",
    "stakeholders": ["usuarios"],
    "constraints": ["tiempo"],
    "time_horizon": "immediate"
  }'
```

### Test 4: API v2 (con autenticación)

Primero necesitas generar una API key:

```bash
# En tu máquina local
cd backend
python generate_api_keys.py
```

Copia el `demo_key` y úsalo:

```bash
curl -X POST https://binahsigma.onrender.com/v2/analyze \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TU_API_KEY_AQUI" \
  -d '{
    "context": "Test producción",
    "decision_question": "¿Funciona la API v2?",
    "stakeholders": ["usuarios"],
    "constraints": ["tiempo"],
    "time_horizon": "immediate",
    "provider": "mistral",
    "industry": "technology"
  }'
```

---

## 🌐 Opciones de Deployment Frontend

Tu backend está en Render, pero ¿dónde vas a hostear el frontend?

### Opción 1: Netlify (Recomendado para SPAs)

1. Crea cuenta en https://netlify.com
2. Conecta tu repo de GitHub
3. Configura:
   - **Build command:** (dejar vacío)
   - **Publish directory:** `frontend`
4. Deploy

Tu frontend estará en: `https://tu-app.netlify.app`

### Opción 2: Render Static Site

1. En Render dashboard → **New Static Site**
2. Conecta tu repo
3. Configura:
   - **Publish directory:** `frontend`
4. Deploy

### Opción 3: GitHub Pages

```bash
# Desde el directorio raíz
git checkout -b gh-pages
git push origin gh-pages
```

Luego en GitHub: Settings → Pages → Source: gh-pages branch

### Opción 4: Vercel

1. Instala Vercel CLI: `npm i -g vercel`
2. Desde `frontend/`:
   ```bash
   cd frontend
   vercel
   ```

---

## ⚠️ Importante: Actualizar CORS Después

Si deployeas el frontend en otro dominio (ej: Netlify), necesitarás actualizar CORS:

```python
# backend/main_v2.py
allow_origins=[
    "https://binahsigma.onrender.com",     # Backend
    "https://tu-app.netlify.app",          # Frontend en Netlify
    "http://localhost:3000",               # Local dev
    "http://localhost:8000",               # Local dev
]
```

Luego haz commit y push.

---

## 🔐 Security Check

Después del deployment, verifica:

- [ ] CORS solo permite dominios específicos (no `*`)
- [ ] HTTPS habilitado en producción
- [ ] API keys funcionan correctamente
- [ ] Rate limiting activo
- [ ] Health checks pasando

---

## 📊 URLs de Producción

| Servicio | URL |
|----------|-----|
| Backend API | https://binahsigma.onrender.com |
| Health Check | https://binahsigma.onrender.com/health |
| API v1 | https://binahsigma.onrender.com/binah-sigma/analyze |
| API v2 | https://binahsigma.onrender.com/v2/analyze |
| API Docs | https://binahsigma.onrender.com/docs |
| ReDoc | https://binahsigma.onrender.com/redoc |

---

## 🚀 Próximos Pasos

1. **Deploy el frontend** en Netlify/Vercel/GitHub Pages
2. **Actualizar CORS** con el dominio del frontend
3. **Generar API keys** de producción
4. **Configurar monitoring** (Sentry, UptimeRobot)
5. **Custom domain** (opcional)
6. **Marketing!** Product Hunt, Reddit, HN

---

## 🆘 Troubleshooting

### Error: "blocked by CORS policy"

**Causa:** El dominio del frontend no está en `allow_origins`

**Solución:** Agrega el dominio a `backend/main_v2.py` y redeploya

### Error: "Network error"

**Causa:** La URL del backend es incorrecta

**Solución:** Verifica que `https://binahsigma.onrender.com` esté activo

### Error: "401 Unauthorized" (v2)

**Causa:** API key inválida o no enviada

**Solución:**
1. Genera nueva API key con `python backend/generate_api_keys.py`
2. Asegúrate de enviar header: `Authorization: Bearer <key>`

### Error: "Health check failing"

**Causa:** Render no pudo iniciar la app

**Solución:**
1. Revisa logs en Render dashboard
2. Verifica que variables de entorno estén configuradas
3. Check que `requirements.txt` esté completo

---

## ✅ Status

- [x] CORS configurado para https://binahsigma.onrender.com
- [x] Frontend apunta a backend de producción
- [x] Localhost mantenido para desarrollo
- [ ] Deploy frontend a Netlify/Vercel
- [ ] Actualizar CORS con dominio del frontend (si es diferente)
- [ ] Generar API keys de producción
- [ ] Configurar monitoring

---

**¡CORS listo para producción! 🎉**

Ahora haz commit, push y Render re-deployrá automáticamente.
