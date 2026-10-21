
import unittest
from detector import redact_text


class TestDetector(unittest.TestCase):

    def test_clean_text_is_unchanged(self):
        text = "def add(a, b): return a + b"
        sanitized, categories = redact_text(text)
        self.assertEqual(sanitized, text)
        self.assertEqual(categories, [])

    def test_aws_key_is_redacted(self):
        text = "AWS key: AKIAIOSFODNN7EXAMPLE"
        sanitized, categories = redact_text(text)
        self.assertNotIn("AKIAIOSFODNN7EXAMPLE", sanitized)
        self.assertIn("AWS_ACCESS_KEY_ID", categories)

    def test_password_value_is_redacted(self):
        text = 'password="example-fake-password"'
        sanitized, categories = redact_text(text)
        self.assertNotIn("example-fake-password", sanitized)
        self.assertIn("SECRET_ASSIGNMENT", categories)

    def test_email_is_redacted(self):
        text = "Contact person@example.com for help"
        sanitized, categories = redact_text(text)
        self.assertNotIn("person@example.com", sanitized)
        self.assertIn("EMAIL", categories)

    def test_private_key_block_is_redacted(self):
        text = (
            "-----BEGIN PRIVATE KEY-----\n"
            "FAKE-TEST-KEY-MATERIAL\n"
            "-----END PRIVATE KEY-----"
        )
        sanitized, categories = redact_text(text)
        self.assertNotIn("FAKE-TEST-KEY-MATERIAL", sanitized)
        self.assertIn("PRIVATE_KEY", categories)


if __name__ == "__main__":
    unittest.main()
