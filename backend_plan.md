## Refactoring Plan

1. Keep main.py with:
   - App initialization
   - Middleware setup
   - Global exception handler
   - Router registration

2. Create these API files:
   - api/tenants.py - Tenant operations
   - api/query.py - Prompt processing
   - api/rules.py - Rule management
   - api/logs.py - Log viewing
   - api/prompts.py - Prompt viewing
   - api/admin.py - Admin operations
   - api/routers.py - Combine all routers

The refactoring is substantial. Should I proceed with creating all these files?
