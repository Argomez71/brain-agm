## Brief description
[1-2 lines executive summary - what was done/decided/solved]

## What
[Specific concrete description of what was done, decided or solved]

**Technical details**:
- Modified files: [path:lines]
- Executed commands: [if applicable]
- Changed configuration: [if applicable]
- Key code: [if applicable]

## Why

**Context**: [Situation that led to this - the problem or need]

**Key decisions**:
1. [Decision 1 with its reason]
2. [Decision 2 with its reason]
3. [Decision 3 with its reason]

**Alternatives considered**:
- [Alternative 1]: [Why it was discarded]
- [Alternative 2]: [Why it was discarded]

**Trade-offs**:
- [Pro 1 vs Con 1]
- [Pro 2 vs Con 2]

## References (optional)
- PR: #[number]
- Issue: #[number]
- Documentation: [path or URL]
- Related memories: [titles of other memories]
- Conversation: [link or reference]

---

**Usage example**:

```markdown
## Brief description
OAuth 2.0 authentication implementation with Google and Microsoft as providers

## What
Implemented complete OAuth 2.0 flow:

**Technical details**:
- Files: src/auth/oauth.py:45-120, src/config/providers.py:12-30
- Endpoints: /auth/login, /auth/callback, /auth/logout
- Providers: Google OAuth 2.0, Microsoft Azure AD
- Storage: Redis with 7-day TTL for tokens

## Why

**Context**: Client requires corporate Single Sign-On to comply with their security policy. Previous system used local credentials that don't meet new requirements.

**Key decisions**:
1. authlib over python-oauth2 - better PKCE support and more active maintenance
2. Redis for tokens - automatic TTL without manual logic, low volume (<10k users)
3. Don't implement refresh tokens this phase - client prefers re-authentication every 7 days

**Alternatives considered**:
- Main database for tokens: Discarded because it requires manual expiration logic
- Auth0 as service: Discarded due to cost ($200/month) vs low complexity

**Trade-offs**:
- More complex than local auth but it's a client requirement
- External service dependency (Google/MS) mitigated with retry logic and fallbacks
- Redis as additional dependency but we already use it for cache

## References
- PR: #234
- OAuth documentation: docs/auth/oauth-flow.md
- Decision to not use refresh tokens: [memory: decision-no-refresh-tokens]
```
