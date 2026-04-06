import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
import sys
import random
import joblib
from scipy import sparse

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from utils.similarity import calculate_cosine_similarity
    from embeddings.word2vec import get_sentence_vector
except ImportError:
    pass

# ─────────────────────────────────────────────────────────────────
# Rich Intent Response Bank
# The dataset only contains generic bot placeholders, so we build
# a comprehensive, curated response bank keyed by intent.
# Each intent has multiple responses to avoid repetition.
# ─────────────────────────────────────────────────────────────────

INTENT_RESPONSES = {
    "greeting": [
        "Hey there! 👋 How can I help you today?",
        "Hello! Great to see you. What's on your mind?",
        "Hi! I'm your AI assistant — ask me anything!",
        "Hey! What would you like to talk about today?",
    ],
    "farewell": [
        "Goodbye! It was great chatting with you. Take care! 👋",
        "See you later! Don't hesitate to come back anytime.",
        "Bye for now! Have an amazing day ahead!",
        "Take care! I'll be here whenever you need me.",
    ],
    "shopping": [
        "Great question! For the best deals, try comparing prices on platforms like Amazon, Flipkart, or use a price-tracking tool like CamelCamelCamel. What are you looking to buy?",
        "Smart shopping tip: Always check for coupon codes before checkout, read reviews, and compare across at least 3 stores. What product are you interested in?",
        "I'd recommend making a wishlist and waiting for seasonal sales like Black Friday or Prime Day for the biggest discounts. Need help finding something specific?",
        "For electronics, check review sites like RTINGS or Tom's Hardware before purchasing. For clothes, measure yourself and check the size chart. What are you shopping for?",
    ],
    "ai": [
        "AI (Artificial Intelligence) is the simulation of human intelligence by machines. It includes sub-fields like Machine Learning, Deep Learning, NLP, and Computer Vision. Modern AI systems like GPT and BERT use transformer architectures trained on massive datasets. What aspect interests you most?",
        "Large Language Models (LLMs) work by predicting the next token in a sequence. They're trained on billions of parameters using transformer architectures with self-attention mechanisms. Want to know more about how they work?",
        "AI is revolutionizing industries from healthcare (medical imaging diagnosis) to finance (fraud detection) to transportation (self-driving cars). The key branches are: supervised learning, unsupervised learning, and reinforcement learning. What would you like to explore?",
        "Some exciting AI developments include: GPT-4 for text generation, DALL-E for image creation, AlphaFold for protein structure prediction, and autonomous driving systems. Which area fascinates you?",
    ],
    "ml": [
        "Machine Learning is a subset of AI where systems learn patterns from data without being explicitly programmed. The three main types are: Supervised Learning (labeled data), Unsupervised Learning (unlabeled data), and Reinforcement Learning (reward-based). Want to dive deeper into any of these?",
        "Key ML algorithms include: Linear Regression, Decision Trees, Random Forests, SVM, K-Means Clustering, and Neural Networks. The choice depends on your data type and problem. What are you working on?",
        "To get started with ML: 1) Learn Python + NumPy/Pandas, 2) Study statistics fundamentals, 3) Practice with scikit-learn, 4) Move to deep learning with TensorFlow/PyTorch. Would you like a learning roadmap?",
        "The ML pipeline typically involves: Data Collection → Data Cleaning → Feature Engineering → Model Selection → Training → Evaluation → Deployment. Each step is critical for good results!",
    ],
    "dl": [
        "Deep Learning uses artificial neural networks with multiple layers to learn complex patterns. Key architectures include CNNs (for images), RNNs/LSTMs (for sequences), and Transformers (for language). What would you like to learn about?",
        "Popular deep learning frameworks include PyTorch (research-friendly) and TensorFlow/Keras (production-ready). For beginners, I'd recommend starting with Keras for its simplicity. Want a tutorial recommendation?",
        "Deep Learning breakthroughs: ResNet solved vanishing gradients with skip connections, Transformers revolutionized NLP with self-attention, and GANs can generate realistic images. Which interests you?",
    ],
    "coding": [
        "Good coding practices include: writing clean & readable code, using version control (Git), writing tests, following SOLID principles, and documenting your work. What language or concept do you need help with?",
        "For learning to code, I recommend: 1) Start with Python (beginner-friendly), 2) Build small projects, 3) Practice on LeetCode/HackerRank, 4) Read other people's code on GitHub. What's your current level?",
        "Some useful coding tips: Use meaningful variable names, keep functions short and focused, handle errors gracefully, and always write comments for complex logic. Need help with a specific problem?",
        "Popular programming languages by use case: Python (AI/Data Science), JavaScript (Web), Java (Enterprise), C++ (Systems/Games), Rust (Systems/Safety), Go (Cloud/Backend). What are you building?",
    ],
    "coding_errors": [
        "Debugging tips: 1) Read the error message carefully — it usually tells you the line and type of error. 2) Use print statements or a debugger. 3) Google the exact error message. 4) Check Stack Overflow. What error are you seeing?",
        "Common coding errors: SyntaxError (typo/missing bracket), TypeError (wrong data type), IndexError (accessing invalid index), KeyError (missing dictionary key), and ImportError (missing module). Which one are you facing?",
        "When you hit a bug: isolate the problem by commenting out code sections, test with simple inputs first, and check your assumptions about variable values. Can you share the error message?",
    ],
    "habits": [
        "Building good habits takes consistency! The 21/90 rule says: commit to a goal for 21 days to make it a habit, and 90 days to make it a lifestyle. Start with tiny habits — even 2 minutes a day counts. What habit are you trying to build?",
        "James Clear's 'Atomic Habits' framework: 1) Make it obvious (set reminders), 2) Make it attractive (pair with something you enjoy), 3) Make it easy (reduce friction), 4) Make it satisfying (track progress). Which step do you struggle with?",
        "Top habits of successful people: morning routines, daily exercise, reading 30 min/day, journaling, setting clear goals, and practicing gratitude. Start with one and build from there!",
    ],
    "fitness": [
        "A balanced fitness routine includes: 3-4 days of strength training, 2-3 days of cardio, flexibility work, and adequate rest days. Nutrition is equally important — aim for sufficient protein (0.8-1g per lb of body weight). What are your fitness goals?",
        "For beginners: Start with bodyweight exercises (push-ups, squats, lunges, planks), walk 30 minutes daily, and gradually increase intensity. Consistency beats intensity! What's your current fitness level?",
        "Key fitness tips: 1) Warm up before every workout, 2) Focus on form over weight, 3) Progressive overload is key for growth, 4) Sleep 7-9 hours for recovery, 5) Stay hydrated. Need a workout plan?",
    ],
    "health": [
        "Key health fundamentals: drink 8 glasses of water daily, sleep 7-9 hours, eat plenty of fruits and vegetables, exercise regularly, and manage stress through meditation or hobbies. What specific health topic interests you?",
        "Mental health is just as important as physical health! Practices like mindfulness meditation, regular exercise, social connections, and limiting screen time can significantly improve your well-being. Need specific advice?",
        "Preventive health tips: get regular check-ups, maintain a balanced diet, stay physically active, avoid smoking/excessive alcohol, practice good hygiene, and manage stress effectively. What area concerns you?",
    ],
    "food": [
        "Nutrition basics: fill half your plate with vegetables, a quarter with lean protein, and a quarter with whole grains. Don't forget healthy fats from nuts, avocados, and olive oil! Looking for specific recipes or meal plans?",
        "Easy healthy meals: overnight oats for breakfast, grain bowls with roasted veggies for lunch, and stir-fries for dinner. Meal prepping on Sundays can save you tons of time during the week! What cuisine do you enjoy?",
        "Food tip: cooking at home is healthier and cheaper than eating out. Start with simple recipes and build your skills. YouTube channels like Basics with Babish are great for learning. What dish would you like to make?",
    ],
    "books": [
        "Must-read books by category: Fiction — '1984', 'To Kill a Mockingbird'. Self-help — 'Atomic Habits', 'Deep Work'. Tech — 'Clean Code', 'Designing Data-Intensive Applications'. Business — 'Zero to One', 'The Lean Startup'. What genre interests you?",
        "Reading tips: set a daily reading goal (even 10 pages), try audiobooks during commutes, join a book club for accountability, and keep a reading journal. What was the last book you enjoyed?",
        "For personal development: 'Mindset' by Carol Dweck, 'The 7 Habits of Highly Effective People' by Stephen Covey, and 'Thinking, Fast and Slow' by Daniel Kahneman are game-changers!",
    ],
    "music": [
        "Music has been shown to improve mood, reduce stress, and boost productivity! Different genres work for different tasks — classical/lo-fi for studying, upbeat pop for workouts, and jazz for relaxation. What music do you enjoy?",
        "Want to learn an instrument? Guitar and ukulele are great for beginners — you can learn basic chords in a week! Piano is excellent for understanding music theory. Apps like Yousician and Simply Piano can help. Interested?",
        "Fun music fact: listening to music releases dopamine in the brain, similar to eating food or exercising. Creating playlists for different moods can help regulate your emotions throughout the day!",
    ],
    "career": [
        "Career growth tips: 1) Continuously learn new skills, 2) Build a strong network, 3) Seek mentorship, 4) Document your achievements, 5) Don't be afraid to negotiate your salary. Where are you in your career journey?",
        "For career transitions: identify your transferable skills, take online courses to fill gaps (Coursera, Udemy), build a portfolio showcasing your work, and leverage LinkedIn for networking. What field interests you?",
        "Hot career fields in 2026: AI/ML Engineering, Cloud Architecture, Cybersecurity, Data Science, UX Design, and Product Management. Many offer remote work options. Which one catches your eye?",
    ],
    "interview": [
        "Top interview tips: 1) Research the company thoroughly, 2) Practice STAR method for behavioral questions (Situation, Task, Action, Result), 3) Prepare 3-5 thoughtful questions to ask, 4) Follow up with a thank-you email within 24 hours. What type of interview are you preparing for?",
        "Common interview questions and how to answer them: 'Tell me about yourself' — give a 2-min professional summary. 'Why this company?' — show you've researched them. 'Biggest weakness?' — pick a real one and show how you're improving. Need practice?",
        "Technical interview prep: 1) Review data structures and algorithms, 2) Practice on LeetCode (start with Easy), 3) Do mock interviews on Pramp, 4) Study system design basics. The key is consistent practice over 4-6 weeks!",
    ],
    "resume": [
        "Resume tips: 1) Keep it to 1-2 pages, 2) Use action verbs ('Led', 'Built', 'Increased'), 3) Quantify achievements ('Increased sales by 25%'), 4) Tailor it for each job application, 5) Use a clean, ATS-friendly format. Need specific help?",
        "Key resume sections: Contact Info, Professional Summary (2-3 lines), Work Experience (reverse chronological), Skills (technical + soft), Education, and optional sections like Projects or Certifications. What part do you need help with?",
        "Common resume mistakes to avoid: typos/grammar errors, generic objective statements, irrelevant work experience, inconsistent formatting, and missing keywords from the job description. Want me to review yours?",
    ],
    "salary": [
        "Salary negotiation tips: 1) Research market rates on Glassdoor/Levels.fyi, 2) Let the employer make the first offer, 3) Negotiate total compensation (base + bonus + equity + benefits), 4) Practice your pitch beforehand. What role are you negotiating for?",
        "Average tech salaries in 2026 vary widely: Junior Dev ($60-90K), Senior Dev ($120-180K), Staff Engineer ($180-280K), ML Engineer ($130-200K). Location, company size, and skills matter a lot. What's your background?",
        "When discussing salary: focus on the value you bring, cite specific achievements with numbers, have a target range (not a single number), and be willing to walk away if the offer doesn't meet your minimum. Need coaching?",
    ],
    "weather": [
        "I don't have access to real-time weather data, but I can suggest great weather apps! Try: Weather.com, AccuWeather, or your phone's built-in weather app for accurate local forecasts. What location are you interested in?",
        "General weather tip: always check the forecast before heading out, especially for outdoor activities. Layer your clothing so you can adapt to temperature changes throughout the day!",
        "Fun weather fact: the difference between weather and climate is time — weather is short-term atmospheric conditions, while climate is the average weather pattern over 30+ years!",
    ],
    "travel": [
        "Travel planning tips: 1) Book flights 6-8 weeks in advance for best prices, 2) Use Google Flights for fare tracking, 3) Consider shoulder season for fewer crowds and lower prices, 4) Always get travel insurance. Where are you thinking of going?",
        "Budget travel hacks: use hostel booking sites, eat where locals eat, take public transportation, visit free attractions, and travel during off-peak seasons. You can explore amazing places without breaking the bank!",
        "Must-have travel apps: Google Maps (offline maps), Google Translate (camera translation), Booking.com (accommodation), Rome2Rio (transport routes), and XE Currency (exchange rates). Planning a trip?",
    ],
    "finance": [
        "Personal finance basics: 1) Follow the 50/30/20 rule (needs/wants/savings), 2) Build an emergency fund (3-6 months of expenses), 3) Pay off high-interest debt first, 4) Start investing early — even small amounts compound over time. What's your financial question?",
        "Investment options for beginners: index funds (low risk, diversified), ETFs (flexible trading), fixed deposits (guaranteed returns), and PPF/retirement accounts (tax benefits). Start with what you understand and diversify over time!",
        "Money-saving tips: track every expense for a month, cancel unused subscriptions, cook more at home, automate your savings, and use the 24-hour rule before impulse purchases. Need a budgeting template?",
    ],
    "business": [
        "Starting a business? Key steps: 1) Validate your idea (talk to potential customers), 2) Create a lean business plan, 3) Build an MVP (Minimum Viable Product), 4) Test and iterate based on feedback, 5) Scale what works. What's your business idea?",
        "Business fundamentals: understand your target market, define your value proposition, keep overhead low initially, focus on customer acquisition, and track key metrics (CAC, LTV, churn rate). What stage is your business at?",
        "Top business books I'd recommend: 'The Lean Startup' by Eric Ries, 'Zero to One' by Peter Thiel, 'Good to Great' by Jim Collins, and '$100M Offers' by Alex Hormozi. Want specific advice?",
    ],
    "marketing": [
        "Digital marketing essentials: SEO (Search Engine Optimization), content marketing (blogs/videos), social media marketing, email marketing, and paid ads (Google/Meta). The best strategy depends on your audience and budget. What are you marketing?",
        "Marketing tips: 1) Know your audience deeply, 2) Create valuable content consistently, 3) Use data to measure what works, 4) Build an email list (your most valuable asset), 5) Focus on one channel before expanding. Need a strategy?",
        "Social media marketing: post consistently, engage with your audience, use stories/reels for visibility, collaborate with micro-influencers, and analyze your metrics weekly. Which platform are you focusing on?",
    ],
    "philosophy": [
        "Philosophy tackles life's biggest questions: What is consciousness? What makes an action moral? Does free will exist? Great starting points: Plato's 'Republic', Marcus Aurelius' 'Meditations', and Sartre's 'Existentialism is a Humanism'. What philosophical question interests you?",
        "Major philosophical schools: Stoicism (control what you can), Existentialism (create your own meaning), Utilitarianism (maximize overall happiness), and Absurdism (embrace life's lack of inherent meaning). Which resonates with you?",
        "A thought-provoking question: If you could know the absolute truth about one thing, what would you want to know? Philosophy is about asking better questions, not always finding definitive answers!",
    ],
    "history": [
        "History is full of fascinating stories! Key turning points: the Agricultural Revolution, the fall of Rome, the Renaissance, the Industrial Revolution, and the Digital Age. Each fundamentally changed how humans live. Which era interests you?",
        "Learning from history: 'Those who cannot remember the past are condemned to repeat it' — George Santayana. Understanding historical patterns helps us make better decisions today. What historical event are you curious about?",
        "Interesting history resources: 'Sapiens' by Yuval Noah Harari (big picture), Dan Carlin's 'Hardcore History' podcast (deep dives), and Crash Course History on YouTube (quick overviews). Want recommendations for a specific topic?",
    ],
    "science": [
        "Science is all about understanding the natural world through observation and experimentation! Major branches: Physics (fundamental forces), Chemistry (matter and reactions), Biology (life), Astronomy (space), and Earth Sciences. What fascinates you?",
        "Cool science facts: neutron stars are so dense that a teaspoon would weigh 6 billion tons; your body has more bacteria cells than human cells; and light from the Sun takes 8 minutes to reach Earth! Want more?",
        "The scientific method: 1) Observe, 2) Question, 3) Hypothesize, 4) Experiment, 5) Analyze, 6) Conclude. This systematic approach has driven every major discovery in human history!",
    ],
    "technology": [
        "Tech trends in 2026: Generative AI, quantum computing advances, edge computing, sustainable tech, Web3 evolution, and autonomous systems. The pace of innovation keeps accelerating! What tech topic interests you?",
        "Useful tech skills to learn: programming (Python/JavaScript), cloud computing (AWS/Azure), data analysis, cybersecurity basics, and AI/ML fundamentals. These are in high demand across industries. Want a learning path?",
        "Technology tip: stay updated by following tech news (TechCrunch, The Verge, Hacker News), listening to tech podcasts, and experimenting with new tools. The best way to learn tech is by building things!",
    ],
    "security": [
        "Online security essentials: 1) Use strong, unique passwords (password manager recommended), 2) Enable 2-factor authentication everywhere, 3) Keep software updated, 4) Be cautious of phishing emails, 5) Use a VPN on public WiFi. What security concern do you have?",
        "Cybersecurity tips: never share passwords, verify sender emails before clicking links, regularly backup your data, use antivirus software, and be careful with public WiFi. Stay safe online!",
        "Data privacy matters: review app permissions regularly, use encrypted messaging apps, be mindful of what you share on social media, and read privacy policies. Want specific security advice?",
    ],
    "emotions": [
        "It's completely normal to feel a range of emotions! If you're feeling down: try talking to someone you trust, go for a walk, practice deep breathing, journal your thoughts, or listen to uplifting music. Remember, tough times are temporary. How are you feeling right now?",
        "Emotional wellness tips: acknowledge your feelings without judgment, practice mindfulness, maintain social connections, set healthy boundaries, engage in hobbies you enjoy, and don't hesitate to seek professional help if needed. I'm here to listen!",
        "A helpful perspective: emotions are signals, not commands. Feeling anxious before a presentation? That's your body preparing you. Feeling sad? It means something matters to you. Understanding your emotions gives you power over them. Want to talk more?",
    ],
    "sleep": [
        "Better sleep tips: 1) Keep a consistent sleep schedule, 2) Avoid screens 1 hour before bed, 3) Keep your room cool and dark, 4) Avoid caffeine after 2 PM, 5) Try relaxation techniques like deep breathing or meditation. What's disrupting your sleep?",
        "The science of sleep: adults need 7-9 hours per night. Sleep cycles last ~90 minutes (light sleep → deep sleep → REM). Waking at the end of a cycle feels better. Try a sleep calculator app to time your alarm!",
        "If you can't fall asleep: try the 4-7-8 breathing technique (inhale 4 sec, hold 7 sec, exhale 8 sec), progressive muscle relaxation, or a boring audiobook. Avoid lying in bed awake for more than 20 minutes. Need more tips?",
    ],
    "motivation": [
        "You've got this! 💪 Remember: every expert was once a beginner. Progress isn't always visible day-to-day, but looking back you'll see how far you've come. What goal are you working towards?",
        "Powerful motivation hack: don't wait for motivation — start small and motivation will follow. The hardest part is beginning. Set a timer for just 5 minutes and take that first step!",
        "Motivation fades, but discipline endures. Build systems instead of relying on willpower: 1) Set clear goals, 2) Break them into tiny steps, 3) Track progress daily, 4) Celebrate small wins. What's your current challenge?",
    ],
    "motivation_strong": [
        "Winners aren't people who never fail — they're people who never quit! Every setback is a setup for a comeback. You have the strength within you. KEEP GOING! 🔥",
        "The difference between where you are and where you want to be is the work you're willing to put in TODAY. No more excuses. Take massive action NOW!",
        "Remember: diamonds are made under pressure. Your struggles are shaping you into something extraordinary. Stay focused, stay hungry, and NEVER stop believing in yourself! 💎",
    ],
    "motivation_daily": [
        "Daily motivation: 'The only way to do great work is to love what you do' — Steve Jobs. Make today count by focusing on what matters most to you!",
        "Good morning! Here's your daily boost: small consistent actions lead to massive results over time. What's one thing you can accomplish today that your future self will thank you for?",
        "Today is full of potential! Set 3 micro-goals you can achieve by tonight. Crossing them off will give you momentum for tomorrow. You're making progress even when it doesn't feel like it! ✨",
    ],
    "college": [
        "College success tips: attend classes consistently, form study groups, visit professors during office hours, start assignments early, and build a portfolio alongside your degree. Which area do you need most help with?",
        "Engineering student tips: focus on problem-solving skills over memorization, work on hands-on projects, participate in hackathons, learn Git and at least one programming language well, and do internships. What's your major?",
        "Making the most of college: balance academics with extracurriculars, network with seniors and alumni, contribute to open-source projects or research, and develop communication skills. These matter as much as GPA!",
    ],
    "study": [
        "Effective study techniques backed by science: 1) Spaced repetition (review material at increasing intervals), 2) Active recall (test yourself instead of re-reading), 3) Pomodoro technique (25 min focus, 5 min break), 4) Teach what you learn. What are you studying?",
        "Study environment matters: find a quiet, well-lit space; silence your phone; use noise-cancelling headphones or lo-fi music; keep water nearby; and organize your materials before starting. How's your study routine?",
        "Avoid these study mistakes: passive re-reading, highlighting everything, cramming the night before, and multitasking. Instead: make flashcards, practice problems, summarize in your own words, and space out your sessions!",
    ],
    "education": [
        "Education is the most powerful tool you have! Whether it's formal schooling, online courses (Coursera, edX, Khan Academy), or self-study — continuous learning is the key to success. What subject are you focusing on?",
        "Free learning resources: Khan Academy (foundations), MIT OpenCourseWare (advanced), YouTube (tutorials), freeCodeCamp (coding), and your local library! Knowledge has never been more accessible. What do you want to learn?",
        "The future of education is personalized and accessible. AI tutors, interactive simulations, and project-based learning are transforming how we learn. What excites you most about learning?",
    ],
    "entertainment": [
        "Looking for entertainment? Here are some ideas: binge a highly-rated series, start a new video game, try a new hobby (painting, cooking, photography), explore podcasts, or have a movie marathon night! What type of entertainment do you enjoy?",
        "Top-rated shows to watch: Breaking Bad, Stranger Things, The Last of Us, Arcane, and Succession. For movies: Everything Everywhere All at Once, Oppenheimer, and Dune. What genre do you prefer?",
        "Fun activities for free: explore a local park, have a game night with friends, try a new recipe, start a journal, listen to a podcast, or learn to draw on YouTube. Entertainment doesn't have to be expensive!",
    ],
    "gaming": [
        "Gaming in 2026: exciting titles across PC, console, and mobile! Key trends include AI-powered NPCs, cloud gaming (Xbox Cloud, GeForce NOW), and VR experiences. What platform do you game on?",
        "Gaming tips: take regular breaks (20-20-20 rule for eye health), stay hydrated, join gaming communities for multiplayer fun, and try different genres to find what you love. What games are you into?",
        "Want to start game development? Try Unity (C#) or Godot (GDScript) for beginners. Start with a simple 2D game, follow tutorials, and join game jam events for practice. Interested?",
    ],
    "sports": [
        "Sports are great for physical and mental health! Popular sports to try: running (free and anywhere), swimming (low-impact), basketball (team-based), tennis (social), or rock climbing (adventure). What sports interest you?",
        "Sports tip: find an activity you genuinely enjoy — you're much more likely to stick with it long-term. Try a few different things, join local clubs or communities, and don't worry about being perfect from day one!",
        "Watching sports can be exciting! Follow leagues, join fantasy sports for deeper engagement, and use stats/analytics to understand the strategy behind the games. Which sport do you follow?",
    ],
    "productivity": [
        "Productivity boosters: 1) Time-blocking (schedule deep work sessions), 2) Eat the frog (hardest task first), 3) Two-minute rule (if it takes <2 min, do it now), 4) Batch similar tasks together, 5) Limit meetings and context switches. What's your productivity challenge?",
        "Best productivity tools: Notion (all-in-one workspace), Todoist (task management), Toggl (time tracking), Focus@Will (concentration music), and Forest (phone detox). Which area needs improvement?",
        "The 80/20 principle: 80% of your results come from 20% of your efforts. Identify your highest-impact activities and protect time for them. Saying 'no' to unimportant things is a superpower!",
    ],
    "projects": [
        "Great project ideas by skill level — Beginner: to-do app, weather app, portfolio site. Intermediate: chat app, expense tracker, blog platform. Advanced: ML model deployment, real-time collaboration tool, game engine. What's your skill level?",
        "Project management tips: 1) Define clear scope, 2) Break into milestones, 3) Use Git for version control, 4) Write documentation as you go, 5) Get feedback early and often. What project are you working on?",
        "The best way to learn is by building! Pick a project that solves a problem you have, use technologies you want to learn, and share it on GitHub. Employers love seeing real projects. Need project ideas?",
    ],
    "datascience": [
        "Data Science roadmap: 1) Learn Python + SQL, 2) Study statistics and probability, 3) Master Pandas, NumPy, and Matplotlib, 4) Learn ML with scikit-learn, 5) Practice with Kaggle competitions. Want detailed resources?",
        "A data scientist's toolkit: Jupyter Notebooks (exploration), Pandas (data wrangling), Matplotlib/Seaborn (visualization), scikit-learn (ML), and Tableau/Power BI (dashboards). What aspect are you learning?",
        "Data Science career tip: build a strong portfolio with 3-5 end-to-end projects on Kaggle or GitHub, create a blog explaining your analyses, and network on LinkedIn. Storytelling with data is the most underrated skill!",
    ],
    "cloud": [
        "Cloud computing essentials: the big three are AWS (market leader), Azure (enterprise-focused), and GCP (great for AI/ML). Start with one platform and learn: compute (EC2/VMs), storage (S3/Blob), and databases. Which interests you?",
        "Cloud certifications worth getting: AWS Solutions Architect, Azure Administrator, or Google Cloud Professional. These can significantly boost your career and validate your skills. Planning to get certified?",
        "Cloud benefits: scalability, cost-efficiency (pay-as-you-go), global reach, reliability, and security. It's the backbone of modern tech — from Netflix to Spotify to most startups. Want to learn the basics?",
    ],
    "networking": [
        "Professional networking tips: 1) Optimize your LinkedIn profile, 2) Attend industry events/meetups, 3) Offer value before asking for help, 4) Follow up after meetings, 5) Join relevant online communities. Looking for networking advice?",
        "Computer networking basics: understand TCP/IP, DNS, HTTP/HTTPS, firewalls, routers, and switches. For deeper knowledge, explore subnetting, VLANs, and network security. Which type of networking — professional or technical?",
        "Building genuine connections: be curious about others, ask thoughtful questions, share your knowledge freely, and maintain relationships even when you don't need anything. The best opportunities come through networks!",
    ],
    "communication": [
        "Effective communication skills: 1) Listen actively (don't just wait to talk), 2) Be clear and concise, 3) Adapt to your audience, 4) Use storytelling to make points memorable, 5) Ask open-ended questions. What communication area do you want to improve?",
        "Public speaking tips: practice out loud, structure your talk (hook → main points → conclusion), make eye contact, use pauses for emphasis, and remember — nervousness means you care! Have a presentation coming up?",
        "Written communication: use short paragraphs, lead with the key point, avoid jargon, proofread before sending, and consider your reader's perspective. Whether it's emails, reports, or messages — clarity is king!",
    ],
    "relationship": [
        "Healthy relationship foundations: trust, communication, respect, and shared values. No relationship is perfect — what matters is how you handle conflicts and support each other's growth. What aspect would you like to discuss?",
        "Relationship tip: the quality of your relationships depends on the quality of your conversations. Practice active listening, express appreciation regularly, and address issues before they become resentments. Need specific advice?",
        "Self-love is the foundation of all good relationships! Take care of your mental health, set healthy boundaries, know your worth, and don't settle just because you're afraid of being alone. How can I help?",
    ],
    "psychology": [
        "Psychology insights: cognitive biases shape our decisions more than we realize — confirmation bias, anchoring effect, and the Dunning-Kruger effect are just a few. Understanding them helps you make better choices! What psychology topic interests you?",
        "Positive psychology practices: gratitude journaling, flow state activities, acts of kindness, meditation, and cultivating a growth mindset. These are scientifically proven to increase well-being! Want to try any?",
        "Interesting psychology fact: it takes about 66 days (not 21) to form a new habit, according to research from University College London. The timeline varies based on habit complexity and individual differences!",
    ],
    "quotes": [
        "'The only limit to our realization of tomorrow is our doubts of today.' — Franklin D. Roosevelt. What kind of quotes inspire you? I can share more!",
        "'In the middle of difficulty lies opportunity.' — Albert Einstein. Whether you need motivational, philosophical, or funny quotes, I've got you covered!",
        "'Be yourself; everyone else is already taken.' — Oscar Wilde. Quotes can be powerful reminders of what matters most. Want quotes on a specific topic?",
    ],
    "news": [
        "For reliable news, I recommend: Reuters and AP News (objective reporting), BBC/NPR (broad coverage), and topic-specific outlets for your interests. Always cross-reference important stories across multiple sources!",
        "Media literacy tip: check the source, look for primary sources, be aware of headlines designed for clicks, distinguish between news and opinion, and be skeptical of stories that seem too outrageous. Stay curious and critical!",
        "I don't have access to live news, but I can discuss current events topics, help you understand complex issues, or recommend trustworthy news sources for staying informed. What topic are you interested in?",
    ],
    "geography": [
        "Geography is fascinating! From the deepest point on Earth (Mariana Trench at ~36,000 ft) to the tallest (Mt. Everest at 29,032 ft), our planet is full of extremes. What geographical topic interests you?",
        "Geography fun facts: Russia spans 11 time zones, Africa contains 54 countries, the Sahara Desert is roughly the size of the US, and Indonesia has over 17,000 islands! Want to learn about a specific region?",
        "Understanding geography helps you understand politics, culture, economics, and climate. Tools like Google Earth and maps make exploration easy from anywhere. What part of the world fascinates you?",
    ],
    "android": [
        "Android development: Start with Kotlin (official language), learn Android Studio IDE, understand Activities/Fragments/ViewModels, and use Jetpack Compose for modern UI. Google's official docs are excellent! Building an app?",
        "Useful Android tips: clear cache regularly for better performance, manage app permissions, use Digital Wellbeing to track screen time, and explore developer options for advanced settings. What do you need help with?",
        "Top Android development resources: Google's Android Developers site, Udacity's Android courses, Philipp Lackner on YouTube, and the official Kotlin documentation. What's your experience level?",
    ],
    "ios": [
        "iOS development: Learn Swift (Apple's language), master Xcode IDE, understand SwiftUI for modern UIs, and study design principles from Apple's Human Interface Guidelines. Planning to build an iOS app?",
        "iPhone tips: manage storage by offloading unused apps, use Focus modes to reduce distractions, enable iCloud backup, and explore Shortcuts for automation. What iOS topic interests you?",
        "App Store publishing: you'll need an Apple Developer Account ($99/year), follow Apple's review guidelines, prepare screenshots and descriptions, and plan your app submission carefully. Need guidance?",
    ],
    "life": [
        "Life advice: focus on what you can control, invest in relationships, take care of your health, never stop learning, practice gratitude, and don't compare your journey to others. What's on your mind?",
        "A meaningful life isn't about having it all together — it's about learning, growing, and finding joy in the journey. Set goals that align with your values, not society's expectations. What matters most to you?",
        "Life is about balance: work hard but rest well, plan ahead but enjoy the present, be independent but nurture connections. No one has it all figured out — and that's perfectly okay! How can I help you today?",
    ],
    "general": [
        "That's an interesting topic! I'd love to help. Could you give me a bit more detail about what you'd like to know? The more specific your question, the better I can assist you!",
        "I'm here to help with all sorts of topics — from tech and career advice to health, productivity, and more. What would you like to explore?",
        "Great question! Let me do my best to help. Can you elaborate a little so I can give you the most useful answer?",
    ],
}


class ResponseGenerator:
    TFIDF_PATH = os.path.join(os.path.dirname(__file__), 'tfidf_vectorizer.joblib')
    TFIDF_MATRIX_PATH = os.path.join(os.path.dirname(__file__), 'tfidf_matrix.npz')
    DATASET_PATH = os.path.join(os.path.dirname(__file__), 'dataset.pkl')

    def __init__(self):
        self.dataset = None
        self.tfidf_vectorizer = TfidfVectorizer(
            ngram_range=(1, 3),    # Unigrams + bigrams + trigrams for richer patterns
            max_features=40000,
            min_df=2,
            sublinear_tf=True,
            norm='l2',
            # NOTE: No stop_words removal — user queries are short and
            # stripping common words like 'what', 'is', 'how' destroys matching.
        )
        self.tfidf_matrix = None
        self.is_trained = False
        self.w2v_corpus = None
        self.load_pretrained()
        
    def load_and_train(self, dataset_path: str):
        if not os.path.exists(dataset_path):
            print(f"Failed to load dataset at {dataset_path} for Response Generator.")
            return False
            
        # Load full dataset for better matching and accuracy
        df = pd.read_csv(dataset_path, nrows=25000)
        
        pairs = []
        if 'conversation_id' in df.columns and 'role' in df.columns and 'message' in df.columns:
            for _, group in df.groupby('conversation_id'):
                group = group.sort_values('turn')
                u_msg = None
                intent_val = 'general'
                for _, row in group.iterrows():
                    if row['role'] == 'user':
                        u_msg = str(row['message']).strip()
                        intent_val = str(row.get('intent', 'general'))
                    elif row['role'] == 'bot' and u_msg:
                        b_msg = str(row['message']).strip()
                        pairs.append({'User': u_msg, 'Chatbot': b_msg, 'Intent': intent_val})
                        u_msg = None 
            self.dataset = pd.DataFrame(pairs)
        else:
            self.dataset = df.iloc[:, [0, 1]].dropna().copy()
            self.dataset.columns = ['User', 'Chatbot']
            
        self.dataset['User'] = self.dataset['User'].astype(str).str.lower()
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.dataset['User'])
        self.is_trained = True
        self.save_pretrained()
        print(f"TF-IDF generator trained on {len(self.dataset)} user-bot pairs.")
        return True

    def save_pretrained(self):
        try:
            joblib.dump(self.tfidf_vectorizer, self.TFIDF_PATH)
            sparse.save_npz(self.TFIDF_MATRIX_PATH, self.tfidf_matrix)
            joblib.dump(self.dataset, self.DATASET_PATH)
            print("Saved TF-IDF model and dataset for fast startup.")
        except Exception as e:
            print("Failed to save pretrained model:", e)

    def load_pretrained(self):
        if os.path.exists(self.TFIDF_PATH) and os.path.exists(self.TFIDF_MATRIX_PATH) and os.path.exists(self.DATASET_PATH):
            try:
                self.tfidf_vectorizer = joblib.load(self.TFIDF_PATH)
                self.tfidf_matrix = sparse.load_npz(self.TFIDF_MATRIX_PATH)
                self.dataset = joblib.load(self.DATASET_PATH)
                self.is_trained = True
                print("Loaded TF-IDF model from saved files.")
            except Exception as e:
                print("Failed to load pretrained model:", e)
                self.is_trained = False

    # Keyword hints for fallback intent detection when model confidence is low
    KEYWORD_INTENT_MAP = {
        "ai": ["artificial intelligence", "ai", "neural network", "deep learning", "machine learning", "llm", "gpt", "chatgpt", "transformer"],
        "ml": ["machine learning", "ml ", "supervised", "unsupervised", "regression", "classification", "random forest"],
        "dl": ["deep learning", "cnn", "rnn", "lstm", "neural net"],
        "coding": ["coding", "programming", "python", "javascript", "java ", "code", "developer", "software"],
        "coding_errors": ["error", "bug", "debug", "traceback", "exception", "crash", "fix my"],
        "fitness": ["workout", "exercise", "gym", "lose weight", "weight loss", "diet", "muscle", "cardio", "bodybuilding"],
        "health": ["health", "doctor", "sick", "illness", "medicine", "disease", "symptom", "mental health"],
        "food": ["food", "recipe", "cook", "meal", "eat", "restaurant", "cuisine", "nutrition", "diet plan"],
        "books": ["book", "read", "novel", "author", "reading list", "literature"],
        "music": ["music", "song", "album", "artist", "guitar", "piano", "playlist", "concert"],
        "career": ["career", "job", "profession", "promotion", "work life"],
        "interview": ["interview", "hiring", "recruiter"],
        "resume": ["resume", "cv ", "curriculum vitae", "cover letter"],
        "salary": ["salary", "pay", "compensation", "negotiate", "raise"],
        "weather": ["weather", "rain", "temperature", "forecast", "sunny", "cloudy"],
        "travel": ["travel", "trip", "flight", "vacation", "destination", "tourism", "hotel"],
        "finance": ["finance", "invest", "stock", "budget", "save money", "bank", "crypto", "mutual fund"],
        "business": ["business", "startup", "entrepreneur", "company"],
        "marketing": ["marketing", "seo", "social media", "branding", "advertis"],
        "philosophy": ["philosophy", "meaning of life", "existential", "morality", "ethics", "consciousness"],
        "history": ["history", "ancient", "war", "civilization", "historical"],
        "science": ["science", "physics", "chemistry", "biology", "experiment", "atom", "molecule"],
        "technology": ["technology", "tech", "gadget", "innovation", "iot", "blockchain"],
        "security": ["security", "safe online", "password", "hacking", "phishing", "cyber", "privacy"],
        "emotions": ["sad", "happy", "angry", "depressed", "anxious", "lonely", "stressed", "feel ", "feeling"],
        "sleep": ["sleep", "insomnia", "nap", "rest", "tired", "fatigue"],
        "motivation": ["motivation", "motivate", "inspire", "give up", "don't quit", "keep going"],
        "habits": ["habit", "routine", "discipline", "consistency"],
        "college": ["college", "university", "campus", "engineering student", "semester", "gpa"],
        "study": ["study", "exam", "test prep", "homework", "assignment", "revision"],
        "education": ["education", "learn", "course", "tutorial", "teach", "school"],
        "entertainment": ["entertainment", "movie", "tv show", "series", "netflix", "anime"],
        "gaming": ["game", "gaming", "xbox", "playstation", "nintendo", "esports"],
        "sports": ["sports", "football", "cricket", "basketball", "soccer", "tennis", "athlete"],
        "productivity": ["productivity", "productive", "time management", "focus", "distraction"],
        "projects": ["project idea", "side project", "portfolio"],
        "datascience": ["data science", "data analysis", "pandas", "kaggle", "visualization"],
        "cloud": ["cloud", "aws", "azure", "gcp", "docker", "kubernetes", "devops"],
        "networking": ["networking", "linkedin", "connection", "meetup"],
        "communication": ["communication", "public speaking", "presentation", "email writing"],
        "relationship": ["relationship", "love", "dating", "partner", "marriage", "breakup"],
        "psychology": ["psychology", "cognitive", "behavior", "mindset", "bias"],
        "greeting": ["hello", "hi ", "hey", "good morning", "good evening", "what's up", "howdy"],
        "farewell": ["goodbye", "bye", "see you", "take care", "good night", "cya"],
    }

    def _detect_intent_by_keywords(self, user_input: str):
        """Fallback: detect intent using keyword matching when model confidence is low."""
        text = user_input.lower().strip()
        best_intent = None
        best_hits = 0
        for intent, keywords in self.KEYWORD_INTENT_MAP.items():
            hits = sum(1 for kw in keywords if kw in text)
            if hits > best_hits:
                best_hits = hits
                best_intent = intent
        return best_intent

    def _get_response_for_intent(self, intent: str, user_input: str):
        """Get a rich, contextual response based on the matched intent."""
        intent_lower = intent.lower().strip()
        
        if intent_lower in INTENT_RESPONSES:
            responses = INTENT_RESPONSES[intent_lower]
            # Use a hash of the user input to get a deterministic but varied response
            idx = hash(user_input.lower().strip()) % len(responses)
            return responses[idx]
        
        # Dynamic fallback for unknown intents
        return f"That's an interesting question about {intent}! I'd love to help. Could you tell me a bit more about what specifically you'd like to know?"
        
    def _fallback_response(self, user_input: str):
        """Fallback when models are not yet trained: keyword-driven intent response."""
        intent = self._detect_intent_by_keywords(user_input) or "general"
        reply = self._get_response_for_intent(intent, user_input)
        return reply, 0.0, intent

    def level_1_tfidf(self, user_input: str):
        """TF-IDF + Cosine Similarity — matches user input to training data, 
           then delivers a rich response based on the matched intent."""
        if not self.is_trained:
            return self._fallback_response(user_input)
            
        user_input_clean = user_input.lower().strip()
        user_vec = self.tfidf_vectorizer.transform([user_input_clean])
        similarities = cosine_similarity(user_vec, self.tfidf_matrix).flatten()
        
        best_idx = similarities.argmax()
        best_score = similarities[best_idx]
        
        best_match_user = str(self.dataset.iloc[best_idx]['User'])
        intent = str(self.dataset.iloc[best_idx].get('Intent', 'general'))
        
        reply = self._get_response_for_intent(intent, user_input)
        
        print(f"[DEBUG] TF-IDF Matched: '{best_match_user}' (Score: {best_score:.2f}) -> Intent: {intent}")
        return reply, float(best_score), intent
        
    def level_2_w2v(self, user_input: str):
        """Word2Vec Semantic Similarity — captures meaning even with different words."""
        if not self.is_trained:
            return self._fallback_response(user_input)
            
        user_vec = get_sentence_vector(user_input)
        if not np.any(user_vec):
            return self._get_response_for_intent("general", user_input), 0.0, "general"
            
        if self.w2v_corpus is None:
            self.w2v_corpus = np.array([get_sentence_vector(str(text)) for text in self.dataset['User']])
            
        similarities = cosine_similarity(user_vec.reshape(1, -1), self.w2v_corpus).flatten()
        best_idx = similarities.argmax()
        best_score = similarities[best_idx]
        
        best_match_user = str(self.dataset.iloc[best_idx]['User'])
        intent = str(self.dataset.iloc[best_idx].get('Intent', 'general'))
        
        reply = self._get_response_for_intent(intent, user_input)
        
        print(f"[DEBUG] W2V Matched: '{best_match_user}' (Score: {best_score:.2f}) -> Intent: {intent}")
        return reply, float(best_score), intent
        
    def level_3_hybrid(self, user_input: str):
        """Hybrid approach — combines TF-IDF precision with Word2Vec semantics."""
        if not self.is_trained:
            return self._fallback_response(user_input)
            
        # 1. First try exact keyword matching for high-confidence intents
        keyword_intent = self._detect_intent_by_keywords(user_input)
        if keyword_intent:
            return self._get_response_for_intent(keyword_intent, user_input), 1.0, keyword_intent
            
        # 2. Use ML models for semantic/conversational matching
        tfidf_resp, tfidf_score, tfidf_intent = self.level_1_tfidf(user_input)
        w2v_resp, w2v_score, w2v_intent = self.level_2_w2v(user_input)
        
        # If TF-IDF found a strong keyword match, trust it
        if tfidf_score > 0.35:
            return tfidf_resp, float(tfidf_score), tfidf_intent
            
        # If W2V found a strong semantic match, trust it
        if w2v_score > 0.5:
            return w2v_resp, float(w2v_score), w2v_intent
        
        # 3. Weighted hybrid score
        hybrid_score = (tfidf_score * 0.4) + (w2v_score * 0.6)
        
        if hybrid_score >= 0.1:
            # Use whichever method found the better match
            if tfidf_score >= w2v_score:
                return tfidf_resp, float(hybrid_score), tfidf_intent
            else:
                return w2v_resp, float(hybrid_score), w2v_intent
                
        # Final fallback
        return self._get_response_for_intent("general", user_input), float(hybrid_score), "general"

generator = ResponseGenerator()
