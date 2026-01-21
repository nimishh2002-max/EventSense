# --- PROMPT TEMPLATES ---

INFERENCE_PROMPT = """
You are an expert Event Planner. 
Analyze the event name: "{event_name}".
Infer the likely details. If ambiguous, make a conservative estimate based on standard university events.

Return strictly JSON:
{{
    "type": "Social | Academic | Fundraiser | Performance | Workshop",
    "estimated_attendees": integer,
    "is_outdoors": boolean,
    "duration_hours": integer,
    "vibes": "formal | casual | energetic | professional",
    "venue_requirements": ["stage", "projector", "open space", "tables"]
}}
"""

CLASSIFICATION_PROMPT = """
Given these event details: {event_details_json}

Generate 3-5 specific semantic search tags to find relevant safety rules and past memories in the database.
Focus on high-risk factors (e.g., "alcohol", "crowd control", "electrical", "late night", "outdoor weather").

Return strictly JSON:
{{
    "queries": ["tag1", "tag2", "tag3", "tag4"]
}}
"""

RISK_ANALYSIS_PROMPT = """
You are a University Risk Officer. Analyze this event plan against institutional rules and history.

Event Details:
{event_details_json}

Relevant Standard Operating Procedures (SOPs):
{sops_json}

Historical Lessons Learned (Memory):
{memories_json}

Task:
1. Check for specific SOP violations (e.g., capacity vs fire exits, noise rules).
2. Check if similar past failures might repeat based on the Memory Logs.
3. Assign a Risk Score (0-100). 
   - 0-20: Low Risk
   - 21-60: Medium Risk
   - 61-100: High Risk (Requires Intervention)

Return strictly JSON:
{{
    "score": integer,
    "level": "Low | Medium | High",
    "reasoning": "Clear explanation citing specific SOPs (e.g. 'Violates SOP-102') or Past Events (e.g. 'Repeat of 2023 failure').",
    "mitigation_plan": "A concrete step to reduce this risk."
}}
"""

# --- UPDATED MARKETING PROMPT (Content Only) ---
MARKETING_PROMPT = """
You are a Content Designer. 
The Event Name is: "{event_name}"
Context: {event_details_json}

Your goal is to generate HTML content blocks that will be injected into a High-End Glassmorphism Template.

Requirements:
1. **Hero Section:** A section with `class="text-center py-20"`. Include a massive `h1` (text-6xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-pink-400 to-purple-400) and a catchy `p` (text-xl text-gray-300 mb-8).
2. **Features Grid:** A `div` with `class="grid grid-cols-1 md:grid-cols-3 gap-8 my-16"`. Inside, create 3 "Feature Cards" using `class="glass-card p-8 hover:bg-white/10 transition duration-300"`. Use FontAwesome icons (e.g., `<i class="fas fa-music text-4xl mb-4 text-pink-500"></i>`) inside the cards.
3. **Details Section:** A centered `div` with date, time, and location details using `class="glass-card inline-block px-10 py-6"`.

Constraints:
- **DO NOT** write `<html>`, `<head>`, `<body>`, or `<style>` tags. The system adds those automatically.
- **DO NOT** use markdown backticks (```html). Just return the raw HTML divs.
- Use strictly Tailwind classes.
"""