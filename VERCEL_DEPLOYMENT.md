# 🚀 Deploy Frontend a Vercel

## Método 1: Deploy desde Dashboard (Más Fácil)

### Paso 1: Preparar el Repositorio

```bash
# 1. Agregar vercel.json
git add vercel.json

# 2. Commit todos los cambios pendientes
git add .
git commit -m "Add Vercel configuration for frontend deployment"

# 3. Push a GitHub
git push origin main
```

### Paso 2: Conectar con Vercel

1. Ve a https://vercel.com y crea una cuenta (puedes usar GitHub)
2. Click en **"Add New Project"**
3. Click en **"Import Git Repository"**
4. Selecciona tu repositorio `binah-sigma`

### Paso 3: Configurar el Proyecto

En la pantalla de configuración:

**Framework Preset:** `Other`

**Build Settings:**
- **Build Command:** (dejar vacío)
- **Output Directory:** (dejar vacío)
- **Install Command:** (dejar vacío)

**Root Directory:**
- Click en **"Edit"**
- Selecciona **`frontend`**

**Environment Variables:** (ninguna necesaria por ahora)

### Paso 4: Deploy

1. Click en **"Deploy"**
2. Espera ~30 segundos
3. ¡Listo! Tu app estará en: `https://binah-sigma-XXXXX.vercel.app`

---

## Método 2: Deploy desde CLI (Más Rápido)

### Paso 1: Instalar Vercel CLI

```bash
npm install -g vercel
```

### Paso 2: Login

```bash
vercel login
```

Sigue las instrucciones en tu navegador.

### Paso 3: Deploy

```bash
# Desde el directorio raíz del proyecto
cd frontend
vercel
```

**Responde las preguntas:**
- Set up and deploy? `Y`
- Which scope? (selecciona tu cuenta)
- Link to existing project? `N`
- What's your project's name? `binah-sigma`
- In which directory is your code located? `./` (ya estás en frontend/)
- Want to override settings? `N`

**Deployment completado!** Vercel te dará una URL como:
```
https://binah-sigma-XXXXX.vercel.app
```

### Deploy a Producción

```bash
# Para futuras actualizaciones
vercel --prod
```

---

## Paso 4: Actualizar CORS del Backend

Una vez que tengas tu URL de Vercel, actualiza el backend:

```python
# backend/main_v2.py
allow_origins=[
    "https://binahsigma.onrender.com",          # Backend URL
    "https://binah-sigma-XXXXX.vercel.app",     # ← Tu URL de Vercel
    "http://localhost:3000",                     # Local dev
    "http://localhost:8000",                     # Local dev
]
```

Luego:
```bash
git add backend/main_v2.py backend/main.py
git commit -m "Add Vercel frontend URL to CORS"
git push
```

Render re-deployrá automáticamente con el nuevo CORS.

---

## 🌐 URLs después del Deploy

| Servicio | URL |
|----------|-----|
| Frontend v2 | https://binah-sigma-XXXXX.vercel.app |
| Frontend v1 | https://binah-sigma-XXXXX.vercel.app/v1 |
| Backend API | https://binahsigma.onrender.com |

---

## 🎨 Custom Domain (Opcional)

### En Vercel:

1. Ve a tu proyecto en Vercel dashboard
2. Click en **"Settings"** → **"Domains"**
3. Agrega tu dominio (ej: `binahsigma.com`)
4. Sigue las instrucciones para configurar DNS

### Configurar DNS:

Si tu dominio está en Namecheap/GoDaddy/etc:

**A Record:**
```
Type: A
Host: @
Value: 76.76.21.21
```

**CNAME Record:**
```
Type: CNAME
Host: www
Value: cname.vercel-dns.com
```

Luego actualiza CORS del backend con tu dominio custom.

---

## 🔧 Configuración Avanzada (Opcional)

### 1. Variables de Entorno en Vercel

Si necesitas configurar algo del lado del cliente:

1. Vercel Dashboard → Tu Proyecto → **Settings** → **Environment Variables**
2. Agrega:
   ```
   NEXT_PUBLIC_API_URL=https://binahsigma.onrender.com
   ```

### 2. Redirects Personalizados

Edita `vercel.json` para agregar redirects:

```json
{
  "redirects": [
    {
      "source": "/old-path",
      "destination": "/new-path",
      "permanent": true
    }
  ]
}
```

### 3. Analytics

Vercel ofrece analytics gratis:

1. Dashboard → Tu Proyecto → **Analytics**
2. Activa **Web Analytics**

---

## 🧪 Verificar el Deployment

### Test 1: Frontend Carga Correctamente

```bash
curl https://binah-sigma-XXXXX.vercel.app
```

Deberías ver el HTML de `index_v2.html`.

### Test 2: Llamada al Backend desde Frontend

1. Abre tu Vercel URL en el navegador
2. Abre Developer Tools (F12) → Console
3. Intenta un análisis con los ejemplos pre-cargados
4. Verifica que no haya errores de CORS

### Test 3: Performance

Vercel optimiza automáticamente:
- ✅ Compression (gzip/brotli)
- ✅ CDN global
- ✅ Edge caching
- ✅ HTTPS automático

Prueba con: https://pagespeed.web.dev

---

## 📊 Monitoreo con Vercel

### Deployment Logs

```bash
# Ver logs en tiempo real
vercel logs

# Ver logs de producción
vercel logs --prod
```

### Analytics

Dashboard → Tu Proyecto → **Analytics**

Métricas disponibles:
- Page views
- Unique visitors
- Top pages
- Referrers
- Devices

---

## 🚨 Troubleshooting

### Error: "Cannot find module"

**Causa:** Vercel está buscando dependencias de Node.js

**Solución:** En `vercel.json`, asegúrate de:
```json
"builds": [
  {
    "src": "frontend/**",
    "use": "@vercel/static"
  }
]
```

### Error: "404 - File not found"

**Causa:** Root directory mal configurado

**Solución:**
1. Vercel Dashboard → Settings → General
2. Root Directory → `frontend`
3. Redeploy

### Error: "CORS blocked"

**Causa:** URL de Vercel no está en CORS del backend

**Solución:** Agrega tu Vercel URL a `backend/main_v2.py` y redeploya Render

### Error: "API request failed"

**Causa:** Frontend apuntando a localhost en vez de producción

**Solución:** Verifica que `frontend/index_v2.html` tenga:
```javascript
const API_URL_V2 = 'https://binahsigma.onrender.com/v2/analyze';
```

---

## 🔄 Workflow de Actualizaciones

Para futuras actualizaciones del frontend:

```bash
# 1. Hacer cambios en frontend/
# 2. Commit
git add frontend/
git commit -m "Update frontend feature X"

# 3. Push
git push origin main

# 4. Vercel re-deploya automáticamente
```

Vercel detecta cambios en tu repo y re-deploya automáticamente en ~30 segundos.

---

## 💰 Costos

### Vercel Free Tier:

- ✅ 100 GB bandwidth/mes
- ✅ Deployments ilimitados
- ✅ HTTPS automático
- ✅ CDN global
- ✅ Preview deployments

**Suficiente para:**
- ~50,000 page views/mes
- Proyectos personales
- MVPs y prototipos

### Vercel Pro ($20/mes):

- 1 TB bandwidth
- Analytics avanzadas
- Más concurrencia
- Password protection

---

## 🎯 Checklist Post-Deployment

- [ ] Frontend deployado en Vercel
- [ ] URL de Vercel funciona
- [ ] CORS actualizado en backend con URL de Vercel
- [ ] Backend re-deployado en Render
- [ ] Test de análisis v2 funciona end-to-end
- [ ] Test de análisis v1 funciona
- [ ] Performance check (PageSpeed)
- [ ] Mobile responsive verificado
- [ ] Custom domain configurado (opcional)
- [ ] Analytics activado
- [ ] README actualizado con URLs de producción

---

## 🚀 Deploy en 3 Comandos

```bash
# 1. Commit vercel.json
git add vercel.json && git commit -m "Add Vercel config" && git push

# 2. Deploy a Vercel
cd frontend && vercel --prod

# 3. Actualizar CORS y redeploy backend
# (editar backend/main_v2.py con URL de Vercel)
git add backend/main_v2.py && git commit -m "Add Vercel URL to CORS" && git push
```

---

## 📞 Soporte

- **Vercel Docs:** https://vercel.com/docs
- **Vercel Discord:** https://vercel.com/discord
- **Vercel Status:** https://www.vercel-status.com

---

## ✅ Arquitectura Final

```
┌─────────────────────────────────────┐
│   Frontend (Vercel)                 │
│   https://binah-sigma.vercel.app    │
│                                     │
│   - index_v2.html (v2 UI)          │
│   - index.html (v1 UI)             │
│   - Optimized by Vercel CDN        │
└────────────┬────────────────────────┘
             │
             │ HTTPS Requests
             │ (CORS configured)
             ↓
┌─────────────────────────────────────┐
│   Backend (Render)                  │
│   https://binahsigma.onrender.com   │
│                                     │
│   - FastAPI v2.0                   │
│   - Multi-provider LLM             │
│   - JWT Authentication             │
│   - Rate Limiting                  │
└────────────┬────────────────────────┘
             │
             │ API Calls
             ↓
┌─────────────────────────────────────┐
│   LLM Providers                     │
│                                     │
│   - Mistral AI                     │
│   - Google Gemini                  │
│   - DeepSeek                       │
└─────────────────────────────────────┘
```

---

**¡Listo para deployar a Vercel! 🎉**

Método recomendado: **Dashboard** (más visual)
Método más rápido: **CLI** (1 comando)
