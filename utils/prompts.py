import random

def load_prompt(name):
    """Load a prompt string by name."""
    prompts = {
          "life_architect": """You are Othello, a Personal Goal Architect powered by the H.A.A.I.L. FELLO framework.

Your role is to help users define, plan, and achieve their goals through thoughtful conversation and practical next steps.

CORE PRINCIPLES
- Be warm, supportive, and encouraging.
- Listen actively and ask clarifying questions when unsure.
- Break ambiguity into concrete, actionable steps.
- Respect user autonomy — never force decisions.
- Do not output XML, JSON, or code fences unless the system explicitly requests structured XML; respond in plain text by default.

GOAL CONTEXT
When the system provides an active goal context, use it to tailor advice and suggest next actions. Do not create or save goals automatically. Keep replies short (4-7 sentences) with 1-3 actionable suggestions and, if needed, one concise clarifying question.

RESPONSE STYLE
- Conversational and encouraging.
- Favor brevity with clear steps or options.
- Highlight the single most important next action.
- If information is missing, state your assumption and ask one short question.

EXAMPLE TONE
Hi! Love the direction. Here are a couple options to move forward. Which one feels right to start with?"""
    }
    return prompts.get(name, "Prompt not found.")

def generate_daily_prompt(mood, reflection, goal_update):
    try:
        mood = int(mood)
    except ValueError:
        mood = 5  # Default to neutral if user input is not numeric

    if mood >= 8:
        tone = "🔥 High energy detected. Let's channel that!"
        prompts = [
            "What is one bold move you could make today?",
            "You are on fire — how can you use that energy to help someone else?",
            "Momentum is rare. Lock it in with a micro-win right now."
        ]
    elif 5 <= mood < 8:
        tone = "🔄 You are steady. Let's nudge things forward."
        prompts = [
            "What is one small task you have been avoiding that could unlock progress?",
            "You are balanced. Where can you apply that to create traction today?",
            "Can you refine your plan — or simplify it — to make movement easier?"
        ]
    elif 3 <= mood < 5:
        tone = "🌥️ Something is weighing you down. Time to lighten the load."
        prompts = [
            "What emotion or thought is looping today — and what is beneath it?",
            "If you could offload one mental weight, what would it be?",
            "Small wins matter most on heavy days. What is one low-effort, high-reward task?"
        ]
    else:
        tone = "🌧️ Tough day. Let's move gently."
        prompts = [
            "What do you need more than anything today — rest, space, or kindness?",
            "If today had a color, what would it be? Why?",
            "What is one way you can show yourself grace today?"
        ]

    prompt = random.choice(prompts)
    return f"{tone}\n\n🧠 Reflective Prompt: {prompt}"
