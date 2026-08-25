import pytest
from ai_engine.adapters import GenerationRequest, ImageGenerationAdapter

class FakeRuntime:
    def execute(self, stage, model, prompt, parameters=None):
        return type("Output", (), {"assets": (b"artifact",), "metadata": {"model": model, "stage": stage}})()

@pytest.mark.asyncio
async def test_image_adapter_uses_runtime():
    result = await ImageGenerationAdapter(FakeRuntime()).generate(GenerationRequest("j", "f", "character_generation", "hero"))
    assert result.status == "completed"
    assert result.output_assets == (b"artifact",)
    assert result.metadata["model"] == "flux.1-dev"
