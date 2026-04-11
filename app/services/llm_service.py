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

    def generate_answer_breakdown(self, question, reference, student, score, max_score, covered, missing, wrong):
        prompt = f"""You are an academic evaluator analyzing a student's answer.

Question: {question}
Reference Answer: {reference}
Student Answer: {student}
Score: {score}/{max_score}

Analyze what the student got right, wrong, and missed compared to the reference answer.
Return STRICT JSON only, no markdown, no extra text.

{{
  "correct_points": ["specific thing student said correctly"],
  "wrong_points": ["specific incorrect statement student made and why it is wrong"],
  "missing_points": ["specific concept from reference that student did not mention"],
  "summary": "one sentence overall assessment of the student answer"
}}

IMPORTANT RULES:
- correct_points: Quote what the student said correctly in their own words
- wrong_points: Quote what the student said incorrectly and explain the correct answer briefly. Example: 'Student said Stack stores objects — incorrect, Stack is used for method calls and local variables'
- missing_points: Mention specific concepts from reference that are completely absent in student answer
- summary: One sentence like 'Student confused Stack and Heap definitions' or 'Good answer but missed LIFO and Garbage Collector'
- Keep each point under 20 words
- If none for a category return empty array []"""
        try:
            import json
            raw = self.model.generate_content(prompt).text
            raw = raw.strip().strip("```json").strip("```").strip()
            return json.loads(raw)
        except Exception:
            return {
                "correct_points": [],
                "wrong_points":   [f"{c[:80]}" for c in wrong[:3]]   if wrong   else [],
                "missing_points": [f"{c[:80]}" for c in missing[:3]] if missing else [],
                "summary": f"Score: {score}/{max_score}"
            }

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