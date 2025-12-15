# 🚀 Deploy a Vercel - GUÍA RÁPIDA

## Método 1: Dashboard de Vercel (Recomendado - Más Visual)

### Paso 1: Commit y Push a GitHub

```bash
# Asegúrate de estar en el directorio raíz
cd C:\Users\jesus\BinahSigma

# Agregar todos los archivos nuevos
git add .

# Commit
git commit -m "Ready for Vercel deployment - Frontend v2.0"

# Push a GitHub
git push origin main
```

**⚠️ Si no tienes GitHub configurado todavía:**

```bash
# 1. Crear repo en GitHub (ve a github.com/new)
# Nombre sugerido: binah-sigma

# 2. Configurar git local
git init
git add .
git commit -m "Initial commit - Binah-Sigma v2.0"

# 3. Conectar con GitHub (reemplaza TU_USERNAME)
git remote add origin https://github.com/TU_USERNAME/binah-sigma.git
git branch -M main
git push -u origin main
```

---

### Paso 2: Crear Cuenta en Vercel

1. Ve a https://vercel.com
2. Click en **"Sign Up"**
3. Selecciona **"Continue with GitHub"**
4. Autoriza Vercel a acceder a tus repos

---

### Paso 3: Importar Proyecto

1. En el dashboard de Vercel, click **"Add New..."** → **"Project"**

2. Busca tu repo **"binah-sigma"** y click **"Import"**

3. Verás la pantalla de configuración:

---

### Paso 4: Configurar Deployment

**Configure Project:**

```
Framework Preset: Other
Root Directory: frontend  ← IMPORTANTE: Edita esto
Build Command: (dejar vacío)
Output Directory: (dejar vacío)
Install Command: (dejar vacío)
```

**Cómo editar Root Directory:**
1. Click en **"Edit"** al lado de "Root Directory"
2. Escribe: `frontend`
3. Click en el check ✓

**Environment Variables:**
- No necesitas agregar ninguna (el frontend no tiene secrets)

---

### Paso 5: Deploy!

1. Click en **"Deploy"**
2. Espera ~30-60 segundos
3. Verás la animación de build

**Cuando termine, verás:**
```
🎉 Congratulations!
Your project is live at:
https://binah-sigma-XXXXX.vercel.app
```

4. Click en **"Visit"** para ver tu app live!

---

### Paso 6: Actualizar CORS del Backend

Una vez que tengas tu URL de Vercel (ej: `https://binah-sigma-abc123.vercel.app`):

1. Copia la URL completa
2. Edita `backend/main_v2.py`:

```python
# Línea 34 aproximadamente
allow_origins=[
    "https://binahsigma.onrender.com",          # Backend
    "https://binah-sigma-XXXXX.vercel.app",     # ← Pega tu URL aquí
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
]
```

3. También actualiza `backend/main.py` (línea 16)

4. Commit y push:
```bash
git add backend/main_v2.py backend/main.py
git commit -m "Add Vercel URL to CORS"
git push
```

Render re-deployrá automáticamente con el nuevo CORS.

---

## Método 2: CLI de Vercel (Más Rápido)

### Paso 1: Instalar Vercel CLI

```bash
npm install -g vercel
```

### Paso 2: Login

```bash
vercel login
```

Se abrirá tu navegador. Confirma el login.

### Paso 3: Deploy

```bash
# Desde el directorio raíz del proyecto
cd C:\Users\jesus\BinahSigma\frontend

# Deploy
vercel
```

**Responde las preguntas:**

```
? Set up and deploy? [Y/n] Y
? Which scope? (selecciona tu cuenta)
? Link to existing project? [y/N] N
? What's your project's name? binah-sigma
? In which directory is your code located? ./
? Want to override the settings? [y/N] N
```

**¡Listo!** Vercel te dará URLs:

```
🔍  Inspect: https://vercel.com/tu-cuenta/binah-sigma/XXXXX
✅  Preview: https://binah-sigma-XXXXX.vercel.app
```

### Paso 4: Deploy a Producción

```bash
# Desde frontend/
vercel --prod
```

Esto te dará la URL final de producción.

---

## 🧪 Verificar el Deployment

### Test 1: Frontend Carga

Abre tu URL de Vercel en el navegador:
```
https://binah-sigma-XXXXX.vercel.app
```

Deberías ver la interfaz de Binah-Σ v2.0.

### Test 2: Health Check del Backend

Abre Developer Tools (F12) → Console y ejecuta:

```javascript
fetch('https://binahsigma.onrender.com/health')
  .then(r => r.json())
  .then(console.log)
```

Deberías ver:
```json
{"status":"healthy","version":"2.0.0"}
```

### Test 3: Análisis Completo

1. En tu Vercel URL, selecciona un ejemplo (ej: "Twitter Layoffs")
2. Click en "Run Analysis"
3. Verifica que no haya errores de CORS
4. Deberías ver el resultado del análisis

**Si hay error de CORS:**
- Asegúrate de haber actualizado `backend/main_v2.py` con tu URL de Vercel
- Espera 2-3 minutos para que Render re-deploye

---

## 🔧 Configuración Post-Deployment

### 1. Configurar Custom Domain (Opcional)

En Vercel Dashboard:
1. Ve a tu proyecto → **Settings** → **Domains**
2. Agrega tu dominio: `binahsigma.com`
3. Sigue las instrucciones de DNS

### 2. Activar Analytics

En Vercel Dashboard:
1. Ve a tu proyecto → **Analytics**
2. Click en **"Enable"**
3. Verás métricas de tráfico, performance, etc.

### 3. Configurar Preview Deployments

Vercel automáticamente crea preview URLs para cada push:

```bash
# Cada push a GitHub crea un preview
git push origin feature-branch

# Vercel te dará: https://binah-sigma-git-feature-branch-XXXXX.vercel.app
```

---

## 🎯 URLs Finales

Después del deployment, tendrás:

| Servicio | URL |
|----------|-----|
| **Frontend (Producción)** | https://binah-sigma-XXXXX.vercel.app |
| **Frontend v1** | https://binah-sigma-XXXXX.vercel.app/v1 |
| **Backend API** | https://binahsigma.onrender.com |
| **API Docs** | https://binahsigma.onrender.com/docs |
| **Health Check** | https://binahsigma.onrender.com/health |

---

## 🚨 Troubleshooting

### Error: "404 - Page Not Found"

**Causa:** Root directory no está configurado

**Solución:**
1. Vercel Dashboard → Tu proyecto → **Settings** → **General**
2. Root Directory → Edita a `frontend`
3. **Redeploy** en la pestaña Deployments

### Error: "CORS policy blocked"

**Causa:** Tu URL de Vercel no está en CORS del backend

**Solución:**
1. Agrega tu Vercel URL a `backend/main_v2.py`
2. Commit y push
3. Espera 2 minutos a que Render re-deploye

### Error: "Failed to fetch API"

**Causa:** Frontend apuntando a localhost

**Solución:**
Verifica en `frontend/index_v2.html` línea 467:
```javascript
const API_URL_V2 = 'https://binahsigma.onrender.com/v2/analyze';
```

### Build Logs con Errores

**Solución:**
1. Vercel Dashboard → Tu proyecto → **Deployments**
2. Click en el deployment fallido
3. Ve a **Build Logs** para ver el error específico

---

## 🔄 Workflow de Actualizaciones

Para futuras actualizaciones:

```bash
# 1. Hacer cambios en frontend/
# 2. Commit
git add frontend/
git commit -m "Update: nueva feature"

# 3. Push
git push origin main

# 4. Vercel re-deploya automáticamente en ~30 segundos
```

---

## 📊 Monitoreo

### Ver Deployments

```bash
vercel ls
```

### Ver Logs en Tiempo Real

```bash
vercel logs
```

### Ver Logs de Producción

```bash
vercel logs --prod
```

---

## ✅ Checklist Final

- [ ] Código pusheado a GitHub
- [ ] Proyecto importado en Vercel
- [ ] Root directory configurado a `frontend`
- [ ] Deployment exitoso
- [ ] URL de Vercel funciona
- [ ] Agregada URL de Vercel a CORS del backend
- [ ] Backend re-deployado en Render
- [ ] Test de análisis end-to-end funciona
- [ ] Analytics activado
- [ ] Custom domain configurado (opcional)

---

## 🎉 ¡Listo!

Tu stack completo en producción:

```
Frontend (Vercel)
    ↓ HTTPS
Backend (Render)
    ↓ API Calls
LLM Providers (Mistral, Gemini, DeepSeek)
```

**Costo total:** $0/mes (con free tiers)

---

**¿Preguntas? Revisa los logs en Vercel Dashboard → Deployments → View Function Logs**
