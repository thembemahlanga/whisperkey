
import unittest

from orchestrator import run_whisperkey_agent
from policy import PolicyAction


class FakeDecider:
    def __init__(self, status="SUCCESS", score=0.10):
        self.status = status
        self.score = score

    def evaluate_noul(self, processed_text, question_id):
        return {
            "status": self.status,
            "noul_score": self.score,
        }


class FakeBedrock:
    def __init__(self):
        self.called = False
        self.received_text = None

    def generate_response(self, text):
        self.called = True
        self.received_text = text
        return "Fake AI response"


class TestOrchestrator(unittest.TestCase):
    def test_blocked_request_does_not_call_bedrock(self):
        decider = FakeDecider(score=0.90)
        bedrock = FakeBedrock()

        result = run_whisperkey_agent(
            'password="fake-demo-password"',
            decider,
            bedrock,
        )

        self.assertEqual(result["action"], PolicyAction.BLOCK_FOR_REVIEW)
        self.assertFalse(bedrock.called)
        self.assertIsNone(result["text"])

    def test_sanitized_text_is_sent_to_bedrock(self):
        decider = FakeDecider(score=0.10)
        bedrock = FakeBedrock()

        result = run_whisperkey_agent(
            'password="fake-demo-password"',
            decider,
            bedrock,
        )

        self.assertEqual(result["action"], PolicyAction.SANITIZED_PASS)
        self.assertTrue(bedrock.called)
        self.assertNotIn("fake-demo-password", bedrock.received_text)
        self.assertEqual(result["text"], "Fake AI response")

    def test_decider_failure_does_not_call_bedrock(self):
        decider = FakeDecider(status="ERROR")
        bedrock = FakeBedrock()

        result = run_whisperkey_agent("Hello", decider, bedrock)

        self.assertEqual(result["action"], PolicyAction.BLOCK_FOR_REVIEW)
        self.assertFalse(bedrock.called)


if __name__ == "__main__":
    unittest.main()
