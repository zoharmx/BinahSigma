"""
Script para generar y mostrar API keys de demo.
Ejecutar: python generate_api_keys.py
"""

import os
from dotenv import load_dotenv

# IMPORTANTE: Cargar variables de entorno primero
load_dotenv()

from auth import create_api_key, Tier

# Verificar que tenemos el secret key correcto
print(f"Using JWT_SECRET_KEY: {os.getenv('JWT_SECRET_KEY')[:20]}...")
print()

# Generar API keys
demo_key = create_api_key("demo_user", Tier.DEMO, "demo@example.com")
startup_key = create_api_key("startup_user", Tier.STARTUP, "startup@example.com")
professional_key = create_api_key("professional_user", Tier.PROFESSIONAL, "professional@example.com")
enterprise_key = create_api_key("enterprise_user", Tier.ENTERPRISE, "enterprise@example.com")

# Mostrar resultados
print("\n" + "="*70)
print("BINAH-SIGMA v2.0 - DEMO API KEYS")
print("="*70)
print("\nUsa estas API keys en el header 'Authorization: Bearer <key>'")
print("\n")

print(f"Demo Tier (10 requests/month):")
print(f"  {demo_key}")
print()

print(f"Startup Tier (100 requests/month):")
print(f"  {startup_key}")
print()

print(f"Professional Tier (1,000 requests/month):")
print(f"  {professional_key}")
print()

print(f"Enterprise Tier (Unlimited):")
print(f"  {enterprise_key}")
print()

print("="*70)
print("\nEjemplo de uso:")
print(f'curl -X POST http://localhost:8000/v2/analyze \\')
print(f'  -H "Content-Type: application/json" \\')
print(f'  -H "Authorization: Bearer {startup_key}" \\')
print(f'  -d \'{{...}}\'')
print("="*70 + "\n")

# Guardar en archivo para referencia
with open("API_KEYS.txt", "w") as f:
    f.write("BINAH-SIGMA v2.0 - DEMO API KEYS\n")
    f.write("="*70 + "\n\n")
    f.write(f"Demo Tier: {demo_key}\n")
    f.write(f"Startup Tier: {startup_key}\n")
    f.write(f"Professional Tier: {professional_key}\n")
    f.write(f"Enterprise Tier: {enterprise_key}\n")

print("API keys también guardadas en: API_KEYS.txt\n")
