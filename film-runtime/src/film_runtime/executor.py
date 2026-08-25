from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Character, FilmAsset, FilmMetadata, ProductionJob, Scene
from .rag import FilmKnowledgeIndex
from .scope import validate_payload_scope


class FilmRuntimeExecutor:
    def __init__(self, session: AsyncSession, knowledge: FilmKnowledgeIndex) -> None:
        self.session = session
        self.knowledge = knowledge

    async def execute(self, *, job_id: str, operation: str, payload: dict[str, Any]) -> dict[str, Any]:
        validate_payload_scope(payload)
        job = await self.session.get(ProductionJob, job_id)
        if job is None:
            job = ProductionJob(job_id=job_id, operation=operation, payload=payload, status='running')
            self.session.add(job)
        else:
            if job.operation != operation:
                raise ValueError('job operation mismatch')
            if job.status == 'completed' and job.result:
                return job.result
            job.status = 'running'

        result: dict[str, Any]
        if operation == 'script_analysis':
            result = await self._script_analysis(payload)
        elif operation == 'character_generation':
            result = await self._characters(payload)
        elif operation == 'environment_generation':
            result = {'status': 'accepted', 'operation': operation}
        elif operation == 'storyboard':
            result = await self._storyboard(payload)
        elif operation in {'shot_generation', 'video_generation', 'voice_generation', 'translation', 'dubbing', 'music', 'sfx', 'editing', 'upscaling', 'final_render'}:
            result = {'status': 'accepted', 'operation': operation, 'film_scoped': True}
        else:
            raise ValueError(f'unsupported film operation: {operation}')

        job.result = result
        job.status = 'completed'
        await self.session.commit()
        return result

    async def _script_analysis(self, payload: dict[str, Any]) -> dict[str, Any]:
        script = str(payload.get('script', '')).strip()
        if not script:
            raise ValueError('script is required for script_analysis')
        return {'status': 'analyzed', 'characters': [], 'scenes': [], 'script_length': len(script)}

    async def _characters(self, payload: dict[str, Any]) -> dict[str, Any]:
        characters = payload.get('characters', [])
        created = []
        for item in characters:
            obj = Character(name=str(item.get('name', 'Unnamed')), description=item.get('description'), metadata_json=item.get('metadata', {}))
            self.session.add(obj)
            created.append(obj.name)
        await self.session.flush()
        return {'status': 'completed', 'characters': created}

    async def _storyboard(self, payload: dict[str, Any]) -> dict[str, Any]:
        scenes = payload.get('scenes', [])
        created = []
        for index, item in enumerate(scenes, start=1):
            obj = Scene(scene_number=int(item.get('scene_number', index)), title=item.get('title'), description=item.get('description'), metadata_json=item.get('metadata', {}))
            self.session.add(obj)
            created.append(obj.scene_number)
        await self.session.flush()
        return {'status': 'completed', 'scenes': created}
