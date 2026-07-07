"""Example custom processor plugin.

Place this file in videomarker/plugins/ or register the path:
    PluginRegistry.add_search_path(Path("/path/to/plugins"))
"""

from videomarker.core.processor import Processor
from videomarker.core.plugin import processor


@processor("code_detector", dependencies=["vision"], priority=55)
class CodeDetector(Processor):
    """Detects code-related scenes and extracts programming languages."""

    def process(self, context):
        vision_results = context.data.get("vision_results", {})
        if not vision_results:
            return

        code_found = []
        for scene_id, vision in vision_results.items():
            if vision.description and vision.description.is_code:
                code_found.append({
                    "scene_id": scene_id,
                    "language": self._detect_language(vision.description.detailed),
                })

        context.data["code_detections"] = code_found

    def _detect_language(self, description: str) -> str:
        """Simple heuristic to detect programming language from description."""
        languages = {
            "python": ["python", "def ", "import ", "class "],
            "javascript": ["javascript", "const ", "function", "=>"],
            "typescript": ["typescript", "interface", "type "],
            "java": ["java", "public class", "public static"],
            "cpp": ["c++", "cpp", "#include", "int main"],
            "rust": ["rust", "fn ", "let mut", "impl "],
            "go": ["golang", "go ", "func ", "package "],
        }
        desc_lower = description.lower()
        for lang, patterns in languages.items():
            if any(p in desc_lower for p in patterns):
                return lang
        return "unknown"
