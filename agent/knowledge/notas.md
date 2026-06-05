# Notas de desarrollo

## Setup rápido
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install chromium
python server.py --port 9090
```

## Comandos útiles
```powershell
# Tests
pytest tests/ -v

# Coverage
pytest tests/ --cov=. --cov-report=term-missing

# Lint
ruff check .

# Formatear
ruff format .
```

## Debugging
- Usar `--no-headless` para ver el navegador
- Revisar `/health` para diagnóstico
- Logs en consola muestran cada request con emojis
- `conversations.json` guarda chats, `usage.json` guarda métricas

## Errores comunes
1. **"No se detectó sesión"** → Ejecutar con `--no-headless` y hacer login manual
2. **Timeout** → ChatGPT puede estar lento, aumentar timeout en config.yaml
3. **Selector no encontrado** → ChatGPT cambió la UI, actualizar css_selectors.py
4. **ImportError** → Activar el venv: `.venv\Scripts\Activate.ps1`
