# AI Film Studio Control Plane Backend

Central SaaS backend responsibilities:

- Authentication and authorization
- Client and film registry
- Environment registry
- Deployment orchestration
- Subdomain/environment mapping
- Platform audit events
- Billing metadata

The control plane must not become shared film memory. Film scripts, assets, embeddings, prompts, LoRAs, generated media, and film-specific databases remain inside the isolated film environment.
