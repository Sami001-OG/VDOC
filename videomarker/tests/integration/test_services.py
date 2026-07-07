"""Integration tests for the service layer."""

from vdoc.services.pipeline_service import PipelineService


class TestPipelineServiceIntegration:
    def test_build_pipeline(self):
        pipeline = PipelineService.build_pipeline({"output_dir": "/tmp/out"})
        assert pipeline is not None

    def test_build_partial_pipeline(self):
        for names in [["video"], ["video", "scene"], ["speech"]]:
            pipeline = PipelineService.build_partial_pipeline(names)
            assert pipeline is not None
