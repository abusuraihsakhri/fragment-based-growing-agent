## Fragment Based Growing Agent v2.0.1

- Added descriptor-based Congreve Rule-of-Three screening to both Python CLIs and the static browser app.
- Fixed CSV boolean interpretation and numeric input validation.
- Verified HMAC signatures across the audit trail; replaced the embedded key with an operator-supplied or process-local key.
- Restricted audit-log access with an optional bearer token and bound Docker Compose to localhost.
- Removed fabricated browser results, corrected misleading scientific claims, and added JSON export.
- Expanded Python, API, and browser regression tests and introduced dependency scanning.

**Scope:** Structural fragment growing, docking, molecular descriptor generation, model inference, and biomedical validation are not implemented. The browser app processes user inputs locally. For public hosting, repository GitHub Pages settings must permit GitHub Actions publication.
