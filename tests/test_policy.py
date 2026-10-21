
import unittest

from policy import PolicyAction, evaluate_pipeline_policy


class TestPolicy(unittest.TestCase):

    def evaluate(self, text, score, status="SUCCESS"):
        return evaluate_pipeline_policy(
            text,
            {"status": status, "noul_score": score},
        )

    def test_clean_text_passes(self):
        result = self.evaluate("print('hello')", 0.05)
        self.assertEqual(result["action"], PolicyAction.DIRECT_PASS)

    def test_detected_secret_is_sanitized(self):
        result = self.evaluate(
            "Key: AKIAIOSFODNN7EXAMPLE", 0.10
        )
        self.assertEqual(result["action"], PolicyAction.SANITIZED_PASS)
        self.assertNotIn("AKIAIOSFODNN7EXAMPLE", result["processed_text"])

    def test_high_risk_is_blocked(self):
        result = self.evaluate("ordinary text", 0.90)
        self.assertEqual(result["action"], PolicyAction.BLOCK_FOR_REVIEW)
        self.assertIsNone(result["processed_text"])

    def test_ambiguous_risk_is_blocked(self):
        result = self.evaluate("ordinary text", 0.50)
        self.assertEqual(result["action"], PolicyAction.BLOCK_FOR_REVIEW)

    def test_decider_error_is_blocked(self):
        result = self.evaluate("ordinary text", None, "ERROR: timeout")
        self.assertEqual(result["action"], PolicyAction.BLOCK_FOR_REVIEW)

    def test_invalid_scores_are_blocked(self):
        for score in (None, "invalid", float("nan"), float("inf"), 1.5, -0.1):
            with self.subTest(score=score):
                result = self.evaluate("ordinary text", score)
                self.assertEqual(
                    result["action"], PolicyAction.BLOCK_FOR_REVIEW
                )


if __name__ == "__main__":
    unittest.main()
