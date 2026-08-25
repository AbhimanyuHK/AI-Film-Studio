from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutionPolicy:
    max_attempts: int = 3
    claim_timeout_seconds: int = 1800
    presigned_url_seconds: int = 900
    max_concurrent_jobs_per_environment: int = 4

    def validate(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be positive")
        if self.claim_timeout_seconds < 60:
            raise ValueError("claim_timeout_seconds must be at least 60 seconds")
        if self.presigned_url_seconds < 60:
            raise ValueError("presigned_url_seconds must be at least 60 seconds")
        if self.max_concurrent_jobs_per_environment < 1:
            raise ValueError("max_concurrent_jobs_per_environment must be positive")
