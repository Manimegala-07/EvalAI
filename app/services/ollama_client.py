import requests
import app.config as config


def call_ollama(prompt):

    response = requests.post(
        config.OLLAMA_URL,
        json={
            "model": config.OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        }
    )

    return response.json()["response"]
