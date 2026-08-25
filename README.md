# AI-Film-Studio

To build an **AI-powered virtual studio** capable of taking a script like *The Centerline* and producing a complete 2 to 3-hour feature film, you need an **AI Orchestration Tech Stack**. Because no single AI tool can generate 2 hours of continuous, consistent feature film in one click, filmmakers break the process down into specialized pipelines.

For the **Cloud GPU + open-source** approach, I would build the AI Film Studio as a **production platform**, not just a collection of AI models.

Below is the full stack I would recommend for your **3-hour feature-film target**.

# AI Film Studio — Full Technology Stack

```text
┌───────────────────────────────────────────────────────────────────┐
│                         AI FILM STUDIO                            │
│                         Web Application                          │
│                    React / Next.js + FastAPI                      │
└───────────────────────────────┬───────────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────────┐
│                    AI DIRECTOR / ORCHESTRATOR                     │
│                           LangGraph                               │
│                                                                   │
│ Script Agent │ Scene Agent │ Character Agent │ Shot Agent         │
│ Video Agent  │ Voice Agent │ Music Agent     │ QA Agent           │
└───────────────────────────────┬───────────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────────┐
│                         JOB SYSTEM                                │
│                  Redis + Celery / Temporal                        │
└───────────────────────────────┬───────────────────────────────────┘
                                │
                  ┌─────────────┼─────────────┐
                  ▼             ▼             ▼
          IMAGE WORKERS   VIDEO WORKERS   AUDIO WORKERS
                  │             │             │
                  └─────────────┼─────────────┘
                                ▼
┌───────────────────────────────────────────────────────────────────┐
│                         CLOUD GPU                                 │
│                    RunPod / Vast.ai                               │
│                                                                   │
│ PyTorch │ ComfyUI │ HuggingFace Diffusers │ CUDA                  │
└───────────────────────────────┬───────────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────────┐
│                         AI MODELS                                 │
│                                                                   │
│ Image │ Video │ Character │ LoRA │ TTS │ Music │ SFX │ Upscaling  │
└───────────────────────────────┬───────────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────────┐
│                       ASSET STORAGE                               │
│                              S3                                   │
│                                                                   │
│ Scripts / Characters / Locations / Shots / Video / Audio / Final │
└───────────────────────────────┬───────────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────────┐
│                    CONTINUITY + QUALITY                           │
│             AI evaluation + metadata + embeddings                 │
└───────────────────────────────┬───────────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────────┐
│                       POST PRODUCTION                              │
│                    FFmpeg + DaVinci Resolve                        │
└───────────────────────────────────────────────────────────────────┘
```

---

# 1. Frontend

### Recommended

**Next.js + React + TypeScript**

This becomes the actual Film Studio UI.

```text
Film Studio
│
├── Projects
├── Script
├── Characters
├── Locations
├── Props
├── Storyboard
├── Scenes
├── Shots
├── Generation Queue
├── Review
├── Timeline
└── Export
```

For an initial prototype, you could use **Streamlit**, but for a serious production platform I'd move to React/Next.js.

---

# 2. Backend

### FastAPI + Python

This fits your existing skill set very well.

```text
React
  ↓
FastAPI
  ↓
Services
  ├── Project Service
  ├── Script Service
  ├── Character Service
  ├── Scene Service
  ├── Shot Service
  ├── Generation Service
  ├── QA Service
  └── Rendering Service
```

---

# 3. AI Orchestration

### LangGraph

This should be your **AI Director**, rather than using LangGraph to perform the actual video generation.

Example:

```text
                    FILM DIRECTOR
                         │
                         ▼
                   Scene Manager
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
         Character    Location     Props
           Agent        Agent       Agent
              │          │          │
              └──────────┼──────────┘
                         ▼
                     Shot Agent
                         │
                         ▼
                   Video Worker
                         │
                         ▼
                     QA Agent
                         │
                 ┌───────┴───────┐
                 ▼               ▼
               FAIL             PASS
                 │               │
                 ▼               ▼
             Regenerate       Approve
```

---

# 4. LLM

You don't need the LLM to generate the actual video.

Use the LLM for:

* screenplay expansion
* scene decomposition
* character analysis
* shot planning
* camera instructions
* dialogue
* prompt generation
* continuity reasoning
* QA analysis

### Model strategy

Have an abstraction:

```text
LLMProvider
   ├── Qwen
   ├── Llama
   ├── Mistral
   └── Commercial fallback
```

For your open-source philosophy, I'd start with a strong Hugging Face model rather than locking the platform to one provider.

---

# 5. Database

### PostgreSQL

This is your **production metadata database**.

Don't put everything into S3.

PostgreSQL stores:

```text
films
projects
characters
character_versions
locations
props
scenes
shots
shot_versions
generation_jobs
generation_attempts
audio_tracks
music_tracks
assets
prompts
models
model_versions
qa_results
continuity_results
```

Example:

```text
shot
──────────────────────
shot_id
scene_id
shot_number
duration
camera
lens
location_id
time_of_day
character_ids
prompt
status
approved_version
```

---

# 6. Object Storage

### AWS S3

This stores the actual heavy assets.

```text
s3://ai-film-studio/

films/
  centerline/

    script/
    characters/
    locations/
    props/

    storyboards/

    scenes/
      scene_001/
      scene_002/

    shots/
      shot_001/
      shot_002/
      shot_003/

    audio/
      dialogue/
      music/
      sfx/

    approved/

    final/
```

PostgreSQL tells you **what the asset is**.

S3 stores **the asset itself**.

---

# 7. GPU Cloud

### Primary choice: RunPod

RunPod currently offers a wide range of GPUs and bills GPU instances by time; its current listed options include RTX 4090, RTX 5090, A40/A6000, L40S, A100, H100 and newer accelerators. ([Runpod][1])

For example, current listed Secure Cloud pricing is roughly:

| GPU      |  VRAM | Approx. $/hr |
| -------- | ----: | -----------: |
| RTX 4090 | 24 GB |        $0.74 |
| RTX 5090 | 32 GB |        $0.99 |
| A40      | 48 GB |        $0.44 |
| L40S     | 48 GB |        $0.99 |
| A100     | 80 GB |        $1.59 |
| H100     | 80 GB |        $3.29 |

These are current listed rates and can vary by cloud/availability. ([Runpod][2])

For the initial system, I'd investigate **RTX 5090 / 4090 / A40 / L40S** before jumping to H100.

---

# 8. Containerization

### Docker

Every GPU worker should run as a container.

```text
film-video-worker
├── CUDA
├── PyTorch
├── ComfyUI
├── Diffusers
├── Video models
├── FFmpeg
└── API worker
```

This makes the GPU environment reproducible.

---

# 9. GPU AI Runtime

### PyTorch

Core ML framework.

```text
Python
 ↓
PyTorch
 ↓
CUDA
 ↓
NVIDIA GPU
```

### Hugging Face Diffusers

Use Diffusers when you want programmatic control over image/video diffusion pipelines. It supports interchangeable components, LoRA adapters, quantization, offloading and other inference optimizations. ([Hugging Face][3])

---

# 10. ComfyUI

### ComfyUI = visual generation engine

I would absolutely include it.

ComfyUI provides a node-based generation engine and API and supports image, video, 3D and audio workflows. ([GitHub][4])

Your architecture:

```text
LangGraph
     ↓
Generation Job
     ↓
ComfyUI API
     ↓
Workflow
     ↓
GPU
     ↓
Output
```

Example workflows:

```text
workflows/

character_generation.json
character_consistency.json

location_generation.json

storyboard.json

image_to_video.json
text_to_video.json

action_scene.json
dialogue_scene.json

upscale.json
```

---

# 11. Image Generation

I'd make the image layer pluggable.

```text
ImageProvider
      │
      ├── FLUX
      ├── SDXL ecosystem
      └── Future models
```

Used for:

* character sheets
* locations
* props
* storyboards
* reference images
* keyframes

---

# 12. Character Consistency

This deserves its own subsystem.

```text
Character Engine

Character
   │
   ├── Reference images
   ├── LoRA
   ├── Face identity
   ├── Costume
   ├── Hair
   ├── Age
   ├── Body characteristics
   └── Style
```

### Technologies

* LoRA
* IP-Adapter/reference conditioning where appropriate
* Face/identity embeddings
* image similarity
* CLIP-style embeddings
* OpenCV
* PyTorch

---

# 13. Video Generation

Don't hard-code a single model.

```text
VideoProvider
      │
      ├── Open-source Model A
      ├── Open-source Model B
      ├── Open-source Model C
      └── Commercial fallback
```

The exact model should be selected after benchmarking on your target GPU.

That's important because the video-model ecosystem is changing extremely quickly.

---

# 14. Voice Generation

You have two choices.

### Open-source

```text
TTS
├── XTTS
├── F5-TTS
└── other current open models
```

### Commercial fallback

```text
ElevenLabs
```

For your architecture:

```text
VoiceProvider
    ├── LocalTTS
    └── CommercialTTS
```

Character voice profiles:

```text
Dhruva
 └── voice_profile

Inspector
 └── voice_profile

Judge
 └── voice_profile
```

---

# 15. Music

For an open-source-first system:

```text
Music generation
      │
      ├── Open-source music models
      └── Commercial fallback
```

Store:

```text
theme.wav
scene_001_music.wav
scene_002_music.wav
action_theme.wav
court_theme.wav
```

---

# 16. Sound Effects

Use a similar provider abstraction:

```text
SFXProvider
    ├── Open-source SFX model
    └── Commercial fallback
```

Examples:

```text
JCB engine
footsteps
door
rain
wind
courtroom ambience
vehicle
impact
crowd
```

---

# 17. Video processing

### FFmpeg

This is essential.

Use it for:

* concatenation
* trimming
* transcoding
* audio synchronization
* frame extraction
* format conversion
* intermediate rendering
* final encoding

Architecture:

```text
Generated clips
      ↓
FFmpeg
      ↓
Scene
      ↓
Film timeline
      ↓
Master
```

---

# 18. Upscaling

Add a dedicated upscale worker.

```text
Final approved 1080p
       ↓
Upscaler
       ↓
4K master
```

Don't upscale every failed generation.

Only:

> **approved shots → upscale**

This can save substantial compute.

---

# 19. Continuity Engine

This is one of the most important parts of the entire platform.

For every shot:

```text
Shot 143

Character:
    Dhruva

Location:
    Police Station

Costume:
    Blue shirt

Time:
    7:30 PM

Weather:
    Rain

Camera:
    50mm

Lighting:
    Low-key

Previous shot:
    Shot 142
```

The system compares the generated shot against the production bible.

---

# 20. Vector database

You can use:

### PostgreSQL + pgvector

rather than introducing another database initially.

Store embeddings for:

```text
Character
Location
Prop
Scene
Shot
Dialogue
Script
Reference image
Generated frame
```

Then:

```text
New generated frame
        ↓
Embedding
        ↓
pgvector
        ↓
Compare against
approved character reference
        ↓
Consistency score
```

---

# 21. Queue / Job Management

For the initial version:

### Redis + Celery

```text
FastAPI
   ↓
Redis
   ↓
Celery
   ↓
GPU worker
```

For a larger production platform:

### Temporal

Temporal becomes attractive when workflows become long-running and need durable retries/state.

For your first MVP, **Celery is simpler**.

---

# 22. Monitoring

### Prometheus + Grafana

Monitor:

```text
GPU utilization
VRAM
generation time
queue length
failed jobs
cost
storage
worker health
```

---

# 23. AI Observability

### LangSmith / OpenTelemetry

Track:

```text
Film
 ↓
Scene
 ↓
Shot
 ↓
Prompt
 ↓
Model
 ↓
Generation
 ↓
QA
```

You want to be able to answer:

> "Why was Shot 327 generated incorrectly?"

---

# 24. Authentication

For the first version:

```text
JWT
FastAPI
PostgreSQL
```

Later:

```text
OAuth2 / OIDC
```

---

# 25. Infrastructure

### AWS

I'd use:

```text
AWS
│
├── S3             → assets
├── PostgreSQL     → RDS
├── CloudFront     → video delivery
├── Route53        → DNS
├── Secrets Manager
├── CloudWatch
└── ECS/EKS        → application services
```

But **do not necessarily run your GPU workloads on AWS**.

Use:

```text
AWS
  └── Control plane + storage

RunPod/Vast
  └── GPU plane
```

That's the important cost optimization.

---

# 26. CI/CD

You already know this area, so:

```text
GitHub
   ↓
GitHub Actions
   ↓
Docker
   ↓
Test
   ↓
Build
   ↓
Deploy
```

Use separate environments:

```text
DEV
QA
PROD
```

---

# 27. Infrastructure as Code

### Terraform

```text
terraform/

aws/
  s3/
  rds/
  networking/
  ecs/

gpu/
  runpod/
```

---

# 28. Complete stack

### Application

```text
Frontend
    Next.js
    React
    TypeScript

Backend
    Python
    FastAPI

AI orchestration
    LangGraph

LLM
    Open-source LLM
```

### Data

```text
PostgreSQL
pgvector
Redis
S3
```

### AI

```text
PyTorch
CUDA
Hugging Face
Diffusers
ComfyUI
LoRA
Open-source image models
Open-source video models
Open-source TTS
Open-source music/SFX
```

### GPU

```text
RunPod
Vast.ai

RTX 4090
RTX 5090
A40
L40S
A100/H100 when required
```

### Media

```text
FFmpeg
OpenCV
DaVinci Resolve
```

### Infrastructure

```text
Docker
Terraform
GitHub Actions
AWS
```

### Observability

```text
Prometheus
Grafana
OpenTelemetry
LangSmith
CloudWatch
```

---

# 29. The production architecture I'd actually build

For **your project**, I'd keep the first production version much smaller:

```text
                    ┌──────────────────┐
                    │  Next.js UI      │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  FastAPI         │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  LangGraph       │
                    │  AI Director     │
                    └────────┬─────────┘
                             │
                      Redis / Celery
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        Image Worker    Video Worker    Audio Worker
              │              │              │
              └──────────────┼──────────────┘
                             │
                        Cloud GPU
                             │
                    ┌────────┴────────┐
                    │                 │
                ComfyUI          Diffusers
                    │                 │
                    └────────┬────────┘
                             │
                             ▼
                            S3
                             │
                 ┌───────────┴───────────┐
                 ▼                       ▼
            PostgreSQL                pgvector
                 │                       │
                 └───────────┬───────────┘
                             ▼
                     Continuity Engine
                             │
                             ▼
                       QA / Approval
                             │
                             ▼
                           FFmpeg
                             │
                             ▼
                       Final Feature
```

### One architectural principle I'd strongly recommend

**Keep the model layer replaceable.**

Don't build:

```text
LangGraph → Model X
```

Build:

```text
LangGraph
    ↓
VideoProvider
    ├── Model X
    ├── Model Y
    └── Model Z
```

Same for image, voice, music and SFX.

That protects your project from the rapid changes in AI models.

And **ComfyUI + Diffusers is a particularly good combination** here: ComfyUI gives you modular, API-accessible workflows, while Diffusers gives you programmatic control over diffusion pipelines, adapters and inference optimization. ([GitHub][4])

For GPU economics, cloud rental is also attractive for this architecture because you can spin up GPU workers only when there is a rendering queue; current RunPod pricing, for example, offers both hourly and per-second GPU billing and a wide range of GPU sizes. ([Runpod][5])

**My recommended MVP stack:**
**Next.js + FastAPI + LangGraph + PostgreSQL/pgvector + Redis/Celery + S3 + ComfyUI + Diffusers + PyTorch/CUDA + open-source image/video/TTS models + RunPod + FFmpeg + Docker + GitHub Actions.**

That is enough to start building the actual **AI Film Studio**, without prematurely adding 20 different infrastructure components.

[1]: https://www.runpod.io/gpu-models?utm_source=chatgpt.com "GPU Models | Available GPUs on Runpod"
[2]: https://www.runpod.io/product/cloud-gpus?utm_source=chatgpt.com "Cloud GPU Instances for AI Workloads | Runpod"
[3]: https://huggingface.co/docs/diffusers/index?utm_source=chatgpt.com "Diffusers · Hugging Face"
[4]: https://github.com/comfy-org/ComfyUI?utm_source=chatgpt.com "GitHub - Comfy-Org/ComfyUI: The most powerful and modular diffusion model GUI, api and backend with a graph/nodes interface. · GitHub"
[5]: https://www.runpod.io/articles/guides/ai-server-cost?utm_source=chatgpt.com "What an AI Server Costs: Buy Price vs Rental Price Guide"


Yes. If **quality is the primary objective**, I would change the strategy: **do not optimize the first version around lightweight/basic models**. Build the studio around the strongest practical open-weight models, and use smaller models only for orchestration, QA, preprocessing, and utility tasks.

For a **commercial multi-film studio**, I'd define the stack like this.

## 🎬 Premium Open-Weight AI Film Studio Stack

| Function                 | Primary model                                          | Role                                   | GPU target |
| ------------------------ | ------------------------------------------------------ | -------------------------------------- | ---------- |
| 🎬 Director / screenplay | **Qwen3-235B-A22B**                                    | Script, scene reasoning, shot planning | Multi-GPU  |
| 🖼️ Image generation     | **FLUX.1 Kontext [max/proprietary depending license]** | Characters, environments, keyframes    | 48–80GB+   |
| 🎨 Image editing         | **FLUX.1 Kontext**                                     | Identity/location consistency          | 48GB+      |
| 🎥 Main video            | **Wan 2.2 14B**                                        | High-quality T2V/I2V                   | 48–80GB    |
| 🎥 Advanced video        | **HunyuanVideo**                                       | High-end cinematic shots               | 80GB       |
| 🎥 Alternative video     | **LTX-2.x**                                            | High-quality video/audio               | 32–48GB+   |
| 🧍 Character             | **Dedicated LoRA + reference conditioning**            | Actor consistency                      | 48GB+      |
| 🗣️ Voice                | **Qwen3-TTS**                                          | Main character dialogue                | 24–48GB    |
| 🎭 Voice alternative     | **F5-TTS**                                             | High-quality expressive speech         | 24GB+      |
| 🎵 Music                 | **ACE-Step 1.5**                                       | Film score / songs                     | 24–48GB    |
| 🔊 SFX                   | **Best available open audio model**                    | Foley / ambience                       | 24GB+      |
| 📝 ASR                   | **Whisper large-v3 / Turbo**                           | Transcription / alignment              | 16–24GB    |
| 👁️ Vision QA            | **Qwen2.5-VL / Qwen3-VL-class model**                  | Visual inspection                      | 24–48GB    |
| 🔎 Visual embeddings     | **SigLIP 2 / DINOv2**                                  | Continuity scoring                     | 16–24GB    |
| 🆙 Upscaling             | **High-quality video upscaler**                        | 4K master                              | 24GB+      |

There is one important distinction: **“full trained” doesn't necessarily mean “largest possible model everywhere.”** For example, using a 235B LLM for every prompt-generation task would be wasteful. But for **creative direction and difficult reasoning**, a frontier open-weight model makes sense.

---

# 1. 🎬 Director — Qwen3-235B-A22B

I would move away from a 1B/7B/14B model as the main director.

Use:

### **Qwen3-235B-A22B**

This becomes your:

> **AI Showrunner / Director / Screenwriter**

It handles:

```text
Novel / screenplay
       ↓
Story structure
       ↓
Character arcs
       ↓
Scene breakdown
       ↓
Shot list
       ↓
Camera instructions
       ↓
Video prompts
       ↓
Continuity instructions
```

You can still use a smaller model for cheap utility tasks.

---

# 2. 🖼️ Image generation — FLUX family

For film production, **don't use a basic SDXL workflow as your primary renderer**.

Use the strongest appropriate FLUX family model available under a license compatible with your intended commercial use.

You need:

```text
FLUX
 │
 ├── Character generation
 ├── Environment generation
 ├── Props
 ├── Storyboards
 ├── Keyframes
 └── Concept art
```

And especially:

### Kontext

For:

```text
Character A
      ↓
Change clothing
      ↓
Change location
      ↓
Change camera
      ↓
Keep identity
```

This is extremely valuable for filmmaking.

**But:** the licensing of specific FLUX variants matters. Some high-quality FLUX releases have non-commercial or otherwise restricted licenses, so the exact production model needs to be selected based on your intended distribution.

---

# 3. 🎥 Main video — Wan 2.2

For your primary open video engine:

### **Wan 2.2 14B**

Don't use a tiny video model simply because it fits on a 16GB GPU.

For your project:

```text
Quality
   ↑
   │          Wan 2.2 14B
   │
   │     LTX
   │
   │  smaller models
   │
   └────────────────────→
                 Cost
```

Use the larger model for final shots.

---

# 4. 🎥 HunyuanVideo

I would keep **HunyuanVideo** as your high-end specialist.

Don't necessarily use it for every shot.

Use it when the shot requires:

* complicated motion
* cinematic composition
* difficult environments
* complex interactions
* high visual quality

The original HunyuanVideo documentation indicates substantial VRAM requirements for its high-resolution configurations, so this is where your **80GB-class GPUs** become useful.

---

# 5. 🎥 LTX

Use **LTX** as your second major video engine.

Why?

You don't want:

```text
All shots → Wan
```

Instead:

```text
                Shot Router
                    │
       ┌────────────┼────────────┐
       ▼            ▼            ▼
     Wan          LTX        Hunyuan
       │            │            │
       └────────────┼────────────┘
                    ▼
                 QA
```

The router chooses the model based on:

```text
shot_type
duration
motion
camera
resolution
characters
environment
GPU availability
cost
```

---

# 6. 🧍 Character model — don't rely only on prompts

For a 3-hour movie, character consistency is probably **more important than the raw video model**.

Build a character-specific model.

For example:

```text
DHruva
│
├── 100–300 curated reference images
│
├── Character LoRA
│
├── Face identity
│
├── Body characteristics
│
├── Hair
│
├── Clothing
│
├── Age
│
└── Expression library
```

Then every shot gets:

```text
Character identity
+
Character LoRA
+
Reference image
+
Scene
+
Camera
+
Video model
```

---

# 7. 🗣️ Voice — Qwen3-TTS

For your main cast, I would use **Qwen3-TTS** as the primary voice system and F5-TTS as an alternative.

But don't create one generic voice.

Create:

```text
Voice Bible

Dhruva
 ├── neutral
 ├── angry
 ├── sad
 ├── frightened
 └── whisper

Inspector
 ├── authority
 ├── anger
 └── interrogation

Judge
 ├── authority
 └── courtroom
```

The dialogue engine needs **emotion + acting direction**, not just text-to-speech.

---

# 8. 🎵 Music — ACE-Step 1.5

For a feature film, music needs to be treated as a separate production pipeline.

```text
Film Theme
    ↓
Character Theme
    ↓
Location Theme
    ↓
Tension Theme
    ↓
Action Theme
    ↓
Courtroom Theme
    ↓
Ending Theme
```

ACE-Step 1.5 is a strong candidate for the open-weight music layer.

---

# 9. 👁️ Vision QA — use a large VLM

This is another place I would **not use a tiny vision model**.

Use a strong vision-language model such as a current **Qwen-VL-class model** for semantic QA.

Example:

```text
Generated Shot
      ↓
Vision Model
      ↓
"Is Dhruva wearing the correct shirt?"
      ↓
YES / NO
```

And:

```text
"Is this the same police station?"
```

```text
"Is the character holding the correct object?"
```

```text
"Does the scene match the screenplay?"
```

---

# 10. 🔎 Embeddings

For automatic numerical similarity, use strong embedding models such as:

### SigLIP 2

and

### DINOv2

For example:

```text
Approved Dhruva
      ↓
Embedding A

Generated Dhruva
      ↓
Embedding B

Similarity(A,B)
      ↓
0.93
      ↓
PASS
```

But don't rely on one number.

Use:

```text
Identity score
+
Clothing score
+
Location score
+
Prompt adherence
+
Motion quality
+
Artifact score
```

---

# 11. 🧠 The important change: use multiple GPU tiers

If you want **quality first**, don't try to run everything on one RTX 5090.

I'd build three GPU pools.

### Pool A — Development

```text
RTX 5090
32GB
```

For:

* workflow development
* LoRA testing
* small generations
* ComfyUI
* debugging

### Pool B — Production

```text
L40S / A100
48–80GB
```

For:

* video generation
* high-quality images
* TTS
* VLM QA

### Pool C — Ultra-quality

```text
H100 / H200-class
```

For:

* huge models
* difficult video shots
* high-resolution generation
* large LLM reasoning
* batch processing

---

# 12. Your model routing becomes very important

Instead of:

```text
Shot → Wan
```

build:

```text
                      AI DIRECTOR
                           │
                           ▼
                      SHOT ANALYZER
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
   Simple shot        Complex shot       Critical shot
        │                  │                  │
        ▼                  ▼                  ▼
      Wan/LTX           Hunyuan             Best model
        │                  │                  │
        └──────────────────┼──────────────────┘
                           ▼
                          QA
                           │
                    ┌──────┴──────┐
                    ▼             ▼
                  FAIL           PASS
                    │             │
                    ▼             ▼
                Regenerate      Lock
```

This gives you **quality without wasting expensive GPU time**.

---

# 13. Final recommended model lineup

If I were designing your production repository today, I'd organize it as:

```text
models/
│
├── director/
│   └── Qwen3-235B
│
├── vision/
│   ├── Qwen-VL-class
│   ├── SigLIP2
│   └── DINOv2
│
├── image/
│   ├── FLUX
│   ├── FLUX Kontext
│   └── control/reference models
│
├── character/
│   ├── LoRA/
│   ├── identity/
│   └── reference/
│
├── video/
│   ├── Wan-2.2-14B
│   ├── LTX
│   └── HunyuanVideo
│
├── audio/
│   ├── Qwen3-TTS
│   ├── F5-TTS
│   └── Whisper-large-v3
│
├── music/
│   └── ACE-Step-1.5
│
└── post/
    ├── video-upscaler
    └── FFmpeg
```

## My quality-first priority

If we have to spend the GPU budget selectively, I'd prioritize:

**1. Video generation** → biggest impact
**2. Character consistency** → essential for a 3-hour story
**3. Image/keyframe generation** → controls video quality
**4. Voice acting** → critical for dialogue scenes
**5. AI Director/VLM** → controls continuity
**6. Music/SFX** → important for cinematic feel
**7. Upscaling** → final polish

And I would **not call the studio “production ready” until we benchmark the models on 5–10 representative scenes** from *The Centerline*: dialogue close-up, two-person conversation, walking shot, rural landscape, police station, courtroom, action/demolition, emotional scene, night scene, and crowd scene.

That benchmark will tell us whether **Wan vs LTX vs Hunyuan** is actually the right production mix instead of choosing models based only on published demos.


**Both.** The AI Film Studio should use a **hybrid execution model**: some stages are strictly sequential because they depend on previous outputs, while many generation jobs should run **in parallel**.

The key is: **don't make the entire 3-hour film pipeline sequential.**

## 1. High-level execution

```text
                    PROJECT
                       │
                       ▼
                 MASTER SCRIPT
                       │
                       ▼
              STORY / CHARACTERS
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
       Character    Locations      Props
       Generation   Generation    Generation
          │            │            │
          └────────────┼────────────┘
                       ▼
                 SCENE BREAKDOWN
                       │
                       ▼
                  SHOT PLANNING
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
       Shot 001     Shot 002     Shot 003
          │            │            │
          │       PARALLEL         │
          ▼            ▼            ▼
       GPU #1       GPU #2       GPU #3
          │            │            │
          └────────────┼────────────┘
                       ▼
                  QA / CONTINUITY
                       │
                ┌──────┴──────┐
                ▼             ▼
              FAIL           PASS
                │             │
                ▼             ▼
            Regenerate      LOCK
                              │
                              ▼
                         Scene Assembly
                              │
                              ▼
                         Film Assembly
```

---

# 2. What should be sequential?

Some things **must** happen sequentially.

### Script → scenes → shots

```text
Script
  ↓
Scene breakdown
  ↓
Shot list
```

You can't reliably generate the final shot list before knowing the scene structure.

### Character Bible

```text
Character design
       ↓
Character approval
       ↓
Character LoRA/reference
       ↓
Shot generation
```

You want the character identity locked before generating hundreds of shots.

### Location Bible

Same principle:

```text
Location concept
       ↓
Location approval
       ↓
Location reference
       ↓
Scene generation
```

---

# 3. What should be parallel?

Once the dependencies are satisfied, **generate as much as possible in parallel**.

For example:

```text
Scene 12
│
├── Shot 121 ── GPU 01
├── Shot 122 ── GPU 02
├── Shot 123 ── GPU 03
├── Shot 124 ── GPU 04
├── Shot 125 ── GPU 05
└── Shot 126 ── GPU 06
```

These don't necessarily need to wait for each other.

---

# 4. Character generation is parallel

Suppose your film has:

```text
Dhruva
Inspector
Judge
Lawyer
Police officers
Villagers
```

After the character definitions are approved:

```text
                 Character Pipeline
                       │
       ┌───────────────┼───────────────┐
       ▼               ▼               ▼
    Dhruva          Inspector         Judge
       │               │               │
      GPU             GPU             GPU
       │               │               │
       ▼               ▼               ▼
     LoRA             LoRA             LoRA
```

Parallel.

---

# 5. Locations are parallel too

```text
Location Pipeline
│
├── Bhujanganagar road
├── Police station
├── Courtroom
├── House
└── Market
```

All can be generated simultaneously once the location specifications are finalized.

---

# 6. Video generation is massively parallel

This is where cloud GPUs become valuable.

Suppose you have:

**1,000 shots**

You don't do:

```text
Shot 1
 ↓
Shot 2
 ↓
Shot 3
 ↓
...
Shot 1000
```

That would be painfully slow.

Instead:

```text
                    1000 SHOTS
                         │
                    Job Queue
                         │
       ┌─────────────────┼─────────────────┐
       ▼                 ▼                 ▼
    Worker 1          Worker 2          Worker 3
       │                 │                 │
   20 shots           20 shots           20 shots
       │                 │                 │
       └─────────────────┼─────────────────┘
                         ▼
                       S3
```

With enough GPUs, hundreds of jobs can execute concurrently.

---

# 7. But there's a catch: shot continuity

This is where you **cannot blindly parallelize everything**.

Consider:

```text
Shot 101
Dhruva enters the police station.

Shot 102
Dhruva walks toward Inspector.

Shot 103
Inspector stands up.
```

Shot 102 may need information from Shot 101:

```text
Dhruva's:
position
clothing
lighting
camera direction
environment
```

So you need a **continuity dependency graph**.

---

# 8. Use a DAG

This is the architecture I'd recommend.

```text
                 Scene 10
                    │
             ┌──────┴──────┐
             ▼             ▼
          Shot 101       Shot 102
             │             │
             └──────┬──────┘
                    ▼
                 Shot 103
                    │
             ┌──────┴──────┐
             ▼             ▼
          Shot 104       Shot 105
             │             │
             └──────┬──────┘
                    ▼
                 Shot 106
```

So:

**Independent shots → parallel**

**Dependent shots → sequential**

---

# 9. Example from your film

Imagine a courtroom sequence:

```text
Scene 45
Courtroom
│
├── Establishing shot
│
├── Judge close-up
│
├── Dhruva close-up
│
├── Inspector close-up
│
├── Lawyer
│
├── Judge dialogue
│
├── Dhruva reaction
│
└── Courtroom wide
```

Some can be generated concurrently:

```text
Judge close-up ───── GPU 1
Dhruva close-up ──── GPU 2
Inspector ────────── GPU 3
Lawyer ───────────── GPU 4
```

But the **dialogue/reaction timing and continuity** should be coordinated afterward.

---

# 10. Audio can run in parallel with video

This is another major optimization.

You don't need:

```text
Video
 ↓
Voice
 ↓
Music
```

Instead:

```text
                  Scene
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
        Video     Dialogue   Music
          │         │         │
          ▼         ▼         ▼
        Video      WAV       WAV
          │         │         │
          └─────────┼─────────┘
                    ▼
                  Mix
```

Voice generation can happen while video generation is running.

---

# 11. QA is sequential relative to generation

For each shot:

```text
Generate
   ↓
QA
   ↓
PASS / FAIL
```

You shouldn't QA a shot before it exists.

But **QA for multiple completed shots can run in parallel**:

```text
Shot 101 ──→ QA Worker 1
Shot 102 ──→ QA Worker 2
Shot 103 ──→ QA Worker 3
Shot 104 ──→ QA Worker 4
```

---

# 12. Regeneration is asynchronous

Suppose:

```text
100 shots generated
```

QA finds:

```text
78 PASS
15 REVIEW
7 FAIL
```

Don't stop the entire pipeline.

Do:

```text
78 → LOCK

15 → Human review

7 → Regeneration queue
```

The 7 failed shots can regenerate while other scenes continue.

---

# 13. The entire film therefore behaves like a DAG

This is the most important architectural concept.

```text
                         SCRIPT
                           │
                    ┌──────┴──────┐
                    ▼             ▼
              CHARACTER         LOCATION
                 PIPE             PIPE
                    │             │
                    └──────┬──────┘
                           ▼
                      SCENE PLAN
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
          Scene 1       Scene 2       Scene 3
             │             │             │
        ┌────┼────┐   ┌────┼────┐   ┌────┼────┐
        ▼    ▼    ▼   ▼    ▼    ▼   ▼    ▼    ▼
       S1   S2   S3  S1   S2   S3  S1   S2   S3
        │    │    │   │    │    │   │    │    │
        └────┼────┘   └────┼────┘   └────┼────┘
             │             │             │
             ▼             ▼             ▼
             QA            QA            QA
             │             │             │
             └─────────────┼─────────────┘
                           ▼
                     Scene Assembly
                           │
                           ▼
                     Film Assembly
```

---

# 14. LangGraph vs Celery

This distinction is important.

### LangGraph

Should manage:

> **AI reasoning / decision workflow**

```text
"What should happen next?"
```

### Celery / Temporal

Should manage:

> **actual distributed compute**

```text
"Run this video generation job on GPU #12."
```

So:

```text
             LangGraph
            AI Director
                 │
                 ▼
           Job Dispatcher
                 │
                 ▼
        Redis / Temporal
                 │
       ┌─────────┼─────────┐
       ▼         ▼         ▼
     GPU 1     GPU 2     GPU 3
```

Don't make LangGraph itself responsible for thousands of GPU jobs.

---

# 15. Recommended execution strategy

For your AI Film Studio:

### Sequential

* Story development
* Character definition
* Location definition
* Scene planning
* Dependency resolution
* Shot generation where continuity requires previous-shot information
* QA after generation
* Final scene/timeline assembly

### Parallel

* Character asset generation
* Location generation
* Props
* Independent shot generation
* Voice generation
* Music generation
* SFX generation
* QA across completed shots
* Upscaling of approved shots
* Failed-shot regeneration
* Rendering/export jobs

---

## The ideal architecture

**Not:**

```text
Everything → Sequential
```

and not:

```text
Everything → Parallel
```

but:

```text
              DEPENDENCY GRAPH
                     │
        ┌────────────┼────────────┐
        │            │            │
    Sequential   Parallel      Parallel
    dependencies  generation   generation
        │            │            │
        └────────────┼────────────┘
                     ▼
                 QA / Lock
                     │
                     ▼
               Next dependency
```

This is exactly why I would use **LangGraph + a proper distributed job queue + cloud GPU workers** for your architecture. The AI decides **what should happen**, while the compute layer decides **where and when it should run**.
