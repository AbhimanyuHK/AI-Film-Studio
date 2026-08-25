# Database Architecture

The platform uses two database boundaries:

## Central control-plane database

Stores users, clients, films, environments, deployments, permissions, subscriptions, billing metadata, and platform audit events.

## Film database

Each film environment has its own database for scenes, shots, characters, production jobs, film metadata, and related runtime state.

Film content and knowledge must not be consolidated into the central control-plane database.
