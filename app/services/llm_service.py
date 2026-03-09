import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def _sep(title=""):
    line = "─" * 60
    if title:
        print(f"\n┌{line}┐")
        print(f"│  🤖 {title:<55}│")
        print(f"└{line}┘")
    else:
        print(f"{'─'*62}")


class LLMService:

    def __init__(self):
        self.model = genai.GenerativeModel("gemini-2.0-flash")
        print("✅ LLMService initialized with model: gemini-2.0-flash")

    def generate_feedback(self, reference, student, score):

        # ── DEBUG ──────────────────────────────────────────
        _sep("GEMINI — generate_feedback()")
        print(f"  📝 Reference  ({len(reference.split())} words): {reference[:100]}...")
        print(f"  ✍️  Student   ({len(student.split())} words):   {student[:100]}...")
        print(f"  🏆 Score passed to Gemini: {score}")
        # ───────────────────────────────────────────────────

        prompt = f"""
Reference:
{reference}

Student:
{student}

Score:
{score}

Give short constructive academic feedback in 3-5 sentences.
"""
        # ── DEBUG ──────────────────────────────────────────
        print(f"\n  📤 Sending prompt to Gemini ({len(prompt)} chars):")
        print(f"  {'─'*50}")
        print(prompt[:400])
        print(f"  {'─'*50}")
        print(f"  ⏳ Waiting for Gemini response...")
        # ───────────────────────────────────────────────────

        try:
            response = self.model.generate_content(prompt)
            feedback = response.text

            # ── DEBUG ──────────────────────────────────────
            print(f"\n  ✅ Gemini responded ({len(feedback)} chars):")
            print(f"  {'─'*50}")
            print(f"  {feedback}")
            print(f"  {'─'*50}")
            # ───────────────────────────────────────────────

            return feedback

        except Exception as e:
            print(f"  ❌ Gemini API error: {str(e)}")
            return f"Feedback unavailable: {str(e)}"

    def generate_structured_report(self, summary_text):

        # ── DEBUG ──────────────────────────────────────────
        _sep("GEMINI — generate_structured_report()")
        print(f"  📋 Summary text ({len(summary_text)} chars):")
        print(f"  {summary_text[:300]}{'...' if len(summary_text)>300 else ''}")
        print(f"\n  ⏳ Requesting structured JSON from Gemini...")
        # ───────────────────────────────────────────────────

        prompt = f"""
You are an academic evaluator.

Evaluation Summary:
{summary_text}

Return STRICT JSON only, no markdown:

{{
  "strengths": [],
  "weaknesses": [],
  "missing_concepts": [],
  "overall_summary": "",
  "improvement_plan": ""
}}
"""
        try:
            response = self.model.generate_content(prompt)
            raw = response.text

            # ── DEBUG ──────────────────────────────────────
            print(f"\n  ✅ Gemini raw JSON response:")
            print(f"  {'─'*50}")
            print(f"  {raw[:600]}")
            print(f"  {'─'*50}")
            # ───────────────────────────────────────────────

            return raw

        except Exception as e:
            print(f"  ❌ Gemini structured report error: {str(e)}")
            return "{}"