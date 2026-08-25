# GPU Workers

GPU workers execute expensive AI inference and media-processing jobs inside the film's isolated AWS environment.

Workers should be ephemeral where practical. They consume jobs from the film environment, write outputs only to film-owned storage, and are never shared across client films.
