# Product Overview

## Purpose
EvalAI is an AI-powered exam evaluation platform that automatically grades student short-answer responses using NLP/ML techniques. It reduces teacher workload by providing instant, consistent, and explainable scoring with multilingual support.

## Key Features
- **Automated Grading**: Scores student answers using semantic similarity, NLI entailment, concept coverage, and length ratio signals
- **Multilingual Support**: Handles answers in English, Tamil, and Hindi; auto-generates translated model answers
- **AI Feedback**: Generates natural language feedback per answer via a local LLM (Ollama/phi)
- **Heatmap Visualization**: Sentence-level similarity heatmaps show which parts of an answer matched the model
- **Teacher Tools**: Create/manage tests, question banks, import from Excel/Moodle, view analytics and reports
- **Student Tools**: Take timed tests, view scored results with per-question feedback and concept breakdowns
- **Analytics Dashboard**: Class-level performance stats, score distributions, concept mastery heatmaps
- **PDF Reports**: Downloadable per-student and per-test reports
- **Role-Based Access**: Separate teacher and student flows with JWT authentication

## Target Users
- **Teachers/Instructors**: Create tests, manage question banks, review AI-graded results, export reports
- **Students**: Take online exams, receive instant AI feedback on short-answer responses

## Use Cases
- Short-answer and descriptive exam grading in educational institutions
- Multilingual classrooms where students answer in their native language
- Formative assessment with immediate feedback loops
- Moodle LMS integration for question import/export
