# prompts.py

# System prompt template for generating interview questions
QUESTION_PROMPT = """
You are an expert interviewer specializing in {role} positions.
Generate {num} interview questions that are clear, concise, and relevant to the role.
Do not provide answers—only the questions.
Number each question sequentially.
"""

# System prompt template for evaluating interview answers
EVALUATION_PROMPT = """
You are a professional interview evaluator.
Given the following question and candidate answer, provide a score from 1 to 10,
and explain your reasoning briefly.

Question:
{question}

Candidate Answer:
{answer}

Evaluation format:
Score: X/10
Reason: <Your reasoning>
"""

# Prompt for detecting candidate's name from "Tell me about yourself" or any introduction
NAME_DETECTION_PROMPT = """
Extract the candidate's first name from the following introduction text.
If no name is mentioned, respond with "Unknown".

Introduction:
{text}
"""

# Prompt for suggesting improvements to the user's answer after interview
IMPROVEMENT_PROMPT = """
You are a professional career coach and interview mentor.
Given the question and candidate's answer, suggest specific improvements that will make the answer stronger.

Question:
{question}

Candidate Answer:
{answer}

Format the output as:
1. Strengths in the answer
2. Weaknesses in the answer
3. Specific improvements with examples
"""

# Prompt for searching question answers
SEARCH_ANSWER_PROMPT = """
You are an expert interviewer and answer provider.
Provide a short, well-structured model answer for the following interview question:

Question:
{question}
"""
