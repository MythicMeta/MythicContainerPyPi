import importlib.util
from pathlib import Path
import unittest

KEYWORD_RESOLUTION_PATH = (
    Path(__file__).resolve().parents[1]
    / "mythic_container"
    / "keyword_resolution.py"
)
spec = importlib.util.spec_from_file_location(
    "keyword_resolution",
    KEYWORD_RESOLUTION_PATH,
)
keyword_resolution = importlib.util.module_from_spec(spec)
spec.loader.exec_module(keyword_resolution)

PTTaskKeywordResolution = keyword_resolution.PTTaskKeywordResolution
RevertKeywords = keyword_resolution.RevertKeywords


class KeywordResolutionTests(unittest.TestCase):
    def test_revert_keywords_scalar_replacement(self):
        keyword_resolution = [
            PTTaskKeywordResolution(
                raw="@cred:12.credential",
                value_type="string",
                expanded_value="abc123",
                parameter_names=["args"],
            )
        ]
        self.assertEqual(
            RevertKeywords("asktgs /ticket:abc123 /nowrap", keyword_resolution),
            "asktgs /ticket:@cred:12.credential /nowrap",
        )

    def test_revert_keywords_longest_first(self):
        keyword_resolution = [
            PTTaskKeywordResolution(
                raw="@token:1.value",
                value_type="string",
                expanded_value="abc",
            ),
            PTTaskKeywordResolution(
                raw="@token:2.value",
                value_type="string",
                expanded_value="abc123",
            ),
        ]
        self.assertEqual(
            RevertKeywords("value=abc123 next=abc", keyword_resolution),
            "value=@token:2.value next=@token:1.value",
        )

    def test_revert_keywords_parameter_name_filtering(self):
        keyword_resolution = [
            PTTaskKeywordResolution(
                raw="@cred:12.credential",
                value_type="string",
                expanded_value="shared",
                parameter_names=["args"],
            ),
            PTTaskKeywordResolution(
                raw="@file:7.filename",
                value_type="string",
                expanded_value="shared",
                parameter_names=["filename"],
            ),
        ]
        self.assertEqual(
            RevertKeywords("shared", keyword_resolution, "filename"),
            "@file:7.filename",
        )

    def test_revert_keywords_structured(self):
        keyword_resolution = [
            PTTaskKeywordResolution(
                raw="@cred:12",
                value_type="structured",
                parameter_names=["cred"],
            )
        ]
        self.assertEqual(RevertKeywords({"id": 12}, keyword_resolution, "cred"), "@cred:12")

    def test_revert_keywords_passthrough(self):
        self.assertEqual(RevertKeywords("unchanged", []), "unchanged")

    def test_revert_keywords_does_not_reprocess_restored_keywords(self):
        keyword_resolution = [
            PTTaskKeywordResolution(
                raw="@cred:12.credential",
                value_type="string",
                expanded_value="abc123",
            ),
            PTTaskKeywordResolution(
                raw="@token:7.value",
                value_type="string",
                expanded_value="cred",
            ),
        ]
        self.assertEqual(
            RevertKeywords("value=abc123 other=cred", keyword_resolution),
            "value=@cred:12.credential other=@token:7.value",
        )


if __name__ == "__main__":
    unittest.main()
