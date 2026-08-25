# AI Film Studio — Finalized Architecture

**Status:** Architecture baseline
**Cloud:** AWS-first
**Deployment model:** One film = one isolated production environment
**SaaS model:** One central SaaS control plane + isolated film data planes

---

## 1. Architecture Decision

AI Film Studio is a single SaaS product that provisions and manages independent production environments for individual films and clients.

The platform is **not** a conventional shared multi-tenant film-production runtime.

The core rule is:

> **One film + one client = one isolated AWS account/environment + one film subdomain.**

The central SaaS manages environments, users, billing, deployment, configuration, and operations. Actual film content and film-generation workloads remain inside the film's isolated environment.

---

## 2. High-Level Architecture

```text
                                  AI FILM STUDIO SaaS
                              =========================
                                      CONTROL PLANE

                    +---------------------------------------------+
                    | Web Frontend                                |
                    | Next.js / React / TypeScript                |
                    +----------------------+----------------------+
                                           |
                    +----------------------v----------------------+
                    | SaaS Backend / Control API                  |
                    | FastAPI / Python                            |
                    | Auth | Clients | Films | Billing | Admin   |
                    +----------------------+----------------------+
                                           |
                    +----------------------v----------------------+
                    | Control Database                             |
                    | PostgreSQL                                   |
                    | Users | Clients | Films | Environments     |
                    | Deployments | Billing | Platform Audit     |
                    +----------------------+----------------------+
                                           |
                    +----------------------v----------------------+
                    | Deployment Orchestrator                      |
                    | Terraform + AWS Organizations/IAM          |
                    +-----------+----------------+----------------+
                                |                |
               +----------------+                +----------------+
               |                                                  |
               v                                                  v
        +---------------+                                  +---------------+
        | AWS Account A |                                  | AWS Account B |
        | FILM A        |                                  | FILM B        |
        +-------+-------+                                  +-------+-------+
                |                                                  |
        +-------v--------------------------------+         +-------v--------------------------------+
        | Dedicated Film Environment             |         | Dedicated Film Environment             |
        |                                        |         |                                        |
        | Frontend | Backend | Film DB          |         | Frontend | Backend | Film DB          |
        | S3 | RAG/Vector | SQS | EventBridge   |         | S3 | RAG/Vector | SQS | EventBridge   |
        | GPU Workers | Models | Secrets | KMS   |         | GPU Workers | Models | Secrets | KMS   |
        | CloudWatch | CloudTrail | ECR          |         | CloudWatch | CloudTrail | ECR          |
        +------------------+---------------------+         +------------------+---------------------+
                           |                                                   |
                           v                                                   v
                 film-a.studio.example.com                         film-b.studio.example.com

                    FILM A DATA  XXXXXXXXXXXXXXXXXX  FILM B DATA
                              NO CROSS-FILM DATA PATH
```

---

## 3. Control Plane vs Data Plane

### Control Plane — shared SaaS

The central SaaS owns only platform/control information:

- User authentication and authorization
- Client accounts
- Film registry
- Environment registry
- AWS account/environment mapping
- Subdomain mapping
- Deployment state
- Infrastructure configuration
- Subscription and billing metadata
- Platform-level audit records
- Model catalog and approved model metadata
- Deployment orchestration
- Operational health/status

The control plane must **not** become a shared repository for confidential film content.

### Film Data Plane — isolated per film

Every film environment owns:

- Script and screenplay
- Character bible
- Location/world bible
- Scene and shot metadata
- Character reference assets
- Film-specific prompts/context
- Film-specific embeddings/RAG indexes
- Film-specific LoRAs/fine-tuned models
- Generated images
- Generated video
- Dialogue and voice assets
- Music and SFX
- Production files
- QA artifacts
- Final masters

---

## 4. Isolation Boundary

The target isolation model is:

```text
Film A / Client 1
    |
    +-- AWS Account A
        +-- Dedicated VPC
        +-- Dedicated IAM roles
        +-- Dedicated KMS keys
        +-- Dedicated S3 buckets
        +-- Dedicated Film PostgreSQL
        +-- Dedicated RAG/vector store
        +-- Dedicated queues/events
        +-- Dedicated GPU workers
        +-- Dedicated model/LoRA storage
        +-- Dedicated secrets
        +-- Dedicated application deployment
        +-- Dedicated monitoring

Film B / Client 2
    |
    +-- AWS Account B
        +-- Completely separate equivalent resources

Film A  -------------------- X -------------------- Film B
                         NO NORMAL DATA ACCESS
```

Security rules:

1. Film environments must not share film databases.
2. Film environments must not share film S3 buckets or prefixes as a data boundary.
3. Film environments must not share film vector/RAG indexes.
4. Film-specific LoRAs and fine-tuned models stay inside the film account.
5. GPU workers should use ephemeral storage and secure cleanup where practical.
6. IAM follows least privilege.
7. Secrets and encryption keys are isolated per environment.
8. Cross-account access is disabled by default and explicitly allow-listed only for required control-plane operations.
9. The central SaaS stores environment metadata, not film content.
10. Production logs must avoid recording confidential prompts, scripts, or generated assets unless explicitly required by the client policy.

---

## 5. Film Creation Lifecycle

A customer interacts with one SaaS application.

```text
User
  |
  v
studio.example.com
  |
  | Create Film
  v
SaaS Control API
  |
  +--> Create Film record
  +--> Create Environment record
  +--> Allocate deployment ID
  +--> Provision/attach AWS account
  +--> Configure IAM and security guardrails
  +--> Terraform infrastructure
  +--> Deploy application
  +--> Configure DNS/subdomain
  +--> Run health checks
  |
  v
Film Environment Ready
  |
  v
film-a.studio.example.com
```

A deployment is therefore **created once per film**, not once per generation job.

Generating scenes, shots, voices, or masters happens inside the existing film environment through its job system and GPU workers.

---

## 6. Customer Experience

### Central SaaS

```text
https://studio.example.com
```

Used for:

- Sign in
- Create/manage clients
- Create films
- Provision environments
- View deployment status
- Manage subscriptions/billing
- Manage platform permissions
- Access approved model catalog

### Film workspace

```text
https://film-a.studio.example.com
```

Used for:

- Script upload and analysis
- Character development
- Location/world design
- Storyboards
- Shot planning
- Video generation
- Voice/dialogue generation
- Music/SFX
- Localization
- Lip sync
- QA
- Editing/export
- 4K/8K mastering
- Production monitoring

---

## 7. AI Film Pipeline

```text
SCRIPT
  |
  v
Script Analysis
  |
  v
Film Bible
  +-- Character Bible
  +-- World/Location Bible
  +-- Cinematography Bible
  |
  v
Scene Breakdown
  |
  v
Shot List
  |
  v
Character/Location References
  |
  v
Image / Keyframe Generation
  |
  v
Video Generation
  |
  v
Video QA / Continuity Checks
  |
  +-------------------+
  |                   |
  v                   v
Voice / Dialogue     Music / SFX
  |                   |
  +---------+---------+
            v
        Lip Sync
            |
            v
       Editing / FFmpeg
            |
            v
      Color / Enhancement
            |
       +----+----+
       |         |
       v         v
      4K        8K
       |
       +-----> Final Masters
```

---

## 8. Multilingual Production

The studio should support a single visual master with multiple language/audio masters.

Current target language set:

### Indian languages

- Kannada
- Hindi
- Telugu
- Tamil
- Malayalam
- Marathi
- Bengali

### International languages

- English (US)
- English (UK)
- Chinese
- Japanese
- French

Localization pipeline:

```text
Visual Master
    |
    +--> Kannada
    +--> Hindi
    +--> Telugu
    +--> Tamil
    +--> Malayalam
    +--> Marathi
    +--> Bengali
    +--> English US
    +--> English UK
    +--> Chinese
    +--> Japanese
    +--> French
             |
             v
       Voice / Dubbing
             |
             v
          Lip Sync
             |
             v
        Audio Mixing
             |
             v
      Language-specific Masters
```

Language-specific assets remain inside the film environment.

---

## 9. Resolution Strategy

The platform should support:

- 1080p
- 2K cinema
- 4K
- 4K HDR
- 8K premium master
- Future spatial/volumetric output

Do not assume every generative model must natively generate 4K/8K frames.

Preferred approach:

```text
Model-optimal generation
        |
        v
Temporal/visual QA
        |
        v
High-quality enhancement
        |
        +--> 4K Master
        |
        +--> 8K Premium Master
```

8K should be treated as a finishing/mastering pipeline where appropriate.

---

## 10. Future 4D / Spatial Capability

"4D" is not the same as 4K/8K.

The architecture should leave room for:

- 3D scene reconstruction
- NeRF-style representations
- 3D Gaussian Splatting
- Depth estimation
- Multi-view generation
- Spatial/volumetric video
- Virtual-camera rendering
- 4D theatre/effects timelines

Potential future pipeline:

```text
AI Scene
   |
   v
3D / Volumetric Representation
   |
   v
Time-aware Scene
   |
   v
Virtual Camera
   |
   v
Spatial / Volumetric Output
```

This is a future production mode and should not complicate the initial 2D feature-film pipeline.

---

## 11. Recommended AWS Services

| Capability | AWS service / technology |
|---|---|
| Cloud organization | AWS Organizations |
| Compute | EC2 |
| GPU inference | GPU-enabled EC2 |
| Container registry | ECR |
| Containers | ECS or EKS |
| Object storage | S3 |
| Film database | RDS PostgreSQL |
| Queues | SQS |
| Event routing | EventBridge |
| Secrets | Secrets Manager |
| Encryption | KMS |
| DNS | Route 53 |
| Load balancing | Application Load Balancer |
| Monitoring | CloudWatch |
| Audit | CloudTrail |
| Identity | IAM |
| Infrastructure as code | Terraform |
| CI/CD | GitHub Actions |

GPU worker orchestration should remain decoupled from the web request lifecycle. Long-running video/model jobs must run asynchronously.

---

## 12. Application Stack

### Central SaaS

- Next.js / React / TypeScript
- FastAPI / Python
- PostgreSQL
- Redis where useful for caching/session/short-lived coordination
- Terraform deployment orchestration
- AWS SDK/Boto3
- GitHub Actions

### Film environment

- Same core frontend/backend codebase
- Film-scoped configuration
- Film PostgreSQL
- S3
- SQS/EventBridge
- GPU workers
- PyTorch
- Hugging Face Diffusers/Transformers where compatible
- ComfyUI where useful for visual workflows
- FFmpeg for media processing
- Model-specific inference runtimes

The platform should avoid coupling all generation to a single vendor API.

---

## 13. AI Agent / Orchestration Layer

The orchestration layer should coordinate specialized production tasks:

```text
AI Director / Orchestrator
        |
        +-- Script Agent
        +-- Scene Agent
        +-- Character Agent
        +-- Location Agent
        +-- Shot Agent
        +-- Image Agent
        +-- Video Agent
        +-- Voice Agent
        +-- Music/SFX Agent
        +-- Localization Agent
        +-- QA Agent
        +-- Mastering Agent
```

LangGraph can be used for stateful workflows where it adds value. The job system remains responsible for durable asynchronous execution of long-running GPU workloads.

---

## 14. Job Architecture

Never make the browser wait for video generation.

```text
Frontend
   |
   v
Film API
   |
   v
Job Queue
   |
   +--> Image Worker
   +--> Video Worker
   +--> Audio Worker
   +--> Localization Worker
   +--> QA Worker
   +--> Mastering Worker
   |
   v
Film Storage
```

Each job must include a non-guessable film/environment identifier and must be authorized against the current film environment before execution.

Recommended job states:

```text
QUEUED
RUNNING
RETRYING
SUCCEEDED
FAILED
CANCELLED
```

---

## 15. Data Model Boundaries

### Central SaaS database

```text
users
clients
films
film_environments
deployments
subscriptions
billing_accounts
subdomains
platform_audit_events
approved_models
```

### Film database

```text
film_metadata
characters
locations
scenes
shots
storyboards
prompts
production_jobs
dialogue
language_tracks
qa_results
asset_metadata
```

The actual large assets are stored in the film's S3 environment.

---

## 16. Storage Layout

Example Film A S3 layout:

```text
s3://film-a-assets/
├── source/
│   ├── scripts/
│   └── references/
├── preproduction/
│   ├── characters/
│   ├── locations/
│   └── storyboards/
├── generation/
│   ├── images/
│   ├── video/
│   └── audio/
├── localization/
│   ├── kn/
│   ├── hi/
│   ├── te/
│   ├── ta/
│   ├── ml/
│   ├── mr/
│   ├── bn/
│   ├── en-us/
│   ├── en-gb/
│   ├── zh/
│   ├── ja/
│   └── fr/
├── qa/
└── masters/
```

The equivalent bucket for Film B is a separate AWS resource in Account B.

---

## 17. Model Registry and Licensing

The studio must track model licensing before a model is approved for commercial production.

Registry fields should include:

```text
model_id
model_name
version
provider/source
license
commercial_use_allowed
redistribution_allowed
fine_tuning_allowed
attribution_required
usage_restrictions
approved_for_production
```

Preferred licenses include permissive licenses such as Apache-2.0 and MIT where technically suitable, but the platform must not reject a high-quality model solely because it uses another license. Each model must be reviewed against its actual license terms.

Base models may be distributed through approved mechanisms, while film-specific LoRAs/fine-tunes remain private to the film environment.

---

## 18. Security Architecture

Minimum controls:

- Separate AWS account per film where the isolation tier requires it
- Dedicated VPC per film
- Private subnets for databases and GPU infrastructure where practical
- Least-privilege IAM
- KMS encryption
- S3 Block Public Access
- Secrets Manager
- CloudTrail
- CloudWatch security/operational monitoring
- Network egress controls where appropriate
- No hard-coded credentials
- No film secrets in Git
- No film content in application logs by default
- Separate Terraform state per environment
- Immutable/versioned deployment artifacts
- Explicit cross-account trust only when required
- Secure deletion/cleanup of temporary GPU storage

---

## 19. Terraform State Isolation

Terraform state is security-sensitive.

Do not use one state file for every film.

```text
Film A -> isolated Terraform state
Film B -> isolated Terraform state
Film C -> isolated Terraform state
```

The deployment control plane should know which state/environment belongs to which film, while access to state remains tightly controlled.

---

## 20. CI/CD

The desired deployment flow is:

```text
GitHub
   |
   v
CI
   |
   +--> Unit tests
   +--> Security scanning
   +--> Build containers
   +--> Build/version artifacts
   |
   v
Artifact Registry / ECR
   |
   v
Deployment Controller
   |
   v
Film Environment
```

A platform release should not automatically mix application data between film environments.

Application code may be shared; runtime data is environment-specific.

---

## 21. Environment Lifecycle

Each film environment has an independent lifecycle:

```text
REQUESTED
   |
   v
PROVISIONING
   |
   v
READY
   |
   v
PRODUCTION
   |
   v
COMPLETED
   |
   +--> ARCHIVED
   |
   +--> DESTROYED (according to retention policy)
```

GPU capacity can be scaled up for active production and reduced when idle. The film environment itself remains logically isolated regardless of compute scaling.

---

## 22. Client-Owned Cloud Option

For enterprise clients, support deployment into a client-controlled AWS organization/account.

```text
Client AWS Organization
        |
        +-- Film Account
              |
              +-- AI Film Studio deployment
```

The client can retain control of:

- Billing
- IAM
- KMS
- Data retention
- Network controls
- Security policies

The studio receives only the minimum operational permissions required.

---

## 23. What Is Shared vs Private

| Component | Shared? | Notes |
|---|---:|---|
| SaaS source code | Yes | Same product codebase |
| Terraform modules | Yes | Reusable infrastructure modules |
| CI/CD templates | Yes | Deployment automation |
| Approved model catalog | Yes | Metadata only |
| Base model artifacts | Potentially | Must comply with license and deployment policy |
| Client account metadata | Control plane | Not film content |
| Film script | No | Film account only |
| Film database | No | Dedicated per film |
| Film S3 assets | No | Dedicated per film |
| Film embeddings/RAG | No | Dedicated per film |
| Film LoRA/fine-tunes | No | Dedicated per film |
| Film prompts/context | No | Dedicated per film |
| Generated media | No | Dedicated per film |
| Film secrets/keys | No | Dedicated per film |
| Film GPU workspace | No | Dedicated/ephemeral per film |

---

## 24. Key Architecture Principles

1. **One SaaS product.**
2. **One central control plane.**
3. **One isolated production environment per film.**
4. **One AWS account per film for the strongest isolation tier.**
5. **One subdomain per film.**
6. **No shared film database.**
7. **No shared film storage.**
8. **No shared film RAG/vector memory.**
9. **No sharing of film-specific LoRAs/fine-tunes.**
10. **Asynchronous GPU job execution.**
11. **Terraform provisions environments automatically.**
12. **Central SaaS stores control metadata, not confidential film content.**
13. **Base models and film-specific models have different security boundaries.**
14. **4K is the standard premium production target; 8K is a finishing/mastering target.**
15. **Spatial/4D is a future capability, not a dependency of the first release.**
16. **AWS is the primary cloud architecture for this isolation model.**
17. **Client-owned AWS deployment is supported for enterprise security requirements.**

---

## 25. Final Architecture Statement

> **AI Film Studio is a single SaaS control platform that provisions, operates, and monitors fully isolated AWS production environments for individual films. Each film/client receives its own environment, AWS account, application deployment, database, storage, RAG/vector memory, secrets, encryption keys, GPU workers, film-specific models, and subdomain. The central SaaS manages the lifecycle but does not provide shared film memory. Film A and Film B therefore remain cryptographically, logically, and operationally separated while being managed through one unified studio product.**
