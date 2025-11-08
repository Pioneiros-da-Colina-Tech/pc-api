## 0.2.0 (2025-11-08)

### BREAKING CHANGE

- now its possible to run on windows
- database is now ready for use
- granian running on production, high perf boost with rust and workers
- initial template

### Feat

- auth
- added basic auth flow
- added uvloop
- added basic database session management
- **granian**: substituted uvicorn for granian in production
- **meetings**: added basic route schema
- first commit

### Fix

- removed escudeiro package
- removed model append
- removed unused modules

### Refactor

- new structure
- improved code readability and testability by using ddd arch as intended
- **schemas.py**: removed <3.13 deprecated modules
- changed app contact url
- new metadata
- added docstrings
