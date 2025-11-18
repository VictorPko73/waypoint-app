#!/usr/bin/env bash
# exit on error
set -o errexit

npm install
npm run build

# Actualizar pip antes de instalar pipenv
pip install --upgrade pip

# Instalar o actualizar pipenv
pip install --upgrade pipenv

# Instalar dependencias desde Pipfile
pipenv install --deploy

# Ejecutar migraciones
pipenv run upgrade
