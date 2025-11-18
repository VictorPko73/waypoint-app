#!/usr/bin/env bash
# exit on error
set -o errexit

echo "🚀 Iniciando build en Render..."

# Frontend build
echo "📦 Instalando dependencias de Node.js..."
npm install

echo "🔨 Construyendo frontend..."
npm run build

# Backend setup
echo "🐍 Configurando Python..."
pip install --upgrade pip
pip install --upgrade pipenv

echo "📦 Instalando dependencias de Python..."
pipenv install --deploy

# Database migrations
echo "🗄️  Ejecutando migraciones de base de datos..."
pipenv run upgrade

# Initialize production data (idempotent - safe to run multiple times)
echo "🌱 Inicializando datos por defecto en producción..."
pipenv run python init_production_data.py || echo "⚠️  Advertencia: No se pudieron inicializar datos por defecto (puede ser normal si ya existen)"

echo "✅ Build completado exitosamente!"
