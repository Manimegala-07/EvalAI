import requests
import app.config as config


class FeedbackService:

    def generate(self, correct, missing, extra, score):

        prompt = f"""
You are an academic evaluator.

The student received a score of {score}.

Correct concepts identified:
{correct}

Missing concepts:
{missing}

Extra / incorrect concepts:
{extra}

Generate short, constructive feedback for the student.
Focus on improvement.
Keep it concise (3-5 sentences).
"""

        response = requests.post(
            config.OLLAMA_URL,
            json={
                "model": config.OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            }
        )

        data = response.json()

        if "response" in data:
            return data["response"]

        if "message" in data and "content" in data["message"]:
            return data["message"]["content"]

        return str(data)