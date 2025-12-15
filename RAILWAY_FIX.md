# 🔧 Railway Deployment Fix

## Problema Solucionado

El error de Railway se debía a que el Dockerfile estaba en `backend/` pero Railway no sabía usar ese directorio como contexto de build.

## ✅ Solución Aplicada

He movido el Dockerfile al directorio raíz y actualizado los paths:

- ✅ `Dockerfile` ahora en raíz (copia desde `backend/`)
- ✅ `.dockerignore` en raíz (optimiza build)
- ✅ `railway.json` actualizado con `dockerfilePath: "Dockerfile"`

## 📋 Pasos para Re-deployar en Railway

### Opción A: Si ya hiciste commit/push

```bash
# Si ya commiteaste los archivos anteriores, actualiza:
git add Dockerfile .dockerignore railway.json
git commit -m "Fix: Move Dockerfile to root for Railway"
git push
```

Railway detectará los cambios y re-deployrá automáticamente.

---

### Opción B: Si NO has hecho commit todavía

```bash
# Asegúrate de NO commitear .env.production
git add .
git commit -m "Binah-Sigma v2.0 - Production ready"
git push
```

---

## ⚙️ Configurar Variables en Railway

1. Ve a tu proyecto en Railway dashboard
2. Click en tu servicio "binah-sigma-api"
3. Ve a la pestaña **Variables**
4. Agrega estas variables:

```
MISTRAL_API_KEY=cqrcNINDiUWdfsRkUk9BBCq52XzphD1V
GEMINI_API_KEY=AIzaSyBxSQ6GGcujsIqNznxNQjJt-kKG4Wcuogo
DEEPSEEK_API_KEY=sk-181034ba355c4292ad7f149d569ce4e7
JWT_SECRET_KEY=v0nFwgGQbleNgcJSSDjTpXOVCPH75x5bIvFY-yc-sfQ
ENVIRONMENT=production
INIT_DEMO_KEYS=false
```

5. Click **Save** (Railway re-deployrá automáticamente)

---

## 🧪 Verificar el Deployment

Una vez que Railway termine de deployar:

```bash
# 1. Health check
curl https://binah-sigma-api-production.up.railway.app/health

# Deberías ver:
# {"status":"healthy","version":"2.0.0"}

# 2. Test con API key (genera una primero)
curl -X POST https://binah-sigma-api-production.up.railway.app/v2/analyze \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TU_API_KEY" \
  -d '{
    "context": "Test de producción",
    "decision_question": "¿Funciona el deployment?",
    "stakeholders": ["usuarios"],
    "constraints": ["tiempo"],
    "time_horizon": "immediate",
    "provider": "mistral",
    "industry": "technology"
  }'
```

---

## 📊 Estructura Actualizada

```
BinahSigma/
├── Dockerfile                 ← NUEVO (en raíz)
├── .dockerignore             ← NUEVO (en raíz)
├── railway.json              ← ACTUALIZADO
├── docker-compose.yml
├── backend/
│   ├── Dockerfile            ← ANTIGUO (mantener para local)
│   ├── requirements.txt
│   ├── main_v2.py
│   ├── engine_v2.py
│   └── ...
└── frontend/
    └── index_v2.html
```

---

## 🔍 Logs de Railway

Si algo falla, revisa los logs:

1. Railway Dashboard → Tu servicio
2. Tabs disponibles:
   - **Build Logs** - Ver el proceso de build
   - **Deploy Logs** - Ver el inicio de la aplicación
   - **HTTP Logs** - Ver requests HTTP

---

## ⚠️ Importante: CORS

Después del primer deployment exitoso, actualiza CORS:

```python
# backend/main_v2.py (línea 32)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://binah-sigma-api-production.up.railway.app",  # Tu Railway URL
        "http://localhost:3000"  # Solo para desarrollo local
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Luego:
```bash
git add backend/main_v2.py
git commit -m "Update CORS for production"
git push
```

---

## 🎯 Checklist Post-Deployment

Después de que Railway despliegue exitosamente:

- [ ] Health check funciona (`/health`)
- [ ] Generar API keys de producción (`python backend/generate_api_keys.py`)
- [ ] Test endpoint `/v2/analyze` con API key
- [ ] Actualizar CORS con tu dominio
- [ ] Actualizar frontend con tu Railway URL
- [ ] Configurar custom domain (opcional)
- [ ] Configurar monitoring (Sentry, UptimeRobot)

---

## 🆘 Troubleshooting

### Error: "Module not found"
→ Verifica que `requirements.txt` esté en `backend/` y el Dockerfile lo copie correctamente

### Error: "Permission denied"
→ El Dockerfile ya crea usuario `binah` no-root, esto es correcto

### Error: "Port already in use"
→ Railway asigna el port automáticamente vía `$PORT`, ya configurado

### Error: "Health check failing"
→ Espera 30-60 segundos para que la app inicie completamente

---

## ✅ Expected Build Output

Cuando Railway haga el build correctamente, verás:

```
[Region: europe-west4]
=========================
Using Detected Dockerfile
=========================

✓ COPY requirements.txt .
✓ RUN pip install --no-cache-dir -r requirements.txt
✓ COPY backend/ .
✓ RUN useradd -m -u 1000 binah
✓ Build successful

=========================
Deploying...
=========================

✓ Health check passed
✓ Service is live
```

---

## 💡 Comandos Útiles

```bash
# Ver estado de Railway
railway status

# Ver logs en tiempo real
railway logs

# Redeploy manual
railway up

# Abrir en navegador
railway open
```

---

**¡El fix está listo! Haz push de los cambios y Railway deployrá correctamente.** 🚀
