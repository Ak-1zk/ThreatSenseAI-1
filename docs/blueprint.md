# **App Name**: ThreatSense-AI Sentinel

## Core Features:

- URL Analyzer UI: User interface elements for inputting and analyzing URLs, including the URL input field, analyze button, and safety warning text.
- URL Risk Analysis: Analyzes URLs using Gemini to detect phishing patterns, suspicious keywords, and domain structure, returning a JSON object with classification, risk score, reasons, and recommendations. Uses a tool when analyzing urls to decide if context from previous analyses are useful.
- Rule-Based Fallback: Implements rule-based logic as a fallback when Gemini analysis fails, using keywords like 'login', 'verify', 'bank', etc., to classify URLs.
- Classification Badge: Displays a classification badge (GENUINE, SUSPICIOUS, or SCAM), risk score meter, reasons list, and recommendation box based on the URL analysis.
- Cyber Safety Assistant Chatbot: AI-powered chatbot that answers cybersecurity questions and provides explanations, leveraging Gemini. A tool can choose if previous URL was analyzed, use it in the response to enrich answers and offer context-aware assistance.
- Chatbot UI: User interface components for the chatbot, including chat history display and an input box with an ask button.
- Anonymous Usage: No database storage of user inputs to ensure user privacy and data security.

## Style Guidelines:

- Primary color: Deep scarlet (#C2255C) for a modern cybersecurity feel.
- Background color: Dark grey (#2A2A2A) for a professional, high-tech aesthetic.
- Accent color: Electric crimson (#FF4455) for interactive elements.
- Body and headline font: 'Inter' for a modern, objective, and neutral appearance.
- Code font: 'Source Code Pro' for displaying code snippets.
- Use a set of consistent, visually appealing icons to help illustrate safety and risks.
- Dashboard layout that supports responsive design to render appropriately in a full range of browser window sizes.
- Subtle transitions for UI feedback and engaging user interactions.