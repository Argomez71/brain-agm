## Breve descripción
[1-2 líneas de resumen ejecutivo - qué se hizo/decidió/resolvió]

## El qué
[Descripción específica y concreta de lo que se hizo, decidió o resolvió]

**Detalles técnicos**:
- Archivos modificados: [ruta:líneas]
- Comandos ejecutados: [si aplica]
- Configuración cambiada: [si aplica]
- Código clave: [si aplica]

## El por qué

**Contexto**: [Situación que llevó a esto - el problema o necesidad]

**Decisiones clave**:
1. [Decisión 1 con su razón]
2. [Decisión 2 con su razón]
3. [Decisión 3 con su razón]

**Alternativas consideradas**:
- [Alternativa 1]: [Por qué se descartó]
- [Alternativa 2]: [Por qué se descartó]

**Trade-offs**:
- [Pro 1 vs Contra 1]
- [Pro 2 vs Contra 2]

## Referencias (opcional)
- PR: #[número]
- Issue: #[número]
- Documentación: [ruta o URL]
- Memorias relacionadas: [títulos de otras memorias]
- Conversación: [enlace o referencia]

---

**Ejemplo de uso**:

```markdown
## Breve descripción
Implementación de autenticación OAuth 2.0 con Google y Microsoft como proveedores

## El qué
Se implementó flujo completo de OAuth 2.0:

**Detalles técnicos**:
- Archivos: src/auth/oauth.py:45-120, src/config/providers.py:12-30
- Endpoints: /auth/login, /auth/callback, /auth/logout
- Providers: Google OAuth 2.0, Microsoft Azure AD
- Storage: Redis con TTL de 7 días para tokens

## El por qué

**Contexto**: El cliente requiere Single Sign-On corporativo para cumplir con su política de seguridad. El sistema anterior usaba credenciales locales que no cumplen con los nuevos requisitos.

**Decisiones clave**:
1. authlib sobre python-oauth2 - mejor soporte para PKCE y mantenimiento más activo
2. Redis para tokens - TTL automático sin lógica manual, volumen bajo (<10k usuarios)
3. No implementar refresh tokens en esta fase - cliente prefiere re-autenticación cada 7 días

**Alternativas consideradas**:
- Base de datos principal para tokens: Descartada porque requiere lógica de expiración manual
- Auth0 como servicio: Descartada por costo ($200/mes) vs complejidad baja

**Trade-offs**:
- Más complejo que auth local pero es requerimiento del cliente
- Dependencia de servicios externos (Google/MS) mitigada con retry logic y fallbacks
- Redis como dependencia adicional pero ya lo usamos para cache

## Referencias
- PR: #234
- Documentación OAuth: docs/auth/oauth-flow.md
- Decisión de no usar refresh tokens: [memoria: decision-no-refresh-tokens]
```
