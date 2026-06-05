# Errores comunes y soluciones

## Browser / Playwright

### Error: "Browser closed unexpectedly"
**Causa**: Playwright no encuentra Chromium o se cerró inesperadamente.
**Solución**: `playwright install chromium`

### Error: "Target closed"
**Causa**: La página de ChatGPT se cerró o el navegador crasheó.
**Solución**: El watchdog debería reiniciar automáticamente. Si no, reiniciar el servidor.

## ChatGPT Web

### Error: "Unusual activity detected"
**Causa**: ChatGPT detectó comportamiento sospechoso (muchas requests en poco tiempo).
**Solución**: Reducir RPM en config.yaml, activar antiban, aumentar delays.

### Error: "Login required"
**Causa**: La sesión expiró.
**Solución**: Ejecutar `python server.py` (sin --no-headless) y hacer login manual.

## API

### Error: "QUEUE_FULL"
**Causa**: Demasiadas requests en cola.
**Solución**: Aumentar `max_queue` en config.yaml o esperar.

### Error: "RATE_LIMITED"
**Causa**: Se alcanzó el límite de RPM.
**Solución**: Aumentar `rpm` en config.yaml o esperar.
