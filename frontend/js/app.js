/**
 * App.js — ThreatSense AI Dashboard Orchestrator
 * Wires up: tabs, analysis, chatbot, daily briefing, header user info.
 */

(function () {
    /* ─────────────── State ─────────────── */
    const chatMessages = []; // { id, role, content, image? }
    let isBotReplying = false;
    let briefingFetched = false;
    let briefingLoading = false;
    let uploadedImage = null; // base64 string
    let recognition = null;
    let isListening = false;

    /* ─────────────── DOM Ready ─────────────── */
    auth.onAuthStateChanged((user) => {
        if (!user) return; // auth.js handles redirect
        document.getElementById('loading-overlay').classList.add('hidden');
        document.getElementById('app-shell').classList.remove('hidden');
        initHeader(user);
        initTabs();
        initAnalyzers();
        initChatbot();
        initBriefing();
    });

    /* ═══════════════════════════════════════
       HEADER
       ═══════════════════════════════════════ */
    function initHeader(user) {
        const area = document.getElementById('header-user-area');
        const initials = user.isAnonymous
            ? 'AN'
            : (user.email || '?').substring(0, 2).toUpperCase();
        const displayName = user.isAnonymous ? 'Anonymous User' : user.email;

        area.innerHTML = `
      <div class="header-user">
        <div class="avatar">${initials}</div>
        <span class="header-email">${displayName}</span>
      </div>
      <button id="btn-signout" class="btn btn-secondary btn-sm">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" x2="9" y1="12" y2="12"/></svg>
        Sign Out
      </button>
    `;
        document.getElementById('btn-signout').addEventListener('click', () => auth.signOut());
    }

    /* ═══════════════════════════════════════
       TABS
       ═══════════════════════════════════════ */
    function initTabs() {
        const triggers = document.querySelectorAll('.tab-trigger');
        triggers.forEach((btn) => {
            btn.addEventListener('click', () => {
                triggers.forEach((t) => t.classList.remove('active'));
                btn.classList.add('active');
                document.querySelectorAll('.tab-content').forEach((c) => c.classList.remove('active'));
                document.getElementById('tab-' + btn.dataset.tab).classList.add('active');
            });
        });
    }

    /* ═══════════════════════════════════════
       ANALYZERS
       ═══════════════════════════════════════ */
    function initAnalyzers() {
        // URL
        document.getElementById('url-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const input = document.getElementById('url-input');
            const errorEl = document.getElementById('url-error');
            errorEl.classList.add('hidden');

            const url = input.value.trim();
            if (!url) {
                errorEl.textContent = 'Please enter a URL.';
                errorEl.classList.remove('hidden');
                return;
            }
            try { new URL(url); } catch {
                errorEl.textContent = 'Please enter a valid URL. e.g. https://google.com';
                errorEl.classList.remove('hidden');
                return;
            }

            await runAnalysis(`Analyze this URL for security risks: ${url}`, 'url');
        });

        // Email
        document.getElementById('email-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const input = document.getElementById('email-content');
            const errorEl = document.getElementById('email-content-error');
            errorEl.classList.add('hidden');

            if (input.value.trim().length < 10) {
                errorEl.textContent = 'Please paste the content of the email.';
                errorEl.classList.remove('hidden');
                return;
            }

            await runAnalysis(
                `Analyze this email for phishing or scam indicators:\n\n${input.value.trim()}`,
                'email'
            );
        });

        // Message
        document.getElementById('message-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const input = document.getElementById('message-content');
            const errorEl = document.getElementById('message-content-error');
            errorEl.classList.add('hidden');

            if (input.value.trim().length < 10) {
                errorEl.textContent = 'Please paste the content of the message.';
                errorEl.classList.remove('hidden');
                return;
            }

            await runAnalysis(
                `Analyze this message for smishing or phishing indicators:\n\n${input.value.trim()}`,
                'message'
            );
        });

        // QR Code
        const qrInput = document.getElementById('qr-input');
        const qrPreviewContainer = document.getElementById('qr-preview-container');
        const qrPreviewImg = document.getElementById('qr-preview-img');
        
        if (qrInput) {
            qrInput.addEventListener('change', (e) => {
                const file = e.target.files[0];
                if (!file) {
                    qrPreviewContainer.classList.add('hidden');
                    return;
                }
                const reader = new FileReader();
                reader.onload = (ev) => {
                    qrPreviewImg.src = ev.target.result;
                    qrPreviewContainer.classList.remove('hidden');
                };
                reader.readAsDataURL(file);
            });
            
            document.getElementById('qr-form').addEventListener('submit', async (e) => {
                e.preventDefault();
                const errorEl = document.getElementById('qr-input-error');
                errorEl.classList.add('hidden');

                if (!qrPreviewImg.src || qrPreviewImg.src === window.location.href) {
                    errorEl.textContent = 'Please select a QR code image.';
                    errorEl.classList.remove('hidden');
                    return;
                }

                await runQRAnalysis(qrPreviewImg.src);
            });
        }
    }

    async function runAnalysis(prompt, type) {
        showResultLoading();
        disableAnalyzerForm(type, true);

        try {
            const result = await aiManager.analyze(prompt);
            showResultData(result, type);
        } catch (err) {
            console.error('Analysis failed:', err);
            showResultData(
                {
                    classification: 'SUSPICIOUS',
                    risk_score: 50,
                    reasons: ['Analysis could not be completed. Please try again.'],
                    recommendation: 'Unable to fully analyze. Exercise caution.',
                },
                type
            );
        } finally {
            disableAnalyzerForm(type, false);
        }
    }

    async function runQRAnalysis(base64Image) {
        showResultLoading();
        disableAnalyzerForm('qr', true);

        try {
            const result = await aiManager.analyzeQR(base64Image);
            showResultData(result, 'qr');
        } catch (err) {
            console.error('QR Analysis failed:', err);
            showResultData(
                {
                    classification: 'SUSPICIOUS',
                    risk_score: 50,
                    reasons: ['Analysis could not be completed. Please try again.'],
                    recommendation: 'Unable to fully analyze the QR code. Exercise caution.',
                },
                'qr'
            );
        } finally {
            disableAnalyzerForm('qr', false);
        }
    }

    function disableAnalyzerForm(type, disabled) {
        const formId = type === 'url' ? 'url-form' : type === 'email' ? 'email-form' : type === 'message' ? 'message-form' : 'qr-form';
        const form = document.getElementById(formId);
        form.querySelectorAll('input, textarea, button').forEach((el) => (el.disabled = disabled));

        const btnId = type === 'url' ? 'url-btn' : type === 'email' ? 'email-btn' : type === 'message' ? 'message-btn' : 'qr-btn';
        const btn = document.getElementById(btnId);
        if (disabled) {
            btn.innerHTML = '<span class="spinner"></span> Analyzing...';
        } else {
            const labels = { url: 'Analyze URL', email: 'Analyze Email', message: 'Analyze Message', qr: 'Analyze QR Code' };
            btn.textContent = labels[type] || 'Analyze';
        }
    }

    /* ── Result Rendering ── */
    function showResultLoading() {
        document.getElementById('result-placeholder').classList.add('hidden');
        document.getElementById('result-data').classList.add('hidden');
        document.getElementById('result-skeleton').classList.remove('hidden');
        document.getElementById('result-skeleton').style.display = 'flex';
    }

    function showResultData(analysis, type) {
        document.getElementById('result-skeleton').classList.add('hidden');
        document.getElementById('result-placeholder').classList.add('hidden');

        // Ensure classification matches risk score
        if (analysis.risk_score < 60) {
            analysis.classification = 'SAFE';
        } else if (analysis.risk_score < 80) {
            analysis.classification = 'SUSPICIOUS';
        } else {
            analysis.classification = 'DANGEROUS';
        }

        const container = document.getElementById('result-data');
        container.classList.remove('hidden');

        const badgeClass =
            analysis.classification === 'GENUINE' || analysis.classification === 'SAFE'
                ? 'badge-success'
                : analysis.classification === 'SUSPICIOUS'
                    ? 'badge-warning'
                    : 'badge-destructive';

        const headerIcon = getClassificationIcon(analysis.classification);
        const progressColor =
            analysis.risk_score >= 80
                ? 'hsl(var(--destructive))'
                : analysis.risk_score >= 60
                    ? 'hsl(var(--warning))'
                    : 'hsl(var(--success))';

        const reasonsHtml = (analysis.reasons || [])
            .map(
                (r) => `
      <li class="result-reason">
        <svg class="result-reason-icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="hsl(var(--primary))" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="m9 11 3 3L22 4"/></svg>
        <span>${escapeHtml(r)}</span>
      </li>`
            )
            .join('');

        container.innerHTML = `
      <div class="result-header">
        <div>
          <h2 class="text-2xl font-bold font-headline">Analysis Complete</h2>
          <p class="text-sm text-muted-foreground">Risk assessment for the provided ${type === 'qr' ? 'QR code' : type}.</p>
          ${analysis.decoded_content ? `<p class="text-sm text-muted-foreground" style="margin-top:0.5rem; word-break: break-all;"><strong>Decoded Content:</strong> ${escapeHtml(analysis.decoded_content)}</p>` : ''}
        </div>
        ${headerIcon}
      </div>
      <div class="result-body">
        <div class="result-classification">
          <h4 class="font-semibold">Classification</h4>
          <span class="badge ${badgeClass}">${escapeHtml(analysis.classification)}</span>
        </div>
        <div>
          <h4 class="font-semibold" style="margin-bottom:0.5rem;display:flex;align-items:center;gap:0.5rem;">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 14 4-4"/><path d="M3.34 19a10 10 0 1 1 17.32 0"/></svg>
            Risk Score: ${analysis.risk_score}/100
          </h4>
          <div class="progress-track">
            <div class="progress-fill" style="width:${analysis.risk_score}%;background:${progressColor};"></div>
          </div>
        </div>
        <div>
          <h4 class="font-semibold" style="margin-bottom:0.75rem;display:flex;align-items:center;gap:0.5rem;">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12h16"/><path d="M4 6h16"/><path d="M4 18h16"/><path d="m2 10 2 2-2 2"/><path d="m22 10-2 2 2 2"/></svg>
            Reasons
          </h4>
          <ul class="result-reasons">${reasonsHtml}</ul>
        </div>
        <div class="result-recommendation">
          <h4 class="font-semibold" style="margin-bottom:0.5rem;display:flex;align-items:center;gap:0.5rem;">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><line x1="12" x2="12" y1="8" y2="12"/><line x1="12" x2="12.01" y1="16" y2="16"/></svg>
            Recommendation
          </h4>
          <p>${escapeHtml(analysis.recommendation || '')}</p>
        </div>
      </div>
    `;
    }

    function getClassificationIcon(classification) {
        if (classification === 'GENUINE' || classification === 'SAFE') {
            return '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="hsl(var(--success))" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="m9 11 3 3L22 4"/></svg>';
        }
        if (classification === 'SUSPICIOUS') {
            return '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="hsl(var(--warning))" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg>';
        }
        return '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="hsl(var(--destructive))" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><line x1="12" x2="12" y1="8" y2="12"/><line x1="12" x2="12.01" y1="16" y2="16"/></svg>';
    }

    /* ═══════════════════════════════════════
       CHATBOT
       ═══════════════════════════════════════ */
    function initChatbot() {
        const form = document.getElementById('chat-form');
        const input = document.getElementById('chat-input');
        const btnUpload = document.getElementById('btn-upload');
        const btnMic = document.getElementById('btn-mic');
        const fileInput = document.getElementById('file-input');

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const text = input.value.trim();
            if (!text && !uploadedImage) return;
            if (isBotReplying) return;

            const userMsg = {
                id: Date.now().toString(),
                role: 'user',
                content: text || (uploadedImage ? '[Image uploaded]' : ''),
                image: uploadedImage || null,
            };

            chatMessages.push(userMsg);
            appendChatBubble(userMsg);
            input.value = '';
            clearImagePreview();

            isBotReplying = true;
            showTypingIndicator();

            try {
                const response = await aiManager.chat(
                    chatMessages.map((m) => ({ id: m.id, role: m.role, content: m.content }))
                );
                const botMsg = {
                    id: (Date.now() + 1).toString(),
                    role: 'assistant',
                    content: response.text,
                };
                chatMessages.push(botMsg);
                hideTypingIndicator();
                appendChatBubble(botMsg);
            } catch (err) {
                hideTypingIndicator();
                const errorMsg = {
                    id: (Date.now() + 1).toString(),
                    role: 'assistant',
                    content: '❌ Error contacting Aegis AI. Please check your connection.',
                };
                chatMessages.push(errorMsg);
                appendChatBubble(errorMsg);
            } finally {
                isBotReplying = false;
            }
        });

        // Image upload
        btnUpload.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (!file) return;
            const reader = new FileReader();
            reader.onload = (ev) => {
                uploadedImage = ev.target.result;
                document.getElementById('preview-img').src = uploadedImage;
                document.getElementById('image-preview-area').classList.remove('hidden');
            };
            reader.readAsDataURL(file);
            fileInput.value = '';
        });
        document.getElementById('remove-image-btn').addEventListener('click', clearImagePreview);

        // Speech to text
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SRec = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SRec();
            recognition.continuous = true;
            recognition.interimResults = true;

            recognition.onresult = (event) => {
                let transcript = '';
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    transcript += event.results[i][0].transcript;
                }
                input.value = transcript;
            };

            recognition.onend = () => {
                isListening = false;
                btnMic.classList.remove('active');
            };

            btnMic.addEventListener('click', () => {
                if (isListening) {
                    recognition.stop();
                    isListening = false;
                    btnMic.classList.remove('active');
                } else {
                    recognition.start();
                    isListening = true;
                    btnMic.classList.add('active');
                }
            });
        } else {
            btnMic.disabled = true;
            btnMic.title = 'Speech recognition not supported';
        }
    }

    function appendChatBubble(msg) {
        const container = document.getElementById('chat-messages-inner');
        const div = document.createElement('div');
        div.className = `chat-bubble ${msg.role}`;

        const avatarClass = msg.role === 'user' ? 'user-avatar' : 'bot-avatar';
        const avatarContent =
            msg.role === 'user'
                ? '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>'
                : '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/><path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 13v2"/><path d="M9 13v2"/></svg>';

        let imageHtml = '';
        if (msg.image) {
            imageHtml = `<img class="chat-image" src="${msg.image}" alt="Uploaded" />`;
        }

        const renderedContent = msg.role === 'assistant'
            ? renderMarkdown(msg.content)
            : escapeHtml(msg.content);

        div.innerHTML = `
      <div class="chat-avatar ${avatarClass}">${avatarContent}</div>
      <div>
        <div class="chat-text ${msg.role === 'assistant' ? 'md-prose' : ''}">${renderedContent}</div>
        ${imageHtml}
      </div>
    `;

        container.appendChild(div);
        scrollChatToBottom();
    }

    function showTypingIndicator() {
        const container = document.getElementById('chat-messages-inner');
        const div = document.createElement('div');
        div.className = 'typing-indicator';
        div.id = 'typing-indicator';
        div.innerHTML = `
      <div class="chat-avatar bot-avatar">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/><path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 13v2"/><path d="M9 13v2"/></svg>
      </div>
      <div class="typing-dots">
        <span class="typing-dot"></span>
        <span class="typing-dot"></span>
        <span class="typing-dot"></span>
      </div>
    `;
        container.appendChild(div);
        scrollChatToBottom();
    }

    function hideTypingIndicator() {
        const el = document.getElementById('typing-indicator');
        if (el) el.remove();
    }

    function clearImagePreview() {
        uploadedImage = null;
        document.getElementById('image-preview-area').classList.add('hidden');
        document.getElementById('preview-img').src = '';
    }

    function scrollChatToBottom() {
        const el = document.getElementById('chat-messages');
        el.scrollTop = el.scrollHeight;
    }

    /* ═══════════════════════════════════════
       DAILY BRIEFING
       ═══════════════════════════════════════ */
    function initBriefing() {
        const item = document.getElementById('briefing-accordion');
        const trigger = document.getElementById('briefing-trigger');
        const label = document.getElementById('briefing-label');
        const content = document.getElementById('briefing-content');

        trigger.addEventListener('click', async () => {
            const isOpen = item.classList.contains('open');

            if (isOpen) {
                item.classList.remove('open');
                return;
            }

            item.classList.add('open');

            if (briefingFetched || briefingLoading) return;

            briefingLoading = true;
            label.textContent = 'Fetching Intel...';

            try {
                const text = await aiManager.getBriefing();
                content.innerHTML = renderMarkdown(text);
                briefingFetched = true;
                label.textContent = "Today's Threat Briefing";
            } catch (err) {
                content.textContent = 'Unable to fetch the daily briefing at the moment.';
                label.textContent = "Today's Threat Briefing";
            } finally {
                briefingLoading = false;
            }
        });
    }

    /* ─── Premium Markdown Renderer ─── */
    function renderMarkdown(text) {
        if (!text) return '';

        // Normalize line endings & collapse 3+ newlines into 2
        let s = text.replace(/\r\n/g, '\n').replace(/\n{3,}/g, '\n\n');

        // Escape HTML
        s = s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

        // Fenced code blocks
        s = s.replace(/```(\w*)\n([\s\S]*?)```/g, (_, lang, code) => {
            const lbl = lang ? `<span class="code-lang">${lang}</span>` : '';
            return `<div class="code-block">${lbl}<pre><code>${code.trim()}</code></pre></div>`;
        });

        // Inline code
        s = s.replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>');

        // Headings
        s = s.replace(/^#### (.+)$/gm, '<h4 class="md-h4">$1</h4>');
        s = s.replace(/^### (.+)$/gm, '<h3 class="md-h3">$1</h3>');
        s = s.replace(/^## (.+)$/gm, '<h2 class="md-h2">$1</h2>');
        s = s.replace(/^# (.+)$/gm, '<h1 class="md-h1">$1</h1>');

        // Bold + Italic
        s = s.replace(/\*\*\*([^*]+)\*\*\*/g, '<strong><em>$1</em></strong>');
        s = s.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
        s = s.replace(/\*([^*]+)\*/g, '<em>$1</em>');

        // Horizontal rules
        s = s.replace(/^---$/gm, '<hr class="md-hr"/>');

        // Blockquotes
        s = s.replace(/^&gt; (.+)$/gm, '<blockquote class="md-bq">$1</blockquote>');

        // Unordered lists
        s = s.replace(/^[\-\*] (.+)$/gm, '<li class="md-li">$1</li>');
        s = s.replace(/((?:<li class="md-li">.*<\/li>\n?)+)/g, '<ul class="md-ul">$1</ul>');

        // Ordered lists
        s = s.replace(/^\d+\. (.+)$/gm, '<li class="md-oli">$1</li>');
        s = s.replace(/((?:<li class="md-oli">.*<\/li>\n?)+)/g, '<ol class="md-ol">$1</ol>');

        // Links
        s = s.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener" class="md-link">$1</a>');

        // Double newline → paragraph break; single → nothing (just space)
        s = s.replace(/\n\n/g, '</p><p>');
        s = s.replace(/\n/g, ' ');

        // Wrap in <p> and clean up empty/broken tags
        s = '<p>' + s + '</p>';
        s = s.replace(/<p><\/p>/g, '');
        s = s.replace(/<p>(<h[1-4])/g, '$1');
        s = s.replace(/(<\/h[1-4]>)<\/p>/g, '$1');
        s = s.replace(/<p>(<ul|<ol|<div|<hr|<blockquote)/g, '$1');
        s = s.replace(/(<\/ul>|<\/ol>|<\/div>|<\/blockquote>)<\/p>/g, '$1');
        s = s.replace(/<p>\s*<\/p>/g, '');

        return s;
    }

    /* ─── Utilities ─── */
    function escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }
})();
