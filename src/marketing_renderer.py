"""
This file holds the beautiful HTML/CSS Structure.
The LLM only injects content into the {content_body} placeholder.
"""

def get_glass_styles():
    return """
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Outfit', sans-serif; background-color: #0f172a; color: white; overflow-x: hidden; }
        
        /* DYNAMIC BACKGROUND */
        .bg-glow {
            position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: -1;
            background: 
                radial-gradient(circle at 15% 50%, rgba(76, 29, 149, 0.4), transparent 25%),
                radial-gradient(circle at 85% 30%, rgba(236, 72, 153, 0.4), transparent 25%);
        }

        /* GLASSMORPHISM CARD */
        .glass-card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        }

        /* NEON BUTTON */
        .btn-neon {
            background: linear-gradient(45deg, #ec4899, #8b5cf6);
            border: none;
            color: white;
            padding: 12px 30px;
            border-radius: 50px;
            font-weight: bold;
            transition: all 0.3s ease;
            box-shadow: 0 0 15px rgba(236, 72, 153, 0.5);
        }
        .btn-neon:hover {
            transform: translateY(-2px);
            box-shadow: 0 0 25px rgba(139, 92, 246, 0.7);
        }

        /* ANIMATIONS */
        @keyframes float {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
            100% { transform: translateY(0px); }
        }
        .animate-float { animation: float 6s ease-in-out infinite; }
        
        .fade-in { animation: fadeIn 1.5s ease-out; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
    </style>
    """

def render_full_page(title: str, body_content: str) -> str:
    """
    Wraps the LLM-generated content in the beautiful template.
    """
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        {get_glass_styles()}
    </head>
    <body>
        <div class="bg-glow"></div>
        
        <!-- NAVIGATION -->
        <nav class="flex justify-between items-center p-6 glass-card m-4">
            <div class="text-2xl font-bold tracking-wider bg-clip-text text-transparent bg-gradient-to-r from-pink-500 to-violet-500">
                EVENT.AI
            </div>
            <button class="btn-neon text-sm">Pre-Register</button>
        </nav>

        <!-- DYNAMIC CONTENT FROM AGENT -->
        <main class="container mx-auto px-4 py-8 fade-in">
            {body_content}
        </main>

        <!-- FOOTER -->
        <footer class="text-center text-gray-500 py-10 mt-10 border-t border-gray-800">
            <p>Powered by Agentic Event Intelligence System &copy; 2024</p>
        </footer>
    </body>
    </html>
    """