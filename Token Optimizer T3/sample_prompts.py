"""Demonstration prompts covering the required test categories."""

DEMO_PROMPT = ("Can you please explain what Python programming is in simple terms that are easy for a complete "
               "beginner to understand? Please keep the explanation short and avoid unnecessary details.")

SAMPLES = [
    {"name": "Final demo: Python explanation", "category": "Simple Q&A", "prompt": DEMO_PROMPT},
    {"name": "Q&A: machine learning", "category": "Simple Q&A",
     "prompt": "Can you please provide me with a brief explanation of what machine learning is?"},
    {"name": "Python: sum of two numbers", "category": "Python programming",
     "prompt": "Write a Python program. The program should take two numbers as input. It should calculate their sum and display the result."},
    {"name": "Summarization", "category": "Summarization",
     "prompt": ("Hello! I hope you are doing well. Could you please provide me with a brief summary of the following text? "
                "I would really appreciate it if you could keep the summary short.\n\n"
                "Text: Photosynthesis is the process by which green plants, algae and some bacteria convert light energy "
                "into chemical energy. Using chlorophyll, they absorb sunlight and use it to turn carbon dioxide and water "
                "into glucose and oxygen. The glucose fuels growth, while the oxygen is released into the atmosphere.")},
    {"name": "Data analysis (pandas)", "category": "Data analysis",
     "prompt": ("I have a CSV file with the columns date, region, units and revenue. Could you please tell me how to use pandas "
                "in order to calculate the total revenue per region for 2024 and then sort the results in descending order? "
                "Please show the code and keep the explanation short.")},
    {"name": "Multiple constraints (optimizer must refuse to cut)", "category": "Multiple constraints",
     "prompt": ("Please write a product description for a stainless steel water bottle. It must be under 60 words. "
                "Do not mention price. Never use the word \"cheap\". Use a friendly tone. "
                "Include the phrase \"keeps drinks cold for 24 hours\".")},
    {"name": "Repeated instructions", "category": "Repeated instructions",
     "prompt": "Answer briefly. Keep your response short. Do not provide unnecessary details. Make the answer concise."},
    {"name": "Already minimal (no reduction expected)", "category": "No-reduction case",
     "prompt": "Explain recursion."},
]
