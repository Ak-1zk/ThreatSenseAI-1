/**
 * AI Manager — ThreatSense AI
 * Backend-first API calls with Puter.js fallback.
 * Exact port of src/lib/ai-manager.ts
 */

const BACKEND_URL = "/api";

const aiManager = {
    /**
     * Chat with the AI.
     * @param {Array<{id:string, role:string, content:string}>} messages
     * @returns {Promise<{text: string}>}
     */
    async chat(messages) {
        const lastMessage = messages[messages.length - 1]?.content || "";
        const history = messages.slice(0, -1).map((m) => ({
            role: m.role === "user" ? "user" : "model",
            parts: [{ text: m.content }],
        }));

        try {
            console.log("🔵 [AIManager] Trying backend chat...");
            const res = await fetch(`${BACKEND_URL}/chat`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: lastMessage, history }),
            });

            if (!res.ok) throw new Error(`Backend returned ${res.status}`);
            const data = await res.json();
            return { text: data.reply || "I'm not sure how to respond." };
        } catch (err) {
            console.warn("⚠️ [AIManager] Backend chat failed, falling back to Puter.js:", err.message);
            return this._fallbackChat(messages);
        }
    },

    async _fallbackChat(messages) {
        try {
            const puterMessages = messages.map((m) => ({
                role: m.role,
                content: m.content,
            }));
            const text = await chatWithPuter(puterMessages);
            return { text };
        } catch (err) {
            console.error("❌ [AIManager] Puter.js chat also failed:", err);
            throw err;
        }
    },

    /**
     * Analyze text for security risks.
     * @param {string} text
     * @returns {Promise<Object>}
     */
    async analyze(text) {
        try {
            console.log("🔵 [AIManager] Trying backend analysis...");
            const res = await fetch(`${BACKEND_URL}/analyze`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: text }),
            });

            if (!res.ok) throw new Error(`Backend returned ${res.status}`);
            return await res.json();
        } catch (err) {
            console.warn("⚠️ [AIManager] Backend analysis failed, falling back to Puter.js:", err.message);
            return this._fallbackAnalyze(text);
        }
    },

    async _fallbackAnalyze(text) {
        try {
            return await analyzeWithPuter(text);
        } catch (err) {
            console.error("❌ [AIManager] Puter.js analysis also failed:", err);
            throw err;
        }
    },

    /**
     * Get the daily cybersecurity briefing.
     * @returns {Promise<string>}
     */
    async getBriefing() {
        try {
            console.log("🔵 [AIManager] Trying backend briefing...");
            const res = await fetch(`${BACKEND_URL}/daily-briefing`);
            if (!res.ok) throw new Error(`Backend returned ${res.status}`);
            const data = await res.json();
            return data.briefing || "Unable to fetch briefing.";
        } catch (err) {
            console.warn("⚠️ [AIManager] Backend briefing failed, falling back to Puter.js:", err.message);
            return this._fallbackBriefing();
        }
    },

    async _fallbackBriefing() {
        try {
            if (!window.puter) throw new Error("Puter.js not loaded");
            const response = await window.puter.ai.chat(
                [
                    {
                        role: "system",
                        content:
                            "You are a cybersecurity threat intelligence analyst. Provide a concise daily threat briefing in Markdown format with ### headings, **bold** keywords, and --- separators.",
                    },
                    {
                        role: "user",
                        content: `Give me today's cybersecurity threat briefing with the most important items.`,
                    },
                ],
                { model: "gpt-4o-mini" }
            );
            return response?.message?.content || "Unable to fetch briefing.";
        } catch (err) {
            console.error("❌ [AIManager] Puter.js briefing also failed:", err);
            throw err;
        }
    },

    /**
     * Analyze a QR code image for security risks.
     * @param {string} base64Image
     * @returns {Promise<Object>}
     */
    async analyzeQR(base64Image) {
        try {
            console.log("🔵 [AIManager] Trying backend QR analysis...");
            const res = await fetch(`${BACKEND_URL}/qr-scan`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ image: base64Image }),
            });

            if (!res.ok) throw new Error(`Backend returned ${res.status}`);
            return await res.json();
        } catch (err) {
            console.warn("⚠️ [AIManager] Backend QR analysis failed, falling back to Puter.js:", err.message);
            return this._fallbackAnalyzeQR(base64Image);
        }
    },

    async _fallbackAnalyzeQR(base64Image) {
        try {
            return await analyzeQRWithPuter(base64Image);
        } catch (err) {
            console.error("❌ [AIManager] Puter.js QR analysis also failed:", err);
            throw err;
        }
    },
};
