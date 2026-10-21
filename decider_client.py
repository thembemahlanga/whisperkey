
import math

import requests


class DeciderClient:
    def __init__(
        self,
        base_url="http://127.0.0.1:8000",
        timeout=5,
    ):
        self.endpoint = f"{base_url.rstrip('/')}/v1/systemone"
        self.timeout = timeout

    def evaluate_noul(self, processed_text, question_id="contains_secret"):
        payload = {
            "state": processed_text,
            "questions": {
                question_id: {
                    "type": "noul",
                    "instructions": (
                        "Does this text contain a secret or credential "
                        "that remains unredacted, such as an API key, "
                        "password, access token, or private key?"
                    ),
                }
            },
        }

        try:
            response = requests.post(
                self.endpoint,
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()

            score = data["answers"][question_id]["noul"]
            score = float(score)

            if not math.isfinite(score) or not 0 <= score <= 1:
                raise ValueError("Invalid Decider score")

            return {
                "status": "SUCCESS",
                "noul_score": score,
            }

        except (
            requests.RequestException,
            ValueError,
            TypeError,
            KeyError,
        ):
            return {
                "status": "ERROR",
                "noul_score": None,
            }
