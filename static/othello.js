    console.log("Othello UI boot OK");
    console.info("[build] othello.js", "v2026-01-06-A", new Date().toISOString());

    // DOM element bindings for globals that may be missing
    const modeToggle = document.getElementById('mode-toggle');
    const inputBar = document.getElementById('input-bar');
    const modeDropdown = document.getElementById('mode-dropdown');
    const focusRibbon = document.getElementById('focus-ribbon');
    const modeOptions = Array.from(document.querySelectorAll('.mode-option'));
    if (typeof setBootState !== 'function') {
      function setBootState(state) {
        console.log('bootState:', state);
      }
    }
    const loginOverlay = document.getElementById('login-overlay');
    const loginForm = document.getElementById('loginForm');
    const loginPin = document.getElementById('login-pin');
    const loginBtn = document.getElementById('login-btn');
    const loginError = document.getElementById('login-error');
    const settingsOverlay = document.getElementById('settings-overlay');
    const settingsCloseBtn = document.getElementById('settings-close');
    const settingsDevReset = document.getElementById('settings-dev-reset');
    const devResetConfirm = document.getElementById('dev-reset-confirm');
    const devResetBtn = document.getElementById('dev-reset-btn');
    const settingsStatus = document.getElementById('settings-status');
    const clearGoalsBtn = document.getElementById('clear-goals-btn');
    const clearPlansBtn = document.getElementById('clear-plans-btn');
    const clearRoutinesBtn = document.getElementById('clear-routines-btn');
    const clearInsightsBtn = document.getElementById('clear-insights-btn');
    const clearHistoryBtn = document.getElementById('clear-history-btn');
    const clearDataStatus = document.getElementById('clear-data-status');
    const archiveOverlay = document.getElementById('archive-overlay');
    const archiveCloseBtn = document.getElementById('archive-close');
    const archiveCancelBtn = document.getElementById('archive-cancel');
    const archiveConfirmBtn = document.getElementById('archive-confirm');
    const archiveStatus = document.getElementById('archive-status');
    const archiveGoalLabel = document.getElementById('archive-goal-label');
    let settingsWarningLogged = false;
    let pendingChatRequests = 0; // Moved to top-level to avoid TDZ errors
    const BOOT_STATE = {
      CHECKING_AUTH: "checking_auth",
      NEEDS_LOGIN: "needs_login",
      BOOTING_APP: "booting_app",
      AUTHENTICATED: "authenticated",
      ERROR: "error",
    };
    let isAuthed = false;
      // --- Boot State Machine ---
      // BOOT_DEBUG flag for boot instrumentation
      const BOOT_DEBUG = location.search.includes("bootdebug=1");
            // Boot debug panel elements
            const bootDebugPanel = document.getElementById('boot-debug-panel');
            const bootDebugHealthUrl = document.getElementById('bootdebug-healthurl');
            const bootDebugAttempt = document.getElementById('bootdebug-attempt');
            const bootDebugHttp = document.getElementById('bootdebug-http');
            const bootDebugJson = document.getElementById('bootdebug-json');
            const bootDebugError = document.getElementById('bootdebug-error');
            const bootDebugElapsed = document.getElementById('bootdebug-elapsed');
            const bootDebugRetry = document.getElementById('bootdebug-retry');

            if (BOOT_DEBUG && bootDebugPanel) {
              bootDebugPanel.style.display = '';
            }

            function updateBootDebug({
              healthUrl = '',
              attempt = '',
              http = '',
              json = '',
              error = '',
              elapsed = '',
              retry = ''
            } = {}) {
              if (!BOOT_DEBUG || !bootDebugPanel) return;
              if (bootDebugHealthUrl) bootDebugHealthUrl.textContent = healthUrl;
              if (bootDebugAttempt) bootDebugAttempt.textContent = attempt;
              if (bootDebugHttp) bootDebugHttp.textContent = http;
              if (bootDebugJson) bootDebugJson.textContent = json;
              if (bootDebugError) bootDebugError.textContent = error;
              if (bootDebugElapsed) bootDebugElapsed.textContent = elapsed;
              if (bootDebugRetry) bootDebugRetry.textContent = retry;
            }
      // --- Connection Overlay Logic ---
      const connectOverlay = document.getElementById('connect-overlay');
      const connectSpinner = document.getElementById('connect-spinner');
      const connectStatus = document.getElementById('connect-status');
      const connectRetry = document.getElementById('connect-retry');
      let connectBackoff = 500;
      let connectAttempts = 0;
      let connectRetryTimeout = null;
      function showConnectOverlay(message) {
        connectOverlay.style.display = 'flex';
        connectSpinner.style.display = '';
        connectStatus.textContent = message || 'Connecting to server…';
        connectRetry.classList.remove('visible');
      }
      function showConnectError(message) {
        connectOverlay.style.display = 'flex';
        connectSpinner.style.display = 'none';
        connectStatus.textContent = message || 'Unable to connect. Please try again.';
        connectRetry.classList.add('visible');
      }
      function hideConnectOverlay() {
        connectOverlay.style.display = 'none';
        connectOverlay.style.pointerEvents = 'none';
        connectRetry.classList.remove('visible');
      }

      function showLoginOverlay(message) {
        if (loginOverlay) {
          loginOverlay.style.display = 'flex';
          loginOverlay.style.pointerEvents = 'all';
        }
        if (loginError) {
          loginError.textContent = message || '';
        }
        if (loginPin) {
          loginPin.value = '';
          loginPin.disabled = false;
          loginPin.focus();
        }
        if (loginBtn) {
          loginBtn.disabled = false;
        }
      }

      function hideLoginOverlay() {
        if (loginOverlay) {
          loginOverlay.style.display = 'none';
          loginOverlay.style.pointerEvents = 'none';
        }
        if (loginError) {
          loginError.textContent = '';
        }
      }

      let _waitForReadyActive = false;
      async function checkApiHealth() {
        showConnectOverlay('Connecting to server…');
        connectAttempts++;
        let resp = null;
        let data = null;
        try {
          const controller = new AbortController();
          const timeout = setTimeout(() => controller.abort(), 10000);
          resp = await fetch('/ready', { credentials: 'omit', cache: 'no-store', signal: controller.signal });
          clearTimeout(timeout);
          const ct = resp.headers.get('content-type') || '';
          if (ct.includes('application/json')) {
            try {
              data = await resp.json();
            } catch (e) {
              // leave data null; will fall through to error messaging
            }
          }

          const ready = data && (data.ready === true || data.ok === true || data.status === 'ok');
          if (resp.ok && ready) {
            hideConnectOverlay();
            if (connectOverlay) {
              connectOverlay.style.display = 'none';
              connectOverlay.style.pointerEvents = 'none';
            }
            connectBackoff = 500;
            connectAttempts = 0;
            return true;
          }

          if (data && data.ready === false) {
            const reason = data.details || data.reason || data.message || `status ${resp.status}`;
            showConnectError(`Service not ready: ${reason}`);
            return false;
          }

          if (resp.status === 503) {
            showConnectError('Service not ready (503).');
            return false;
          }

          showConnectError(`Server is unreachable (status ${resp.status || 'unknown'}).`);
        } catch (e) {
          showConnectError('Server is unreachable.');
        }
        // Exponential backoff for auto-retry
        connectBackoff = Math.min(2000, Math.floor(connectBackoff * 1.7 + 200));
        if (connectAttempts < 5) {
          connectRetryTimeout = setTimeout(checkApiHealth, connectBackoff);
        }
        return false;
      }

      async function checkAuth() {
        setBootState(BOOT_STATE.CHECKING_AUTH);
        if (BOOT_DEBUG) console.log('[BOOT] Transition: CHECKING_AUTH');
        try {
          const resp = await fetch('/api/auth/me', { credentials: 'include', cache: 'no-store' });
          if (resp.ok) {
            const data = await resp.json();
            if (BOOT_DEBUG) console.log('[BOOT] /api/auth/me', data);
            if (data && (data.authenticated || data.authed)) {
              isAuthed = true;
              hideLoginOverlay();
              setBootState(BOOT_STATE.AUTHENTICATED);
              if (BOOT_DEBUG) console.log('[BOOT] Transition: AUTHENTICATED');
              bootApp();
              return;
            }
          }
        } catch (e) {
          if (BOOT_DEBUG) console.log('[BOOT] /api/auth/me error', e);
        }
        isAuthed = false;
        resetAuthBoundary("needs_login");
        showLoginOverlay();
        setBootState(BOOT_STATE.NEEDS_LOGIN);
        if (BOOT_DEBUG) console.log('[BOOT] Transition: NEEDS_LOGIN');
            // Global error handlers for bootdebug
            if (BOOT_DEBUG && window) {
              window.onerror = function (msg, url, line, col, error) {
                updateBootDebug({ error: (msg || '') + (error ? (' | ' + error.stack) : '') });
                setBootState(BOOT_STATE.ERROR);
                if (bootDebugPanel) bootDebugPanel.style.display = '';
                return false;
              };
              window.onunhandledrejection = function (event) {
                updateBootDebug({ error: (event.reason && event.reason.stack) || event.reason || 'Unhandled promise rejection' });
                setBootState(BOOT_STATE.ERROR);
                if (bootDebugPanel) bootDebugPanel.style.display = '';
                return false;
              };
            }
      }

      async function handleLogin(pin) {
        if (!loginBtn || !loginPin) return;
        loginBtn.disabled = true;
        loginPin.disabled = true;
        if (loginError) loginError.textContent = '';
        try {
          const resp = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ password: pin })
          });
          if (resp.ok) {
            const data = await resp.json();
            if (BOOT_DEBUG) console.log('[BOOT] /api/auth/login', data);
            if (data && (data.ok || data.authed || data.authenticated)) {
              isAuthed = true;
              hideLoginOverlay();
              setBootState(BOOT_STATE.AUTHENTICATED);
              bootApp();
              return;
            } else {
              if (loginError) {
                loginError.textContent = (data && (data.message || data.error)) || 'Invalid access code.';
              }
            }
          } else {
            let errMsg = 'Login failed.';
            try {
              const data = await resp.json();
              errMsg = (data && (data.message || data.error)) || errMsg;
            } catch {}
            if (loginError) loginError.textContent = errMsg;
          }
        } catch (e) {
          if (loginError) loginError.textContent = 'Network error.';
        }
        loginPin.value = '';
        loginBtn.disabled = false;
        loginPin.disabled = false;
        loginPin.focus();
      }

      async function handleLogout() {
        try {
          await fetch('/api/auth/logout', { method: 'POST', credentials: 'include' });
        } catch {}
        // Clear UI state if needed
        isAuthed = false;
        resetAuthBoundary("logout");
        closeSettings();
        showLoginOverlay();
        setBootState(BOOT_STATE.NEEDS_LOGIN);
        if (window && window.location) {
          window.location.reload();
        }
      }

      async function handleUnauthorized(origin) {
        if (BOOT_DEBUG) console.log('[AUTH] Unauthorized', origin || '');
        await handleLogout();
      }

      function warnSettingsUnavailable() {
        if (settingsWarningLogged) return;
        settingsWarningLogged = true;
        console.warn('[Othello UI] Settings UI unavailable: missing modal elements.');
      }

      function closeSettings() {
        if (!settingsOverlay) {
          warnSettingsUnavailable();
          return;
        }
        settingsOverlay.style.display = 'none';
      }

      function closeArchiveModal() {
        if (!archiveOverlay) return;
        archiveOverlay.style.display = 'none';
      }

      function openArchiveModal(goal) {
        if (!archiveOverlay) return;
        if (archiveStatus) {
          archiveStatus.textContent = '';
          archiveStatus.style.color = '';
        }
        if (archiveGoalLabel) {
          const title = goal && goal.text ? goal.text : 'this goal';
          archiveGoalLabel.textContent = `Archive "${title}"? This will hide it from your goals list.`;
        }
        archiveOverlay.style.display = 'flex';
      }

      function updateSettingsVisibility() {
        if (settingsDevReset) {
          settingsDevReset.style.display = devResetEnabled ? 'flex' : 'none';
        }
      }

      async function fetchAdminCapabilities() {
        if (!isAuthed) return false;
        try {
          const resp = await fetch('/api/admin/capabilities', { credentials: 'include' });
          if (resp.status === 401 || resp.status === 403) {
            await handleUnauthorized('admin-capabilities');
            return false;
          }
          if (!resp.ok) {
            throw new Error('Failed to load capabilities');
          }
          const data = await resp.json();
          devResetEnabled = !!(data && data.dev_reset_enabled);
        } catch (err) {
          devResetEnabled = false;
          console.warn('[Othello UI] admin capabilities unavailable', err);
        }
        updateSettingsVisibility();
        return devResetEnabled;
      }

      function openSettings() {
        if (!settingsOverlay || !settingsCloseBtn) {
          warnSettingsUnavailable();
          return;
        }
        if (devResetConfirm) devResetConfirm.value = '';
        if (devResetBtn) devResetBtn.disabled = true;
        if (settingsStatus) settingsStatus.textContent = '';
        settingsOverlay.style.display = 'flex';
        fetchAdminCapabilities();
      }

      async function handleDevReset() {
        if (!devResetEnabled) return;
        const confirmText = (devResetConfirm && devResetConfirm.value || '').trim();
        if (confirmText !== 'RESET') {
          if (settingsStatus) settingsStatus.textContent = 'Type RESET to confirm.';
          return;
        }
        if (devResetBtn) devResetBtn.disabled = true;
        if (settingsStatus) settingsStatus.textContent = 'Wiping data...';
        try {
          const resp = await fetch('/api/admin/reset', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ confirm: 'RESET' })
          });
          if (resp.status === 401 || resp.status === 403) {
            await handleUnauthorized('admin-reset');
            return;
          }
          if (!resp.ok) {
            let errMsg = `Reset failed (${resp.status}).`;
            const contentType = resp.headers.get('content-type') || '';
            if (contentType.includes('application/json')) {
              const data = await resp.json();
              errMsg = data && (data.message || data.error) || errMsg;
            } else {
              const text = await resp.text();
              console.error('[Othello UI] reset non-JSON error:', text.slice(0, 200));
            }
            if (settingsStatus) settingsStatus.textContent = errMsg;
            if (devResetBtn) devResetBtn.disabled = false;
            return;
          }
          if (settingsStatus) settingsStatus.textContent = 'Wipe complete. Reloading...';
          othelloState.goals = [];
          othelloState.activeGoalId = null;
          othelloState.goalUpdateCounts = {};
          setTimeout(() => window.location.reload(), 500);
        } catch (err) {
          console.error('[Othello UI] dev reset failed', err);
          if (settingsStatus) settingsStatus.textContent = 'Reset failed.';
          if (devResetBtn) devResetBtn.disabled = false;
        }
      }

      function formatDeletedCounts(deleted) {
        if (!deleted || typeof deleted !== "object") return "No records deleted.";
        const parts = Object.entries(deleted).map(([key, value]) => `${key}: ${value}`);
        return parts.length ? parts.join(", ") : "No records deleted.";
      }

      async function handleClearData(scopes, label) {
        if (!isAuthed) return;
        const confirmText = window.prompt(`Type DELETE to clear ${label}.`);
        if (confirmText !== "DELETE") {
          if (clearDataStatus) clearDataStatus.textContent = "Cancelled.";
          return;
        }
        if (clearDataStatus) clearDataStatus.textContent = `Clearing ${label}...`;
        const payload = { scopes, confirm: "DELETE" };
        try {
          const resp = await fetch("/v1/data/clear", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify(payload)
          });
          if (resp.status === 401 || resp.status === 403) {
            await handleUnauthorized("clear-data");
            return;
          }
          if (!resp.ok) {
            let errMsg = `Clear failed (${resp.status}).`;
            try {
              const data = await resp.json();
              errMsg = (data && (data.message || data.error)) || errMsg;
            } catch {}
            if (clearDataStatus) clearDataStatus.textContent = errMsg;
            return;
          }
          const data = await resp.json();
          const deleted = data && data.deleted ? data.deleted : {};
          if (clearDataStatus) clearDataStatus.textContent = `Cleared ${label}.`;
          showToast(`Deleted ${formatDeletedCounts(deleted)}`);
          if (Array.isArray(scopes)) {
            let refreshPlanner = false;
            if (scopes.includes("goals")) {
              othelloState.goals = [];
              othelloState.activeGoalId = null;
              othelloState.goalUpdateCounts = {};
              updateFocusRibbon();
              if (typeof hideGoalDetail === "function") hideGoalDetail();
              if (typeof refreshGoals === "function") {
                await refreshGoals();
              }
              refreshPlanner = true;
            }
            if (scopes.includes("plans")) {
              refreshPlanner = true;
            }
            if (scopes.includes("routines")) {
              othelloState.routines = [];
              if (typeof loadRoutinePlanner === "function") {
                await loadRoutinePlanner();
              }
              // Clear week view cache to prevent stale routine counts
              if (typeof weekViewCache !== "undefined") {
                for (const key in weekViewCache) delete weekViewCache[key];
              }
              // Refresh week view if open
              const weekView = document.getElementById("week-view-container");
              if (weekView && weekView.style.display !== "none" && typeof openWeekView === "function") {
                openWeekView();
              }
              refreshPlanner = true;
            }
            if (scopes.includes("insights")) {
              if (typeof refreshInsightsCounts === "function") {
                await refreshInsightsCounts();
              }
              if (typeof loadInsightsInbox === "function") {
                await loadInsightsInbox();
              }
            }
            if (scopes.includes("history")) {
              clearChatState();
              chatHydrated = false;
              if (typeof loadChatHistory === "function") {
                await loadChatHistory();
              }
            }
            if (refreshPlanner) {
              othelloState.todayPlannerGoalTasks = [];
              if (typeof renderGoalTasks === "function") {
                renderGoalTasks([]);
              }
              if (typeof loadTodayPlanner === "function") {
                await loadTodayPlanner();
              }
            }
          }
        } catch (err) {
          console.error("[Othello UI] clear data failed", err);
          if (clearDataStatus) clearDataStatus.textContent = "Clear failed.";
        }
      }

      async function loadConversations() {
        if (!isAuthed) return;
        try {
          const resp = await fetch("/api/conversations", { credentials: "include" });
          if (resp.ok) {
            const data = await resp.json();
            const conversations = data.conversations || [];
            if (conversations.length > 0) {
               if (!othelloState.activeConversationId) {
                   othelloState.activeConversationId = conversations[0].conversation_id;
               }
            } else {
               if (!othelloState.activeConversationId) {
                   await createNewConversation();
               }
            }
            renderConversationsList(conversations);
          }
        } catch (e) {
          console.warn("Failed to load conversations", e);
        }
      }
  
      async function createNewConversation() {
          try {
              const resp = await fetch("/api/conversations", { method: "POST", credentials: "include" });
              if (resp.ok) {
                  const data = await resp.json();
                  othelloState.activeConversationId = data.conversation_id;
                  clearChatState();
                  chatHydrated = false;
                  await loadChatHistory();
                  await loadConversations(); // Refresh list
              }
          } catch (e) {
              console.error("Failed to create conversation", e);
          }
      }

      async function switchConversation(id) {
          if (othelloState.activeConversationId === id) return;
          othelloState.activeConversationId = id;
          clearChatState();
          chatHydrated = false;
          await loadChatHistory();
          closeSettings();
      }

      function renderConversationsList(conversations) {
          const container = document.getElementById("settings-conversations-list");
          if (!container) return;
          container.innerHTML = "";
          
          if (!conversations || conversations.length === 0) {
              container.innerHTML = "<div class='conversations-list-empty'>No conversations found.</div>";
              return;
          }

          conversations.forEach(conv => {
              const row = document.createElement("div");
              row.className = "conversation-row";
              
              const info = document.createElement("div");
              const date = new Date(conv.updated_at || conv.created_at).toLocaleString();
              const isCurrent = conv.conversation_id === othelloState.activeConversationId;
              info.innerHTML = `
                  <div class="conversation-info-title ${isCurrent ? 'current' : ''}">
                      ${isCurrent ? 'Current: ' : ''}Conversation #${conv.conversation_id}
                  </div>
                  <div class="conversation-info-date">${date}</div>
              `;
              
              const actions = document.createElement("div");
              if (!isCurrent) {
                  const switchBtn = document.createElement("button");
                  switchBtn.textContent = "Open";
                  switchBtn.className = "btn-secondary conversation-switch-btn";
                  switchBtn.onclick = () => switchConversation(conv.conversation_id);
                  actions.appendChild(switchBtn);
              }
              
              row.appendChild(info);
              row.appendChild(actions);
              container.appendChild(row);
          });
      }

      function bootApp() {
        setBootState(BOOT_STATE.BOOTING_APP);
        if (BOOT_DEBUG) console.log('[BOOT] Booting app…');
        setTimeout(async () => {
          try {
            if (!isAuthed) {
              await checkAuth();
              if (!isAuthed) return;
            }
            hideLoginOverlay();
            if (typeof refreshGoals === 'function') {
              await refreshGoals();
            }
            if (typeof loadChatHistory === 'function') {
              await loadChatHistory();
            }
            if (typeof refreshInsightsCounts === 'function') {
              await refreshInsightsCounts();
            }
            if (typeof loadTodayPlanner === 'function') {
              await loadTodayPlanner();
            }
            await loadConversations();
            await fetchAdminCapabilities();
            setBootState(BOOT_STATE.AUTHENTICATED);
          } catch (e) {
            if (e && (e.status === 401 || e.status === 403)) {
              if (BOOT_DEBUG) console.log('[BOOT] Data call 401/403, forcing re-auth');
              await handleUnauthorized('boot');
            } else {
              // Show in-app error banner (not overlay)
              if (plannerError) {
                plannerError.style.display = 'block';
                plannerError.textContent = 'App error: ' + (e && e.message ? e.message : 'Unknown error.');
              }
            }
          }
        }, 100);
      }

      connectRetry.addEventListener('click', () => {
        connectBackoff = 500;
        connectAttempts = 0;
        checkApiHealth();
      });

      if (loginForm && loginPin) {
        loginForm.addEventListener('submit', (e) => {
          e.preventDefault();
          if (loginPin.value.trim()) {
            handleLogin(loginPin.value.trim());
          }
        });
        loginPin.addEventListener('keydown', (e) => {
          if (e.key === 'Enter') {
            e.preventDefault();
            if (loginBtn) loginBtn.click();
          }
        });
      }

      // Add settings + logout buttons to header (minimal UI)
      const brandRow = document.querySelector('.brand-row');
      let newChatBtn = document.getElementById('new-chat-btn');
      if (!newChatBtn) {
        newChatBtn = document.createElement('button');
        newChatBtn.id = 'new-chat-btn';
        newChatBtn.className = 'icon-button';
        newChatBtn.setAttribute('aria-label', 'New Chat');
        newChatBtn.textContent = '+';
        newChatBtn.style.marginRight = '0.5rem';
        newChatBtn.title = "New Chat";
        if (brandRow) {
             // Insert before settings button or at end
             const settingsBtnRef = document.getElementById('settings-btn');
             if (settingsBtnRef) {
                 brandRow.insertBefore(newChatBtn, settingsBtnRef);
             } else {
                 brandRow.appendChild(newChatBtn);
             }
        }
      }
      newChatBtn.onclick = createNewConversation;

      let settingsBtn = document.getElementById('settings-btn');
      if (!settingsBtn) {
        settingsBtn = document.createElement('button');
        settingsBtn.id = 'settings-btn';
        settingsBtn.className = 'icon-button';
        settingsBtn.setAttribute('aria-label', 'Settings');
        settingsBtn.textContent = '⚙';
        if (brandRow) brandRow.appendChild(settingsBtn);
      }
      let logoutBtn = document.getElementById('logout-btn');
      if (!logoutBtn) {
        logoutBtn = document.createElement('button');
        logoutBtn.id = 'logout-btn';
        logoutBtn.textContent = 'Logout';
        logoutBtn.style = 'margin-left:1.5rem;font-size:1rem;padding:0.3rem 1.1rem;border-radius:8px;border:1px solid var(--accent);background:var(--accent-soft);color:var(--accent);';
        if (brandRow) brandRow.appendChild(logoutBtn);
      }
      logoutBtn.onclick = handleLogout;
      const settingsReady = !!(settingsOverlay && settingsCloseBtn);
      if (!settingsReady) {
        warnSettingsUnavailable();
        if (settingsBtn) settingsBtn.style.display = 'none';
      } else {
        if (settingsBtn) settingsBtn.onclick = openSettings;
        settingsCloseBtn.onclick = closeSettings;
        settingsOverlay.addEventListener('click', (event) => {
          if (event.target === settingsOverlay) {
            closeSettings();
          }
        });
        if (devResetConfirm) {
          devResetConfirm.addEventListener('input', () => {
            if (devResetBtn) {
              devResetBtn.disabled = devResetConfirm.value.trim() !== 'RESET';
            }
          });
        }
        if (devResetBtn) devResetBtn.onclick = handleDevReset;
        const newChatSettingsBtn = document.getElementById("new-chat-settings-btn");
        if (newChatSettingsBtn) {
            newChatSettingsBtn.onclick = async () => {
                await createNewConversation();
                closeSettings();
            };
        }
        if (clearGoalsBtn) clearGoalsBtn.onclick = () => handleClearData(["goals"], "goals");
        if (clearPlansBtn) clearPlansBtn.onclick = () => handleClearData(["plans"], "plans");
        if (clearRoutinesBtn) clearRoutinesBtn.onclick = () => handleClearData(["routines"], "routines");
        if (clearInsightsBtn) clearInsightsBtn.onclick = () => handleClearData(["insights"], "insights");
        if (clearHistoryBtn) clearHistoryBtn.onclick = () => handleClearData(["history"], "history");
      }

      if (archiveCloseBtn) archiveCloseBtn.onclick = closeArchiveModal;
      if (archiveCancelBtn) archiveCancelBtn.onclick = closeArchiveModal;
      if (archiveOverlay) {
        archiveOverlay.addEventListener('click', (event) => {
          if (event.target === archiveOverlay) {
            closeArchiveModal();
          }
        });
      }

      // --- Unified boot sequence ---
      (async function bootUnified() {
        if (BOOT_DEBUG) console.log('[BOOT] Starting unified boot sequence');
        const healthy = await checkApiHealth();
        if (healthy) {
          await checkAuth();
        }
      })();
    const API = "/api/message";
    const GOALS_API = "/api/goals";
    const PLAN_UPDATE_API = "/api/plan/update";
    const V1_MESSAGES_API = "/v1/messages";

    let recognition = null;
    let isRecording = false;
    let voice = {
      recognition: null,
      active: false
    };
    // Composer State
    let composerMode = "idle"; // idle | typing | recording
    let silenceInterval = null;
    let audioContext = null;
    let analyser = null;
    let microphoneStream = null;
    let silenceStart = 0;
    let lastParaInsertAt = 0;
    const SILENCE_THRESHOLD = 0.02; // RMS threshold
    const SILENCE_DELAY_MS = 2500;
    const PARA_COOLDOWN_MS = 1200;

    let sttFullTranscript = "";
    let sttLastInterim = "";
    let pendingMicStart = false;
    let pendingStartTimeout = null;
    let chatHydrated = false;

    // DOM elements - declare all elements used in the script
    const input = document.getElementById('user-input');
    const composerActionBtn = document.getElementById('composer-action-btn');
    const inputBarContainer = document.getElementById('input-bar');

    // Legacy mocks for safety
    const sendBtn = { disabled: false, onclick: null };
    const micBtn = { disabled: false, classList: { add:()=>{}, remove:()=>{} }, title:'', addEventListener:()=>{} }; 
    const cancelTranscriptBtn = { classList: { add:()=>{}, remove:()=>{} }, addEventListener:()=>{} };

    const chatLog = document.getElementById('chat-log');
    // Relocated status to chat header (Phase 6 Fix)
    const statusEl = document.getElementById('chat-status-text') || { textContent: "" };
    const modeLabel = document.getElementById('current-mode-label');
    const modeSubtitle = document.getElementById('mode-subtitle');
    const plannerTabBadge = document.getElementById('planner-tab-badge');
    const goalsTabBadge = document.getElementById('goals-tab-badge');
    const middleTabBadge = null; // Deprecated
    const insightsTabBadge = document.getElementById('insights-tab-badge');
    const focusRibbonTitle = document.getElementById('focus-ribbon-title');
    const viewFocusBtn = document.getElementById('view-focus-btn');
    const updateFocusBtn = document.getElementById('update-focus-btn');
    const appendFocusBtn = document.getElementById('append-focus-btn');
    const unfocusBtn = document.getElementById('unfocus-btn');
    const goalsList = document.getElementById('goals-list');
    const goalDetail = document.getElementById('goal-detail');
    const detailGoalId = document.getElementById('detail-goal-id');
    const detailGoalTitle = document.getElementById('detail-goal-title');
    const detailContent = document.getElementById('detail-content');
    const backFromDetailBtn = document.getElementById('back-from-detail');
    const goalDetailRefreshBtn = document.getElementById('goal-detail-refresh');
    const continueWorkingBtn = document.getElementById('continue-working-btn');
    const archiveGoalBtn = document.getElementById('archive-goal-btn');
    const plannerHeadline = document.getElementById('planner-headline');
    const plannerEnergy = document.getElementById('planner-energy');
    const plannerError = document.getElementById('planner-error');
    const plannerRoutinesList = document.getElementById('planner-routines-list');
    const plannerRoutinesCount = document.getElementById('planner-routines-count');
    const plannerGoalsList = document.getElementById('planner-goals-list');
    const plannerGoalsCount = document.getElementById('planner-goals-count');
    const todayPlanCount = document.getElementById('today-plan-count');
    const todayPlanItems = document.getElementById('today-plan-items');
    const todayPlanError = document.getElementById('today-plan-error');
    const todayPlanSuggestions = document.getElementById('today-plan-suggestions');
    const buildPlanBtn = document.getElementById('build-plan-btn');
    const buildPlanStatus = document.getElementById('build-plan-status');
    const insightsList = document.getElementById('insights-list');
    const insightsEmpty = document.getElementById('insights-empty');
    const insightsError = document.getElementById('insights-error');
    const toastEl = document.getElementById('toast');

    // App state
    const othelloState = {
      chatViewMode: "duet", // "duet" | "history"
      connectivity: 'online', // online | offline | degraded
      currentView: "today-planner",
      currentMode: "today", // companion | today | routine
      manualChannelOverride: null, // Phase 5: For Dialogue Selector
      goals: [],
      activeGoalId: null,
      activeConversationId: null, // New Chat support
      activeDraft: null, // { draft_id, draft_type, source_message_id }
      activeDraftPayload: null,
      lastGoalDraftByConversationId: {}, // Stores the last assistant goal summary per conversation
      currentDetailGoalId: null,
      pendingGoalEdit: null,
      goalUpdateCounts: {},
      currentAgentStatus: null,
      todayPlannerGoalTasks: [],
      messagesByClientId: {},
      dismissedSuggestionIds: new Set(),
      goalIntentSuggestions: {},
      secondarySuggestionsByClientId: {},
      intentHintsByClientId: {},
      mobileEditorPinned: false,
      mobileBackJustPressedAt: 0,
      creatingRoutine: false,
      needsRoutineRefresh: false,
      pendingRoutineSuggestionId: null,
      pendingRoutineAcceptFn: null,
      isGeneratingSteps: false
    };
    let devResetEnabled = false;

    const DISMISSED_SUGGESTIONS_KEY = "othello_dismissed_suggestions_v1";
    const SUGGESTION_DISMISS_API = "/api/suggestions/dismiss";

    function loadDismissedSuggestionIds() {
      if (!othelloState.dismissedSuggestionIds) {
        othelloState.dismissedSuggestionIds = new Set();
      }
      try {
        const raw = localStorage.getItem(DISMISSED_SUGGESTIONS_KEY);
        if (!raw) return;
        const parsed = JSON.parse(raw);
        if (Array.isArray(parsed)) {
          parsed.forEach((item) => {
            if (typeof item === "string" && item.trim()) {
              othelloState.dismissedSuggestionIds.add(item);
            }
          });
        }
      } catch (err) {
        console.warn("[Othello UI] dismissed suggestions load failed:", err);
      }
    }

    function persistDismissedSuggestionIds() {
      try {
        const items = Array.from(othelloState.dismissedSuggestionIds || []);
        localStorage.setItem(DISMISSED_SUGGESTIONS_KEY, JSON.stringify(items));
      } catch (err) {
        console.warn("[Othello UI] dismissed suggestions save failed:", err);
      }
    }

    function showToast(message, timeoutMs = 1800) {
      if (!toastEl) return;
      toastEl.textContent = message;
      toastEl.classList.add("visible");
      window.clearTimeout(showToast._timer);
      showToast._timer = window.setTimeout(() => {
        toastEl.classList.remove("visible");
      }, timeoutMs);
    }

    function generateClientMessageId() {
      if (window.crypto && typeof window.crypto.randomUUID === "function") {
        return window.crypto.randomUUID();
      }
      const rand = Math.random().toString(16).slice(2, 10);
      return `msg_${Date.now()}_${rand}`;
    }

    loadDismissedSuggestionIds();

    const insightsCounts = {
      plan_pending: 0,
      goal_pending: 0,
      routine_pending: 0,
      idea_pending: 0,
      generic_pending: 0,
    };

    const MODE_LABELS = {
      companion: "Companion Chat",
      today: "Today Planner",
      routine: "Routine Planner",
    };

    const MODE_SUBTITLES = {
      companion: "Personal Goal Architect",
      today: "Daily Plan Engine",
      routine: "Adaptive Routine Coach",
    };

    const MODE_TAB_CONFIG = {
      companion: { label: "Goals", view: "goals" },
      today: { label: "Today Planner", view: "today-planner" },
      routine: { label: "Routine Planner", view: "routine-planner" },
    };

    const MODE_ALLOWED_VIEWS = {
      companion: ["chat", "goals", "insights"],
      today: ["chat", "today-planner", "insights"],
      routine: ["chat", "routine-planner", "insights"],
    };

    function applyInsightsMeta(meta) {
      if (!meta) return;
      const pending = meta.pending_counts || meta.pending || meta;
      if (pending) {
        insightsCounts.plan_pending = pending.plan ?? pending.plan_pending ?? insightsCounts.plan_pending;
        insightsCounts.goal_pending = pending.goal ?? pending.goal_pending ?? insightsCounts.goal_pending;
        insightsCounts.routine_pending = pending.routine ?? pending.routine_pending ?? insightsCounts.routine_pending;
        insightsCounts.idea_pending = pending.idea ?? pending.idea_pending ?? insightsCounts.idea_pending;
        insightsCounts.generic_pending = pending.generic ?? pending.generic_pending ?? insightsCounts.generic_pending;
      }
      updateTabBadges();
    }

    function totalPendingInsights() {
      return (
        (insightsCounts.plan_pending || 0) +
        (insightsCounts.goal_pending || 0) +
        (insightsCounts.routine_pending || 0) +
        (insightsCounts.idea_pending || 0) +
        (insightsCounts.generic_pending || 0)
      );
    }

    function updateTabBadges() {
      // Planner Tab Logic (Today)
      const planCount = insightsCounts.plan_pending || 0;
      if (plannerTabBadge) {
        if (planCount > 0) {
          plannerTabBadge.textContent = planCount;
          plannerTabBadge.classList.remove("hidden");
        } else {
          plannerTabBadge.classList.add("hidden");
        }
      }

      // Goals Tab Logic
      const goalCount = insightsCounts.goal_pending || 0;
      if (goalsTabBadge) {
        if (goalCount > 0) {
          goalsTabBadge.textContent = goalCount;
          goalsTabBadge.classList.remove("hidden");
        } else {
          goalsTabBadge.classList.add("hidden");
        }
      }

      // Insights Tab Logic (Aggregated Total)
      const total = totalPendingInsights();
      if (insightsTabBadge) {
        if (total > 0) {
          insightsTabBadge.textContent = total;
          insightsTabBadge.classList.remove("hidden");
        } else {
          insightsTabBadge.classList.add("hidden");
        }
      }
    }

    async function refreshInsightsCounts(meta) {
      if (meta) {
        applyInsightsMeta(meta);
        return;
      }
      if (!isAuthed) return;
      try {
        const resp = await fetch("/api/insights/summary", { credentials: "include" });
        if (resp.status === 401 || resp.status === 403) {
          await handleUnauthorized('insights-summary');
          return;
        }
        if (!resp.ok) return;
        const data = await resp.json();
        applyInsightsMeta(data);
      } catch (err) {
        console.warn("[Othello UI] failed to refresh insights summary", err);
      }
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    function hideTranscriptCancel() {
      if (cancelTranscriptBtn) {
        cancelTranscriptBtn.classList.add("hidden");
      }
    }

    function showTranscriptCancel() {
      if (cancelTranscriptBtn) {
        cancelTranscriptBtn.classList.remove("hidden");
      }
    }

    if (!SpeechRecognition) {
       // Handled in startVoiceInput check
    } else {
      recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = "en-GB";

      recognition.onstart = () => {
        isRecording = true;
        sttFullTranscript = "";
        sttLastInterim = "";
        pendingMicStart = false;
        if (input) input.value = "";
        updateComposerUI();
      };

      recognition.onend = () => {
        isRecording = false;
        // Final flush logic if needed, but onresult handles it usually.
        updateComposerUI();

        if (pendingMicStart) {
          pendingMicStart = false;
          if (pendingStartTimeout) {
            clearTimeout(pendingStartTimeout);
            pendingStartTimeout = null;
          }
          setTimeout(() => {
            try {
              recognition.start();
            } catch (err) {
              console.warn("[Othello UI] speech deferred start error:", err);
            }
          }, 20);
        }
      };

      recognition.onerror = (event) => {
        console.warn("[Othello UI] speech error:", event.error);
        if (event.error === "aborted") return; // ignore explicit aborts
        
        isRecording = false;
        pendingMicStart = false;
        if (pendingStartTimeout) {
          clearTimeout(pendingStartTimeout);
          pendingStartTimeout = null;
        }
        updateComposerUI();
        
        if (inputBarContainer) {
            inputBarContainer.classList.add("error"); // Optional visual cue
            setTimeout(() => inputBarContainer.classList.remove("error"), 1000);
        }
      };

      recognition.onresult = (event) => {
        let interimBuffer = "";
        let newFinal = "";
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const result = event.results[i];
          const phrase = (result[0] && result[0].transcript ? result[0].transcript : "").trim();
          if (!phrase) continue;
          if (result.isFinal) {
             newFinal += (newFinal ? " " : "") + phrase;
          } else {
             interimBuffer += (interimBuffer ? " " : "") + phrase;
          }
        }
        
        // Append new final to full transcript
        if (newFinal) {
             const needsSpace = sttFullTranscript.length > 0 && !sttFullTranscript.match(/\s$/);
             sttFullTranscript += (needsSpace ? " " : "") + newFinal;
        }
        
        sttLastInterim = interimBuffer;
        
        // Render
        let display = sttFullTranscript;
        if (sttLastInterim) {
             const needsSpace = display.length > 0 && !display.match(/\s$/);
             display += (needsSpace ? " " : "") + sttLastInterim;
        }
        
        if (input) {
            input.value = display;
            input.scrollTop = input.scrollHeight;
        }
        updateComposerUI();
      };
    }

    // API helpers for Today Planner
    function formatDateYYYYMMDD(date) {
      const d = new Date(date.getTime() - (date.getTimezoneOffset() * 60000));
      return d.toISOString().split("T")[0];
    }

    function getTomorrowDate() {
      const d = new Date();
      d.setDate(d.getDate() + 1);
      return formatDateYYYYMMDD(d);
    }

    async function fetchTodayBrief(signal) {
      const resp = await fetch("/api/today-brief", { credentials: "include", signal });
      const status = resp.status;
      const text = await resp.text();
      if (status === 401 || status === 403) {
        const err = new Error("Unauthorized");
        err.status = status;
        throw err;
      }
      if (!resp.ok) {
        const err = new Error("Failed to load brief");
        err.status = status;
        err.bodySnippet = text.slice(0, 300);
        throw err;
      }
      let data = null;
      try {
        data = JSON.parse(text);
      } catch (parseErr) {
        const err = new Error("Failed to parse brief");
        err.status = status;
        err.bodySnippet = text.slice(0, 300);
        err.parseError = parseErr.message;
        throw err;
      }
      return (data && data.brief) || {};
    }

    async function fetchTodayPlan() {
      const resp = await fetch(`/api/today-plan?ts=${Date.now()}`, { cache: "no-store", credentials: "include" });
      if (resp.status === 401 || resp.status === 403) {
        const err = new Error("Unauthorized");
        err.status = resp.status;
        throw err;
      }
      if (!resp.ok) throw new Error("Failed to load plan");
      const data = await resp.json();
      return data.plan || {};
    }

    function setTodayPlanError(message, requestId) {
      if (!todayPlanError) return;
      const suffix = requestId ? ` (request_id: ${requestId})` : "";
      todayPlanError.textContent = `${message || "Plan error."}${suffix}`;
      todayPlanError.style.display = "block";
    }
    function clearTodayPlanError() {
      if (!todayPlanError) return;
      todayPlanError.textContent = "";
      todayPlanError.style.display = "none";
    }
    function setBuildPlanStatus(message) {
      if (!buildPlanStatus) return;
      buildPlanStatus.textContent = message || "";
    }
    async function v1Request(url, options, label) {
      const resp = await fetch(url, options);
      if (resp.status === 401 || resp.status === 403) {
        const err = new Error("Unauthorized");
        err.status = resp.status;
        throw err;
      }
      let payload = null;
      try {
        payload = await resp.json();
      } catch {}
      if (!resp.ok || (payload && payload.ok === false)) {
        const message = payload && payload.error && payload.error.message
          ? payload.error.message
          : `${label} failed (${resp.status}).`;
        const err = new Error(message);
        err.status = resp.status;
        err.requestId = payload && payload.request_id ? payload.request_id : null;
        throw err;
      }
      return payload;
    }
    async function fetchV1TodayPlan(signal) {
      const payload = await v1Request(
        "/v1/read/today",
        { cache: "no-store", credentials: "include", signal },
        "Today plan"
      );
      return payload?.data?.plan || {};
    }
    async function fetchPlanItemSuggestions(signal) {
      const payload = await v1Request(
        "/v1/suggestions?status=pending&kind=plan_item&limit=20",
        { credentials: "include", signal },
        "Plan suggestions"
      );
      return Array.isArray(payload?.data?.suggestions) ? payload.data.suggestions : [];
    }
    function renderTodayPlanItems(plan) {
      if (!todayPlanItems) return;
      const items = Array.isArray(plan && plan.items) ? plan.items : [];
      todayPlanItems.innerHTML = "";
      if (todayPlanCount) {
        todayPlanCount.textContent = `${items.length} item${items.length === 1 ? "" : "s"}`;
      }
      if (!items.length) {
        todayPlanItems.innerHTML = `<div class="planner-empty">No plan items yet.</div>`;
        return;
      }
      items.forEach((item) => {
        const row = document.createElement("div");
        row.className = "planner-task";
        const left = document.createElement("div");
        const label = document.createElement("div");
        label.className = "planner-task__label";
        label.textContent = item.title || item.notes || "Untitled plan item";
        left.appendChild(label);
        const right = document.createElement("div");
        right.className = "planner-block__right";
        right.appendChild(createStatusChip(item.status || "planned"));

        row.appendChild(left);
        row.appendChild(right);
        todayPlanItems.appendChild(row);
      });
    }
    function renderPlanSuggestions(suggestions) {
      if (!todayPlanSuggestions) return;
      const items = Array.isArray(suggestions) ? suggestions : [];
      todayPlanSuggestions.innerHTML = "";
      if (!items.length) {
        todayPlanSuggestions.innerHTML = `<div class="planner-empty">No pending plan suggestions.</div>`;
        return;
      }
      items.forEach((suggestion) => {
        const card = document.createElement("div");
        card.className = "planner-block";

        const header = document.createElement("div");
        header.className = "planner-block__header";

        const headerLeft = document.createElement("div");
        const title = document.createElement("div");
        title.className = "planner-block__title";
        const payload = suggestion && suggestion.payload ? suggestion.payload : {};
        title.textContent = payload.title || `Suggestion ${suggestion.id || ""}`.trim();

        headerLeft.appendChild(title);

        const headerRight = document.createElement("div");
        headerRight.className = "planner-block__right";
        headerRight.appendChild(createStatusChip("pending"));

        const confirmBtn = document.createElement("button");
        confirmBtn.className = "planner-action-btn";
        confirmBtn.textContent = "Confirm";
        confirmBtn.addEventListener("click", async () => {
          if (!suggestion || !suggestion.id) return;
          confirmBtn.disabled = true;
          try {
            const confirmPayload = { reason: "confirm" };
            if (BOOT_DEBUG) {
              console.info("[Today Planner] confirm suggestion", {
                endpoint: `/v1/suggestions/${suggestion.id}/accept`,
                method: "POST",
                payloadKeys: Object.keys(confirmPayload),
              });
            }
            await v1Request(
              `/v1/suggestions/${suggestion.id}/accept`,
              {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "include",
                body: JSON.stringify(confirmPayload)
              },
              "Confirm suggestion"
            );
            setBuildPlanStatus("Suggestion confirmed.");
            await loadTodayPlanPanel();
          } catch (err) {
            if (err && (err.status === 401 || err.status === 403)) {
              await handleUnauthorized('today-plan-accept');
              return;
            }
            setTodayPlanError(err && err.message ? err.message : "Could not confirm suggestion.", err && err.requestId ? err.requestId : null);
          } finally {
            confirmBtn.disabled = false;
          }
        });

        headerRight.appendChild(confirmBtn);
        header.appendChild(headerLeft);
        header.appendChild(headerRight);
        card.appendChild(header);

        todayPlanSuggestions.appendChild(card);
      });
    }
    function getLatestChatMessageText() {
      const entries = Object.values(othelloState.messagesByClientId || {});
      if (!entries.length) return null;
      entries.sort((a, b) => (b.ts || 0) - (a.ts || 0));
      const latest = entries[0];
      return latest && typeof latest.text === "string" ? latest.text.trim() : null;
    }
    async function createV1MessageFromText(text) {
      const payload = await v1Request(
        "/v1/messages",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({ transcript: text, source: "text", channel: "planner" })
        },
        "Create message"
      );
      return payload?.data?.message || null;
    }
    async function buildPlanDraftPayload() {
      const recentText = getLatestChatMessageText();
      if (recentText) {
        const message = await createV1MessageFromText(recentText);
        if (message && typeof message.id === "number") {
          return { payload: { message_ids: [message.id] }, note: "Drafting from latest chat message." };
        }
      }
      return { payload: { include_rollover: true }, note: "No recent chat message found; drafting from rollover only." };
    }
    async function loadTodayPlanPanel(signal) {
      if (othelloState.currentView !== "today-planner") return;
      if (document.hidden) return;
      if (!todayPlanItems || !todayPlanSuggestions) return;
      logPlannerDebug("[Today Planner] loadTodayPlanPanel");
      clearTodayPlanError();
      let panelSignal = signal;
      if (!panelSignal) {
        abortPlannerRequests("panel-reload");
        plannerAbort = new AbortController();
        panelSignal = plannerAbort.signal;
      }
      try {
        const plan = await fetchV1TodayPlan(panelSignal);
        renderTodayPlanItems(plan);
      } catch (e) {
        if (isAbortError(e)) return;
        if (e && (e.status === 401 || e.status === 403)) {
          await handleUnauthorized('today-plan-read');
          return;
        }
        setTodayPlanError(e && e.message ? e.message : "Failed to load today plan.", e && e.requestId ? e.requestId : null);
      }
      try {
        const suggestions = await fetchPlanItemSuggestions(panelSignal);
        renderPlanSuggestions(suggestions);
      } catch (e) {
        if (isAbortError(e)) return;
        if (e && (e.status === 401 || e.status === 403)) {
          await handleUnauthorized('today-plan-suggestions');
          return;
        }
        setTodayPlanError(e && e.message ? e.message : "Failed to load plan suggestions.", e && e.requestId ? e.requestId : null);
      }
    }
    async function handleBuildPlanClick() {
      if (!buildPlanBtn) return;
      clearTodayPlanError();
      buildPlanBtn.disabled = true;
      setBuildPlanStatus("Drafting...");
      try {
        const seed = await buildPlanDraftPayload();
        if (seed.note) setBuildPlanStatus(seed.note);
        const payload = await v1Request(
          "/v1/plan/draft",
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify(seed.payload)
          },
          "Draft plan"
        );
        const ids = Array.isArray(payload?.data?.suggestion_ids) ? payload.data.suggestion_ids : [];
        setBuildPlanStatus(`Drafted ${ids.length} suggestion${ids.length === 1 ? "" : "s"}.`);
        await loadTodayPlanPanel();
      } catch (e) {
        if (e && (e.status === 401 || e.status === 403)) {
          await handleUnauthorized('today-plan-draft');
          return;
        }
        setTodayPlanError(e && e.message ? e.message : "Could not draft plan.", e && e.requestId ? e.requestId : null);
      } finally {
        buildPlanBtn.disabled = false;
      }
    }
    if (buildPlanBtn) buildPlanBtn.addEventListener("click", handleBuildPlanClick);

    function renderTodayBrief(plan, brief) {
      const sections = (plan && plan.sections) || {};
      const routines = sections.routines || [];
      const goalTasks = sections.goal_tasks || [];

      const headline = brief && brief.headline ? brief.headline : (plan && plan.date ? `Plan for ${plan.date}` : "Today Planner");

      const routineBits = routines.length ? `${routines.length} routine${routines.length === 1 ? "" : "s"}` : "No routines";
      const goalBits = goalTasks.length ? `${goalTasks.length} goal task${goalTasks.length === 1 ? "" : "s"}` : "No goal tasks";

      const capacity = (plan && plan.capacity_model) || {};
      const capacityBits = ["heavy", "medium", "light"]
        .map(k => (capacity[k] ? `${capacity[k]} ${k}` : ""))
        .filter(Boolean)
        .join(", ");

      const energyLoad = brief && brief.energy_load ? brief.energy_load : "";
      const backlog = brief && brief.backlog ? brief.backlog : "";

      const notes = [goalBits, routineBits, capacityBits, energyLoad, backlog]
        .filter(Boolean)
        .join(" • ");

      plannerHeadline.textContent = headline;
      plannerEnergy.textContent = notes;

      console.log("[Today Planner] renderTodayBrief", {
        goalTasks: goalTasks.length,
        routines: routines.length,
        capacity,
        headline: plannerHeadline.textContent,
        notes,
      });
    }

    function renderPlannerError(message, httpStatus, details) {
      plannerError.style.display = "block";
      let msg = message || "Could not load today's plan. Please try again later.";
      if (httpStatus) msg += ` (HTTP ${httpStatus})`;
      plannerError.innerHTML = `${msg} <button id="planner-retry-btn" style="margin-left:1em;">Retry</button>`;
      if (details) {
        plannerError.dataset.error = details;
      } else {
        delete plannerError.dataset.error;
      }
      const retryBtn = document.getElementById("planner-retry-btn");
      if (retryBtn) {
        retryBtn.onclick = () => {
          clearPlannerError();
          loadTodayPlanner();
        };
      }
    }

    function clearPlannerError() {
      plannerError.style.display = "none";
      plannerError.textContent = "";
      plannerError.innerHTML = "";
    }



    function createStatusChip(status, item = null) {
      const chip = document.createElement("div");
      chip.className = "planner-status";
      chip.textContent = status || "planned";
      
      if (item) {
        const iid = item.item_id || item.id;
        if (iid && (status === "planned" || status === "in_progress")) {
          chip.style.cursor = "pointer";
          chip.title = status === "planned" ? "Click to Start" : "Click to Complete";
          chip.onclick = async (e) => {
            e.stopPropagation();
            const nextStatus = status === "planned" ? "in_progress" : "complete";
            try {
              const resp = await fetch(PLAN_UPDATE_API, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "include",
                body: JSON.stringify({ item_id: iid, status: nextStatus }),
              });
              if (resp.ok) await loadTodayPlanner();
            } catch (err) { console.error(err); }
          };
        }
      }
      return chip;
    }

    function buildPlannerActions(item) {
      const container = document.createElement("div");
      container.className = "planner-actions";
      
      const iid = item?.item_id || item?.id;
      if (!iid) return container;

      const status = item.status || "planned";
      const metadata = item.metadata || {};
      const isSnoozed = isSnoozedNow(metadata);

      const actions = [];
      
      if (isSnoozed) {
        // If snoozed, allow waking up (clears snooze) or completing
        actions.push({ label: "Wake", status: status }); // Re-sending status clears snooze
        actions.push({ label: "Done", status: "complete" });
      } else {
        if (status === "planned") {
          actions.push({ label: "Start", status: "in_progress" });
          actions.push({ label: "Done", status: "complete" });
          actions.push({ label: "Snooze 1h", snooze: 60 });
          actions.push({ label: "Skip", status: "skipped" });
          actions.push({ label: "Move to Tomorrow", status: "rescheduled" });
        } else if (status === "in_progress") {
          actions.push({ label: "Done", status: "complete" });
          actions.push({ label: "Snooze 30m", snooze: 30 });
          actions.push({ label: "Skip", status: "skipped" });
          actions.push({ label: "Move to Tomorrow", status: "rescheduled" });
        }
      }

      actions.forEach(action => {
        const btn = document.createElement("button");
        btn.className = "planner-action-btn";
        btn.textContent = action.label;
        
        // Style snooze buttons differently?
        if (action.snooze) {
            btn.style.color = "var(--text-soft)";
        }

        btn.addEventListener("click", async () => {
          btn.disabled = true;
          try {
            const payload = { item_id: iid };
            
            if (action.snooze) {
                payload.snooze_minutes = action.snooze;
            } else {
                payload.status = action.status;
                if (action.status === "rescheduled") {
                  payload.reschedule_to = getTomorrowDate();
                }
            }

            const resp = await fetch(PLAN_UPDATE_API, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              credentials: "include",
              body: JSON.stringify(payload),
            });
            if (!resp.ok) {
              const errText = await resp.text();
              throw new Error(errText || "Failed to update item");
            }
            await loadTodayPlanner();
          } catch (err) {
            renderPlannerError("Could not update item. Please try again.");
          } finally {
            btn.disabled = false;
          }
        });
        container.appendChild(btn);
      });

      return container;
    }

    function parseIsoUtcMillis(ts) {
      if (!ts) return 0;
      let s = String(ts);
      if (!/Z$|[+-]\d{2}:\d{2}$/.test(s)) {
        s += "Z";
      }
      const d = new Date(s);
      return isNaN(d.getTime()) ? 0 : d.getTime();
    }

    function parseHmToMinutes(hm) {
      if (!hm || typeof hm !== 'string') return null;
      const parts = hm.split(':');
      if (parts.length !== 2) return null;
      const h = parseInt(parts[0], 10);
      const m = parseInt(parts[1], 10);
      if (isNaN(h) || isNaN(m)) return null;
      return h * 60 + m;
    }

    function getLocalNowMinutes() {
      const now = new Date();
      return now.getHours() * 60 + now.getMinutes();
    }

    function isOutsideTimeWindow(scheduleRule) {
      if (!scheduleRule || !scheduleRule.time_window) return false;
      const start = parseHmToMinutes(scheduleRule.time_window.start);
      const end = parseHmToMinutes(scheduleRule.time_window.end);
      if (start === null || end === null) return false;
      
      const now = getLocalNowMinutes();
      if (start <= end) {
        // Standard window (e.g. 09:00 to 17:00)
        return now < start || now > end;
      } else {
        // Wraps midnight (e.g. 22:00 to 06:00)
        // Inside if >= start OR <= end
        // Outside if > end AND < start
        return now > end && now < start;
      }
    }

    function formatTimeWindow(scheduleRule) {
      if (!scheduleRule || !scheduleRule.time_window) return "";
      const s = scheduleRule.time_window.start;
      const e = scheduleRule.time_window.end;
      if (!s || !e) return "";
      return `${s}–${e}`;
    }

    // --- Date Helpers ---

    function toYmdLocal(d = new Date()) {
      const year = d.getFullYear();
      const month = String(d.getMonth() + 1).padStart(2, '0');
      const day = String(d.getDate()).padStart(2, '0');
      return `${year}-${month}-${day}`;
    }

    function parseYmdToLocalDate(ymd) {
      if (!ymd || typeof ymd !== 'string') return null;
      const parts = ymd.split('-');
      if (parts.length !== 3) return null;
      const d = new Date(parseInt(parts[0]), parseInt(parts[1]) - 1, parseInt(parts[2]));
      if (isNaN(d.getTime())) return null;
      return d;
    }

    function isOnOrBeforeYmd(ymd, refYmd) {
      if (!ymd || !refYmd) return false;
      return ymd <= refYmd; // Lexicographical comparison works for YYYY-MM-DD
    }

    function addDaysYmd(refYmd, n) {
      const d = parseYmdToLocalDate(refYmd);
      if (!d) return null;
      d.setDate(d.getDate() + n);
      return toYmdLocal(d);
    }

    function safeInt(v, fallback = 999999) {
      const i = parseInt(v, 10);
      return isNaN(i) ? fallback : i;
    }

    // --------------------

    function isSnoozedNow(metadata) {
      if (!metadata || !metadata.snoozed_until) return false;
      const ms = parseIsoUtcMillis(metadata.snoozed_until);
      return ms > Date.now();
    }

    function renderDayReview(metrics) {
      const existing = document.getElementById("planner-day-review");
      if (existing) existing.remove();

      const container = document.querySelector(".planner-shell");
      if (!container) return;

      const strip = document.createElement("div");
      strip.id = "planner-day-review";
      strip.className = "planner-card";
      strip.style.padding = "0.5rem 1rem";
      strip.style.marginBottom = "1rem";
      strip.style.fontSize = "0.85rem";
      strip.style.color = "var(--text-soft)";
      strip.style.display = "flex";
      strip.style.justifyContent = "center";
      strip.style.gap = "1rem";
      strip.style.flexWrap = "wrap";
      strip.style.background = "rgba(255, 255, 255, 0.03)";
      strip.style.border = "1px solid var(--border)";

      const parts = [];
      if (metrics.completed > 0) parts.push(`<span style="color:var(--text-main)">Completed: ${metrics.completed}</span>`);
      if (metrics.inProgress > 0) parts.push(`<span style="color:var(--accent)">In progress: ${metrics.inProgress}</span>`);
      if (metrics.snoozed > 0) parts.push(`<span>Snoozed: ${metrics.snoozed}</span>`);
      if (metrics.overdue > 0) parts.push(`<span style="color:var(--accent)">Overdue: ${metrics.overdue}</span>`);
      if (metrics.tomorrow > 0) parts.push(`<span>Tomorrow: ${metrics.tomorrow}</span>`);

      if (parts.length === 0) {
         strip.textContent = "No activity yet today.";
      } else {
         strip.innerHTML = parts.join(" · ");
      }

      // Insert after brief
      const brief = document.getElementById("planner-brief");
      if (brief && brief.parentNode === container && brief.nextSibling) {
         container.insertBefore(strip, brief.nextSibling);
      } else {
         container.prepend(strip);
      }
    }

    function renderGoalTasks(goalTasks, snoozedCollector = null, completedCollector = null, overdueCollector = null, laterCollector = null, tomorrowCounter = null) {
      const goalCount = Array.isArray(goalTasks) ? goalTasks.length : 0;
      othelloState.todayPlannerGoalTasks = Array.isArray(goalTasks) ? goalTasks : [];
      if (plannerGoalsList) {
        plannerGoalsList.innerHTML = "";
      }
      if (plannerGoalsCount) {
        plannerGoalsCount.textContent = `${goalCount} item${goalCount === 1 ? "" : "s"}`;
      }
      if (!plannerGoalsList) {
        console.warn("[Today Planner] goal list element missing");
        return;
      }

      if (!goalCount) {
        plannerGoalsList.innerHTML = `<div class="planner-empty">No goal tasks scheduled.</div>`;
      } else {
        let visibleCount = 0;
        goalTasks.forEach(item => {
          if (item.status === "complete") {
            if (completedCollector) completedCollector.push(item);
            return;
          }
          if (isSnoozedNow(item.metadata)) {
            if (snoozedCollector) snoozedCollector.push(item);
            return;
          }

          // Check reschedule_to (only if not collecting for snoozed/completed)
          if (!snoozedCollector && !completedCollector) {
             const rTo = item.reschedule_to || (item.metadata && item.metadata.reschedule_to);
             if (rTo) {
                if (rTo === tomorrowCounter?.ymd) {
                   // Do not hide if in_progress
                   if (item.status !== "in_progress") {
                      if (tomorrowCounter) tomorrowCounter.count++;
                      return;
                   }
                }
                if (isOnOrBeforeYmd(rTo, tomorrowCounter?.planDate) && rTo !== tomorrowCounter?.planDate) {
                   if (overdueCollector) overdueCollector.push(item);
                   return;
                }
             }
             
             // Check time window (skip if in_progress)
             if (item.status !== "in_progress" && isOutsideTimeWindow(item.schedule_rule || (item.metadata && item.metadata.schedule_rule))) {
               if (laterCollector) laterCollector.push(item);
               return;
             }
          }

          visibleCount++;
          const task = document.createElement("div");
          task.className = "planner-task";

          const label = (item.metadata && item.metadata.label) || item.label || item.description || "(unnamed task)";

          const taskLeft = document.createElement("div");
          taskLeft.innerHTML = `
            <div class="planner-task__label">${label}</div>
            <div class="planner-task__meta">${item.section_hint || item.section || "goal"} · effort ${item.effort || "n/a"}</div>
          `;

          const taskRight = document.createElement("div");
          taskRight.className = "planner-block__right";
          taskRight.appendChild(createStatusChip(item.status, item));
          if (item.item_id) {
            taskRight.appendChild(buildPlannerActions(item));
          }

          task.appendChild(taskLeft);
          task.appendChild(taskRight);
          plannerGoalsList.appendChild(task);
        });
        if (visibleCount === 0 && goalCount > 0) {
           plannerGoalsList.innerHTML = `<div class="planner-empty">All goal tasks snoozed.</div>`;
        }
      }

      console.log("[Today Planner] renderGoalTasks", {
        goalCount,
        headerEl: plannerGoalsCount,
        headerText: plannerGoalsCount ? plannerGoalsCount.textContent : null,
        listEl: plannerGoalsList,
        listChildren: plannerGoalsList ? plannerGoalsList.children.length : null,
      });
    }

    function renderPlannerSections(plan, goalTasksOverride = null) {
      const sections = (plan.sections || {});
      const routines = sections.routines || [];
      const goalTasks = goalTasksOverride !== null ? goalTasksOverride : (sections.goal_tasks || []);
      const snoozedItems = [];
      const completedItems = [];
      const laterItems = [];
      const overdueItems = [];
      const tomorrowCounter = { count: 0, ymd: null, planDate: null };
      let inProgressCount = 0;

      const planDateYmd = plan.plan_date || toYmdLocal();
      const tomorrowYmd = addDaysYmd(planDateYmd, 1);
      tomorrowCounter.ymd = tomorrowYmd;
      tomorrowCounter.planDate = planDateYmd;

      plannerRoutinesList.innerHTML = "";
      if (!routines.length) {
        plannerRoutinesCount.textContent = "0 items";
        plannerRoutinesList.innerHTML = `<div class="planner-empty">No routines planned yet.</div>`;
      } else {
        let visibleRoutines = 0;
        routines.forEach(item => {
          if (item.status === "complete") {
            completedItems.push(item);
            return;
          }
          if (isSnoozedNow(item.metadata)) {
            snoozedItems.push(item);
            return;
          }
          if (item.status === "in_progress") {
             inProgressCount++;
          }

          // Check reschedule_to
          const rTo = item.reschedule_to || (item.metadata && item.metadata.reschedule_to);
          if (rTo) {
             if (rTo === tomorrowYmd) {
                // Do not hide if in_progress
                if (item.status !== "in_progress") {
                   tomorrowCounter.count++;
                   return; 
                }
             }
             if (isOnOrBeforeYmd(rTo, planDateYmd) && rTo !== planDateYmd) {
                overdueItems.push(item);
                return;
             }
          }
          
          // Check time window (skip if in_progress)
          if (item.status !== "in_progress" && isOutsideTimeWindow(item.schedule_rule || (item.metadata && item.metadata.schedule_rule))) {
            laterItems.push(item);
            return;
          }

          visibleRoutines++;
          const block = document.createElement("div");
          block.className = "planner-block";
          const header = document.createElement("div");
          header.className = "planner-block__header";

          const headerLeft = document.createElement("div");
          
          // Schedule badge
          let scheduleBadge = "";
          const sched = item.schedule_rule || (item.metadata && item.metadata.schedule_rule);
          if (sched) {
             const parts = [];
             if (sched.days && sched.days.length > 0 && sched.days.length < 7) {
                parts.push(sched.days.map(d => d.slice(0,3)).join(","));
             }
             if (sched.part_of_day && sched.part_of_day !== "any") {
                parts.push(sched.part_of_day);
             }
             if (sched.time_window && sched.time_window.start) {
                parts.push(`${sched.time_window.start}-${sched.time_window.end || ""}`);
             }
             if (parts.length > 0) {
                scheduleBadge = `<span style="font-size:0.7rem; color:var(--accent); border:1px solid var(--accent-soft); padding:0.1rem 0.3rem; border-radius:4px; margin-left:0.5rem;">${parts.join(" · ")}</span>`;
             }
          }

          headerLeft.innerHTML = `
            <div class="planner-block__title">${item.name || item.label || "Routine"}${scheduleBadge}</div>
            <div class="planner-block__meta">${item.section_hint || item.section || "any"} · ${item.variant || item.type || "routine"}</div>
          `;

          const headerRight = document.createElement("div");
          headerRight.className = "planner-block__right";
          headerRight.appendChild(createStatusChip(item.status, item));
          if (item.item_id) {
            headerRight.appendChild(buildPlannerActions(item));
          }

          header.appendChild(headerLeft);
          header.appendChild(headerRight);
          block.appendChild(header);

          const stepsWrap = document.createElement("div");
          stepsWrap.className = "planner-steps";
          const steps = item.steps || [];
          if (steps.length === 0) {
            stepsWrap.innerHTML = `<div class="planner-empty">No steps listed.</div>`;
          } else {
            let visibleSteps = 0;
            steps.forEach(step => {
              if (step.status === "complete") {
                completedItems.push(step);
                return;
              }
              if (isSnoozedNow(step.metadata)) {
                snoozedItems.push(step);
                return;
              }
              if (step.status === "in_progress") {
                 inProgressCount++;
              }
              
              // Inherit schedule from parent if missing
              const stepSched = step.schedule_rule || (step.metadata && step.metadata.schedule_rule) || sched;
              if (step.status !== "in_progress" && isOutsideTimeWindow(stepSched)) {
                // Attach parent info for context in Later list
                step._parentLabel = item.name || item.label;
                step._scheduleRule = stepSched;
                laterItems.push(step);
                return;
              }

              visibleSteps++;
              const stepRow = document.createElement("div");
              stepRow.className = "planner-step";

              const stepLeft = document.createElement("div");
              stepLeft.innerHTML = `
                <div class="planner-step__label">${step.label || "Step"}</div>
                <div class="planner-step__meta">${step.energy_cost || "energy"} · ${step.friction || "friction"}</div>
              `;

              const stepRight = document.createElement("div");
              stepRight.className = "planner-block__right";
              stepRight.appendChild(createStatusChip(step.status, step));
              if (step.item_id) {
                stepRight.appendChild(buildPlannerActions(step));
              }

              stepRow.appendChild(stepLeft);
              stepRow.appendChild(stepRight);
              stepsWrap.appendChild(stepRow);
            });
            if (visibleSteps === 0 && steps.length > 0) {
               stepsWrap.innerHTML = `<div class="planner-empty">All steps snoozed or later.</div>`;
            }
          }

          block.appendChild(stepsWrap);
          plannerRoutinesList.appendChild(block);
        });
        plannerRoutinesCount.textContent = `${visibleRoutines} item${visibleRoutines === 1 ? "" : "s"}`;
        if (visibleRoutines === 0 && routines.length > 0) {
           plannerRoutinesList.innerHTML = `<div class="planner-empty">All routines snoozed or later.</div>`;
        }
      }
      
      // Count in-progress from goal tasks too
      goalTasks.forEach(t => {
         if (t.status === "in_progress" && !isSnoozedNow(t.metadata)) {
            inProgressCount++;
         }
      });

      renderGoalTasks(goalTasks, snoozedItems, completedItems, overdueItems, laterItems, tomorrowCounter);

      // Render Day Review
      renderDayReview({
         completed: completedItems.length,
         inProgress: inProgressCount,
         snoozed: snoozedItems.length,
         overdue: overdueItems.length,
         tomorrow: tomorrowCounter.count
      });

      // Render Tomorrow Preview
      const existingTomorrow = document.getElementById("planner-tomorrow-preview");
      if (existingTomorrow) existingTomorrow.remove();
      
      if (tomorrowCounter.count > 0) {
         const tmDiv = document.createElement("div");
         tmDiv.id = "planner-tomorrow-preview";
         tmDiv.style.fontSize = "0.85rem";
         tmDiv.style.color = "var(--text-soft)";
         tmDiv.style.marginBottom = "0.5rem";
         tmDiv.style.textAlign = "center";
         tmDiv.textContent = `Tomorrow: ${tomorrowCounter.count} carried item${tomorrowCounter.count === 1 ? "" : "s"}`;
         
         // Insert after the main card (today-plan-card)
         const mainCard = document.getElementById("today-plan-card");
         if (mainCard && mainCard.parentNode) {
            mainCard.parentNode.insertBefore(tmDiv, mainCard.nextSibling);
         }
      }

      // Render Overdue Section
      const existingOverdue = document.getElementById("planner-overdue-section");
      if (existingOverdue) existingOverdue.remove();

      if (overdueItems.length > 0) {
        const overdueSection = document.createElement("div");
        overdueSection.id = "planner-overdue-section";
        overdueSection.className = "planner-card";
        overdueSection.style.marginTop = "1rem";
        overdueSection.style.borderLeft = "3px solid var(--accent)"; // Highlight
        
        const header = document.createElement("div");
        header.className = "planner-card__header";
        header.style.cursor = "pointer";
        header.innerHTML = `
          <div>
            <div class="planner-section__title" style="color:var(--accent);">Overdue</div>
            <div class="planner-section__count">${overdueItems.length} item${overdueItems.length === 1 ? "" : "s"}</div>
          </div>
          <div style="font-size:0.8rem; color:var(--text-soft);">▼</div>
        `;
        overdueSection.appendChild(header);

        const list = document.createElement("div");
        list.className = "planner-blocks";
        // Default expanded for Overdue
        list.style.display = "block"; 
        header.lastElementChild.textContent = "▲";

        header.onclick = () => {
           const isHidden = list.style.display === "none";
           list.style.display = isHidden ? "block" : "none";
           header.lastElementChild.textContent = isHidden ? "▲" : "▼";
        };
        
        overdueItems.forEach(item => {
          const row = document.createElement("div");
          row.className = "planner-task";
          
          const label = (item.metadata && item.metadata.label) || item.label || item.name || item.description || "(unnamed)";
          const rTo = item.reschedule_to || (item.metadata && item.metadata.reschedule_to);
          const context = item._parentLabel ? `From ${item._parentLabel}` : (item.section_hint || "Routine");

          const left = document.createElement("div");
          left.innerHTML = `
            <div class="planner-task__label">${label} <span style="font-size:0.7rem; color:var(--accent); border:1px solid var(--accent-soft); padding:0 0.3rem; border-radius:4px; margin-left:0.3rem;">Overdue ${rTo || ""}</span></div>
            <div class="planner-task__meta">${context}</div>
          `;
          
          const right = document.createElement("div");
          right.className = "planner-block__right";
          right.appendChild(createStatusChip(item.status, item));
          if (item.item_id) {
            right.appendChild(buildPlannerActions(item));
          }
          
          row.appendChild(left);
          row.appendChild(right);
          list.appendChild(row);
        });
        
        overdueSection.appendChild(list);
        const shell = document.querySelector(".planner-shell");
        if (shell) shell.appendChild(overdueSection);
      }

      // Render Later Today Section
      const existingLater = document.getElementById("planner-later-section");
      if (existingLater) existingLater.remove();

      if (laterItems.length > 0) {
        const laterSection = document.createElement("div");
        laterSection.id = "planner-later-section";
        laterSection.className = "planner-card";
        laterSection.style.marginTop = "1rem";
        laterSection.style.opacity = "0.8";
        
        const header = document.createElement("div");
        header.className = "planner-card__header";
        header.style.cursor = "pointer";
        header.innerHTML = `
          <div>
            <div class="planner-section__title">Later Today</div>
            <div class="planner-section__count">${laterItems.length} item${laterItems.length === 1 ? "" : "s"}</div>
          </div>
          <div style="font-size:0.8rem; color:var(--text-soft);">▼</div>
        `;
        laterSection.appendChild(header);

        const list = document.createElement("div");
        list.className = "planner-blocks";
        list.style.display = "none"; // Default collapsed

        header.onclick = () => {
           const isHidden = list.style.display === "none";
           list.style.display = isHidden ? "block" : "none";
           header.lastElementChild.textContent = isHidden ? "▲" : "▼";
        };
        
        laterItems.forEach(item => {
          const row = document.createElement("div");
          row.className = "planner-task"; // Reuse task style
          
          const label = (item.metadata && item.metadata.label) || item.label || item.name || item.description || "(unnamed)";
          const sched = item._scheduleRule || item.schedule_rule || (item.metadata && item.metadata.schedule_rule);
          const timeRange = formatTimeWindow(sched);
          const context = item._parentLabel ? `From ${item._parentLabel}` : (item.section_hint || "Routine");

          const left = document.createElement("div");
          left.innerHTML = `
            <div class="planner-task__label">${label} <span style="font-size:0.7rem; color:var(--text-soft); border:1px solid var(--border); padding:0 0.3rem; border-radius:4px; margin-left:0.3rem;">Later ${timeRange}</span></div>
            <div class="planner-task__meta">${context}</div>
          `;
          
          const right = document.createElement("div");
          right.className = "planner-block__right";
          right.appendChild(createStatusChip(item.status, item));
          if (item.item_id) {
            right.appendChild(buildPlannerActions(item));
          }
          
          row.appendChild(left);
          row.appendChild(right);
          list.appendChild(row);
        });
        
        laterSection.appendChild(list);
        const shell = document.querySelector(".planner-shell");
        if (shell) shell.appendChild(laterSection);
      }

      // Render Snoozed Section
      const existingSnoozed = document.getElementById("planner-snoozed-section");
      if (existingSnoozed) existingSnoozed.remove();

      if (snoozedItems.length > 0) {
        const snoozedSection = document.createElement("div");
        snoozedSection.id = "planner-snoozed-section";
        snoozedSection.className = "planner-card";
        snoozedSection.style.marginTop = "1rem";
        snoozedSection.style.opacity = "0.7";
        
        const header = document.createElement("div");
        header.className = "planner-card__header";
        header.innerHTML = `
          <div>
            <div class="planner-section__title">Snoozed</div>
            <div class="planner-section__count">${snoozedItems.length} item${snoozedItems.length === 1 ? "" : "s"}</div>
          </div>
        `;
        snoozedSection.appendChild(header);

        const list = document.createElement("div");
        list.className = "planner-blocks";
        
        snoozedItems.forEach(item => {
          const row = document.createElement("div");
          row.className = "planner-task"; // Reuse task style
          
          const label = (item.metadata && item.metadata.label) || item.label || item.name || item.description || "(unnamed)";
          let until = "later";
          if (item.metadata && item.metadata.snoozed_until) {
             const ms = parseIsoUtcMillis(item.metadata.snoozed_until);
             if (ms > 0) until = new Date(ms).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
          }

          const left = document.createElement("div");
          left.innerHTML = `
            <div class="planner-task__label">${label}</div>
            <div class="planner-task__meta">Snoozed until ${until}</div>
          `;
          
          const right = document.createElement("div");
          right.className = "planner-block__right";
          
          const wakeBtn = document.createElement("button");
          wakeBtn.className = "planner-action-btn";
          wakeBtn.textContent = "Wake";
          wakeBtn.onclick = async () => {
             wakeBtn.textContent = "...";
             wakeBtn.disabled = true;
             try {
               const payload = {
                 status: item.status || "planned",
                 item_id: item.item_id || item.id,
                 snooze_minutes: 0 // Explicitly clear snooze
               };
               const resp = await fetch(PLAN_UPDATE_API, {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  credentials: "include",
                  body: JSON.stringify(payload),
               });
               if (!resp.ok) {
                 throw new Error("Wake failed");
               }
               await loadTodayPlanner();
             } catch (e) {
               console.error("Wake failed", e);
               wakeBtn.textContent = "Error";
             }
          };
          
          right.appendChild(wakeBtn);
          row.appendChild(left);
          row.appendChild(right);
          list.appendChild(row);
        });
        
        snoozedSection.appendChild(list);
        // Append to planner shell
        const shell = document.querySelector(".planner-shell");
        if (shell) shell.appendChild(snoozedSection);
      }

      // Render Completed Section
      const existingCompleted = document.getElementById("planner-completed-section");
      if (existingCompleted) existingCompleted.remove();

      if (completedItems.length > 0) {
         // Sort by completed_at desc
         completedItems.sort((a, b) => {
            const ta = parseIsoUtcMillis(a?.metadata?.completed_at);
            const tb = parseIsoUtcMillis(b?.metadata?.completed_at);
            return tb - ta;
         });

         const completedSection = document.createElement("div");
         completedSection.id = "planner-completed-section";
         completedSection.className = "planner-card";
         completedSection.style.marginTop = "1rem";
         completedSection.style.opacity = "0.6";
         
         const header = document.createElement("div");
         header.className = "planner-card__header";
         header.style.cursor = "pointer";
         header.innerHTML = `
           <div>
             <div class="planner-section__title">Completed</div>
             <div class="planner-section__count">${completedItems.length} item${completedItems.length === 1 ? "" : "s"}</div>
           </div>
           <div style="font-size:0.8rem; color:var(--text-soft);">▼</div>
         `;
         completedSection.appendChild(header);

         const list = document.createElement("div");
         list.className = "planner-blocks";
         list.style.display = "none"; // Default collapsed

         header.onclick = () => {
            const isHidden = list.style.display === "none";
            list.style.display = isHidden ? "block" : "none";
            header.lastElementChild.textContent = isHidden ? "▲" : "▼";
         };

         completedItems.forEach(item => {
            const row = document.createElement("div");
            row.className = "planner-task";
            
            const label = (item.metadata && item.metadata.label) || item.label || item.name || item.description || "(unnamed)";
            const completedAt = (item.metadata && item.metadata.completed_at) 
               ? new Date(item.metadata.completed_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) 
               : "";

            const left = document.createElement("div");
            left.innerHTML = `
               <div class="planner-task__label" style="text-decoration: line-through; color: var(--text-soft);">${label}</div>
               <div class="planner-task__meta">Completed ${completedAt}</div>
            `;
            
            const right = document.createElement("div");
            right.className = "planner-block__right";
            
            const reopenBtn = document.createElement("button");
            reopenBtn.className = "planner-action-btn";
            reopenBtn.textContent = "Reopen";
            reopenBtn.onclick = async (e) => {
               e.stopPropagation();
               const originalText = reopenBtn.textContent;
               reopenBtn.textContent = "...";
               reopenBtn.disabled = true;
               try {
                  const payload = {
                     status: "planned",
                     item_id: item.item_id || item.id
                  };
                  const resp = await fetch(PLAN_UPDATE_API, {
                     method: "POST",
                     headers: { "Content-Type": "application/json" },
                     credentials: "include",
                     body: JSON.stringify(payload),
                  });
                  if (!resp.ok) throw new Error("Reopen failed");
                  await loadTodayPlanner();
               } catch (err) {
                  console.error(err);
                  reopenBtn.textContent = "Reopen";
                  reopenBtn.disabled = false;
               }
            };
            
            right.appendChild(reopenBtn);
            row.appendChild(left);
            row.appendChild(right);
            list.appendChild(row);
         });
         
         completedSection.appendChild(list);
         const shell = document.querySelector(".planner-shell");
         if (shell) shell.appendChild(completedSection);
      }

      console.log("[Today Planner] renderPlannerSections", {
        goalCount: goalTasks.length,
        snoozedCount: snoozedItems.length,
        headerText: plannerGoalsCount ? plannerGoalsCount.textContent : null,
        listChildren: plannerGoalsList ? plannerGoalsList.children.length : null,
      });
    }

    function renderCurrentFocus(plan) {
      // 1. Find current item
      const allItems = [];
      const sections = plan.sections || {};
      (sections.routines || []).forEach(r => {
         if (r.steps && r.steps.length) {
           r.steps.forEach(s => allItems.push({...s, _section: 'Routine Step', _parent: r.label}));
         } else {
           allItems.push({...r, _section: 'Routine'});
         }
      });
      (sections.goal_tasks || []).forEach(t => allItems.push({...t, _section: 'Goal Task'}));
      (sections.optional || []).forEach(t => allItems.push({...t, _section: 'Optional'}));
      
      const currentItem = allItems.find(item => 
        (item.status === 'in_progress') && !isSnoozedNow(item.metadata)
      );

      const existingCard = document.getElementById("current-focus-card");
      if (existingCard) existingCard.remove();
      
      const existingToggle = document.getElementById("planner-sections-toggle");
      if (existingToggle) existingToggle.remove();

      if (!currentItem) {
        togglePlannerSections(true);
        return null;
      }

      // 2. Render Card
      const container = document.querySelector(".planner-shell");
      const card = document.createElement("div");
      card.id = "current-focus-card";
      card.className = "planner-card";
      card.style.border = "1px solid var(--accent)";
      card.style.background = "rgba(125, 211, 252, 0.08)";
      card.style.marginBottom = "1rem";
      
      const label = (currentItem.metadata && currentItem.metadata.label) || currentItem.label || currentItem.name || "Current Task";
      const itemId = currentItem.item_id || currentItem.id;
      const context = currentItem._section + (currentItem._parent ? ` · ${currentItem._parent}` : "");
      
      card.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
          <div class="planner-headline" style="font-size: 0.9rem; color: var(--accent); text-transform: uppercase; letter-spacing: 0.05em;">
             Current Focus
          </div>
          <div style="font-size:0.8rem; color:var(--text-soft);">${context}</div>
        </div>
        <div class="planner-headline" style="font-size: 1.3rem; margin-bottom: 1rem; line-height:1.3;">${label}</div>
      `;

      const actionsDiv = document.createElement("div");
      actionsDiv.className = "planner-actions";
      actionsDiv.style.gap = "0.5rem";
      actionsDiv.style.flexWrap = "wrap";

      const makeBtn = (text, onClick, primary = false) => {
        const btn = document.createElement("button");
        btn.className = "planner-action-btn";
        btn.textContent = text;
        if (primary) {
          btn.style.background = "var(--accent)";
          btn.style.color = "var(--bg-1)";
          btn.style.borderColor = "var(--accent)";
          btn.style.fontWeight = "600";
        }
        btn.onclick = onClick;
        return btn;
      };

      actionsDiv.appendChild(makeBtn("Done", () => updateItemStatus(itemId, 'complete'), true));
      actionsDiv.appendChild(makeBtn("Revert", () => updateItemStatus(itemId, 'planned')));
      actionsDiv.appendChild(makeBtn("+15m", () => snoozeItem(itemId, 15)));
      actionsDiv.appendChild(makeBtn("+30m", () => snoozeItem(itemId, 30)));
      actionsDiv.appendChild(makeBtn("+1h", () => snoozeItem(itemId, 60)));

      card.appendChild(actionsDiv);

      // Insert after brief
      const brief = document.getElementById("planner-brief");
      if (brief && brief.parentNode === container && brief.nextSibling) {
        container.insertBefore(card, brief.nextSibling);
      } else {
        container.prepend(card);
      }

      // 3. Collapse other sections
      togglePlannerSections(false);

      // 4. Add Toggle
      const toggleBtn = document.createElement("button");
      toggleBtn.id = "planner-sections-toggle";
      toggleBtn.className = "planner-action-btn";
      toggleBtn.style.margin = "0 auto 1rem auto";
      toggleBtn.style.display = "block";
      toggleBtn.textContent = "Show all sections";
      toggleBtn.onclick = () => {
        const probe = document.getElementById("today-plan-card");
        const areHidden = probe ? (probe.style.display === "none") : false;
        togglePlannerSections(areHidden);
        toggleBtn.textContent = areHidden ? "Hide all sections" : "Show all sections";
      };
      
      card.after(toggleBtn);
      
      return currentItem;
    }

    function togglePlannerSections(show) {
      const ids = ["today-plan-card", "planner-routines", "planner-goals", "planner-snoozed-section", "planner-completed-section", "planner-later-section", "planner-overdue-section"];
      ids.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.style.display = show ? "" : "none";
      });
    }

    function renderNextAction(plan, excludeIds = []) {
      let nextAction = plan.next_action;
      
      if (nextAction && excludeIds.includes(nextAction.item_id || nextAction.id)) {
        nextAction = null;
      }
      
      // Fallback to client-side if server didn't provide it (legacy support)
      if (!nextAction) {
        // Compute client-side
        const allItems = [];
        const sections = plan.sections || {};
        
        // Date context
        const planDateYmd = plan.plan_date || toYmdLocal();
        const tomorrowYmd = addDaysYmd(planDateYmd, 1);

        (sections.routines || []).forEach(r => {
           if (r.steps && r.steps.length) {
             // Pass parent schedule rule if needed
             const parentSched = r.schedule_rule || (r.metadata && r.metadata.schedule_rule);
             r.steps.forEach(s => {
               // Ensure step has schedule context for filtering
               if (!s.schedule_rule && !s.metadata?.schedule_rule && parentSched) {
                 s._inheritedSchedule = parentSched;
               }
               allItems.push(s);
             });
           } else {
             allItems.push(r);
           }
        });
        (sections.goal_tasks || []).forEach(t => allItems.push(t));
        
        // Filter
        const candidates = allItems.filter(item => {
           if (excludeIds.includes(item.item_id || item.id)) return false;
           if (isSnoozedNow(item.metadata)) return false;
           
           // Skip "tomorrow" items
           const rTo = item.reschedule_to || (item.metadata && item.metadata.reschedule_to);
           if (rTo === tomorrowYmd) return false;

           // Skip "later" items unless in_progress
           const sched = item.schedule_rule || (item.metadata && item.metadata.schedule_rule) || item._inheritedSchedule;
           if (item.status !== "in_progress" && isOutsideTimeWindow(sched)) return false;

           const s = (item.status || "planned").toLowerCase();
           return s === "planned" || s === "in_progress";
        });
        
        // Sort: in_progress first, then Overdue, then by order
        candidates.sort((a, b) => {
           const aStatus = (a.status || "").toLowerCase();
           const bStatus = (b.status || "").toLowerCase();
           
           // 1. In Progress
           if (aStatus === "in_progress" && bStatus !== "in_progress") return -1;
           if (bStatus === "in_progress" && aStatus !== "in_progress") return 1;
           
           // 2. Overdue
           const aRTo = a.reschedule_to || (a.metadata && a.metadata.reschedule_to);
           const bRTo = b.reschedule_to || (b.metadata && b.metadata.reschedule_to);
           
           const aIsOverdue = aRTo && isOnOrBeforeYmd(aRTo, planDateYmd) && aRTo !== planDateYmd;
           const bIsOverdue = bRTo && isOnOrBeforeYmd(bRTo, planDateYmd) && bRTo !== planDateYmd;
           
           if (aIsOverdue && !bIsOverdue) return -1;
           if (!aIsOverdue && bIsOverdue) return 1;

           // 3. Prefer non-later (soft time window)
           const aSched = a.schedule_rule || (a.metadata && a.metadata.schedule_rule) || a._inheritedSchedule;
           const bSched = b.schedule_rule || (b.metadata && b.metadata.schedule_rule) || b._inheritedSchedule;
           const aLater = isOutsideTimeWindow(aSched);
           const bLater = isOutsideTimeWindow(bSched);
           
           if (!aLater && bLater) return -1;
           if (aLater && !bLater) return 1;

           // 4. Order Index (safe int)
           const aIdx = safeInt(a.order_index);
           const bIdx = safeInt(b.order_index);
           if (aIdx !== bIdx) return aIdx - bIdx;

           // 5. Tie-break by ID
           const aId = a.item_id || a.id || "";
           const bId = b.item_id || b.id || "";
           return aId.localeCompare(bId);
        });
        
        if (candidates.length > 0) {
           nextAction = candidates[0];
        }
      }
      
      const existingCard = document.getElementById("next-action-card");
      if (existingCard) existingCard.remove();

      if (!nextAction) return; // Nothing to do
      
      // Render card
      const container = document.querySelector(".planner-shell");
      
      const card = document.createElement("div");
      card.id = "next-action-card";
      card.className = "planner-card";
      card.style.marginBottom = "0"; // Let gap handle it
      card.style.border = "1px solid var(--accent)";
      card.style.background = "rgba(125, 211, 252, 0.05)";
      
      const label = (nextAction.metadata && nextAction.metadata.label) || nextAction.label || nextAction.name || "Next Action";
      const status = nextAction.status || "planned";
      const itemId = nextAction.item_id || nextAction.id;
      
      card.innerHTML = `
        <div class="planner-headline" style="font-size: 0.9rem; color: var(--accent); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">
           ${status === "in_progress" ? "Current Focus" : "Up Next"}
        </div>
        <div class="planner-headline" style="font-size: 1.2rem; margin-bottom: 1rem;">${label}</div>
        <div class="planner-actions" style="gap: 0.5rem;">
           ${status !== "in_progress" ? `<button class="planner-action-btn" style="border-color: var(--accent); color: var(--accent);" onclick="updateItemStatus('${itemId}', 'in_progress')">Start</button>` : ""}
           <button class="planner-action-btn" onclick="updateItemStatus('${itemId}', 'complete')">Done</button>
           <button class="planner-action-btn" onclick="snoozeItem('${itemId}', 15)">+15m</button>
           <button class="planner-action-btn" onclick="snoozeItem('${itemId}', 60)">+1h</button>
        </div>
      `;
      
      // Insert after brief card (first child of shell usually)
      if (container && container.children.length > 0) {
         container.insertBefore(card, container.children[1] || null);
      } else if (container) {
         container.appendChild(card);
      }
    }
    
    window.updateItemStatus = async (itemId, status) => {
       if (isReadOnlyDayView()) {
           console.warn("Cannot update status in read-only view");
           return;
       }
       try {
         // Invalidate week view cache
         if (typeof weekViewCache !== 'undefined') {
             for (const key in weekViewCache) delete weekViewCache[key];
         }

         const resp = await fetch(PLAN_UPDATE_API, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify({ item_id: itemId, status }),
         });
         if (resp.ok) await loadTodayPlanner();
       } catch(e) { console.error(e); }
    };
    
    window.snoozeItem = async (itemId, minutes) => {
       if (isReadOnlyDayView()) {
           console.warn("Cannot snooze in read-only view");
           return;
       }
       try {
         // Invalidate week view cache
         if (typeof weekViewCache !== 'undefined') {
             for (const key in weekViewCache) delete weekViewCache[key];
         }

         const resp = await fetch(PLAN_UPDATE_API, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify({ item_id: itemId, snooze_minutes: minutes }),
         });
         if (resp.ok) await loadTodayPlanner();
       } catch(e) { console.error(e); }
    };

    // --- Week View Logic ---
    const weekViewCache = {}; 
    let isWeekViewActive = false;
    let dayViewDateYmd = null; // null means "today/live"
    let plannerPollId = null;
    let plannerAbort = null;
    let weekAbort = null;
    let routinesAbort = null;
    let activeWeekDrilldownYmd = null;
    let plannerListenersBound = false;
    const PLANNER_POLL_MS = 60000;

    function isAbortError(err) {
      return err && (err.name === "AbortError" || err.code === 20);
    }

    function logPlannerDebug(message, payload) {
      if (!BOOT_DEBUG) return;
      if (payload) {
        console.log(message, payload);
      } else {
        console.log(message);
      }
    }

    function abortPlannerRequests(reason) {
      if (!plannerAbort) return;
      plannerAbort.abort();
      plannerAbort = null;
      logPlannerDebug("[Today Planner] aborted in-flight request", { reason });
    }

    function abortWeekRequests(reason) {
      if (!weekAbort) return;
      weekAbort.abort();
      weekAbort = null;
      logPlannerDebug("[Week View] aborted in-flight request", { reason });
    }

    function abortRoutineRequests(reason) {
      if (!routinesAbort) return;
      routinesAbort.abort();
      routinesAbort = null;
      logPlannerDebug("[Routine Planner] aborted in-flight request", { reason });
    }

    function stopPlannerPolling(reason) {
      if (plannerPollId) {
        clearInterval(plannerPollId);
        plannerPollId = null;
        logPlannerDebug("[Today Planner] polling stopped", { reason });
      }
    }

    function startPlannerPolling() {
      stopPlannerPolling("restart");
      if (!PLANNER_POLL_MS || PLANNER_POLL_MS < 1000) return;
      plannerPollId = setInterval(() => {
        if (document.hidden) return;
        if (othelloState.currentView !== "today-planner") return;
        loadTodayPlanner();
      }, PLANNER_POLL_MS);
      logPlannerDebug("[Today Planner] polling started", { intervalMs: PLANNER_POLL_MS });
    }

    function getWeekStartYmd(refDate = new Date()) {
      // Monday-start, local time
      const d = new Date(refDate);
      const day = d.getDay(); // 0=Sun, 1=Mon...
      const diff = day === 0 ? -6 : 1 - day; // Delta to Monday
      d.setDate(d.getDate() + diff);
      return toYmdLocal(d);
    }

    function getWeekDays() {
      const startYmd = getWeekStartYmd();
      const days = [];
      for (let i = 0; i < 7; i++) {
        days.push(addDaysYmd(startYmd, i));
      }
      return days;
    }

    function computePlanCounts(plan) {
        let completed = 0;
        let inProgress = 0;
        let overdue = 0;
        let snoozed = 0;
        let tomorrow = 0; 
        
        const planDateYmd = plan.plan_date || (plan.date ? plan.date.split('T')[0] : new Date().toISOString().split('T')[0]);
        const d = new Date(planDateYmd);
        d.setDate(d.getDate() + 1);
        const tomorrowYmd = d.toISOString().split('T')[0];

        const allItems = [];
        const sections = plan.sections || {};
        
        const processItem = (item) => {
            allItems.push(item);
        };
        
        (sections.routines || []).forEach(r => {
            processItem(r);
            if (r.steps) r.steps.forEach(processItem);
        });
        (sections.goal_tasks || []).forEach(processItem);
        
        allItems.forEach(item => {
             if (item.status === 'complete') {
                 completed++;
                 return;
             }
             
             if (isSnoozedNow(item.metadata)) {
                 snoozed++;
                 return;
             }
             
             if (item.status === 'in_progress') {
                 inProgress++;
             }
             
             const rTo = item.reschedule_to || (item.metadata && item.metadata.reschedule_to);
             if (rTo) {
                 if (rTo === tomorrowYmd) {
                     if (item.status !== 'in_progress') {
                         tomorrow++;
                         return;
                     }
                 }
                 if (rTo < planDateYmd) {
                      overdue++;
                      return;
                 }
             }
        });
        
        return { completed, inProgress, overdue, snoozed, tomorrow };
    }

    async function fetchPlanForDate(ymd, options = {}) {
      const { signal, source } = options;
      if (othelloState.currentView !== "today-planner") return null;
      if (!isWeekViewActive && source !== "drilldown") return null;
      if (weekViewCache[ymd]) return weekViewCache[ymd];
      
      try {
        // Use peek=1 to prevent generation/mutation of plans during week view browsing
        const resp = await fetch(
          `/api/today-plan?plan_date=${ymd}&peek=1`,
          { cache: "no-store", credentials: "include", signal }
        );
        if (!resp.ok) throw new Error("Failed to fetch");
        const data = await resp.json();
        const plan = data.plan || {};
        const counts = computePlanCounts(plan);
        
        weekViewCache[ymd] = { plan, counts, fetchedAt: Date.now() };
        return weekViewCache[ymd];
      } catch (e) {
        if (isAbortError(e)) {
          logPlannerDebug("[Week View] fetch aborted", { ymd });
          return null;
        }
        console.error(`Failed to fetch plan for ${ymd}`, e);
        return null;
      }
    }

    async function loadWeekView() {
        if (othelloState.currentView !== "today-planner") return;
        if (!isWeekViewActive) return;
        if (document.hidden) return;
        
        const container = document.getElementById("week-view-content");
        const weekView = document.getElementById("planner-week-view");
        if (!container || (weekView && weekView.style.display === "none")) return;
        container.innerHTML = '<div style="padding:1rem; text-align:center; color:var(--text-soft);">Loading week...</div>';
        
        abortWeekRequests("week-view-reload");
        weekAbort = new AbortController();
        const { signal } = weekAbort;
        logPlannerDebug("[Week View] loadWeekView invoked", { view: othelloState.currentView });
        
        const days = getWeekDays();
        const results = await Promise.all(days.map(ymd => fetchPlanForDate(ymd, { signal })));
        
        if (signal.aborted) return;
        container.innerHTML = '';
        
        results.forEach((res, idx) => {
            const ymd = days[idx];
            // Fix date parsing for display to avoid timezone shifts
            const parts = ymd.split('-');
            const dateObj = new Date(parts[0], parts[1]-1, parts[2]);
            
            const dayName = dateObj.toLocaleDateString('en-US', { weekday: 'short' });
            const dateStr = dateObj.toLocaleDateString('en-US', { day: 'numeric', month: 'numeric' });
            
            const row = document.createElement("div");
            row.className = "planner-task"; 
            row.style.display = "flex";
            row.style.justifyContent = "space-between";
            row.style.alignItems = "center";
            row.style.padding = "0.75rem";
            
            if (!res) {
                row.innerHTML = `
                    <div style="font-weight:600; width: 80px;">${dayName} <span style="font-weight:400; color:var(--text-soft);">${dateStr}</span></div>
                    <div style="color:var(--text-soft);">Unavailable</div>
                `;
            } else {
                const c = res.counts;
                row.style.cursor = "pointer";
                row.onclick = () => openWeekDrilldown(ymd);
                row.innerHTML = `
                    <div style="font-weight:600; width: 80px;">${dayName} <span style="font-weight:400; color:var(--text-soft);">${dateStr}</span></div>
                    <div style="display:flex; gap:0.8rem; font-size:0.9rem;">
                        <span title="Completed" style="color:var(--text-main);">C:${c.completed}</span>
                        <span title="In Progress" style="color:#fcd34d;">IP:${c.inProgress}</span>
                        <span title="Overdue" style="color:#fca5a5;">OD:${c.overdue}</span>
                        ${c.snoozed > 0 ? `<span title="Snoozed" style="color:var(--text-soft);">S:${c.snoozed}</span>` : ''}
                        ${c.tomorrow > 0 ? `<span title="Tomorrow" style="color:var(--text-soft);">T:${c.tomorrow}</span>` : ''}
                    </div>
                `;
            }
            container.appendChild(row);
        });
    }

    function flattenPlanItemsForReadOnly(plan) {
        const items = [];
        const sections = plan.sections || {};
        
        const process = (item, section, parentLabel) => {
            items.push({
                label: (item.metadata && item.metadata.label) || item.label || item.name || "(unnamed)",
                status: item.status,
                section: section,
                parent: parentLabel,
                metadata: item.metadata,
                reschedule_to: item.reschedule_to || (item.metadata && item.metadata.reschedule_to),
                schedule_rule: item.schedule_rule || (item.metadata && item.metadata.schedule_rule)
            });
        };

        (sections.routines || []).forEach(r => {
            if (r.steps && r.steps.length) {
                r.steps.forEach(s => process(s, "Routine", r.label));
            } else {
                process(r, "Routine");
            }
        });
        (sections.goal_tasks || []).forEach(t => process(t, "Goal Task"));
        
        return items;
    }

    function closeWeekDrilldown() {
        const existing = document.getElementById("planner-week-drilldown");
        if (existing) existing.remove();
        activeWeekDrilldownYmd = null;
        logPlannerDebug("[Week View] drilldown closed");
    }

    async function openWeekDrilldown(ymd) {
        if (othelloState.currentView !== "today-planner") return;
        if (activeWeekDrilldownYmd === ymd && document.getElementById("planner-week-drilldown")) return;
        activeWeekDrilldownYmd = ymd;
        logPlannerDebug("[Week View] drilldown open", { ymd });
        
        abortWeekRequests("week-drilldown");
        weekAbort = new AbortController();
        const res = await fetchPlanForDate(ymd, { signal: weekAbort.signal, source: "drilldown" });
        if (!res) {
            activeWeekDrilldownYmd = null;
            return;
        }
        
        closeWeekDrilldown();
        
        const modal = document.createElement("div");
        modal.id = "planner-week-drilldown";
        modal.style.position = "fixed";
        modal.style.zIndex = "2000";
        modal.style.top = "0"; modal.style.left = "0"; modal.style.right = "0"; modal.style.bottom = "0";
        modal.style.background = "rgba(2, 6, 23, 0.9)";
        modal.style.display = "flex";
        modal.style.alignItems = "center";
        modal.style.justifyContent = "center";
        modal.onclick = (e) => { if (e.target === modal) closeWeekDrilldown(); };
        
        const card = document.createElement("div");
        card.className = "planner-card";
        card.style.width = "min(500px, 90%)";
        card.style.maxHeight = "80vh";
        card.style.display = "flex";
        card.style.flexDirection = "column";
        
        // Header
        const parts = ymd.split('-');
        const dateObj = new Date(parts[0], parts[1]-1, parts[2]);
        const dateStr = dateObj.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
        
        const c = res.counts;
        const summary = `C:${c.completed} · IP:${c.inProgress} · OD:${c.overdue} · S:${c.snoozed} · T:${c.tomorrow}`;
        
        card.innerHTML = `
            <div class="planner-card__header" style="border-bottom:1px solid var(--border); padding-bottom:0.5rem; margin-bottom:0.5rem;">
                <div>
                    <div class="planner-section__title" style="font-size:1.1rem;">${dateStr}</div>
                    <div style="font-size:0.85rem; color:var(--text-soft); margin-top:0.2rem;">${summary}</div>
                </div>
                <button class="icon-button" style="border:none; background:transparent;" onclick="closeWeekDrilldown()">✕</button>
            </div>
            <div style="flex:1; overflow-y:auto; padding-right:0.5rem;" id="drilldown-list"></div>
            <div style="margin-top:1rem; padding-top:1rem; border-top:1px solid var(--border); text-align:center;">
                <button class="planner-action-btn" style="width:100%; justify-content:center; padding:0.8rem;" id="drilldown-open-btn">Open in Day View</button>
            </div>
        `;
        
        // Lists
        const listContainer = card.querySelector("#drilldown-list");
        const items = flattenPlanItemsForReadOnly(res.plan);
        const groups = { overdue: [], main: [], later: [], snoozed: [], completed: [] };
        
        const planDateYmd = res.plan.plan_date || ymd;
        const d = new Date(planDateYmd);
        d.setDate(d.getDate() + 1);
        const tomorrowYmd = d.toISOString().split('T')[0];

        items.forEach(item => {
            if (item.status === 'complete') {
                groups.completed.push(item);
                return;
            }
            if (isSnoozedNow(item.metadata)) {
                groups.snoozed.push(item);
                return;
            }
            
            const rTo = item.reschedule_to;
            if (rTo && rTo < planDateYmd) {
                groups.overdue.push(item);
                return;
            }
            
            // Simple heuristic for "Later" vs "Main"
            if (item.status !== 'in_progress' && isOutsideTimeWindow(item.schedule_rule)) {
                groups.later.push(item);
            } else {
                groups.main.push(item);
            }
        });
        
        const renderGroup = (title, list, color) => {
            if (!list.length) return;
            const h = document.createElement("div");
            h.style.fontSize = "0.8rem";
            h.style.fontWeight = "600";
            h.style.color = color || "var(--text-soft)";
            h.style.marginTop = "0.8rem";
            h.style.marginBottom = "0.4rem";
            h.textContent = title.toUpperCase();
            listContainer.appendChild(h);
            
            list.forEach(i => {
                const row = document.createElement("div");
                row.style.padding = "0.4rem 0";
                row.style.borderBottom = "1px solid rgba(255,255,255,0.05)";
                row.style.fontSize = "0.9rem";
                row.innerHTML = `
                    <div style="display:flex; justify-content:space-between;">
                        <span>${i.label}</span>
                        <span style="font-size:0.75rem; opacity:0.7; border:1px solid var(--border); padding:0 0.3rem; border-radius:4px;">${i.status}</span>
                    </div>
                    <div style="font-size:0.75rem; color:var(--text-soft);">${i.section}${i.parent ? ' · ' + i.parent : ''}</div>
                `;
                listContainer.appendChild(row);
            });
        };
        
        renderGroup("Overdue", groups.overdue, "#fca5a5");
        renderGroup("Active / Planned", groups.main, "var(--accent)");
        renderGroup("Later", groups.later);
        renderGroup("Snoozed", groups.snoozed);
        renderGroup("Completed", groups.completed);
        
        if (items.length === 0) {
            listContainer.innerHTML = '<div style="text-align:center; padding:2rem; color:var(--text-soft);">No items planned.</div>';
        }

        card.querySelector("#drilldown-open-btn").onclick = () => openDayViewForDate(ymd);
        
        modal.appendChild(card);
        document.body.appendChild(modal);
    }

    function openDayViewForDate(ymd) {
        dayViewDateYmd = ymd;
        closeWeekDrilldown();
        abortWeekRequests("day-view-open");
        
        isWeekViewActive = false;
        document.getElementById("planner-week-view").style.display = "none";
        document.getElementById("planner-day-view").style.display = "block";
        
        const btn = document.getElementById("week-view-toggle");
        if (btn) btn.textContent = "Week View";
        
        loadTodayPlanner();
    }

    function isReadOnlyDayView() {
        if (!dayViewDateYmd) return false;
        return dayViewDateYmd !== toYmdLocal(new Date());
    }

    function toggleWeekView() {
        if (othelloState.currentView !== "today-planner") return;
        const weekView = document.getElementById("planner-week-view");
        const dayView = document.getElementById("planner-day-view");
        const btn = document.getElementById("week-view-toggle");
        
        isWeekViewActive = !isWeekViewActive;
        
        if (isWeekViewActive) {
            weekView.style.display = "block";
            dayView.style.display = "none";
            btn.textContent = "Back to Today";
            loadWeekView();
        } else {
            weekView.style.display = "none";
            dayView.style.display = "block";
            btn.textContent = "Week View";
            closeWeekDrilldown();
            abortWeekRequests("week-view-close");
        }
    }
    
    function bindPlannerListeners() {
        if (plannerListenersBound) return;
        plannerListenersBound = true;
        const btn = document.getElementById("week-view-toggle");
        if (btn) btn.onclick = toggleWeekView;
        
        const toggle = document.getElementById("suggestions-toggle");
        if (toggle) toggle.onclick = toggleSuggestions;
        
        const genBtn = document.getElementById("generate-suggestions-btn");
        if (genBtn) genBtn.onclick = generateSuggestions;
    }
    
    document.addEventListener("DOMContentLoaded", bindPlannerListeners);

    // --- Suggestions Logic ---
    
    async function toggleSuggestions() {
        const panel = document.getElementById("planner-suggestions-panel");
        if (panel.style.display === "none") {
            panel.style.display = "block";
            loadSuggestions();
        } else {
            panel.style.display = "none";
        }
    }
    
    async function loadSuggestions() {
        const list = document.getElementById("suggestions-list");
        list.innerHTML = "Loading...";
        
        const dateParam = dayViewDateYmd || toYmdLocal(new Date());
        try {
            const res = await fetch(`/api/proposals?plan_date=${dateParam}`);
            const data = await res.json();
            
            if (!data.proposals || data.proposals.length === 0) {
                list.innerHTML = "<div style='color:var(--text-soft); font-style:italic;'>No pending suggestions.</div>";
                return;
            }
            
            list.innerHTML = "";
            data.proposals.forEach(p => {
                const div = document.createElement("div");
                div.style.background = "var(--bg-2)";
                div.style.padding = "0.8rem";
                div.style.marginBottom = "0.5rem";
                div.style.borderRadius = "8px";
                div.style.border = "1px solid var(--border)";
                
                div.innerHTML = `
                    <div style="font-weight:bold; margin-bottom:0.3rem;">${p.title}</div>
                    <div style="font-size:0.9rem; color:var(--text-soft); margin-bottom:0.5rem;">${p.summary}</div>
                    <div style="display:flex; gap:0.5rem;">
                        <button class="planner-action-btn" onclick="applySuggestion('${p.proposal_id}')">Accept</button>
                        <button class="planner-action-btn" style="border-color:var(--border); color:var(--text-soft);" onclick="rejectSuggestion('${p.proposal_id}')">Reject</button>
                    </div>
                `;
                list.appendChild(div);
            });
        } catch (e) {
            list.textContent = "Error loading suggestions.";
            console.error(e);
        }
    }
    
    async function generateSuggestions() {
        const btn = document.getElementById("generate-suggestions-btn");
        btn.disabled = true;
        btn.textContent = "Generating...";
        
        const dateParam = dayViewDateYmd || toYmdLocal(new Date());
        try {
            await fetch("/api/proposals/generate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ plan_date: dateParam })
            });
            await loadSuggestions();
        } catch (e) {
            console.error(e);
        } finally {
            btn.disabled = false;
            btn.textContent = "Generate";
        }
    }
    
    async function applySuggestion(id) {
        try {
            const res = await fetch("/api/proposals/apply", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ proposal_id: id })
            });
            const data = await res.json();
            
            if (res.status === 409) {
                alert("Suggestion is currently being applied. Please wait.");
                await loadSuggestions();
                return;
            }
            
            if (res.ok) {
                if (data.message === "Already decided") {
                    console.log("Suggestion already decided, refreshing...");
                }
                await loadTodayPlanner();
                await loadSuggestions();
            } else {
                console.error("Failed to apply suggestion:", data);
                alert("Failed to apply suggestion: " + (data.message || "Unknown error"));
            }
        } catch (e) {
            console.error(e);
        }
    }
    
    async function rejectSuggestion(id) {
        try {
            const res = await fetch("/api/proposals/reject", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ proposal_id: id })
            });
            const data = await res.json();
            
            if (res.status === 409) {
                alert("Suggestion is currently being applied. Cannot reject now.");
                await loadSuggestions();
                return;
            }

            if (res.ok) {
                await loadSuggestions();
            } else {
                console.error("Failed to reject suggestion:", data);
                alert("Failed to reject suggestion: " + (data.message || "Unknown error"));
            }
        } catch (e) {
            console.error(e);
        }
    }

    async function loadTodayPlanner() {
      if (othelloState.currentView !== "today-planner") {
        logPlannerDebug("[Today Planner] load skipped", { view: othelloState.currentView });
        return;
      }
      if (document.hidden) {
        logPlannerDebug("[Today Planner] load skipped (hidden)", { view: othelloState.currentView });
        return;
      }
      if (BOOT_DEBUG) console.log("[Today Planner] loadTodayPlanner invoked", {
        view: othelloState.currentView,
        ts: new Date().toISOString(),
        dayViewDateYmd
      });
      abortPlannerRequests("planner-reload");
      plannerAbort = new AbortController();
      const { signal } = plannerAbort;
      clearPlannerError();
      plannerHeadline.textContent = "Loading...";
      plannerEnergy.textContent = "";
      plannerRoutinesList.innerHTML = "";
      plannerGoalsList.innerHTML = "";
      
      // Suggestions button state
      const suggBtn = document.getElementById("suggestions-toggle");
      if (suggBtn) {
          const isRO = isReadOnlyDayView();
          suggBtn.disabled = isRO;
          suggBtn.style.opacity = isRO ? "0.5" : "1";
          if (isRO) {
              const panel = document.getElementById("planner-suggestions-panel");
              if (panel) panel.style.display = "none";
          }
      }

      // Read-only banner
      const existingBanner = document.getElementById("planner-readonly-banner");
      if (existingBanner) existingBanner.remove();
      
      if (isReadOnlyDayView()) {
          const banner = document.createElement("div");
          banner.id = "planner-readonly-banner";
          banner.style.background = "rgba(252, 165, 165, 0.15)";
          banner.style.border = "1px solid #fca5a5";
          banner.style.color = "#fca5a5";
          banner.style.padding = "0.5rem";
          banner.style.marginBottom = "1rem";
          banner.style.borderRadius = "8px";
          banner.style.textAlign = "center";
          banner.style.fontSize = "0.9rem";
          banner.innerHTML = `
            Viewing <strong>${dayViewDateYmd}</strong> (read-only) · 
            <span style="text-decoration:underline; cursor:pointer;" id="readonly-back-btn">Back to Today</span>
          `;
          const shell = document.getElementById("planner-shell");
          if (shell) shell.prepend(banner);
          
          document.getElementById("readonly-back-btn").onclick = () => {
              dayViewDateYmd = null;
              loadTodayPlanner();
          };
      }

      let planStatus = null;
      let planSnippet = null;
      let planParseError = null;
      let briefStatus = null;
      let briefSnippet = null;
      let briefParseError = null;
      let planUrl = null;
      try {
        planUrl = dayViewDateYmd 
            ? `/api/today-plan?plan_date=${dayViewDateYmd}` 
            : `/api/today-plan?ts=${Date.now()}`;
        const brief = dayViewDateYmd ? {} : await fetchTodayBrief(signal).catch((err) => {
          if (isAbortError(err)) throw err;
          briefStatus = err && err.status ? err.status : null;
          briefSnippet = err && err.bodySnippet ? err.bodySnippet : null;
          briefParseError = err && err.parseError ? err.parseError : null;
          console.error("[Today Planner] fetchTodayBrief failed", {
            status: briefStatus,
            parseError: briefParseError,
            error: err && err.message,
          });
          return {};
        });
        const planResponse = await fetch(planUrl, { cache: "no-store", credentials: "include", signal });
        planStatus = planResponse.status;
        const planText = await planResponse.text();
        planSnippet = planText.replace(/\s+/g, " ").trim().slice(0, 300);
        if (!planResponse.ok) {
          const err = new Error("Failed to load plan");
          err.status = planStatus;
          err.bodySnippet = planSnippet;
          throw err;
        }
        let planResp = null;
        try {
          planResp = JSON.parse(planText);
        } catch (parseErr) {
          planParseError = parseErr.message;
          const err = new Error("Failed to parse plan");
          err.status = planStatus;
          err.bodySnippet = planSnippet;
          err.parseError = planParseError;
          throw err;
        }

        const plan = planResp.plan || {};
        const goalTasks = (plan.sections?.goal_tasks || []);
        if (BOOT_DEBUG) console.log("[Today Planner] goalTasks count", goalTasks.length, { source: "ui", planSource: plan._plan_source });
        
        if (!dayViewDateYmd) renderTodayBrief(plan, brief);
        else {
            plannerHeadline.textContent = `Plan for ${dayViewDateYmd}`;
            plannerEnergy.textContent = "Read-only view";
        }
        
        renderPlannerSections(plan, goalTasks);
        const currentItem = renderCurrentFocus(plan);
        renderNextAction(plan, currentItem ? [currentItem.item_id || currentItem.id] : []);
        await loadTodayPlanPanel(signal);
      } catch (e) {
        if (isAbortError(e)) {
          logPlannerDebug("[Today Planner] load aborted", { view: othelloState.currentView });
          return;
        }
        let httpStatus = null;
        if (e && (e.status === 401 || e.status === 403)) {
          await handleUnauthorized('today-planner');
          return;
        }
        if (e && e.response && e.response.status) httpStatus = e.response.status;
        if (e && e.message && e.message.startsWith('Failed to load plan')) {
          // Try to extract HTTP status from error message if present
          const match = e.message.match(/HTTP (\d+)/);
          if (match) httpStatus = match[1];
        }
        if (e && e.status) httpStatus = e.status;
        const detailParts = [];
        if (planStatus) detailParts.push(`today-plan:${planStatus}`);
        if (planParseError) detailParts.push(`plan_parse:${planParseError}`);
        if (planSnippet) detailParts.push(`plan_snippet:${planSnippet.slice(0, 120)}`);
        if (briefStatus) detailParts.push(`today-brief:${briefStatus}`);
        if (briefParseError) detailParts.push(`brief_parse:${briefParseError}`);
        if (briefSnippet) detailParts.push(`brief_snippet:${briefSnippet.slice(0, 120)}`);
        if (e && e.message) detailParts.push(`error:${e.message}`);
        const detailString = detailParts.join(" | ").slice(0, 300);
        console.error("[Today Planner] loadTodayPlanner failed", {
          planUrl,
          planStatus,
          briefStatus,
          planParseError,
          briefParseError,
          error: e && e.message,
        });
        renderPlannerError("Planner load failed", httpStatus, detailString);
        if (BOOT_DEBUG) console.log("[Today Planner] loadTodayPlanner error", e);
      }
    }

    async function fetchInsightsList(status = "pending") {
      const resp = await fetch(`/api/insights/list?status=${encodeURIComponent(status)}`, { credentials: "include" });
      if (resp.status === 401 || resp.status === 403) {
        await handleUnauthorized('insights-list');
        throw new Error("Unauthorized");
      }
      if (!resp.ok) throw new Error("Failed to load insights");
      const data = await resp.json();
      return data.insights || [];
    }

    async function fetchInsightsSummary() {
      const resp = await fetch("/api/insights/summary", { credentials: "include" });
      if (!resp.ok) throw new Error("Failed to load insights summary");
      return resp.json();
    }

    function showInsightsError(message) {
      if (insightsError) {
        insightsError.textContent = message || "Unable to load insights right now.";
        insightsError.style.display = "block";
      }
      if (insightsEmpty) {
        insightsEmpty.style.display = "none";
      }
      if (insightsList) {
        insightsList.style.display = "none";
      }
    }

    function clearInsightsError() {
      if (insightsError) {
        insightsError.textContent = "";
        insightsError.style.display = "none";
      }
    }

    function renderInsightsList(items) {
      if (!insightsList || !insightsEmpty) return;

      insightsList.innerHTML = "";
      const hasItems = Array.isArray(items) && items.length > 0;

      clearInsightsError();

      if (!hasItems) {
        insightsList.style.display = "none";
        insightsEmpty.style.display = "block";
        return;
      }
      insightsEmpty.style.display = "none";
      insightsList.style.display = "flex";

      items.forEach(item => {
        const card = document.createElement("div");
        card.className = "insight-card";

        const meta = document.createElement("div");
        meta.className = "insight-card__meta";

        const typeLabel = document.createElement("span");
        typeLabel.textContent = (item.insight_type || item.type || "generic").toLowerCase();
        meta.appendChild(typeLabel);

        const dateLabel = document.createElement("span");
        dateLabel.textContent = item.created_at ? new Date(item.created_at).toLocaleString() : "";
        meta.appendChild(dateLabel);

        const summary = document.createElement("div");
        summary.className = "insight-card__summary";
        summary.textContent = item.summary || item.content || "";

        card.appendChild(meta);
        card.appendChild(summary);

        const actions = document.createElement("div");
        actions.className = "insight-actions";

        const applyBtn = document.createElement("button");
        applyBtn.className = "insight-btn primary";
        applyBtn.textContent = "Apply";
        applyBtn.addEventListener("click", async () => {
          applyBtn.disabled = true;
          const prevLabel = applyBtn.textContent;
          applyBtn.textContent = "Applying…";
          try {
            await handleInsightAction(item, "apply");
          } finally {
            applyBtn.disabled = false;
            applyBtn.textContent = prevLabel;
          }
        });

        const dismissBtn = document.createElement("button");
        dismissBtn.className = "insight-btn";
        dismissBtn.textContent = "Dismiss";
        dismissBtn.addEventListener("click", async () => {
          dismissBtn.disabled = true;
          try {
            await handleInsightAction(item, "dismiss");
          } finally {
            dismissBtn.disabled = false;
          }
        });

        actions.appendChild(applyBtn);
        actions.appendChild(dismissBtn);
        card.appendChild(actions);

        insightsList.appendChild(card);
      });
    }

    async function loadInsightsInbox() {
      if (!insightsList || !insightsEmpty) return;
      clearInsightsError();
      try {
        const [summaryData, insights] = await Promise.all([
          fetchInsightsSummary(),
          fetchInsightsList("pending"),
        ]);

        if (summaryData && summaryData.pending_counts) {
          console.log("[Othello UI] insights summary", summaryData.pending_counts);
          applyInsightsMeta(summaryData);
        }

        renderInsightsList(insights);
      } catch (err) {
        console.error("[Othello UI] failed to load insights", err);
        renderInsightsList([]);
        showInsightsError("Unable to load insights right now.");
      }
    }

    async function handleInsightAction(item, action) {
      const endpoint = action === "apply" ? "/api/insights/apply" : "/api/insights/dismiss";
      const payload = { id: item.id };
      if (action === "apply") {
        console.log("[Insights] applying", {
          id: item.id,
          type: item.insight_type || item.type,
          summary: item.summary || item.content,
          payload,
        });
      }
      try {
        const resp = await fetch(endpoint, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify(payload),
        });
        if (!resp.ok) {
          throw new Error("Insight action failed");
        }
        const data = await resp.json();
        if (data.insights_meta) {
          applyInsightsMeta(data.insights_meta);
        }
        await loadInsightsInbox();
        if (action === "apply") {
          console.log("[Insights] apply succeeded, refreshing Today Planner", {
            id: item.id,
            type: item.insight_type || item.type,
          });
          await loadTodayPlanner();
        }
        return data;
      } catch (err) {
        console.error("[Othello UI] insight action failed", err);
        showInsightsError("Unable to apply insight right now.");
        throw err;
      }
    }

    // ===== CHAT OVERLAY (Phase 3) =====
    const globalChatOverlay = document.getElementById('global-chat-overlay');
    const globalChatFab = document.getElementById('global-chat-fab');
    const chatBackBtn = document.getElementById('chat-back-btn');
    const chatContextSelector = document.getElementById('chat-context-selector');

    
    // Connectivity State Management
    function updateConnectivity(status, message = "") {
        console.debug(`[Connectivity] update: ${status} (msg: ${message})`);
        othelloState.connectivity = status;
        const pill = document.getElementById('chat-status-pill');
        const text = document.getElementById('chat-status-text');
        
        // Provide route context if available, defaulting to "Chat"
        const route = othelloState.lastRoute || "Chat";
        
        if (text) {
             if (status === 'online') {
                 text.textContent = `Online • ${route}`;
             } else if (status === 'thinking') {
                 text.textContent = `Thinking • ${route}`;
             } else if (status === 'offline') {
                 text.textContent = "Offline";
             } else if (status === 'degraded') {
                 text.textContent = message || "Degraded";
             } else {
                 text.textContent = status;
             }
        }
        
        if (pill) {
            pill.classList.remove('offline', 'degraded', 'thinking');
            if (status === 'offline') pill.classList.add('offline');
            if (status === 'degraded') pill.classList.add('degraded');
            if (status === 'thinking') pill.classList.add('thinking'); // Optional styling
        }
    }

    // Ping Logic
    let pingInterval = null;
    function startConnectivityPing() {
        if (pingInterval) return;
        pingInterval = setInterval(async () => {
             try {
                 const res = await fetch('/api/capabilities', { method: 'GET', cache: 'no-store' });
                 if (res.ok) updateConnectivity('online');
                 else updateConnectivity('degraded', `Status ${res.status}`);
             } catch (e) {
                 updateConnectivity('offline');
             }
        }, 15000);
    }

    function stopConnectivityPing() {
        if (pingInterval) {
            clearInterval(pingInterval);
            pingInterval = null;
        }
    }

    function toggleChatOverlay(show) {
      if (!globalChatOverlay) return;
      const isOpen = typeof show === 'boolean' ? show : !globalChatOverlay.classList.contains('open');
      if (globalChatOverlay) {
        globalChatOverlay.classList.toggle('open', isOpen);
      }
      
      // Directive: Hide FAB when open (via body class)
      document.body.classList.toggle('chat-open', isOpen);
      
      if (globalChatFab) {
         globalChatFab.classList.toggle('active', isOpen);
      }

      // [Phase 3] Re-bind composer button when opening overlay
      if (isOpen) {
          if (typeof bindComposerActionButton === 'function') {
              bindComposerActionButton("overlay_open");
              requestAnimationFrame(() => bindComposerActionButton("overlay_open_raf"));
          }
      }

      if (!isOpen) {
          stopConnectivityPing();
      }

      if (isOpen) {
        startConnectivityPing();
        // Ensure the composer button is bound
        if (typeof bindComposerActionButton === 'function') {
            bindComposerActionButton("overlay_open");
            requestAnimationFrame(() => bindComposerActionButton("overlay_open_raf"));
        }

        // Phase 5: Initialize selector based on current effective channel
        // But only if we haven't manually overridden it yet for this session? 
        // Actually, better to reset to context on open, unless user changed it *while* open.
        // Let's reset it to the view's context every time we open, for consistency.
        
        const channel = effectiveChannelForView({ 
            currentView: othelloState.currentView, 
            currentMode: othelloState.currentMode 
        });
        
        if (chatContextSelector) {
            chatContextSelector.value = channel;
        }

        console.log(`[Othello UI] Opened chat overlay. Context: ${channel} (View: ${othelloState.currentView})`);
        
        loadChatHistory(); // Triggers fetch for the effective channel
        scrollChatToBottom(true);
        
        updateFocusRibbon();
        const ui = document.getElementById('user-input');
        if (ui) ui.focus();
      }
    }
    
    // Phase 5: Handle selector changes
    // Refactored to bindChatOverlayHandlers for robustness
    function bindChatOverlayHandlers() {
        const overlayInput = document.getElementById('user-input');
        const overlaySend = document.getElementById('send');
        const overlayClose = document.getElementById('chat-back-btn');
        const overlaySelector = document.getElementById('chat-context-selector');
        const fab = document.getElementById('global-chat-fab');

        if (overlaySelector) {
            overlaySelector.onchange = (e) => {
                const newChannel = e.target.value;
                console.log(`[Othello UI] Switching chat context to: ${newChannel}`);
                othelloState.manualChannelOverride = newChannel;
                loadChatHistory();
            };
        }

        if (overlayClose) {
            overlayClose.onclick = (e) => {
                e.stopPropagation();
                toggleChatOverlay(false);
            };
        }

        if (fab) {
            fab.onclick = () => toggleChatOverlay(true);
        }

        if (overlaySend) {
            overlaySend.onclick = () => {
                console.debug("[Othello UI] Send clicked in overlay");
                sendMessage();
            };
        }

        if (overlayInput) {
             overlayInput.onkeydown = (e) => {
                 if (e.key === "Enter" && !e.shiftKey) { // Allow Shift+Enter?
                     e.preventDefault();
                     console.debug("[Othello UI] Enter pressed in overlay input");
                     sendMessage();
                 }
             };
        }
    }
    
    // Initial Bind
    bindChatOverlayHandlers();

    if (globalChatOverlay) {
        globalChatOverlay.addEventListener('click', (e) => {
            if (e.target === globalChatOverlay) {
                toggleChatOverlay(false);
            }
        });
    }

    // ===== TAB NAVIGATION =====
    // Define tabs and views from DOM
    const tabs = Array.from(document.querySelectorAll('.tab'));
    const views = Array.from(document.querySelectorAll('.view'));

    function switchView(viewName) {
      if (viewName === 'chat') {
        toggleChatOverlay(true);
        return;
      }
      
      toggleChatOverlay(false); // Close chat if switching main views (optional, but good UX)

      // Phase 5: Clear manual channel override when switching views so context resets to natural default
      othelloState.manualChannelOverride = null;

      othelloState.currentView = viewName;

      // Update tabs
      if (!tabs || !tabs.length) return;
      tabs.forEach(tab => {
        const target = tab.dataset.view;
        // Planner tab stays active for both planner subviews
        const isPlannerActive = (viewName === 'today-planner' || viewName === 'routine-planner') && target === 'today-planner';
        if (tab.dataset.view === viewName || isPlannerActive) {
          tab.classList.add("active");
        } else {
          tab.classList.remove("active");
        }
      });

      // Update views
      if (views && views.length) {
        views.forEach(view => {
          if (view.id === `${viewName}-view`) {
            view.classList.add("active");
          } else {
            view.classList.remove("active");
          }
        });
      }

      // Hide focus ribbon in main views (it belongs to chat overlay context now)
      if (focusRibbon) focusRibbon.classList.remove("visible");

      if (viewName !== "today-planner") {
        stopPlannerPolling("view-change");
        abortPlannerRequests("view-change");
        abortWeekRequests("view-change");
        closeWeekDrilldown();
      }
      if (viewName !== "routine-planner") {
        abortRoutineRequests("view-change");
      }

      // Load view-specific data
      if (viewName === "goals") {
        renderGoalsList();
      } else if (viewName === "today-planner") {
        loadTodayPlanner();
        startPlannerPolling();
      } else if (viewName === "insights") {
        loadInsightsInbox();
      } else if (viewName === "routine-planner") {
        loadRoutinePlanner();
        othelloState.needsRoutineRefresh = false;
      }
    }

    if (tabs && tabs.length) {
      tabs.forEach(tab => {
        tab.addEventListener("click", () => {
          const view = tab.dataset.view;
          const plannerMenu = document.getElementById('planner-menu');

          // Planner Tab Special Handling (Submenu)
          if (view === 'today-planner') {
              if (tab.classList.contains('active')) {
                   if (plannerMenu) plannerMenu.classList.toggle('hidden');
              } else {
                   if (plannerMenu) plannerMenu.classList.add('hidden');
                   switchView('today-planner');
              }
              return;
          }

          if (plannerMenu) plannerMenu.classList.add('hidden');
          switchView(tab.dataset.view);
        });
      });
    }
    
    // Planner Menu Handling
    const plannerMenu = document.getElementById('planner-menu');
    if (plannerMenu) {
        plannerMenu.addEventListener('click', (e) => {
            const btn = e.target.closest('.planner-menu-item');
            if (btn) {
                const sub = btn.dataset.subview;
                if (sub === 'today') switchView('today-planner');
                if (sub === 'routine') switchView('routine-planner');
                plannerMenu.classList.add('hidden');
                
                // Update active state in menu
                Array.from(plannerMenu.children).forEach(c => c.classList.remove('active'));
                btn.classList.add('active');
            }
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!plannerMenu.classList.contains('hidden') && 
                !e.target.closest('.planner-menu') && 
                !e.target.closest('#planner-tab')) {
                plannerMenu.classList.add('hidden');
            }
        });
    }

    document.addEventListener("visibilitychange", () => {
      if (document.hidden) {
        stopPlannerPolling("hidden");
        abortPlannerRequests("hidden");
        abortWeekRequests("hidden");
        abortRoutineRequests("hidden");
        return;
      }
      if (othelloState.currentView === "today-planner") {
        startPlannerPolling();
      }
    });

    // ===== MODE SWITCHER =====
    function persistMode(mode) {
      try {
        localStorage.setItem("othelloMode", mode);
      } catch (e) {}
    }

    function loadMode() {
      try {
        const stored = localStorage.getItem("othelloMode");
        if (stored && MODE_LABELS[stored]) {
          return stored;
        }
      } catch (e) {}
      return "today";
    }

    function loadDraftState() {
      try {
        const stored = localStorage.getItem("othello_active_draft");
        if (stored) {
          othelloState.activeDraft = JSON.parse(stored);
          
          const storedPayload = localStorage.getItem("othello_active_draft_payload");
          if (storedPayload) {
              othelloState.activeDraftPayload = JSON.parse(storedPayload);
          }
          
          updateFocusRibbon();
        }
      } catch (e) {}
    }

    function setMode(mode) {
      if (!MODE_LABELS[mode]) return;
      othelloState.currentMode = mode;
      persistMode(mode);
      
      if (modeLabel) modeLabel.textContent = MODE_LABELS[mode];
      else console.warn("[UI] setMode called but modeLabel missing");

      if (modeSubtitle) modeSubtitle.textContent = MODE_SUBTITLES[mode] || "";

      if (modeOptions && modeOptions.length) {
        modeOptions.forEach(opt => {
          opt.classList.toggle("active", opt.dataset.mode === mode);
        });
      }
      
      const tabCfg = MODE_TAB_CONFIG[mode];
      // middleTab manipulation removed - tabs are now static.

      const allowed = MODE_ALLOWED_VIEWS[mode] || [];
      // Default to the primary view for the mode (Goals/Planner), never "chat" as main view
      const fallback = tabCfg ? tabCfg.view : "today-planner";
      const targetView = allowed.includes(othelloState.currentView) ? othelloState.currentView : fallback;
      updateTabBadges();
      refreshInsightsCounts();
      switchView(targetView);
    }

    function toggleDropdown() {
      if (!modeDropdown) return;
      const isOpen = modeDropdown.classList.contains("open");
      modeDropdown.classList.toggle("open", !isOpen);
      if (modeToggle) modeToggle.setAttribute("aria-expanded", (!isOpen).toString());
    }

    if (modeToggle) {
      modeToggle.addEventListener("click", () => {
        toggleDropdown();
      });
    }

    if (modeOptions && modeOptions.length) {
      modeOptions.forEach(opt => {
        opt.addEventListener("click", () => {
          const mode = opt.dataset.mode;
          setMode(mode);
          if (modeDropdown) modeDropdown.classList.remove("open");
          if (modeToggle) modeToggle.setAttribute("aria-expanded", "false");
        });
      });
    }

    document.addEventListener("click", (e) => {
      if (!modeDropdown || (!modeToggle && !modeDropdown)) return;
      if (!modeDropdown.contains(e.target) && (!modeToggle || !modeToggle.contains(e.target))) {
        modeDropdown.classList.remove("open");
        if (modeToggle) modeToggle.setAttribute("aria-expanded", "false");
      }
    });

    // ===== INITIALIZE MODE =====
    // To add new modes later, extend MODE_LABELS, MODE_SUBTITLES, and modeOptions in markup.
    setMode(loadMode());
    loadDraftState();
    refreshInsightsCounts();

    function renderDraftPreview() {
        const container = document.getElementById("draft-preview");
        if (!container) return;
        
        if (!othelloState.activeDraft || !othelloState.activeDraftPayload) {
            container.style.display = "none";
            container.innerHTML = "";
            return;
        }
        
        // Dynamic offset for ribbon
        if (focusRibbon && focusRibbon.classList.contains("visible")) {
            const h = focusRibbon.offsetHeight || 0;
            container.style.marginTop = h ? (h + 8) + "px" : "0px";
        } else {
            container.style.marginTop = "0px";
        }
        
        const p = othelloState.activeDraftPayload;
        // Filter blank steps
        const steps = (p.steps || []).filter(s => typeof s === "string" && s.trim());
        
        console.debug("[Othello UI] Draft preview steps:", steps.length);
        
        let html = `<h3>${p.title || "New Goal"}</h3>`;
        html += `<div class="draft-meta">Target: ${p.target_days || 7} days</div>`;
        
        if (steps.length > 0) {
            html += `<ul class="draft-steps">`;
            steps.forEach(step => {
                html += `<li>${step}</li>`;
            });
            html += `</ul>`;
        } else {
            html += `<div class="draft-meta">No steps generated yet.</div>`;
        }
        
        container.innerHTML = html;
        container.style.display = "block";
    }

    // ===== FOCUS RIBBON =====
    function updateFocusRibbon() {
      renderDraftPreview();
      
      if (!focusRibbon) return;
      
      // Phase 3 Update: Chat is now an overlay.
      const isChatOpen = globalChatOverlay && globalChatOverlay.classList.contains('open');
      // If chat overlay is closed, hide ribbon (unless we are in legacy chat view handling)
      if (!isChatOpen && othelloState.currentView !== "chat") {
        focusRibbon.classList.remove("visible");
        return;
      }

      // Draft Focus (Priority over Active Goal)
      if (othelloState.activeDraft) {
          const draftType = othelloState.activeDraft.draft_type || "Goal";
          const displayType = draftType.charAt(0).toUpperCase() + draftType.slice(1);
          focusRibbonTitle.textContent = `Drafting ${displayType}...`; 
          
          // Add actions if not present
          let actionsDiv = focusRibbon.querySelector(".ribbon-actions");
          if (!actionsDiv) {
              actionsDiv = document.createElement("div");
              actionsDiv.className = "ribbon-actions";
              actionsDiv.style.marginLeft = "auto";
              actionsDiv.style.display = "flex";
              actionsDiv.style.gap = "8px";
              focusRibbon.appendChild(actionsDiv);
          }
          
          // Rebuild actions
          actionsDiv.innerHTML = "";

          const genStepsBtn = document.createElement("button");
          genStepsBtn.textContent = "Generate Steps";
          genStepsBtn.className = "ribbon-btn";
          genStepsBtn.onclick = async (e) => {
              e.stopPropagation();
              if (othelloState.isGeneratingSteps) return;
              
              othelloState.isGeneratingSteps = true;
              genStepsBtn.disabled = true;
              genStepsBtn.textContent = "Generating...";
              const regenBtn = actionsDiv.querySelector(".regen-btn");
              if (regenBtn) regenBtn.disabled = true;
              
              try {
                  await sendMessage("", { ui_action: "generate_draft_steps" });
              } finally {
                  othelloState.isGeneratingSteps = false;
                  if (genStepsBtn) { // Check if still exists
                      genStepsBtn.disabled = false;
                      genStepsBtn.textContent = "Generate Steps";
                  }
                  if (regenBtn) regenBtn.disabled = false;
              }
          };
          
          const regenStepsBtn = document.createElement("button");
          regenStepsBtn.textContent = "Regenerate";
          regenStepsBtn.className = "ribbon-btn regen-btn";
          regenStepsBtn.onclick = async (e) => {
              e.stopPropagation();
              if (othelloState.isGeneratingSteps) return;
              
              othelloState.isGeneratingSteps = true;
              regenStepsBtn.disabled = true;
              regenStepsBtn.textContent = "Generating...";
              genStepsBtn.disabled = true;
              
              try {
                  await sendMessage("", { ui_action: "regenerate_draft_steps" });
              } finally {
                  othelloState.isGeneratingSteps = false;
                  if (regenStepsBtn) {
                      regenStepsBtn.disabled = false;
                      regenStepsBtn.textContent = "Regenerate";
                  }
                  if (genStepsBtn) genStepsBtn.disabled = false;
              }
          };
          
          const confirmBtn = document.createElement("button");
          confirmBtn.textContent = "Confirm";
          confirmBtn.className = "ribbon-btn confirm-btn";
          confirmBtn.onclick = (e) => {
              e.stopPropagation();
              sendMessage("", { ui_action: "confirm_draft" });
          };

          const dismissBtn = document.createElement("button");
          dismissBtn.textContent = "Dismiss";
          dismissBtn.className = "ribbon-btn dismiss-btn";
          dismissBtn.onclick = (e) => {
              e.stopPropagation();
              sendMessage("", { ui_action: "dismiss_draft" });
          };

          actionsDiv.appendChild(genStepsBtn);
          actionsDiv.appendChild(regenStepsBtn);
          actionsDiv.appendChild(confirmBtn);
          actionsDiv.appendChild(dismissBtn);

          focusRibbon.classList.add("visible");
          focusRibbon.classList.add("draft-mode");
          return;
      } else {
          focusRibbon.classList.remove("draft-mode");
          const actions = focusRibbon.querySelector(".ribbon-actions");
          if (actions) actions.remove();
      }

      if (othelloState.activeGoalId !== null) {
        const goal = othelloState.goals.find(g => g.id === othelloState.activeGoalId);
        if (goal) {
          focusRibbonTitle.textContent = goal.text || `Goal #${goal.id}`;
          focusRibbon.classList.add("visible");
        } else {
          focusRibbon.classList.remove("visible");
        }
      } else {
        focusRibbon.classList.remove("visible");
      }
    }

    viewFocusBtn.addEventListener("click", () => {
      if (othelloState.activeGoalId !== null) {
        showGoalDetail(othelloState.activeGoalId);
      }
    });

    async function triggerGoalEdit(mode) {
      const goalId = othelloState.activeGoalId;
      if (goalId == null) return;
      statusEl.textContent = "Preparing update.";
      try {
        const res = await fetch(API, {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({
            message: "__goal_action__",
            goal_action: mode,
            goal_id: goalId,
            active_goal_id: goalId,
            current_mode: othelloState.currentMode,
            current_view: othelloState.currentView,
          })
        });

        if (res.status === 401 || res.status === 403) {
          await handleUnauthorized("goal-edit");
          return;
        }

        if (!res.ok) {
          let errText = "Unable to start goal update.";
          const contentType = res.headers.get("content-type") || "";
          if (contentType.includes("application/json")) {
            const data = await res.json();
            errText = (data && (data.message || data.error)) || errText;
          }
          addMessage("bot", errText);
          statusEl.textContent = "Error";
          return;
        }

        const data = await res.json();
        addMessage("bot", data.reply || "[no reply]");
        statusEl.textContent = "Online";

        const metaIntent = data.meta && data.meta.intent ? data.meta.intent : null;
        if (metaIntent === "pending_goal_edit_set") {
          const pendingMode = data.meta && data.meta.mode ? data.meta.mode : mode;
          othelloState.pendingGoalEdit = { mode: pendingMode, goal_id: goalId };
        } else if (metaIntent === "pending_goal_edit_applied") {
          othelloState.pendingGoalEdit = null;
        }

        await refreshGoals();
      } catch (err) {
        console.error("[Othello UI] goal edit error:", err);
        const isNetwork = err instanceof TypeError && (
             err.message === "Failed to fetch" ||
             err.message.includes("NetworkError") ||
             err.message.includes("Network request failed")
        );
        if (isNetwork) {
             addMessage("bot", `[Network error] backend unreachable: ${err.message}`);
             updateConnectivity('offline');
        } else {
             addMessage("bot", `[Client error] Goal edit failed: ${err.message || String(err)}`);
        }
      }
    }

    if (updateFocusBtn) {
      updateFocusBtn.addEventListener("click", () => {
        triggerGoalEdit("update");
      });
    }

    if (appendFocusBtn) {
      appendFocusBtn.addEventListener("click", () => {
        triggerGoalEdit("append");
      });
    }

    async function unfocusGoal() {
      // If we have an active draft, treat Unfocus as Dismiss Draft
      if (othelloState.activeDraft) {
          console.log("[Othello UI] Unfocus clicked while drafting -> Dismissing draft");
          // Optimistic clear
          othelloState.activeDraft = null;
          localStorage.removeItem("othello_active_draft");
          updateFocusRibbon();
          
          // Tell backend
          await sendMessage("", { ui_action: "dismiss_draft" });
          return;
      }

      const hadFocus = othelloState.activeGoalId !== null;
      if (!hadFocus) return;

      try {
        const res = await fetch("/api/goals/unfocus", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          credentials: "include",
        });
        if (res.status === 401 || res.status === 403) {
          await handleUnauthorized("goals-unfocus");
          return;
        }
        if (!res.ok) {
          let errMsg = "Unable to clear focus.";
          const contentType = res.headers.get("content-type") || "";
          if (contentType.includes("application/json")) {
            const data = await res.json();
            errMsg = (data && (data.message || data.error)) || errMsg;
            if (data && data.request_id) {
              console.error("[Othello UI] unfocus request_id:", data.request_id);
            }
          }
          console.warn("[Othello UI] unfocus failed:", errMsg);
        }
      } catch (err) {
        console.warn("[Othello UI] unfocus network error:", err);
      }

      othelloState.activeGoalId = null;
      othelloState.pendingGoalEdit = null;
      updateFocusRibbon();
      if (othelloState.currentView === "goals") {
        renderGoalsList();
      }
    }

    if (unfocusBtn) {
      unfocusBtn.addEventListener("click", () => {
        unfocusGoal();
      });
    }

    // ===== CHAT FUNCTIONS =====

    function setChatViewMode(mode, reason) {
      if (othelloState.chatViewMode === mode) return;
      othelloState.chatViewMode = mode;
      
      const sheet = document.querySelector('.chat-sheet');
      if (sheet) {
        sheet.setAttribute('data-view-mode', mode);
      }
      
      const chatLog = document.getElementById("chat-log");
      if (mode === "history") {
        if (chatLog) {
            // Scroll to near bottom but allow seeing history
            chatLog.scrollTop = chatLog.scrollHeight - chatLog.clientHeight - 50; 
        }
      } else if (mode === "duet") {
         // Ensure latest content is visible in duet parts
         // (Handled by addMessage or updateDuetView)
      }
      console.log(`[Duet] Switched to ${mode} (${reason})`);
    }

    function updateDuetView(row, role) {
      // Only applicable if duet wrappers exist
      const duetTop = document.getElementById("duet-top");
      const duetBottom = document.getElementById("duet-bottom");
      console.log("DEBUG: updateDuetView called", role, { duetTop: !!duetTop, duetBottom: !!duetBottom });
      if (!duetTop || !duetBottom) return;

      const clone = row.cloneNode(true);
      
      if (role === "user") {
        duetBottom.innerHTML = "";
        duetBottom.appendChild(clone);
        duetBottom.scrollTop = duetBottom.scrollHeight; // Pin bottom
      } else {
        duetTop.innerHTML = "";
        duetTop.appendChild(clone);
        duetTop.scrollTop = 0; // Read from top
      }
      
      // Auto-switch to duet on new turn
      setChatViewMode("duet", "new_message");
    }

    function bindDuetListeners() {
       const duetContainer = document.getElementById("duet-container");
       const chatLog = document.getElementById("chat-log");
       
       if (duetContainer) {
           duetContainer.addEventListener("wheel", (e) => {
               if (e.deltaY < -10) { // Scrolling UP significantly
                   setChatViewMode("history", "scroll_up");
               }
           }, { passive: true });
           
           // Touch gesture
           let touchSY = 0;
           duetContainer.addEventListener("touchstart", e => { touchSY = e.changedTouches[0].clientY; }, {passive: true});
           duetContainer.addEventListener("touchmove", e => {
               const dy = e.changedTouches[0].clientY - touchSY;
               if (dy > 50) { // Dragging DOWN (content moves down) -> wait, scrolling up means content moves down. 
                   // Dragging DOWN = scrolling UP the viewport? 
                   // Standard: Swipe DOWN moves content DOWN, revealing TOP. That's scrolling UP.
                   setChatViewMode("history", "swipe_down"); 
               }
           }, {passive: true});
       }
       
       if (chatLog) {
           chatLog.addEventListener("scroll", () => {
               if (othelloState.chatViewMode === "history") {
                   const distFromBottom = chatLog.scrollHeight - (chatLog.scrollTop + chatLog.clientHeight);
                   if (distFromBottom < 20) {
                       setChatViewMode("duet", "scrolled_bottom");
                   }
               }
           });
       }
       
       // Init default
       setChatViewMode("duet", "init");
    }

    // Call bindDuetListeners on init
    document.addEventListener("DOMContentLoaded", bindDuetListeners);

    function getChatContainer() {
      // B1: Canonical resolution. We strictly use #chat-log.
      // We do NOT fallback to #chat-view (parent) to avoid split-brain messages.
      const chatLog = document.getElementById("chat-log");
      
      if (!chatLog) {
        console.error("[Othello UI] CRITICAL: #chat-log container missing. Chat interaction impossible.");
        // Visible UI Error (Phase A/B Requirement)
        const toastContainer = document.getElementById("toast-container");
        if (toastContainer) {
            const errDiv = document.createElement("div");
            errDiv.className = "toast error";
            errDiv.textContent = "Error: Chat container missing.";
            toastContainer.appendChild(errDiv);
        }
        return null;
      }
      return chatLog;
    }

    function scrollChatToBottom(force=false) {
      const c = getChatContainer();
      if (!c) return;
      const nearBottom = (c.scrollHeight - (c.scrollTop + c.clientHeight)) < 40;
      if (force || nearBottom) {
         requestAnimationFrame(() => { c.scrollTop = c.scrollHeight; });
      }
    }

    function clearChatState() {
      // Use strict resolved container
      const container = getChatContainer();
      if (container) container.innerHTML = "";
      
      const chatPlaceholder = document.getElementById("chat-placeholder");
      if (chatPlaceholder) chatPlaceholder.classList.remove("hidden");
      othelloState.messagesByClientId = {};
      othelloState.goalIntentSuggestions = {};
      
      // Clear draft state on new chat/reset
      othelloState.activeDraft = null;
      othelloState.activeDraftPayload = null;
      localStorage.removeItem("othello_active_draft");
      localStorage.removeItem("othello_active_draft_payload");
      updateFocusRibbon();
    }

    function resetAuthBoundary(reason) {
      stopPlannerPolling("auth-reset");
      abortPlannerRequests("auth-reset");
      abortWeekRequests("auth-reset");
      abortRoutineRequests("auth-reset");
      closeWeekDrilldown();
      if (connectRetryTimeout) {
        clearTimeout(connectRetryTimeout);
        connectRetryTimeout = null;
      }
      if (pendingStartTimeout) {
        clearTimeout(pendingStartTimeout);
        pendingStartTimeout = null;
      }
      if (recognition && isRecording) {
        try { recognition.stop(); } catch {}
        try { recognition.abort(); } catch {}
      }
      isRecording = false;
      clearChatState();
      chatHydrated = false;
      othelloState.goals = [];
      othelloState.activeGoalId = null;
      othelloState.currentDetailGoalId = null;
      othelloState.pendingGoalEdit = null;
      othelloState.goalUpdateCounts = {};
      othelloState.currentAgentStatus = null;
      if (goalsList) goalsList.innerHTML = "";
      if (detailContent) detailContent.innerHTML = "";
      if (typeof hideGoalDetail === "function") hideGoalDetail();
      if (plannerHeadline) plannerHeadline.textContent = "Sign in to view today's plan.";
      if (plannerEnergy) plannerEnergy.textContent = "";
      if (plannerError) plannerError.style.display = "none";
      if (plannerRoutinesList) plannerRoutinesList.innerHTML = "";
      if (plannerRoutinesCount) plannerRoutinesCount.textContent = "";
      if (plannerGoalsList) plannerGoalsList.innerHTML = "";
      if (plannerGoalsCount) plannerGoalsCount.textContent = "";
      if (todayPlanItems) todayPlanItems.innerHTML = "";
      if (todayPlanSuggestions) todayPlanSuggestions.innerHTML = "";
      if (todayPlanCount) todayPlanCount.textContent = "";
      if (buildPlanStatus) buildPlanStatus.textContent = "";
      updateFocusRibbon();
      if (BOOT_DEBUG) console.log("[AUTH] Reset boundary", reason || "");
    }

    function effectiveChannelForView({ currentView, currentMode }) {
      // Phase 5: Check manual override first
      if (othelloState.manualChannelOverride) {
          return othelloState.manualChannelOverride;
      }
      
      const view = (currentView || "").toLowerCase();
      // Phase 4: Route based on explicit views, falling back to mode if needed (though modes are deprecated)
      if (view === "today-planner") return "planner"; // Maps to 'planner' context (originally 'today' mode)
      if (view === "goals") return "companion"; // Goals view uses companion/general chat
      if (view === "routine-planner") return "routine";
      if (view === "insights") return "companion"; // Insights uses companion
      
      // Fallback
      if (view === "chat") return "companion";
      return "companion";
    }

    async function fetchChatHistory(limit = 50, channel = "companion") {
      let target = `${V1_MESSAGES_API}?limit=${limit}&channel=${encodeURIComponent(channel)}`;
      if (othelloState.activeConversationId) {
          target = `/api/conversations/${othelloState.activeConversationId}/messages`;
      }
      const resp = await fetch(target, { credentials: "include", cache: "no-store" });
      if (resp.status === 401 || resp.status === 403) {
        const err = new Error("Unauthorized");
        err.status = resp.status;
        throw err;
      }
      let payload = null;
      try {
        payload = await resp.json();
      } catch {}
      if (!resp.ok || (payload && payload.ok === false)) {
        throw new Error("Failed to load chat history");
      }
      return payload && payload.data && Array.isArray(payload.data.messages)
        ? payload.data.messages
        : [];
    }

    async function loadChatHistory() {
      if (!isAuthed || chatHydrated) return;
      try {
        const viewName = othelloState.currentView || "chat";
        const modeName = othelloState.currentMode || "companion";
        const requestedChannel = effectiveChannelForView({
          currentView: viewName,
          currentMode: modeName,
        });
        const messages = await fetchChatHistory(50, requestedChannel);
        clearChatState();
        chatHydrated = true;
        let renderedCount = Array.isArray(messages) ? messages.length : 0;
        const renderMessages = (rows) => {
          (rows || []).forEach((msg) => {
            const text = msg && msg.transcript ? String(msg.transcript) : "";
            if (!text.trim()) return;
            const role = msg && msg.source === "assistant" ? "bot" : "user";
            addMessage(role, text);
          });
          
          // Force scroll to bottom after initial load
          scrollChatToBottom(true);
        };
        if (renderedCount > 0) {
          renderMessages(messages);
        } else if (
          (viewName || "").toLowerCase() === "chat"
          && requestedChannel === "companion"
          && !othelloState.chatHistoryFallbackTried
        ) {
          othelloState.chatHistoryFallbackTried = true;
          const fallbackMessages = await fetchChatHistory(50, "planner");
          if (Array.isArray(fallbackMessages) && fallbackMessages.length) {
            renderedCount = fallbackMessages.length;
            console.debug("[Othello UI] chat history fallback used planner channel", {
              count: renderedCount,
            });
            renderMessages(fallbackMessages);
          }
        }
        console.log(
          `UI: loadChatHistory view=${viewName} mode=${modeName} requested_channel=${requestedChannel} count=${renderedCount}`
        );
      } catch (err) {
        if (err && (err.status === 401 || err.status === 403)) {
          await handleUnauthorized("chat-history");
          return;
        }
        console.warn("[Othello UI] chat history load failed:", err);
      }
    }

    function renderIntentMarkers(metaEl, markers) {
      if (!metaEl || !markers || !markers.length) return;
      const span = document.createElement("span");
      span.className = "ux-intent-marker";
      span.textContent = markers.join(" · ");
      span.style.marginLeft = "0.45rem";
      span.style.fontSize = "0.75rem";
      span.style.opacity = "0.8";
      span.style.userSelect = "none";
      span.style.cursor = "default";
      metaEl.appendChild(span);
    }

    function formatMessageText(text) {
      if (!text) return "";
      let safe = text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
      return safe.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
    }

    function addMessage(role, text, options = {}) {
      console.log("DEBUG: addMessage called", role, text.substring(0, 20) + "...");
      // Hide chat placeholder when first message appears
      const chatPlaceholder = document.getElementById("chat-placeholder");
      if (chatPlaceholder && !chatPlaceholder.classList.contains("hidden")) {
        chatPlaceholder.classList.add("hidden");
      }

      // Resolve container explicitly (Phase B2)
      const container = getChatContainer();
      if (!container) {
          return { row: null, bubble: null };
      }

      const row = document.createElement("div");
      row.className = `msg-row ${role}`;

      // Apply focus highlighting if a goal is focused
      if (othelloState.activeGoalId) {
        row.classList.add("msg--focus-attached");
      }

      const bubble = document.createElement("div");
      bubble.className = "bubble";
      bubble.innerHTML = formatMessageText(text);
      const clientMessageId = options && typeof options.clientMessageId === "string"
        ? options.clientMessageId.trim()
        : "";
      if (clientMessageId) {
        row.dataset.clientMessageId = clientMessageId;
        bubble.dataset.clientMessageId = clientMessageId;
      }

      const meta = document.createElement("div");
      meta.className = "meta";
      const metaNote = options && typeof options.metaNote === "string" ? options.metaNote.trim() : "";
      const metaSuffix = metaNote ? ` | ${metaNote}` : "";
      meta.textContent = role === "user"
        ? "You · " + new Date().toLocaleTimeString([], {hour: "2-digit", minute: "2-digit"}) + metaSuffix
        : "Othello · " + new Date().toLocaleTimeString([], {hour: "2-digit", minute: "2-digit"});

      if (role === "bot" && options && Array.isArray(options.intentMarkers)) {
        renderIntentMarkers(meta, options.intentMarkers);
      }

      bubble.appendChild(meta);

      if (role === "bot" && othelloState.currentMode === "companion") {
        const sourceClientMessageId = options && typeof options.sourceClientMessageId === "string"
          ? options.sourceClientMessageId.trim()
          : "";
        const listItems = extractListItems(text);
        if (hasStructuredList(text) && listItems.length) {
          const convKey = othelloState.activeConversationId ? String(othelloState.activeConversationId) : "default";
          othelloState.lastGoalDraftByConversationId[convKey] = { items: listItems, rawText: text, sourceClientMessageId };
          const bar = createCommitmentBar(listItems, text, sourceClientMessageId);
          bubble.appendChild(bar);
        }
      }

      if (role === "bot" && othelloState.activeGoalId !== null && isPlanLikeText(text)) {
        const planBar = createPlanActionBar(text);
        bubble.appendChild(planBar);
      }

      row.appendChild(bubble);
      
      // Append to the resolved container
      if (container) {
         container.appendChild(row);
      }
      
      updateDuetView(row, role);

      if (role === "user" && clientMessageId) {
        othelloState.messagesByClientId[clientMessageId] = {
          clientMessageId,
          bubbleEl: bubble,
          rowEl: row,
          text,
          ts: Date.now(),
          panelEl: null,
        };
        refreshSecondarySuggestionUI(othelloState.messagesByClientId[clientMessageId]);
      }

      // Scroll to latest message (Smart Scroll - Phase B3)
      scrollChatToBottom(false);
      return { row, bubble };
    }

    function suggestionKey(type, clientMessageId) {
      return `${type}:${clientMessageId}`;
    }

    function isSuggestionDismissed(type, clientMessageId) {
      if (!type || !clientMessageId) return true;
      const key = suggestionKey(type, clientMessageId);
      return othelloState.dismissedSuggestionIds && othelloState.dismissedSuggestionIds.has(key);
    }

    function recordSuggestionDismissal(type, clientMessageId) {
      if (!type || !clientMessageId) return;
      const key = suggestionKey(type, clientMessageId);
      if (!othelloState.dismissedSuggestionIds) {
        othelloState.dismissedSuggestionIds = new Set();
      }
      othelloState.dismissedSuggestionIds.add(key);
      persistDismissedSuggestionIds();
    }

    async function postSuggestionDismissal(type, clientMessageId) {
      if (!type || !clientMessageId) return;
      try {
        await fetch(SUGGESTION_DISMISS_API, {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          credentials: "include",
          body: JSON.stringify({ type, source_client_message_id: clientMessageId })
        });
      } catch (err) {
        console.warn("[Othello UI] suggestion dismiss failed:", err);
      }
    }

    function getSecondarySuggestions(clientMessageId) {
      if (!clientMessageId) return [];
      const store = othelloState.secondarySuggestionsByClientId || {};
      return store[clientMessageId] || [];
    }

    function updateSecondaryBadge(entry) {
      if (!entry || !entry.clientMessageId || !entry.bubbleEl) return;
      const suggestions = getSecondarySuggestions(entry.clientMessageId);
      const count = suggestions.length;
      const meta = entry.bubbleEl.querySelector(".meta");
      if (!meta) return;
      if (!count) {
        if (entry.secondaryBadgeEl) {
          entry.secondaryBadgeEl.remove();
          entry.secondaryBadgeEl = null;
        }
        if (entry.secondaryPanelEl) entry.secondaryPanelEl.style.display = "none";
        return;
      }
      let badge = entry.secondaryBadgeEl;
      if (!badge || !badge.isConnected) {
        badge = document.createElement("span");
        badge.style.marginLeft = "0.4rem";
        badge.style.cursor = "pointer";
        badge.style.fontSize = "0.75rem";
        badge.style.userSelect = "none";
        badge.addEventListener("click", () => toggleSecondarySuggestionPanel(entry));
        entry.secondaryBadgeEl = badge;
        meta.appendChild(badge);
      }
      
      const hasGoal = suggestions.some(s => s.type === "goal_intent");
      badge.textContent = hasGoal ? "?" : `•${count}`;
      badge.style.fontWeight = hasGoal ? "bold" : "normal";
      badge.style.color = hasGoal ? "var(--accent)" : "inherit";

      if (entry.secondaryPanelEl && entry.secondaryPanelEl.style.display === "flex") {
        renderSecondarySuggestionPanel(entry);
      }
    }

    function refreshSecondarySuggestionUI(entry) {
      updateSecondaryBadge(entry);
    }

    function addSecondarySuggestion(clientMessageId, suggestion) {
      if (!clientMessageId || !suggestion) return false;
      if (!othelloState.secondarySuggestionsByClientId) {
        othelloState.secondarySuggestionsByClientId = {};
      }
      const suggestionType = (suggestion.type || suggestion.kind || "suggestion").toLowerCase();
      const normalizedType = suggestionType === "goal" ? "goal_intent" : suggestionType;
      const suggestionId = suggestion.suggestion_id || suggestion.id || null;
      const key = suggestionId != null ? `${normalizedType}:${suggestionId}` : `${normalizedType}:${clientMessageId}`;
      const list = othelloState.secondarySuggestionsByClientId[clientMessageId] || [];
      
      if (list.some((item) => item.key === key)) return false;
      // Enforce one candidate per type per message
      if (list.some((item) => item.type === normalizedType)) return false;

      list.push({ key, type: normalizedType, suggestionId, suggestion });
      othelloState.secondarySuggestionsByClientId[clientMessageId] = list;
      const entry = othelloState.messagesByClientId[clientMessageId];
      if (entry) {
        entry.clientMessageId = clientMessageId;
        updateSecondaryBadge(entry);
      }
      return true;
    }

    function dismissSecondarySuggestion(clientMessageId, suggestionKey) {
      const list = getSecondarySuggestions(clientMessageId);
      if (!list.length) return;
      const item = list.find((entry) => entry.key === suggestionKey);
      if (item && item.type) {
        recordSuggestionDismissal(item.type, clientMessageId);
        postSuggestionDismissal(item.type, clientMessageId);
      }
      const next = list.filter((entry) => entry.key !== suggestionKey);
      if (next.length) {
        othelloState.secondarySuggestionsByClientId[clientMessageId] = next;
      } else {
        delete othelloState.secondarySuggestionsByClientId[clientMessageId];
      }
      const entry = othelloState.messagesByClientId[clientMessageId];
      if (entry) updateSecondaryBadge(entry);
    }

    async function applySecondarySuggestion(entry, item, uiRefs) {
      if (!entry || !item) return false;
      const statusEl = uiRefs && uiRefs.statusEl ? uiRefs.statusEl : null;
      const actionsEl = uiRefs && uiRefs.actionsEl ? uiRefs.actionsEl : null;
      const applyBtn = uiRefs && uiRefs.applyBtn ? uiRefs.applyBtn : null;
      if (item.type === "routine" && item.suggestionId) {
        const priorPendingId = othelloState.pendingRoutineSuggestionId;
        const priorAcceptFn = othelloState.pendingRoutineAcceptFn;
        const accepted = await acceptRoutineSuggestion(item.suggestionId, { confirmBtn: applyBtn, statusEl, actionsEl });
        if (getActiveFocusKind(othelloState) === "routine_draft" && priorPendingId && priorPendingId !== item.suggestionId) {
          othelloState.pendingRoutineSuggestionId = priorPendingId;
          othelloState.pendingRoutineAcceptFn = priorAcceptFn;
        }
        return accepted;
      }
      if ((item.type === "goal_intent" || item.type === "goal") && item.suggestion) {
        const prevActiveGoalId = othelloState.activeGoalId;
        const title = pickSuggestionTitle(item.suggestion, entry.text);
        const description = pickSuggestionBody(item.suggestion, entry.text);
        const accepted = await createGoalFromSuggestion({
          title,
          description,
          clientMessageId: entry.clientMessageId,
          statusEl,
          panelEl: actionsEl,
          suggestionId: item.suggestionId,
          payload: item.suggestion ? item.suggestion.payload : null
        });
        if (prevActiveGoalId !== othelloState.activeGoalId) {
          setActiveGoal(prevActiveGoalId);
        }
        return accepted;
      }
      return false;
    }

    function ensureSecondaryPanel(entry) {
      if (!entry || !entry.rowEl) return null;
      if (entry.secondaryPanelEl && entry.secondaryPanelEl.isConnected) return entry.secondaryPanelEl;
      const panel = document.createElement("div");
      panel.className = "ux-goal-intent-panel";
      panel.style.display = "none";
      panel.addEventListener("click", async (event) => {
        const button = event.target.closest("button[data-action]");
        if (!button) return;
        const itemEl = button.closest("[data-secondary-key]");
        if (!itemEl) return;
        const key = itemEl.dataset.secondaryKey;
        const suggestions = getSecondarySuggestions(entry.clientMessageId);
        const item = suggestions.find((suggestion) => suggestion.key === key);
        if (!item) return;
        if (button.dataset.action === "dismiss") {
          dismissSecondarySuggestion(entry.clientMessageId, key);
          renderSecondarySuggestionPanel(entry);
          return;
        }
        const statusEl = itemEl.querySelector(".ux-goal-intent-status");
        const actionsEl = itemEl.querySelector(".ux-goal-intent-panel__actions");
        button.disabled = true;
        try {
          const accepted = await applySecondarySuggestion(entry, item, {
            statusEl,
            actionsEl,
            applyBtn: button
          });
          if (accepted) {
            dismissSecondarySuggestion(entry.clientMessageId, key);
          } else {
            button.disabled = false;
          }
        } catch (err) {
          if (statusEl) {
            statusEl.textContent = err && err.message ? err.message : "Apply failed.";
          }
          button.disabled = false;
        }
      });
      entry.secondaryPanelEl = panel;
      entry.rowEl.appendChild(panel);
      return panel;
    }

    function renderSecondarySuggestionPanel(entry) {
      if (!entry || !entry.clientMessageId) return;
      const panel = ensureSecondaryPanel(entry);
      if (!panel) return;
      const suggestions = getSecondarySuggestions(entry.clientMessageId);
      panel.innerHTML = "";
      if (!suggestions.length) {
        panel.style.display = "none";
        return;
      }
      suggestions.forEach((item) => {
        const suggestion = item.suggestion || {};
        const itemEl = document.createElement("div");
        itemEl.dataset.secondaryKey = item.key;
        const title = document.createElement("div");
        title.className = "ux-goal-intent-panel__title";
        title.textContent = item.type === "routine" ? "Routine suggestion" : "Goal suggestion";
        const summary = document.createElement("div");
        summary.className = "ux-goal-intent-panel__subtitle";
        if (item.type === "routine") {
          const draft = suggestion.payload && suggestion.payload.draft ? suggestion.payload.draft : null;
          const details = [];
          if (draft && draft.title) details.push(draft.title);
          if (draft) details.push(formatRoutineTime(draft));
          summary.textContent = details.filter(Boolean).join(" · ") || entry.text || "Routine draft";
        } else {
          summary.textContent = pickSuggestionTitle(suggestion, entry.text);
        }
        const actions = document.createElement("div");
        actions.className = "ux-goal-intent-panel__actions";
        const applyBtn = document.createElement("button");
        applyBtn.className = "ux-goal-intent-btn primary";
        applyBtn.dataset.action = "apply";
        applyBtn.textContent = "Apply";
        const dismissBtn = document.createElement("button");
        dismissBtn.className = "ux-goal-intent-btn link";
        dismissBtn.dataset.action = "dismiss";
        dismissBtn.textContent = "Dismiss";
        const statusEl = document.createElement("div");
        statusEl.className = "ux-goal-intent-status";
        actions.appendChild(applyBtn);
        actions.appendChild(dismissBtn);
        itemEl.appendChild(title);
        itemEl.appendChild(summary);
        itemEl.appendChild(actions);
        itemEl.appendChild(statusEl);
        panel.appendChild(itemEl);
      });
    }

    function toggleSecondarySuggestionPanel(entry) {
      const panel = ensureSecondaryPanel(entry);
      if (!panel) return;
      if (panel.style.display === "flex") {
        panel.style.display = "none";
        return;
      }
      renderSecondarySuggestionPanel(entry);
      panel.style.display = "flex";
    }

    function pickSuggestionBody(suggestion, fallbackText) {
      const raw = suggestion && typeof suggestion.body_suggestion === "string"
        ? suggestion.body_suggestion.trim()
        : "";
      if (raw) return raw;
      return (fallbackText || "").trim();
    }

    function pickSuggestionTitle(suggestion, fallbackText) {
      const raw = suggestion && typeof suggestion.title_suggestion === "string"
        ? suggestion.title_suggestion.trim()
        : "";
      if (raw) return raw;
      const original = (fallbackText || "").trim();
      const trimmed = original
        .replace(/^(my goal is|my goal|next goal|goal)\s*[:\-]?\s*/i, "")
        .replace(/^(i want to|i'm going to|im going to|we need to|i will|we will)\s+/i, "")
        .trim() || original;
      if (!trimmed) return "New goal";
      return trimmed.length > 60 ? trimmed.slice(0, 60).trim() : trimmed;
    }

    function clearGoalIntentUI(clientMessageId) {
      const entry = othelloState.messagesByClientId[clientMessageId];
      if (!entry) return;
      if (entry.bubbleEl) {
        entry.bubbleEl.classList.remove("ux-goal-intent");
      }
      if (entry.panelEl && entry.panelEl.parentNode) {
        entry.panelEl.parentNode.removeChild(entry.panelEl);
      }
      entry.panelEl = null;
    }

    function disablePanelButtons(panelEl, disabled) {
      if (!panelEl) return;
      const buttons = panelEl.querySelectorAll("button");
      buttons.forEach((btn) => {
        btn.disabled = disabled;
      });
    }

    function collectGoalContext(startClientMessageId) {
       if (!startClientMessageId || !othelloState.messagesByClientId[startClientMessageId]) return null;
       const context = [];
       let currentRow = othelloState.messagesByClientId[startClientMessageId].rowEl;
       while (currentRow) {
           if (currentRow.classList.contains("msg-row")) {
               const role = currentRow.classList.contains("user") ? "user" : "assistant";
               const bubble = currentRow.querySelector(".bubble");
               if (bubble) {
                   const clone = bubble.cloneNode(true);
                   // Cleanup UI elements to get just text
                   const meta = clone.querySelector(".meta");
                   if (meta) meta.remove();
                   const bars = clone.querySelectorAll(".commitment-bar, .plan-action-bar, .planner-card");
                   bars.forEach(b => b.remove());
                   
                   context.push({ role, text: clone.textContent.trim() });
               }
           }
           currentRow = currentRow.nextElementSibling;
       }
       return context.length > 0 ? context : null;
    }

    async function createGoalFromSuggestion(opts) {
      const { title, description, clientMessageId, statusEl, panelEl, onSuccess, suggestionId, payload } = opts;
      const trimmedTitle = (title || "").trim();
      const trimmedDesc = (description || "").trim();
      if (trimmedTitle.length < 3) {
        if (statusEl) statusEl.textContent = "Title is too short.";
        return false;
      }
      disablePanelButtons(panelEl, true);
      if (statusEl) statusEl.textContent = "Saving goal...";
      
      const goalContext = collectGoalContext(clientMessageId);

      try {
        // Phase 21: Direct Chat Action (No v1/create)
        // If it's a virtual suggestion (no real ID) or even if it is, we prefer the chat action route
        // to keep the conversation in sync.
        
        // Use global sendMessage if available (it should be)
        if (typeof sendMessage === 'function') {
             await sendMessage("", {
                 ui_action: "create_goal_from_message",
                 source_message_id: clientMessageId,
                 title: trimmedTitle,
                 description: trimmedDesc,
                 payload: payload || (othelloState.goalIntentSuggestions[clientMessageId] ? othelloState.goalIntentSuggestions[clientMessageId].payload : null),
                 goal_context: goalContext
             });
             // The API will return 'focus_goal' action which we handle in socket message
             return true;
        }

        // Fallback (shouldn't be reached in normal flow)
        console.warn("sendMessage not found, falling back to legacy create");
        return false;
      } catch (e) {
        console.error("Failed to create goal", e);
        if (statusEl) statusEl.textContent = "Error saving goal.";
        disablePanelButtons(panelEl, false);
        return false;
      }
    }


    async function addNoteToFocusedGoal(opts) {
      const { text, clientMessageId, statusEl, panelEl } = opts;
      const goalId = othelloState.activeGoalId;
      if (goalId == null) {
        if (statusEl) statusEl.textContent = "No focused goal.";
        return;
      }
      const noteText = (text || "").trim();
      if (!noteText) {
        if (statusEl) statusEl.textContent = "Note text is empty.";
        return;
      }
      disablePanelButtons(panelEl, true);
      if (statusEl) statusEl.textContent = "Adding to focused goal...";
      try {
        const res = await fetch(`/api/goals/${goalId}/notes`, {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          credentials: "include",
          body: JSON.stringify({
            text: noteText,
            source_client_message_id: clientMessageId
          })
        });
        if (!res.ok) {
          const contentType = res.headers.get("content-type") || "";
          let errMsg = "Unable to add note.";
          if (contentType.includes("application/json")) {
            const data = await res.json();
            errMsg = (data && (data.message || data.error)) || errMsg;
          }
          if (statusEl) statusEl.textContent = errMsg;
          disablePanelButtons(panelEl, false);
          return;
        }
        clearGoalIntentUI(clientMessageId);
        showToast("Added to focused goal");
        await refreshGoals();
        if (othelloState.currentDetailGoalId === goalId) {
          refreshGoalDetail();
        }
      } catch (err) {
        console.error("[Othello UI] add note failed:", err);
        if (statusEl) statusEl.textContent = "Network error.";
        disablePanelButtons(panelEl, false);
      }
    }

    function buildGoalIntentPanel(suggestion, entry) {
      const clientMessageId = suggestion.source_client_message_id;
      const suggestionId = suggestion.suggestion_id || suggestion.id || null;
      const panel = document.createElement("div");
      panel.className = "ux-goal-intent-panel";
      panel.dataset.clientMessageId = clientMessageId;
      panel.dataset.suggestionType = suggestion.type;
      if (suggestionId != null) {
        panel.dataset.suggestionId = String(suggestionId);
      }

      const title = document.createElement("div");
      title.className = "ux-goal-intent-panel__title";
      title.textContent = "Is this a goal?";

      const subtitle = document.createElement("div");
      subtitle.className = "ux-goal-intent-panel__subtitle";
      subtitle.textContent = "Nothing is saved until you choose.";

      const actions = document.createElement("div");
      actions.className = "ux-goal-intent-panel__actions";

      const saveBtn = document.createElement("button");
      saveBtn.className = "ux-goal-intent-btn primary";
      saveBtn.textContent = "Save as Goal";

      const editBtn = document.createElement("button");
      editBtn.className = "ux-goal-intent-btn secondary";
      editBtn.textContent = "Edit";

      const dismissBtn = document.createElement("button");
      dismissBtn.className = "ux-goal-intent-btn link";
      dismissBtn.textContent = "Dismiss";

      const addBtn = document.createElement("button");
      addBtn.className = "ux-goal-intent-btn secondary";
      addBtn.textContent = "Add to Focused Goal";
      const showAddBtn = othelloState.activeGoalId != null;
      actions.appendChild(saveBtn);
      if (showAddBtn) {
        actions.appendChild(addBtn);
      }
      actions.appendChild(editBtn);
      actions.appendChild(dismissBtn);

      const editor = document.createElement("div");
      editor.className = "ux-goal-intent-editor";
      editor.style.display = "none";

      const titleInput = document.createElement("input");
      titleInput.className = "ux-goal-intent-input";
      titleInput.type = "text";
      titleInput.value = pickSuggestionTitle(suggestion, entry.text);

      const bodyInput = document.createElement("textarea");
      bodyInput.className = "ux-goal-intent-textarea";
      bodyInput.value = pickSuggestionBody(suggestion, entry.text);

      const editorActions = document.createElement("div");
      editorActions.className = "ux-goal-intent-panel__actions";

      const createBtn = document.createElement("button");
      createBtn.className = "ux-goal-intent-btn primary";
      createBtn.textContent = "Create Goal";

      const addFocusedBtn = document.createElement("button");
      addFocusedBtn.className = "ux-goal-intent-btn secondary";
      addFocusedBtn.textContent = "Add to Focused Goal";

      const cancelBtn = document.createElement("button");
      cancelBtn.className = "ux-goal-intent-btn link";
      cancelBtn.textContent = "Cancel";

      editorActions.appendChild(createBtn);
      if (showAddBtn) {
        editorActions.appendChild(addFocusedBtn);
      }
      editorActions.appendChild(cancelBtn);

      const status = document.createElement("div");
      status.className = "ux-goal-intent-status";

      editor.appendChild(titleInput);
      editor.appendChild(bodyInput);
      editor.appendChild(editorActions);

      panel.appendChild(title);
      panel.appendChild(subtitle);
      panel.appendChild(actions);
      panel.appendChild(editor);
      panel.appendChild(status);

      function openEditor() {
        editor.style.display = "flex";
        status.textContent = "";
        setTimeout(() => titleInput.focus(), 0);
      }

      saveBtn.addEventListener("click", () => {
        openEditor();
      });

      editBtn.addEventListener("click", () => {
        openEditor();
      });

      dismissBtn.addEventListener("click", () => {
        recordSuggestionDismissal(suggestion.type, clientMessageId);
        postSuggestionDismissal(suggestion.type, clientMessageId);
        clearGoalIntentUI(clientMessageId);
      });

      if (showAddBtn) {
        addBtn.addEventListener("click", () => {
          addNoteToFocusedGoal({
            text: pickSuggestionBody(suggestion, entry.text),
            clientMessageId,
            statusEl: status,
            panelEl: panel
          });
        });
      }

      createBtn.addEventListener("click", () => {
        createGoalFromSuggestion({
          title: titleInput.value,
          description: bodyInput.value,
          clientMessageId,
          statusEl: status,
          panelEl: panel,
          suggestionId
        });
      });

      if (showAddBtn) {
        addFocusedBtn.addEventListener("click", () => {
          addNoteToFocusedGoal({
            text: bodyInput.value,
            clientMessageId,
            statusEl: status,
            panelEl: panel
          });
        });
      }

      cancelBtn.addEventListener("click", () => {
        editor.style.display = "none";
        status.textContent = "";
        disablePanelButtons(panel, false);
      });

      return panel;
    }

    function getActiveFocusKind(uiState) {
      // Routine draft wins; otherwise focused goal; else null.
      if (!uiState) return null;
      if (uiState.pendingRoutineSuggestionId != null) return "routine_draft";
      if (uiState.activeGoalId != null) return "goal";
      return null;
    }

    function shouldSuggestGoalDraft(userText, response, uiState) {
      const raw = String(userText || "").trim();
      if (!raw) return false;
      const text = raw.toLowerCase();

      // Hard negative guard: question intent must never trigger goal candidates
      if (text.includes("question") || text.includes("?") || 
          text.startsWith("i want to ask") || text.startsWith("i have a question") ||
          text.startsWith("can i ask") || text.startsWith("could i ask")) {
        return false;
      }

      const tokens = text.split(/\s+/).filter(Boolean);
      const explicitGoal = /(goal:|my goal is|i want to|i'm going to|im going to|i am going to|i will|new goal|i need to achieve|i'm working towards|im working towards)/.test(text);
      if (tokens.length <= 4 && !explicitGoal) return false;
      if (/^(what|why|how|when|where|who|can|should|do|is|are)\b/.test(text)) {
        return false;
      }
      const routineSignals = /\b(every day|each day|daily|weekly|remind me|alarm|routine|habit|meet at)\b/.test(text);
      const timeSignals = /(\b([01]?\d|2[0-3]):([0-5]\d)\b|\b([1-9]|1[0-2])\s*(a\.?m\.?|p\.?m\.?)\b|\b(at|around|by)\s+([1-9]|1[0-2])\b)/.test(text);
      if (routineSignals || timeSignals) return false;
      if (!explicitGoal && uiState && uiState.pendingRoutineSuggestionId) return false;
      const routinePanel = document.querySelector('.ux-goal-intent-panel[data-suggestion-type="routine"]');
      if (routinePanel && routinePanel.offsetParent !== null && !explicitGoal) return false;
      return explicitGoal;
    }

    function handleGoalIntentSuggestion(suggestion) {
      if (!suggestion) return;
      const suggestionType = suggestion.type || suggestion.kind;
      if (suggestionType !== "goal_intent" && suggestionType !== "goal") return;
      const normalizedSuggestion = suggestionType === "goal"
        ? { ...suggestion, type: "goal_intent" }
        : suggestion;
      const clientMessageId = normalizedSuggestion.source_client_message_id;
      if (!clientMessageId) return;
      const entry = othelloState.messagesByClientId[clientMessageId] || null;
      const entryText = entry && typeof entry.text === "string" ? entry.text : "";
      if (!shouldSuggestGoalDraft(entryText, normalizedSuggestion, othelloState)) return;
      if (isSuggestionDismissed(normalizedSuggestion.type, clientMessageId)) return;
      
      // Always use secondary suggestion for goal intents (candidate flow)
      addSecondarySuggestion(clientMessageId, normalizedSuggestion);
    }

    function applySuggestionMeta(meta) {
      const suggestions = meta && Array.isArray(meta.suggestions) ? meta.suggestions : [];
      suggestions.forEach(handleGoalIntentSuggestion);
    }

    function formatRoutineDays(days) {
      if (!Array.isArray(days) || days.length === 0) return "Days TBD";
      const labels = {
        mon: "Mon",
        tue: "Tue",
        wed: "Wed",
        thu: "Thu",
        fri: "Fri",
        sat: "Sat",
        sun: "Sun"
      };
      return days.map((day) => labels[day] || day).join(", ");
    }

    function formatRoutineTime(draft) {
      if (!draft) return "Time TBD";
      return draft.time_local || draft.time_text || "Time TBD";
    }

    function formatRoutineDuration(minutes) {
      if (!Number.isFinite(minutes)) return "";
      return `${Math.trunc(minutes)} min`;
    }

    function requestRoutineRefresh() {
      if (othelloState.currentView === "routine-planner" && typeof loadRoutinePlanner === "function") {
        loadRoutinePlanner();
      } else {
        othelloState.needsRoutineRefresh = true;
      }
    }

    function clearPendingRoutineSuggestion() {
      othelloState.pendingRoutineSuggestionId = null;
      othelloState.pendingRoutineAcceptFn = null;
    }
    function isElementVisible(el) {
      if (!el) return false;
      const style = window.getComputedStyle(el);
      if (!style || style.display === "none" || style.visibility === "hidden") return false;
      return el.offsetParent !== null;
    }

    function findVisiblePendingRoutinePanel() {
      const panels = Array.from(
        document.querySelectorAll('.ux-goal-intent-panel[data-suggestion-type="routine"]')
      );
      const visible = panels.filter(isElementVisible).pop() || null;
      return visible;
    }

    async function acceptRoutineSuggestion(suggestionId, uiRefs) {
      if (!suggestionId) return false;
      const confirmBtn = uiRefs && uiRefs.confirmBtn;
      const statusEl = uiRefs && uiRefs.statusEl;
      const actionsEl = uiRefs && uiRefs.actionsEl;
      if (confirmBtn) confirmBtn.disabled = true;
      if (statusEl) statusEl.textContent = "Saving...";
      try {
        const confirmPayload = { reason: "confirm" };
        await v1Request(
          `/v1/suggestions/${suggestionId}/accept`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify(confirmPayload)
          },
          "Confirm routine suggestion"
        );
        if (statusEl) {
          statusEl.textContent = "Saved";
          if (actionsEl) {
            actionsEl.innerHTML = "";
            actionsEl.appendChild(statusEl);
          }
        }
        requestRoutineRefresh();
        clearPendingRoutineSuggestion();
        return true;
      } catch (err) {
        if (err && (err.status === 401 || err.status === 403)) {
          await handleUnauthorized("routine-accept");
          return false;
        }
        if (statusEl) {
          statusEl.textContent = err && err.message ? err.message : "Save failed.";
        }
        if (confirmBtn) confirmBtn.disabled = false;
        return false;
      }
    }

    async function patchRoutineSuggestion(suggestionId, text, panel) {
      if (!suggestionId) return null;
      const statusEl = panel ? panel.querySelector(".ux-goal-intent-status") : null;
      if (statusEl) statusEl.textContent = "Updating...";
      const payload = await v1Request(
        `/v1/suggestions/${suggestionId}/patch`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({ text })
        },
        "Update routine suggestion"
      );
      const suggestion = payload && payload.data ? payload.data.suggestion : null;
      const row = panel && panel.parentNode ? panel.parentNode : null;
      if (panel && panel.parentNode) panel.parentNode.removeChild(panel);
      if (row && suggestion) {
        const entry = { row };
        if (suggestion.payload && suggestion.payload.status === "incomplete") {
          await buildRoutineClarifyPanel(entry, suggestionId);
        } else {
          buildRoutineReadyPanel(entry, suggestion, suggestionId);
        }
      }
      return suggestion;
    }

    async function rejectRoutineSuggestion(suggestionId, panel) {
      if (!suggestionId) return false;
      const statusEl = panel ? panel.querySelector(".ux-goal-intent-status") : null;
      if (statusEl) statusEl.textContent = "Dismissing...";
      try {
        await v1Request(
          "/v1/confirm",
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify({
              decisions: [{ suggestion_id: suggestionId, action: "reject", reason: "dismiss" }]
            })
          },
          "Dismiss routine suggestion"
        );
        clearPendingRoutineSuggestion();
        if (panel && panel.parentNode) {
          panel.parentNode.removeChild(panel);
        }
        return true;
      } catch (err) {
        if (err && (err.status === 401 || err.status === 403)) {
          await handleUnauthorized("routine-dismiss");
          return false;
        }
        if (statusEl) {
          statusEl.textContent = err && err.message ? err.message : "Dismiss failed.";
        }
        return false;
      }
    }

    function sendQuickReply(text) {
      if (!input) return;
      input.value = text;
      sendMessage();
    }

    async function fetchRoutineSuggestionById(suggestionId) {
      if (!suggestionId) return null;
      const payload = await v1Request(
        "/v1/suggestions?status=pending&kind=routine&limit=20",
        { credentials: "include" },
        "Routine suggestions"
      );
      const suggestions = Array.isArray(payload?.data?.suggestions) ? payload.data.suggestions : [];
      return suggestions.find((s) => String(s.id) === String(suggestionId)) || null;
    }

    function extractRoutineHourHint(draft) {
      const fallback = 7;
      if (!draft) return fallback;
      const timeText = typeof draft.time_text === "string" ? draft.time_text : "";
      const timeLocal = typeof draft.time_local === "string" ? draft.time_local : "";
      let hour = null;
      const textMatch = timeText.match(/\b([01]?\d|2[0-3])(?::[0-5]\d)?\b/);
      if (textMatch) {
        hour = parseInt(textMatch[1], 10);
      } else if (timeLocal) {
        const localMatch = timeLocal.match(/^([01]\d|2[0-3]):/);
        if (localMatch) {
          hour = parseInt(localMatch[1], 10);
        }
      }
      if (!Number.isFinite(hour)) return fallback;
      if (hour === 0) return 12;
      if (hour > 12) return hour - 12;
      return hour;
    }

    async function buildRoutineClarifyPanel(entry, suggestionId) {
      if (!entry || !entry.row) return null;
      const panel = document.createElement("div");
      panel.className = "ux-goal-intent-panel";
      panel.dataset.suggestionType = "routine";
      panel.dataset.suggestionId = suggestionId || "";
      if (suggestionId) {
        othelloState.pendingRoutineSuggestionId = suggestionId;
        othelloState.pendingRoutineAcceptFn = null;
      }

      const title = document.createElement("div");
      title.className = "ux-goal-intent-panel__title";
      title.textContent = "Routine clarification";
      panel.appendChild(title);

      const actions = document.createElement("div");
      actions.className = "ux-goal-intent-panel__actions";

      const collapseRoutineClarifyPanel = (chosenLabel) => {
        if (!actions) return;
        const status = document.createElement("div");
        status.className = "ux-goal-intent-status";
        status.textContent = `Sent: ${chosenLabel} - updating...`;
        actions.innerHTML = "";
        actions.appendChild(status);
        window.setTimeout(() => {
          if (panel && panel.parentNode) {
            panel.style.display = "none";
          }
        }, 600);
      };

      const amBtn = document.createElement("button");
      amBtn.className = "ux-goal-intent-btn secondary";
      amBtn.textContent = "7am";
      amBtn.addEventListener("click", () => {
        const replyText = amBtn.dataset.reply || amBtn.textContent;
        amBtn.disabled = true;
        pmBtn.disabled = true;
        collapseRoutineClarifyPanel(replyText);
        sendQuickReply(replyText);
      });

      const pmBtn = document.createElement("button");
      pmBtn.className = "ux-goal-intent-btn secondary";
      pmBtn.textContent = "7pm";
      pmBtn.addEventListener("click", () => {
        const replyText = pmBtn.dataset.reply || pmBtn.textContent;
        amBtn.disabled = true;
        pmBtn.disabled = true;
        collapseRoutineClarifyPanel(replyText);
        sendQuickReply(replyText);
      });

      const applyHourHint = (hour) => {
        const normalized = Number.isFinite(hour) ? hour : 7;
        const amLabel = `${normalized}am`;
        const pmLabel = `${normalized}pm`;
        amBtn.textContent = amLabel;
        pmBtn.textContent = pmLabel;
        amBtn.dataset.reply = amLabel;
        pmBtn.dataset.reply = pmLabel;
      };
      applyHourHint(7);

      actions.appendChild(amBtn);
      actions.appendChild(pmBtn);

      const dismissBtn = document.createElement("button");
      dismissBtn.className = "ux-goal-intent-btn link";
      dismissBtn.dataset.action = "dismiss";
      dismissBtn.textContent = "Dismiss";
      dismissBtn.addEventListener("click", async () => {
        await rejectRoutineSuggestion(suggestionId, panel);
      });
      actions.appendChild(dismissBtn);
      panel.appendChild(actions);

      entry.row.appendChild(panel);

      if (suggestionId) {
        try {
          const suggestion = await fetchRoutineSuggestionById(suggestionId);
          const draft = suggestion && suggestion.payload ? suggestion.payload.draft : null;
          const hourHint = extractRoutineHourHint(draft);
          applyHourHint(hourHint);
        } catch (err) {
          console.warn("[Othello UI] routine clarify fetch failed:", err);
        }
      }
      return panel;
    }

    function buildRoutineReadyPanel(entry, suggestion, suggestionId) {
      if (!entry || !entry.row) return null;
      const panel = document.createElement("div");
      panel.className = "ux-goal-intent-panel";
      panel.dataset.suggestionType = "routine";
      panel.dataset.suggestionId = suggestionId || "";

      const draft = suggestion && suggestion.payload && suggestion.payload.draft
        ? suggestion.payload.draft
        : {};
      const title = document.createElement("div");
      title.className = "ux-goal-intent-panel__title";
      title.textContent = draft.title || "Routine draft";
      panel.appendChild(title);

      const subtitle = document.createElement("div");
      subtitle.className = "ux-goal-intent-panel__subtitle";
      const details = [
        formatRoutineDays(draft.days_of_week),
        formatRoutineTime(draft)
      ];
      const durationText = formatRoutineDuration(draft.duration_minutes);
      if (durationText) details.push(durationText);
      subtitle.textContent = details.filter(Boolean).join(" · ");
      panel.appendChild(subtitle);

      const actions = document.createElement("div");
      actions.className = "ux-goal-intent-panel__actions";

      const confirmBtn = document.createElement("button");
      confirmBtn.className = "ux-goal-intent-btn primary";
      confirmBtn.dataset.action = "confirm";
      confirmBtn.textContent = "Confirm";

      const editBtn = document.createElement("button");
      editBtn.className = "ux-goal-intent-btn secondary";
      editBtn.dataset.action = "edit";
      editBtn.textContent = "Edit";
      editBtn.addEventListener("click", () => {
        if (!input) return;
        input.value = "Edit: ";
        input.focus();
      });

      const addAnotherBtn = document.createElement("button");
      addAnotherBtn.className = "ux-goal-intent-btn secondary";
      addAnotherBtn.dataset.action = "add-another";
      addAnotherBtn.textContent = "Add another";
      addAnotherBtn.addEventListener("click", async () => {
        if (!suggestionId) return;
        const accepted = await acceptRoutineSuggestion(
          suggestionId,
          { confirmBtn: addAnotherBtn, statusEl: status, actionsEl: actions }
        );
        if (accepted && input) {
          input.value = "Add a routine: ";
          input.focus();
        }
      });

      const dismissBtn = document.createElement("button");
      dismissBtn.className = "ux-goal-intent-btn link";
      dismissBtn.dataset.action = "dismiss";
      dismissBtn.textContent = "Dismiss";
      dismissBtn.addEventListener("click", async () => {
        await rejectRoutineSuggestion(suggestionId, panel);
      });

      const status = document.createElement("div");
      status.className = "ux-goal-intent-status";

      if (suggestionId) {
        othelloState.pendingRoutineSuggestionId = suggestionId;
        othelloState.pendingRoutineAcceptFn = () => acceptRoutineSuggestion(
          suggestionId,
          { confirmBtn, statusEl: status, actionsEl: actions }
        );
      }

      confirmBtn.addEventListener("click", async () => {
        if (!suggestionId) return;
        await acceptRoutineSuggestion(
          suggestionId,
          { confirmBtn, statusEl: status, actionsEl: actions }
        );
      });

      actions.appendChild(confirmBtn);
      actions.appendChild(editBtn);
      actions.appendChild(addAnotherBtn);
      actions.appendChild(dismissBtn);
      panel.appendChild(actions);
      panel.appendChild(status);

      entry.row.appendChild(panel);
      return panel;
    }

    async function applyRoutineMeta(meta, entry, sourceClientMessageId) {
      if (!meta || !entry || !entry.row) return;
      const intent = meta.intent || "";
      const suggestionId = meta.routine_suggestion_id;
      if (!suggestionId) return;
      const focusKind = getActiveFocusKind(othelloState);
      const clientMessageId = meta.source_client_message_id || sourceClientMessageId || "";
      if (focusKind) {
        if (clientMessageId) {
          addSecondarySuggestion(clientMessageId, {
            type: "routine",
            suggestion_id: suggestionId
          });
        }
        return;
      }
      if (intent === "routine_clarify") {
        await buildRoutineClarifyPanel(entry, suggestionId);
        return;
      }
      if (intent === "routine_ready") {
        let suggestion = null;
        try {
          suggestion = await fetchRoutineSuggestionById(suggestionId);
        } catch (err) {
          console.warn("[Othello UI] routine suggestion fetch failed:", err);
        }
        buildRoutineReadyPanel(entry, suggestion, suggestionId);
      }
    }

    function getLatestGoalIntentEntry() {
      const entries = Object.entries(othelloState.messagesByClientId || {});
      let latest = null;
      entries.forEach(([clientMessageId, entry]) => {
        if (!entry || !entry.panelEl) return;
        if (!latest || (entry.ts || 0) > (latest.entry.ts || 0)) {
          latest = { clientMessageId, entry };
        }
      });
      return latest;
    }

    function findVisibleGoalIntentEntry() {
      const latest = getLatestGoalIntentEntry();
      if (!latest || !latest.entry || !latest.entry.panelEl) return null;
      if (!isElementVisible(latest.entry.panelEl)) return null;
      return latest;
    }

    async function acceptVisibleGoalIntentSuggestion() {
      const latest = findVisibleGoalIntentEntry();
      if (!latest || !latest.entry) return { handled: false, accepted: false };
      const { clientMessageId, entry } = latest;
      const suggestion = othelloState.goalIntentSuggestions[clientMessageId];
      if (!suggestion) return { handled: false, accepted: false };
      const panelEl = entry.panelEl;
      const statusEl = panelEl ? panelEl.querySelector(".ux-goal-intent-status") : null;
      const title = pickSuggestionTitle(suggestion, entry.text);
      const description = pickSuggestionBody(suggestion, entry.text);
      const suggestionId = suggestion.suggestion_id || suggestion.id || null;
      try {
        const accepted = await createGoalFromSuggestion({
          title,
          description,
          clientMessageId,
          statusEl,
          panelEl,
          suggestionId
        });
        return { handled: true, accepted: !!accepted };
      } catch (err) {
        console.warn("[Othello UI] goal typed confirm failed:", err);
        return { handled: true, accepted: false };
      }
    }

    function parseGoalIntentDecision(text) {
      const normalized = String(text || "")
        .toLowerCase()
        .replace(/[^\w\s]/g, " ")
        .replace(/\s+/g, " ")
        .trim();
      if (!normalized) return null;
      if (/\b(step|steps|break|split|plan)\b/.test(normalized)) return "steps";
      if (/\b(save|saved|goal|yes|ok|okay|yep)\b/.test(normalized)) return "save";
      return null;
    }

    async function resolveGoalIntentDecision(text) {
      const decision = parseGoalIntentDecision(text);
      if (!decision) return false;
      const latest = getLatestGoalIntentEntry();
      if (!latest) return false;
      const { clientMessageId, entry } = latest;
      const suggestion = othelloState.goalIntentSuggestions[clientMessageId];
      if (!suggestion || !entry) return false;
      const panelEl = entry.panelEl;
      const statusEl = panelEl ? panelEl.querySelector(".ux-goal-intent-status") : null;
      const title = pickSuggestionTitle(suggestion, entry.text);
      const description = pickSuggestionBody(suggestion, entry.text);
      const suggestionId = suggestion.suggestion_id || suggestion.id || null;

      if (decision === "save") {
        await createGoalFromSuggestion({
          title,
          description,
          clientMessageId,
          statusEl,
          panelEl,
          suggestionId
        });
        return true;
      }

      return false;
    }

    function normalizeGoalId(goalId) {
      if (typeof goalId === "number" && Number.isFinite(goalId)) {
        return Math.trunc(goalId);
      }
      const raw = String(goalId || "").trim();
      const match = raw.match(/\d+/);
      if (!match) return null;
      const parsed = parseInt(match[0], 10);
      return Number.isFinite(parsed) ? parsed : null;
    }

    function setActiveGoal(goalId) {
      const normalizedId = goalId == null ? null : normalizeGoalId(goalId);
      othelloState.activeGoalId = normalizedId;
      if (normalizedId != null && !(normalizedId in othelloState.goalUpdateCounts)) {
        othelloState.goalUpdateCounts[normalizedId] = 0;
      }
      othelloState.pendingGoalEdit = null;
      updateFocusRibbon();
    }

    function bumpActiveGoalUpdates() {
      const gid = othelloState.activeGoalId;
      if (gid == null) return;
      othelloState.goalUpdateCounts[gid] = (othelloState.goalUpdateCounts[gid] || 0) + 1;
    }

    function detectUserRoutineHint(text) {
      if (!text) return false;
      const t = text.toLowerCase();
      const signals = ["routine", "remind me", "every day", "each day", "daily", "weekly", "habit", "alarm"];
      return signals.some(s => t.includes(s));
    }

    function detectUserGoalHint(text) {
      if (!text) return false;
      const t = text.toLowerCase();
      // Disqualify questions
      if (t.includes("?")) return false;
      const qWords = ["what", "how", "why", "when", "where", "who", "can", "should", "do", "is", "are"];
      if (qWords.some(w => t.startsWith(w + " ") || t === w)) return false;
      
      const signals = [
        "goal", "i have a goal", "i need to create a goal", "create a goal", 
        "set a goal", "new goal", "my goal is", "working towards"
      ];
      return signals.some(s => t.includes(s));
    }

    function beginSendUI(options = {}) {
      const previousStatus = statusEl ? statusEl.textContent : "", label = options.label || "Thinking…", disableSend = options.disableSend !== false;
      if (disableSend && sendBtn) sendBtn.disabled = true;
      if (disableSend && composerActionBtn) composerActionBtn.disabled = true;
      if (statusEl) statusEl.textContent = label;
      return { previousStatus, label, disableSend };
    }

    function endSendUI(state) {
      if (!state) return;
      if (state.disableSend !== false && sendBtn) sendBtn.disabled = false;
      if (state.disableSend !== false && composerActionBtn) composerActionBtn.disabled = false;
      if (statusEl && (!statusEl.textContent || statusEl.textContent === state.label)) {
        statusEl.textContent = state.previousStatus || "Online";
      }
      if (typeof updateComposerUI === "function") updateComposerUI();
    }

    // KITT Scanner Logic
    function setChatThinking(isThinking) {
        const sheet = document.querySelector('.chat-sheet');
        if(sheet) {
            if(isThinking) sheet.classList.add('is-thinking');
            else sheet.classList.remove('is-thinking');
        }
    }
    function beginThinking() {
        if (typeof pendingChatRequests !== 'number') pendingChatRequests = 0;
        pendingChatRequests++;
        setChatThinking(true);
        updateConnectivity('thinking');
    }
    function endThinking() {
        if (typeof pendingChatRequests !== 'number') pendingChatRequests = 0;
        pendingChatRequests = Math.max(0, pendingChatRequests - 1);
        if (pendingChatRequests === 0) {
            setChatThinking(false);
            updateConnectivity('online');
        }
    }

    async function sendMessage(overrideText = null, extraData = {}) {
      // 1) Robust String Safety & Diagnostic
      let override = overrideText;
      if (override !== null && typeof override !== "string") {
          console.warn("[Othello UI] sendMessage received non-string overrideText:", typeof override, override?.constructor?.name);
          override = null;
      }

      if (!extraData || typeof extraData !== "object") {
          extraData = {};
      }

      // Canonical text variable (Refetch input safely)
      const currentInput = document.getElementById('user-input');
      let rawText = (override !== null ? override : (currentInput?.value ?? ""));
      
      console.debug(`[Othello UI] sendMessage triggered. Text length: ${rawText.length}`);
      
      if (typeof rawText !== "string") {
          rawText = String(rawText ?? "");
      }
      const text = rawText.trim();

      if (!text && !extraData.ui_action) return;

      // Voice-first save command (Strict Command Mode)
      const lowerText = text.toLowerCase().trim().replace(/[.!?]+$/, "");
      
      // Intercept "Focus on Goal <id>" for immediate UI switching
      // Matches: "focus on goal 123", "focus on goal 123."
      const focusMatch = lowerText.match(/^focus\s+on\s+goal\s+(\d+)$/);
      if (focusMatch) {
          const targetId = parseInt(focusMatch[1], 10);
          console.log(`[Othello UI] Intercepted focus command for goal ${targetId}`);
          
          input.value = "";
          addMessage("user", text); // Echo user input
          
          if (typeof setActiveGoal === "function") {
             // Activate the goal in UI state (which updates active_goal_id for future messages)
             setActiveGoal(targetId);
             addMessage("bot", `Focused on Goal ${targetId}.`);
          } else {
             console.warn("[Othello UI] setActiveGoal not available");
          }
          return; // Stop processing (do not send as chat)
      }

      const commandPhrases = new Set(["save as long-term goal", "save this as a goal", "create that goal", "save that goal", "lock that in as a goal"]);
      const isQuestion = text.toLowerCase().match(/^(how|can|should|do) i\b/);

      if (commandPhrases.has(lowerText) && !isQuestion) {
          input.value = "";
          input.focus();
          
          const convKey = othelloState.activeConversationId ? String(othelloState.activeConversationId) : "default";
          const draft = othelloState.lastGoalDraftByConversationId[convKey];

          if (draft) {
              showToast("Saving goal...");
              try {
                  await postCommitment("goal", draft.items, draft.rawText, draft.sourceClientMessageId);
                  showToast("Saved as long-term goal.");
                  refreshGoals();
              } catch (e) {
                  showToast("Failed to save goal: " + e.message);
              }
          } else {
               showToast("No goal draft to save in this chat yet.");
          }
          return;
      }

      const pendingEdit = othelloState.pendingGoalEdit;
      const metaNote = pendingEdit ? `Editing goal #${pendingEdit.goal_id}` : "";
      const clientMessageId = generateClientMessageId();
      
      // Capture intent hints immediately
      const hint = { goal: detectUserGoalHint(text), routine: detectUserRoutineHint(text) };
      if (hint.goal || hint.routine) {
        othelloState.intentHintsByClientId[clientMessageId] = hint;
      }

      const normalizedText = text.toLowerCase().replace(/[.!?]+$/, "").trim(), isConfirmSave = normalizedText === "confirm" || normalizedText === "save";
      
      // Only add user bubble if there is actual text
      if (text) {
          addMessage("user", text, { metaNote, clientMessageId });
      } else if (extraData.ui_action) {
          // No bubble for pure UI actions
      }

      if (overrideText === null) {
          input.value = "";
          input.focus();
      }
      let sendUiState = beginSendUI({ label: isConfirmSave ? "Saving..." : "Thinking…", disableSend: true });
      try {
        const pendingRoutineId = othelloState.pendingRoutineSuggestionId;
        if (pendingRoutineId) {
          const routinePanel = findVisiblePendingRoutinePanel();
          const confirmWords = new Set(["confirm", "save", "ok", "okay", "yes"]);
          const dismissWords = new Set(["dismiss", "cancel", "discard"]);
          const addAnotherMatch = normalizedText.startsWith("add another") || normalizedText.startsWith("another routine");
          const editMatch = normalizedText.match(/^(edit|change|update)\b/i);
          if (confirmWords.has(normalizedText)) {
            try {
              if (await acceptRoutineSuggestion(pendingRoutineId, {
                confirmBtn: routinePanel && routinePanel.querySelector('[data-action="confirm"]'),
                statusEl: routinePanel && routinePanel.querySelector(".ux-goal-intent-status"),
                actionsEl: routinePanel && routinePanel.querySelector(".ux-goal-intent-panel__actions")
              })) {
                addMessage("bot", "Confirmed.");
              }
            } catch (err) {
              console.warn("[Othello UI] routine confirm failed:", err);
            }
            return;
          }
          if (addAnotherMatch) {
            const accepted = await acceptRoutineSuggestion(pendingRoutineId, {
              confirmBtn: routinePanel && routinePanel.querySelector('[data-action="add-another"]'),
              statusEl: routinePanel && routinePanel.querySelector(".ux-goal-intent-status"),
              actionsEl: routinePanel && routinePanel.querySelector(".ux-goal-intent-panel__actions")
            });
            if (accepted && input) {
              input.value = "Add a routine: ";
              input.focus();
            }
            return;
          }
          if (dismissWords.has(normalizedText)) {
            await rejectRoutineSuggestion(pendingRoutineId, routinePanel);
            return;
          }
          const patchText = text.toLowerCase();
          const patchSignal = /(\b([01]?\d|2[0-3]):([0-5]\d)\b|\b([1-9]|1[0-2])\s*(a\.?m\.?|p\.?m\.?)\b|\b(morning|afternoon|evening|tonight)\b|\b(at|around|by)\s+([1-9]|1[0-2])\b|\b(daily|every day|each day|weekday|weekdays|weekend|weekends)\b|\bmon(day)?s?\s*-\s*fri(day)?s?\b|\b(mon|tue|wed|thu|fri|sat|sun)\b|\b\d{1,3}\s*(?:-?\s*)?(?:minutes?|mins?|min)\b)/.test(patchText);
          if (editMatch || patchSignal) {
            try {
              await patchRoutineSuggestion(pendingRoutineId, text, routinePanel);
            } catch (err) {
              if (err && (err.status === 401 || err.status === 403)) {
                await handleUnauthorized("routine-patch");
              }
              const statusEl = routinePanel ? routinePanel.querySelector(".ux-goal-intent-status") : null;
              if (statusEl) {
                statusEl.textContent = err && err.message ? err.message : "Update failed.";
              }
              console.warn("[Othello UI] routine patch failed:", err);
            }
            return;
          }
          if (shouldSuggestGoalDraft(text, null, othelloState)) {
            addSecondarySuggestion(clientMessageId, {
              type: "goal_intent",
              source_client_message_id: clientMessageId,
              body_suggestion: text
            });
          }
          addMessage(
            "bot",
            "You have an unsaved routine draft. Confirm, Edit, Add another, or Dismiss before continuing."
          );
          return;
        }

        if (isConfirmSave) {
          const goalDecision = await acceptVisibleGoalIntentSuggestion();
          if (goalDecision.handled) {
            if (goalDecision.accepted) addMessage("bot", "Confirmed.");
            return;
          }

          const routinePanel = findVisiblePendingRoutinePanel(), panelId = routinePanel ? routinePanel.dataset.suggestionId : null;
          const pendingId = othelloState.pendingRoutineSuggestionId;
          const canAcceptRoutine = routinePanel &&
            typeof othelloState.pendingRoutineAcceptFn === "function" &&
            pendingId && panelId &&
            String(pendingId) === String(panelId);
          if (canAcceptRoutine) {
            try {
              if (await othelloState.pendingRoutineAcceptFn()) addMessage("bot", "Confirmed.");
            } catch (err) {
              console.warn("[Othello UI] routine typed confirm failed:", err);
            }
            return;
          }
        }

        if (!isConfirmSave) {
          const goalIntentResolved = await resolveGoalIntentDecision(text);
          if (goalIntentResolved) {
            fetch(V1_MESSAGES_API, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              credentials: "include",
              body: JSON.stringify({ transcript: text, source: "text" })
            }).catch(() => {});
            statusEl.textContent = "Online";
            return;
          }
        }

        const mode = (othelloState.currentMode || "companion").toLowerCase();
        // Phase 6: Auto-routing (backend decides, avoids forced planner)
        const channel = "auto";
        console.debug(`[Othello UI] sendMessage mode=${mode} channel=${channel} view=${othelloState.currentView}`);
        console.log("[Othello UI] Sending plain-message payload:", text);
        
        // Fallback to currently viewed goal if no active goal is set
        let effectiveGoalId = othelloState.activeGoalId || othelloState.currentDetailGoalId || null;
        if (effectiveGoalId && String(effectiveGoalId).startsWith("draft:")) {
            effectiveGoalId = null;
        }

        // Infer draft context if viewing a draft
        let draftId = othelloState.activeDraft ? othelloState.activeDraft.draft_id : null;
        let draftType = othelloState.activeDraft ? othelloState.activeDraft.draft_type : null;
        
        if (!draftId && othelloState.currentDetailGoalId && String(othelloState.currentDetailGoalId).startsWith("draft:")) {
            const parts = String(othelloState.currentDetailGoalId).split(":");
            if (parts.length > 1) {
                 draftId = parseInt(parts[1], 10);
                 draftType = "goal";
            }
        }

        const payload = { 
            message: text,
            channel,
            goal_id: effectiveGoalId,
            active_goal_id: effectiveGoalId,
            current_mode: othelloState.currentMode,
            current_view: othelloState.currentView,
            client_message_id: clientMessageId,
            conversation_id: othelloState.activeConversationId,
            draft_id: draftId,
            draft_type: draftType,
            ...extraData
        };
        console.debug("[Othello UI] Sending /api/message payload:", payload);
        
        beginThinking();
        let data;
        let res;
        try {
            console.log(`[sendMessage] Fetching ${API}...`);
            res = await fetch(API, {
                  method: "POST",
                  headers: {"Content-Type": "application/json"},
                  credentials: "include",
                  body: JSON.stringify(payload)
            });

            console.log("[sendMessage] /api/message status", res.status);

            if (!res.ok) {
              updateConnectivity('degraded', `Error ${res.status}`);
              const contentType = res.headers.get("content-type") || "";
              
              if (contentType.includes("application/json")) {
                let errorData = null;
                try {
                  errorData = await res.json();
                } catch (e) {
                  console.warn("[sendMessage] Could not parse JSON error body:", e);
                }
                console.error("[sendMessage] HTTP error:", res.status, errorData);
                const errMsg = (errorData && (errorData.message || errorData.error)) || "Unable to process your message.";
                addMessage("bot", `[Server error ${res.status}]: ${errMsg}`);
              } else {
                let errorText = "";
                try {
                  errorText = await res.text();
                } catch (e) {
                  console.warn("[sendMessage] Could not read error response body:", e);
                }
                const preview = (errorText || "").slice(0, 200);
                console.error("[sendMessage] HTTP error (non-JSON):", res.status, preview);
                addMessage("bot", `[Server error ${res.status}]: Unable to process your message.`);
              }
              return;
            }

            updateConnectivity('online');
            
            const contentType = res.headers.get("content-type") || "";
            if (contentType.includes("application/json")) {
                const clone = res.clone();
                try {
                    data = await res.json();
                    
                    // Route Pill Update (Phase A)
                    // If backend returns a route, update our state so the pill reflects it.
                    if (data && data.selected_route) {
                        othelloState.lastRoute = data.selected_route;
                        // Refresh immediately to show new route
                        updateConnectivity('online');
                    }
                } catch (parseErr) {
                    let textBody = "";
                    try { textBody = await clone.text(); } catch(e) {}
                    console.error("[sendMessage] JSON parse error:", parseErr, "Body:", textBody);
                    addMessage("bot", `[Parse error] Invalid JSON from server.`);
                    return;
                }
            } else {
                console.warn("[sendMessage] Unexpected Content-Type:", contentType);
                let textBody = "";
                try { textBody = await res.text(); } catch(e) {}
                console.error("[sendMessage] Unexpected response type. Body:", textBody);
                addMessage("bot", `[Parse error] Unexpected response type (${contentType}).`);
                return;
            }

        } catch (err) {
             console.error("[sendMessage] exception:", err, err?.stack);
             
             // Detect genuine network failures from fetch()
             const isNetwork = err instanceof TypeError && (
                 err.message === "Failed to fetch" ||
                 err.message.includes("NetworkError") ||
                 err.message.includes("Network request failed")
             );

             if (isNetwork) {
                 addMessage("bot", `[Network error] backend unreachable: ${err.message}`);
                 updateConnectivity('offline');
             } else {
                 addMessage("bot", `[Client error] ${err.message || String(err)}`);
             }
             return;
        } finally {
            endThinking();
        }
        
        // Phase 22.3: Handle UI Actions from backend (Auto-Focus)
        if (data.ui_action_call === "focus_goal" && data.ui_action_payload && data.ui_action_payload.goal_id) {
             const goalId = data.ui_action_payload.goal_id;
             setActiveGoal(goalId);
             if (othelloState.currentView !== "goals") {
                 switchView("goals");
             }
             // showGoalDetail will render loading state and fetch valid data
             showGoalDetail(goalId);
        } else if (data.redirect_to && typeof data.redirect_to === 'string') {
             const goalMatch = data.redirect_to.match(/\/goals\/(\d+)/);
             if (goalMatch && goalMatch[1]) {
                 const goalId = parseInt(goalMatch[1], 10);
                 setActiveGoal(goalId);
                 if (othelloState.currentView !== "goals") {
                     switchView("goals");
                 }
                 showGoalDetail(goalId);
             }
        }

        if (data.conversation_id) {
            othelloState.activeConversationId = data.conversation_id;
        }
        const meta = data && data.meta ? data.meta : null;

        // Phase 22: Capture virtual goal intent for User message
        if (meta && meta.suggestions && Array.isArray(meta.suggestions)) {
           meta.suggestions.forEach(s => {
               if (s.type === 'goal_intent' && s.client_message_id) {
                   addSecondarySuggestion(s.client_message_id, s);
               }
           });
        }

        const isRoutineReady = !!(meta && meta.intent === "routine_ready" && meta.routine_suggestion_id);
        let replyText = data.reply || "[no reply]";
        if (isRoutineReady) {
          replyText = "Confirm this routine?";
        }

        // Compute intent markers
        const intentMarkers = [];
        const hint = othelloState.intentHintsByClientId[clientMessageId] || {};
        
        const hasGoalIntentFromServer = !!(
          data.goal_intent_detected ||
          data.goal_intent_suggestion ||
          (Array.isArray(meta && meta.suggestions) && meta.suggestions.some(s => (s.type || "").toLowerCase() === "goal_intent"))
        );
        const hasRoutineIntentFromServer = !!(
          (meta && typeof meta.intent === "string" && meta.intent.toLowerCase().startsWith("routine")) ||
          (meta && meta.routine_suggestion_id)
        );

        const hasGoalIntent = hasGoalIntentFromServer || hint.goal;
        const hasRoutineIntent = hasRoutineIntentFromServer || hint.routine;

        if (hasGoalIntent) intentMarkers.push("🎯 Goal");
        if (hasRoutineIntent) intentMarkers.push("🔁 Routine");

        const botEntry = addMessage("bot", replyText, { sourceClientMessageId: clientMessageId, intentMarkers });
        
        // Clear hint to prevent reuse
        if (othelloState.intentHintsByClientId[clientMessageId]) {
          delete othelloState.intentHintsByClientId[clientMessageId];
        }

        try {
          await applyRoutineMeta(meta, botEntry, clientMessageId);
        } catch (err) {
          console.warn("[Othello UI] routine meta render failed:", err);
        }
        
        // Update agent status display
        if (data.agent_status) {
          othelloState.currentAgentStatus = data.agent_status;
          if (data.agent_status.planner_active) {
            statusEl.textContent = "Online · Planner";
          } else {
            statusEl.textContent = "Online · Chat";
          }
        } else {
          statusEl.textContent = "Online";
        }

        // Handle meta from backend for goal list / selection UX
        const metaIntent = data.meta && data.meta.intent ? data.meta.intent : null;
        if (metaIntent === "select_goal_success" && typeof data.active_goal_id === "number") {
          setActiveGoal(data.active_goal_id);
        } else if (metaIntent === "list_goals" && Array.isArray(data.goals)) {
          othelloState.goals = data.goals;
          othelloState.goals.forEach((g) => {
            if (g && typeof g.id === "number" && !(g.id in othelloState.goalUpdateCounts)) {
              othelloState.goalUpdateCounts[g.id] = 0;
            }
          });
        } else {
          bumpActiveGoalUpdates();
        }

        if (metaIntent === "pending_goal_edit_set") {
          const pendingMode = data.meta && data.meta.mode ? data.meta.mode : "update";
          if (othelloState.activeGoalId !== null) {
            othelloState.pendingGoalEdit = {
              mode: pendingMode,
              goal_id: othelloState.activeGoalId
            };
          }
        } else if (metaIntent === "pending_goal_edit_applied") {
          const pendingGoalId = othelloState.pendingGoalEdit
            ? othelloState.pendingGoalEdit.goal_id
            : null;
          othelloState.pendingGoalEdit = null;
          if (othelloState.currentDetailGoalId != null) {
            if (pendingGoalId == null || othelloState.currentDetailGoalId === pendingGoalId) {
              refreshGoalDetail();
            }
          }
          if (statusEl) {
            const prevStatus = statusEl.textContent;
            const ok = !!(data.meta && data.meta.ok);
            const nextStatus = ok ? "Goal updated." : "Goal update failed.";
            statusEl.textContent = nextStatus;
            setTimeout(() => {
              if (statusEl.textContent === nextStatus) {
                statusEl.textContent = prevStatus;
              }
            }, 1500);
          }
        }

        if (metaIntent === "plan_steps_added") {
          const responseGoalId = typeof data.goal_id === "number" ? data.goal_id : othelloState.activeGoalId;
          if (othelloState.currentDetailGoalId != null) {
            if (responseGoalId == null || othelloState.currentDetailGoalId === responseGoalId) {
              refreshGoalDetail();
            }
          }
          refreshGoals();
        }

        if (data.insights_meta) {
          applyInsightsMeta(data.insights_meta);
        } else {
          await refreshInsightsCounts();
        }

        if (data.meta) {
          applySuggestionMeta(data.meta);
        }

        if (data.draft_context) {
            othelloState.activeDraft = data.draft_context;
            localStorage.setItem("othello_active_draft", JSON.stringify(othelloState.activeDraft));
        }

        if (data.draft_payload) {
            othelloState.activeDraftPayload = data.draft_payload;
            localStorage.setItem("othello_active_draft_payload", JSON.stringify(data.draft_payload));
            updateFocusRibbon();
        } else if (data.draft_context) {
            updateFocusRibbon();
        }
        
        if (data.saved_goal) {
            othelloState.activeDraft = null;
            othelloState.activeDraftPayload = null;
            localStorage.removeItem("othello_active_draft");
            localStorage.removeItem("othello_active_draft_payload");
            
            if (data.saved_goal.goal_id) {
                othelloState.activeGoalId = data.saved_goal.goal_id;
                showToast(`Goal created: ${data.saved_goal.title || "New Goal"}`);
            }
            
            updateFocusRibbon();
        }

        if (data.dismissed_draft_id) {
            if (othelloState.activeDraft && othelloState.activeDraft.draft_id === data.dismissed_draft_id) {
                othelloState.activeDraft = null;
                othelloState.activeDraftPayload = null;
                localStorage.removeItem("othello_active_draft");
                localStorage.removeItem("othello_active_draft_payload");
                updateFocusRibbon();
            }
        }

        // Always refresh from backend to stay in sync
        await refreshGoals();

        if (data.meta && data.meta.goal_updated) {
           refreshGoalDetail();
        }
      } catch (err) {
        console.error("[sendMessage] outer exception:", err);
        const isNetwork = err instanceof TypeError && (
             err.message === "Failed to fetch" ||
             err.message.includes("NetworkError") ||
             err.message.includes("Network request failed")
        );
        if (isNetwork) {
             addMessage("bot", `[Network error] backend unreachable: ${err.message}`);
             updateConnectivity('offline');
        } else {
             addMessage("bot", `[Client error] ${err.message || String(err)}`);
        }
      } finally {
        endSendUI(sendUiState);
      }
    }

    // --- COMPOSER & VOICE LOGIC ---

    // --- DIRECT COMPOSER CLICK HANDLING (FIXED) ---
    function handleComposerAction(e) {
      if (e) {
        e.preventDefault();
        e.stopPropagation();
      }

      const btn = document.getElementById("composer-action-btn");
      const inputEl = document.getElementById("user-input");

      const hasText = ((inputEl && inputEl.value) ? inputEl.value.trim().length : 0) > 0;
      // Robust state check
      const recording = (typeof isRecording !== 'undefined' && isRecording) || 
                        (typeof voice !== 'undefined' && voice.active) || 
                        (btn && (btn.classList.contains("record-mode") || btn.dataset.action === "stop"));

      console.debug("[composer] action", { hasText, recording, target: (e.target && e.target.tagName) });

      if (recording) {
        if (typeof stopVoiceInput === 'function') stopVoiceInput();
      } else if (hasText) {
        if (typeof sendMessage === 'function') sendMessage();
      } else {
        if (typeof startVoiceInput === 'function') startVoiceInput();
      }
      
      if (typeof updateComposerUI === 'function') setTimeout(updateComposerUI, 50);
    }

    function bindComposerActionButton(reason="boot") {
      const btn = document.getElementById("composer-action-btn");
      if (!btn) return false; 
      if (btn.dataset.bound === "1") return true;

      btn.dataset.bound = "1";
      // Use capture for priority
      // changed to click-only for toggle behavior (no push-to-talk)
      btn.addEventListener("click", handleComposerAction, true);

      console.info("[composer] bound composer-action-btn", reason);
      return true;
    }

    // Observer to re-bind if the input bar is replaced
    setTimeout(() => {
        const inputBarRef = document.getElementById("input-bar") || document.querySelector(".input-bar");
        if (inputBarRef && typeof MutationObserver !== 'undefined') {
            const composerObserver = new MutationObserver((mutations) => {
                bindComposerActionButton("mutation");
            });
            composerObserver.observe(inputBarRef, { childList: true, subtree: true });
        }
    }, 1000);

    function updateComposerUI() {
      // Robust element resolution (Fix 2)
      const input = document.getElementById("user-input");
      const composerActionBtn = document.getElementById("composer-action-btn");
      const inputBarContainer = document.querySelector(".input-bar-container") || document.getElementById("input-bar");

      if (!input || !composerActionBtn) return;
      const val = (input.value || "").trim();
      
      // Determine mode (Fix 1: consistent state)
      // Check multiple sources for recording state
      const isVoiceActive = (typeof isRecording !== 'undefined' && isRecording) || 
                            (typeof voice !== 'undefined' && voice.active);

      let currentMode = "idle";
      if (isVoiceActive) {
        currentMode = "recording";
      } else if (val.length > 0) {
        currentMode = "typing";
      } else {
        currentMode = "idle";
      }
      
      // Update global for legacy support
      if (typeof composerMode !== 'undefined') composerMode = currentMode;

      // Update Wrapper
      if (inputBarContainer) {
          if (currentMode === "recording") inputBarContainer.classList.add("is-recording");
          else inputBarContainer.classList.remove("is-recording");
      }
      if (currentMode === "recording") input.classList.add("composer-ghost");
      else input.classList.remove("composer-ghost");

      // Update Button
      composerActionBtn.className = "composer-action-btn"; // reset classes
      
      if (currentMode === "idle") {
        composerActionBtn.setAttribute("data-action", "mic");
        composerActionBtn.setAttribute("aria-label", "Start voice input");
        composerActionBtn.innerHTML = `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="23"></line><line x1="8" y1="23" x2="16" y2="23"></line></svg>`;
      } else if (currentMode === "recording") {
        composerActionBtn.classList.add("record-mode");
        composerActionBtn.setAttribute("data-action", "stop");
        composerActionBtn.setAttribute("aria-label", "Stop recording");
        composerActionBtn.innerHTML = `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="6" y="6" width="12" height="12" rx="2" ry="2"></rect></svg>`;
      } else if (currentMode === "typing") {
        composerActionBtn.classList.add("send-mode");
        composerActionBtn.setAttribute("data-action", "send");
        composerActionBtn.setAttribute("aria-label", "Send message");
        composerActionBtn.innerHTML = `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>`;
      }
    }

    // Delegated Input and Keydown Handling
    document.addEventListener("input", (e) => {
        if (e.target && e.target.id === "user-input") {
             updateComposerUI();
        }
    });

    document.addEventListener("keydown", (e) => {
        if (e.target && e.target.id === "user-input" && e.key === "Enter") {
             if (e.ctrlKey || e.metaKey) {
                 e.preventDefault();
                 sendMessage();
             }
        }
    });
    
    // [Phase 4] Previous delegated click listener removed.
    // Click handling is now managed by bindComposerActionButton() + handleComposerAction().

    // Voice & Silence Logic
    function startVoiceInput() {
        console.debug("[voice] start requested");
        
        // Robust check for SpeechRecognition
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            console.error("[voice] SpeechRecognition API missing");
            addMessage("bot", "[Client error] Voice input not supported in this browser.");
            alert("Speech recognition not supported in this browser.");
            return;
        }

        // Lazy Initialize
        if (!voice.recognition) {
             console.log("[voice] initializing new SpeechRecognition instance");
             try {
                 const rec = new SpeechRecognition();
                 rec.continuous = true;
                 rec.interimResults = true;
                 rec.lang = "en-GB";
                 
                 rec.onstart = () => {
                    console.debug("[voice] onstart");
                    voice.active = true;
                    isRecording = true;
                    sttFullTranscript = "";
                    sttLastInterim = "";
                    const inputEl = document.getElementById("user-input");
                    if (inputEl) inputEl.value = ""; 
                    updateComposerUI();
                    
                    // Start silence monitoring only when voice actually starts
                    startSilenceDetection();
                 };
                 
                 rec.onend = () => {
                    console.debug("[voice] onend");
                    voice.active = false;
                    isRecording = false;
                    updateComposerUI();
                    stopSilenceDetection();
                 };
                 
                 rec.onerror = (event) => {
                    console.warn("[voice] onerror", event.error);
                    if (event.error === "not-allowed" || event.error === "service-not-allowed") {
                        addMessage("bot", "[Client error] Microphone access blocked.");
                        alert("Microphone access denied. Please allow microphone access.");
                    }
                    voice.active = false;
                    isRecording = false;
                    updateComposerUI();
                 };
                 
                 rec.onresult = (event) => {
                    let interimBuffer = "";
                    let newFinal = "";
                    for (let i = event.resultIndex; i < event.results.length; i++) {
                      const result = event.results[i];
                      const phrase = (result[0] && result[0].transcript ? result[0].transcript : "").trim();
                      if (!phrase) continue;
                      if (result.isFinal) {
                         newFinal += (newFinal ? " " : "") + phrase;
                      } else {
                         interimBuffer += (interimBuffer ? " " : "") + phrase;
                      }
                    }
                    if (newFinal) {
                         const needsSpace = sttFullTranscript.length > 0 && !sttFullTranscript.match(/\s$/);
                         sttFullTranscript += (needsSpace ? " " : "") + newFinal;
                    }
                    sttLastInterim = interimBuffer;
                    let display = sttFullTranscript;
                    if (sttLastInterim) {
                         const needsSpace = display.length > 0 && !display.match(/\s$/);
                         display += (needsSpace ? " " : "") + sttLastInterim;
                    }
                    
                    const inputEl = document.getElementById("user-input");
                    if (inputEl) {
                        inputEl.value = display;
                        inputEl.scrollTop = inputEl.scrollHeight;
                    }
                    updateComposerUI();
                 };
                 
                 voice.recognition = rec;

             } catch(e) {
                 console.error("[voice] Failed to create SpeechRecognition", e);
                 addMessage("bot", `[Client error] Voice input failed to initialize: ${e.message}`);
                 return;
             }
        }
        
        console.log("[voice] attempting start");
        try {
            voice.recognition.start();
        } catch(e) { 
            console.warn("[voice] start error:", e);
            if (e.name === "InvalidStateError") {
                 // Already active? ignore
            } else {
                addMessage("bot", `[Client error] Could not start voice input: ${e.message}`);
            }
        }
    }

    function stopVoiceInput() {
        if (voice.recognition) {
            try { voice.recognition.stop(); } catch(e) {}
        }
        stopSilenceDetection();
    }
    
    async function startSilenceDetection() {
        try {
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) return;
            stopSilenceDetection();
            
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            microphoneStream = stream;
            
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            audioContext = new AudioContext();
            analyser = audioContext.createAnalyser();
            analyser.fftSize = 256;
            
            const source = audioContext.createMediaStreamSource(stream);
            source.connect(analyser);
            
            const bufferLength = analyser.frequencyBinCount;
            const dataArray = new Uint8Array(bufferLength);
            
            silenceStart = Date.now();
            lastParaInsertAt = Date.now(); 
            
            silenceInterval = setInterval(() => {
                // Check local state or voice active
                if (!isRecording && !voice.active) {
                    stopSilenceDetection();
                    return;
                }
                if (analyser) {
                    analyser.getByteTimeDomainData(dataArray);
                    
                    let sum = 0;
                    for(let i = 0; i < bufferLength; i++) {
                        const x = (dataArray[i] - 128) / 128.0;
                        sum += x * x;
                    }
                    const rms = Math.sqrt(sum / bufferLength);
                    
                    if (rms < SILENCE_THRESHOLD) {
                        const now = Date.now();
                        if ((now - silenceStart) > SILENCE_DELAY_MS) {
                             if ((now - lastParaInsertAt) > PARA_COOLDOWN_MS) {
                                  insertParagraphBreak();
                                  lastParaInsertAt = now;
                             }
                        }
                    } else {
                        silenceStart = Date.now();
                    }
                }
            }, 100);
            
        } catch (err) {
            console.warn("[Composer] Silence detection setup failed", err);
        }
    }
    
    function stopSilenceDetection() {
        if (silenceInterval) { clearInterval(silenceInterval); silenceInterval = null; }
        if (microphoneStream) {
             microphoneStream.getTracks().forEach(track => track.stop());
             microphoneStream = null;
        }
        if (audioContext) {
            try { audioContext.close(); } catch(e){}
            audioContext = null;
        }
    }
    
    function insertParagraphBreak() {
        if (!input) return;
        const oldVal = input.value;
        if (!oldVal.trim().length) return; 
        
        let suffix = "\n\n";
        if (oldVal.endsWith("\n\n")) return;
        if (oldVal.endsWith("\n")) suffix = "\n";
        
        const newVal = oldVal + suffix;
        input.value = newVal;
        input.scrollTop = input.scrollHeight;
        
        if (isRecording) {
             sttFullTranscript = newVal;
        }

        // Flash
        input.classList.remove("para-flash");
        void input.offsetWidth; // trigger reflow
        input.classList.add("para-flash");
        setTimeout(() => input.classList.remove("para-flash"), 600);
        console.log("[Composer] Paragraph break inserted via silence");
    }

    // Note: Click handling is now managed by the direct binder setup above.
    // Delegated listener removed to avoid conflicts.

    // Initial render
    updateComposerUI();
    bindComposerActionButton("boot");

    // ===== GOALS FUNCTIONS =====
    function extractListItems(text) {
      if (!text) return [];
      const lines = text.split(/\r?\n/);
      return lines
        .map(l => l.trim())
        .filter(l => /^[-*•]\s+/.test(l) || /^\d+\.\s+/.test(l))
        .map(l => l.replace(/^[-*•]\s+/, "").replace(/^\d+\.\s+/, ""));
    }

    function hasStructuredList(text) {
      if (!text) return false;
      if (/<ul|<ol|<li/i.test(text)) return true;
      return extractListItems(text).length > 0;
    }

    function isPlanLikeText(text) {
      if (!text) return false;
      if (/^\s*#{2,6}\s+\S+/m.test(text)) return true;
      if (/\bplan:\b/i.test(text) || /\bsteps?:\b/i.test(text)) return true;
      if (/^\s*\d+[.)]\s+\S+/m.test(text)) return true;
      if (/^\s*[-*•]\s+\S+/m.test(text)) return true;
      return hasStructuredList(text);
    }

    function parseIntentItems(text) {
      if (!text) return [];
      const lines = text.split(/\r?\n/);
      const numbered = [];
      lines.forEach((line) => {
        const match = line.trim().match(/^(\d+)[.)]\s+(.+)$/);
        if (match) {
          numbered.push({ index: parseInt(match[1], 10), text: match[2].trim() });
        }
      });
      if (numbered.length > 0) {
        return numbered;
      }
      const fallback = text.trim();
      return fallback ? [{ index: 1, text: fallback }] : [];
    }

    async function confirmGoalPlanSuggestion(suggestionId) {
      if (!suggestionId) return null;
      const payload = await v1Request(
        `/v1/suggestions/${suggestionId}/accept`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({ reason: "confirm" })
        },
        "Confirm goal plan"
      );
      const results = payload && payload.data && Array.isArray(payload.data.results)
        ? payload.data.results
        : [];
      const result = results[0] || null;
      if (result && result.ok === false) {
        const err = new Error(result.error || "Failed to confirm plan.");
        err.requestId = payload && payload.request_id ? payload.request_id : null;
        throw err;
      }
      return result;
    }

    async function postPlanFromText(planText) {
      const goalId = othelloState.activeGoalId;
      if (goalId == null) throw new Error("No focused goal.");
      const res = await fetch(API, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: "__plan_from_text_append__",
          ui_action: "plan_from_text_append",
          plan_text: planText,
          goal_id: goalId,
          active_goal_id: goalId,
          current_mode: othelloState.currentMode,
          current_view: othelloState.currentView,
        }),
      });
      if (res.status === 401 || res.status === 403) {
        await handleUnauthorized("plan-from-text");
        throw new Error("Authentication required.");
      }
      if (!res.ok) {
        let errMsg = "Unable to add steps to the plan.";
        const contentType = res.headers.get("content-type") || "";
        if (contentType.includes("application/json")) {
          const data = await res.json();
          errMsg = (data && (data.message || data.error)) || errMsg;
        } else {
          const text = await res.text();
          if (text) errMsg = text.slice(0, 200);
        }
        throw new Error(errMsg);
      }
      const data = await res.json();
      const pendingId = data && data.meta ? data.meta.pending_suggestion_id : null;
      if (pendingId) {
        await confirmGoalPlanSuggestion(pendingId);
        data.meta = data.meta || {};
        data.meta.intent = "plan_steps_added";
        data.meta.confirmed_suggestion_id = pendingId;
      }
      return data;
    }

    async function postPlanFromIntent(goalId, intentIndex, intentText) {
      if (goalId == null) throw new Error("No focused goal.");
      console.log("[Othello UI] Sending ui_action=plan_from_intent payload");
      const res = await fetch(API, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: "__plan_from_intent__",
          ui_action: "plan_from_intent",
          intent_index: intentIndex,
          intent_text: intentText,
          goal_id: goalId,
          active_goal_id: goalId,
          current_mode: othelloState.currentMode,
          current_view: othelloState.currentView,
        }),
      });
      if (res.status === 401 || res.status === 403) {
        await handleUnauthorized("plan-from-intent");
        throw new Error("Authentication required.");
      }
      if (!res.ok) {
        let errMsg = "Unable to build plan from intent.";
        const contentType = res.headers.get("content-type") || "";
        if (contentType.includes("application/json")) {
          const data = await res.json();
          errMsg = (data && (data.message || data.error)) || errMsg;
        } else {
          const text = await res.text();
          if (text) errMsg = text.slice(0, 200);
        }
        throw new Error(errMsg);
      }
      const data = await res.json();
      const pendingId = data && data.meta ? data.meta.pending_suggestion_id : null;
      if (pendingId) {
        await confirmGoalPlanSuggestion(pendingId);
        data.meta = data.meta || {};
        data.meta.intent = "plan_steps_added";
        data.meta.confirmed_suggestion_id = pendingId;
        if (typeof data.reply === "string") {
          const cleaned = data.reply.replace(/\n?\s*Confirm to apply these steps\.?\s*$/i, "").trim();
          data.reply = cleaned ? `${cleaned}\n\nSaved to Current Plan.` : "Saved to Current Plan.";
        }
      }
      return data;
    }

    function formatStepStatus(status) {
      const raw = (status || "pending").toString().replace(/_/g, " ");
      return raw ? raw.charAt(0).toUpperCase() + raw.slice(1) : "Pending";
    }

    async function postPlanStepStatus(goalId, stepId, status) {
      const res = await fetch(`/api/goals/${goalId}/steps/${stepId}/status`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status }),
      });
      if (res.status === 401 || res.status === 403) {
        await handleUnauthorized("plan-step-status");
        throw new Error("Authentication required.");
      }
      if (!res.ok) {
        let errMsg = "Unable to update step status.";
        const contentType = res.headers.get("content-type") || "";
        if (contentType.includes("application/json")) {
          const data = await res.json();
          errMsg = (data && (data.message || data.error)) || errMsg;
        } else {
          const text = await res.text();
          if (text) errMsg = text.slice(0, 200);
        }
        throw new Error(errMsg);
      }
      return res.json();
    }

    async function postPlanStepDetail(goalId, stepId, detail, stepIndex = null) {
      const payload = { detail };
      if (Number.isFinite(stepIndex)) {
        payload.step_index = stepIndex;
      }
      const res = await fetch(`/api/goals/${goalId}/steps/${stepId}/detail`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (res.status === 401 || res.status === 403) {
        await handleUnauthorized("plan-step-detail");
        throw new Error("Authentication required.");
      }
      if (!res.ok) {
        let errMsg = "Unable to update step detail.";
        const contentType = res.headers.get("content-type") || "";
        if (contentType.includes("application/json")) {
          const data = await res.json();
          errMsg = (data && (data.message || data.error)) || errMsg;
        } else {
          const text = await res.text();
          if (text) errMsg = text.slice(0, 200);
        }
        throw new Error(errMsg);
      }
      return res.json();
    }

    function extractGoalTitleFromDraft(rawText) {
      if (!rawText) return "";
      const match = rawText.match(/^(?:ok\s*-\s*)?goal:\s*(.+)$/im);
      if (match) return match[1].trim();
      return "";
    }

    async function draftPlanFromSteps(items, rawText, sourceClientMessageId) {
      const steps = (items || [])
        .map(item => String(item || "").trim())
        .filter(Boolean);
      if (!steps.length) {
        throw new Error("No steps found.");
      }
      const messageIds = [];
      for (const step of steps) {
        const payload = await v1Request(
          V1_MESSAGES_API,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify({
              transcript: step,
              source: "text",
              channel: "planner",
            }),
          },
          "Create plan step"
        );
        const message = payload && payload.data ? payload.data.message : null;
        const msgId = message && typeof message.id === "number" ? message.id : null;
        if (msgId) {
          messageIds.push(msgId);
        }
      }
      if (!messageIds.length) {
        throw new Error("No step messages created.");
      }
      const goalTitle = extractGoalTitleFromDraft(rawText);
      const draftPayload = {
        message_ids: messageIds,
        channel: "companion",
        steps,
      };
      if (goalTitle) {
        draftPayload.title = goalTitle;
      }
      if (sourceClientMessageId) {
        draftPayload.source_client_message_id = sourceClientMessageId;
      }
      const draft = await v1Request(
        "/v1/plan/draft",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify(draftPayload),
        },
        "Draft plan"
      );
      const suggestionIds = Array.isArray(draft?.data?.suggestion_ids)
        ? draft.data.suggestion_ids
        : [];
      console.debug("[Othello UI] plan draft created", {
        suggestionCount: suggestionIds.length,
        suggestionIds,
      });
      return { suggestionIds };
    }

    async function postCommitment(action, items, rawText, sourceClientMessageId) {
      const safeItems = items && items.length ? items : [rawText];
      let title = (safeItems[0] || "New commitment").trim();
      let message;

      if (action === "goal") {
        // Construct full description from all items (clean markdown)
        const description = safeItems.map(i => i.replace(/\*\*/g, "")).join("\n");
        
        // Improve title: try to get user intent from source message
        if (sourceClientMessageId) {
            const userMsgRow = document.querySelector(`.msg-row[data-client-message-id="${sourceClientMessageId}"]`);
            if (userMsgRow) {
                const bubble = userMsgRow.querySelector(".bubble");
                if (bubble) {
                    const clone = bubble.cloneNode(true);
                    const meta = clone.querySelector(".meta");
                    if (meta) meta.remove();
                    const userText = clone.textContent.trim();
                    if (userText) {
                        const firstSentence = userText.split(/[.!?]/)[0];
                        title = firstSentence.length > 60 ? firstSentence.substring(0, 60) + "..." : firstSentence;
                    }
                }
            }
        }
        // Fallback title cleanup
        if (title.startsWith("**")) title = title.replace(/\*\*/g, "");
        if (title.startsWith("Deadline:")) title = "Long-term Goal";

        const res = await fetch(GOALS_API, {
          method: "POST",
          credentials: "include",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ title, description })
        });
        if (res.status === 401 || res.status === 403) {
          await handleUnauthorized("goals-create");
          throw new Error("Authentication required.");
        }
        if (!res.ok) {
          let errMsg = "Unable to save goal.";
          try {
            const errJson = await res.json();
            errMsg = errJson.message || errMsg;
          } catch (err) {
            try {
              const errText = await res.text();
              if (errText) errMsg = errText;
            } catch (e) {}
          }
          throw new Error(errMsg);
        }
        return res.json();
      } else if (action === "plan") {
        return draftPlanFromSteps(safeItems, rawText, sourceClientMessageId);
      } else if (action === "idea") {
        message = `Save this as an idea/inbox entry:\n${rawText}\nItems:\n- ${safeItems.join("\n- ")}`;
      } else {
        return;
      }

      const res = await fetch(API, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
      });
      if (!res.ok) {
        const txt = await res.text();
        throw new Error(txt || "Commitment failed");
      }
      return res.json();
    }

    function createCommitmentBar(items, rawText, sourceClientMessageId = "") {
      const bar = document.createElement("div");
      bar.className = "commitment-bar";

      const status = document.createElement("span");
      status.className = "commitment-status";

      const makeBtn = (label, action) => {
        const btn = document.createElement("button");
        btn.className = "commitment-btn";
        btn.textContent = label;
        btn.addEventListener("click", async () => {
          status.textContent = "Sending…";
          btn.disabled = true;
          try {
            const result = await postCommitment(action, items, rawText, sourceClientMessageId);
            if (action === "plan") {
              const count = Array.isArray(result?.suggestionIds) ? result.suggestionIds.length : 0;
              const label = `Drafted ${count} plan item${count === 1 ? "" : "s"}`;
              status.textContent = count ? label : "Drafted plan items";
              showToast(`${label} \u2014 review in Today Planner \u2192 Pending Suggestions.`);
              if (othelloState.currentView === "today-planner") {
                await loadTodayPlanner();
              } else {
                setMode("today");
                switchView("today-planner");
              }
            } else {
              status.textContent = "Saved";
              if (action === "goal") {
                refreshGoals();
              }
            }
          } catch (err) {
            if (err && (err.status === 401 || err.status === 403)) {
              await handleUnauthorized("plan-draft-cta");
              return;
            }
            status.textContent = err && err.message ? err.message : "Failed";
          } finally {
            setTimeout(() => { status.textContent = ""; }, 1500);
            btn.disabled = false;
          }
        });
        return btn;
      };

      bar.appendChild(makeBtn("Save as long-term goal", "goal"));
      bar.appendChild(makeBtn("Add tasks to Today Plan", "plan"));
      bar.appendChild(makeBtn("Save as idea", "idea"));
      bar.appendChild(status);

      return bar;
    }

    function createPlanActionBar(planText) {
      const bar = document.createElement("div");
      bar.className = "commitment-bar";

      const status = document.createElement("span");
      status.className = "commitment-status";

      const btn = document.createElement("button");
      btn.className = "commitment-btn";
      btn.textContent = "Add to Current Plan";
      btn.addEventListener("click", async () => {
        status.textContent = "Sending.";
        btn.disabled = true;
        try {
          const data = await postPlanFromText(planText);
          status.textContent = "Saved";
          if (data && data.meta && data.meta.intent === "plan_steps_added") {
            if (othelloState.currentDetailGoalId === othelloState.activeGoalId) {
              refreshGoalDetail();
            }
            refreshGoals();
          }
        } catch (err) {
          status.textContent = err && err.message ? err.message : "Failed";
        } finally {
          setTimeout(() => { status.textContent = ""; }, 1500);
          btn.disabled = false;
        }
      });

      bar.appendChild(btn);
      bar.appendChild(status);
      return bar;
    }

    async function refreshGoals() {
      if (!isAuthed) return;
      try {
        const res = await fetch(GOALS_API, { credentials: "include" });
        if (res.status === 401 || res.status === 403) {
          await handleUnauthorized('goals');
          return;
        }
        if (!res.ok) throw new Error("Failed to fetch goals");
        const data = await res.json();
        const goals = data.goals || [];

        othelloState.goals = goals;

        // Ensure counters exist for existing goals
        goals.forEach((g) => {
          if (g && typeof g.id === "number" && !(g.id in othelloState.goalUpdateCounts)) {
            othelloState.goalUpdateCounts[g.id] = 0;
          }
        });

        updateFocusRibbon();
        
        // If currently viewing goals, re-render
        if (othelloState.currentView === "goals") {
          renderGoalsList();
        }
      } catch (err) {
        console.warn("[Othello UI] Failed to refresh goals:", err);
      }
    }

    function renderGoalsList() {
      goalsList.innerHTML = "";

      if (!othelloState.goals || othelloState.goals.length === 0) {
        goalsList.innerHTML = `
          <div class="empty-state">
            <div class="empty-state__icon">🎯</div>
            <div class="empty-state__text">
              No goals yet. Start a conversation in the Chat tab to set your first goal.
            </div>
          </div>
        `;
        return;
      }

      othelloState.goals.forEach(goal => {
        const card = document.createElement("div");
        card.className = "goal-card";
        if (goal.is_draft) {
             card.classList.add("goal-card--draft");
        }
        
        const isActive = goal.id === othelloState.activeGoalId;
        const updateCount = othelloState.goalUpdateCounts[goal.id] || 0;

        let badge = "";
        let actions = "";
        if (goal.is_draft) {
             badge = '<div class="goal-card__badge" style="background:var(--accent-color);color:#000;">Draft</div>';
             actions = `<div class="goal-card__dismiss" title="Dismiss Draft" style="cursor:pointer;font-weight:bold;margin-left:8px;padding:2px 6px;">×</div>`;
        } else if (isActive) {
             badge = '<div class="goal-card__badge">Active</div>';
        }

        card.innerHTML = `
          <div class="goal-card__header">
            <div>
              <div class="goal-card__id">${goal.is_draft ? 'Draft' : 'Goal #' + goal.id}</div>
              <div class="goal-card__title">${formatMessageText(goal.text || "Untitled")}</div>
            </div>
            <div style="display:flex;align-items:center;">
                ${badge}
                ${actions}
            </div>
          </div>
          ${goal.deadline ? `<div class="goal-card__meta">Target: ${formatMessageText(goal.deadline)}</div>` : ''}
          ${goal.is_draft ? `<div class="goal-card__meta">Seed Steps: ${(goal.checklist||[]).length}</div>` : ''}
          ${updateCount > 0 ? `<div class="goal-card__meta">${updateCount} update${updateCount !== 1 ? 's' : ''} this session</div>` : ''}
        `;

        if (goal.is_draft) {
             const dismissBtn = card.querySelector(".goal-card__dismiss");
             if (dismissBtn) {
                 dismissBtn.addEventListener("click", async (e) => {
                     e.stopPropagation();
                     if (!confirm("Dismiss this draft?")) return;
                     if (!goal.real_draft_id) return;
                     try {
                         const res = await fetch(`/v1/suggestions/${goal.real_draft_id}/dismiss`, {
                             method: "POST",
                             headers: { "Content-Type": "application/json" },
                             credentials: "include",
                             body: JSON.stringify({ reason: "user_dismissed_gui" })
                         });
                         if (res.ok) {
                             await refreshGoals();
                         }
                     } catch(err) {
                         console.error("Dismiss failed", err);
                     }
                 });
             }
        }


        card.addEventListener("click", () => {
          if (goal.is_draft) {
              // Open draft ribbon context directly? 
              // Better: Show detail panel with draft info.
              showGoalDetail(goal.id); 
          } else {
              showGoalDetail(goal.id);
          }
        });

        goalsList.appendChild(card);
      });
    }

    function normalizeGoalActivity(goal) {
      if (!goal) return [];
      const conversation = Array.isArray(goal.conversation) ? goal.conversation : null;
      if (conversation && conversation.length) return conversation;
      const events = Array.isArray(goal.events)
        ? goal.events
        : (Array.isArray(goal.goal_events) ? goal.goal_events : []);
      if (!events || !events.length) return [];
      return events.map((entry) => {
        if (!entry || typeof entry !== "object") return null;
        const payload = entry.payload && typeof entry.payload === "object" ? entry.payload : {};
        const role = entry.role || payload.role || entry.event_type || "system";
        const content = entry.content || entry.message || payload.content || payload.message || "";
        const timestamp = entry.timestamp || entry.occurred_at || payload.timestamp || "";
        return { role, content, timestamp };
      }).filter((entry) => entry && entry.content);
    }

    function escapeHtml(value) {
      return String(value || "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
    }

    function renderGoalDetail(goal) {
      if (!goal) return;
      detailGoalId.textContent = `Goal #${goal.id}`;
      detailGoalTitle.innerHTML = formatMessageText(goal.text || "Untitled Goal");

      // Build detail content
      let contentHtml = "";

      // Draft (New)
      if (goal.draft_text) {
        contentHtml += `
          <div class="detail-section">
            <div class="detail-section__title">Draft</div>
            <div class="detail-section__body" style="white-space: pre-wrap;">${formatMessageText(goal.draft_text)}</div>
          </div>
        `;
      }

      // Seed Steps (Checklist)
      if (goal.checklist && Array.isArray(goal.checklist) && goal.checklist.length > 0) {
        const stepsHtml = goal.checklist.map((step, idx) => {
            const stepText = typeof step === 'string' ? step : (step.text || JSON.stringify(step));
            return `<div class="intent-item"><div class="intent-item__text">${idx + 1}. ${formatMessageText(stepText)}</div></div>`;
        }).join("");
        
        contentHtml += `
          <div class="detail-section">
            <div class="detail-section__title">Seed Steps</div>
            <div class="intent-list">
              ${stepsHtml}
            </div>
          </div>
        `;
      }

      // Description / Intent
      const intentBody = (goal.description || goal.intent || goal.body || "").trim();
      const intentText = intentBody || goal.text || "No description provided.";
      const intentItems = parseIntentItems(intentBody || intentText);
      const goalIdNum = normalizeGoalId(goal.id);
      const activeIdNum = normalizeGoalId(othelloState.activeGoalId);
      const isFocusedGoal = goalIdNum != null && activeIdNum != null && goalIdNum === activeIdNum;
      if (BOOT_DEBUG) {
        console.log("[Goal Detail] intent buttons", {
          activeGoalId: othelloState.activeGoalId,
          activeGoalIdType: typeof othelloState.activeGoalId,
          goalId: goal.id,
          goalIdType: typeof goal.id,
          goalIdNum,
          activeIdNum,
          isFocusedGoal,
          intentCount: intentItems.length,
        });
      }
      if (intentItems.length > 0) {
        const itemsHtml = intentItems.map((item, idx) => {
          const itemIndex = Number.isFinite(item.index) ? item.index : (idx + 1);
          const itemText = item.text || "";
          const safeText = formatMessageText(itemText);
          const planBtn = `
            <button class="commitment-btn intent-plan-btn" data-intent-index="${itemIndex}" data-intent-text="${encodeURIComponent(itemText)}" data-goal-id="${goalIdNum || ""}">
              Build plan
            </button>
          `;
          return `
            <div class="intent-item">
              <div class="intent-item__text">${itemIndex}. ${safeText}</div>
              <div class="intent-item__actions">${planBtn}</div>
            </div>
          `;
        }).join("");
        contentHtml += `
          <div class="detail-section">
            <div class="detail-section__title">Intent</div>
            <div class="intent-list">
              ${itemsHtml}
            </div>
          </div>
        `;
      } else {
        contentHtml += `
          <div class="detail-section">
            <div class="detail-section__title">Intent</div>
            <div class="detail-section__body">${formatMessageText(intentText)}</div>
          </div>
        `;
      }

      // Phase 18: Clarify Intent Button
      contentHtml += `
          <div class="detail-actions" style="padding: 0 16px 16px 16px;">
            <button class="action-btn clarify-intent-btn" data-goal-id="${goal.id}" style="font-size: 0.9em; padding: 6px 12px; border: 1px solid var(--border-color); background: var(--bg-secondary); border-radius: 4px; cursor: pointer; display: flex; align-items: center; gap: 6px;">
               <span class="codicon codicon-question"></span> Clarify Intent
            </button>
          </div>
      `;

      // Deadline
      if (goal.deadline) {
        contentHtml += `
          <div class="detail-section">
            <div class="detail-section__title">Deadline</div>
            <div class="detail-section__body">${goal.deadline}</div>
          </div>
        `;
      }

      // Activity log (conversation history)
      const activityEntries = normalizeGoalActivity(goal);
      if (activityEntries.length > 0) {
        contentHtml += `
          <div class="detail-section">
            <div class="detail-section__title">Activity Log</div>
            <div class="activity-log">
        `;

        const canPlanFromActivity = goalIdNum != null && activeIdNum != null && goalIdNum === activeIdNum;
        activityEntries.forEach(entry => {
          const roleRaw = entry.role || "";
          const role = roleRaw === "user"
            ? "You"
            : (roleRaw === "othello" || roleRaw === "assistant" || roleRaw === "bot")
              ? "Othello"
              : (roleRaw ? roleRaw.charAt(0).toUpperCase() + roleRaw.slice(1) : "System");
          const isAssistant = roleRaw === "othello" || roleRaw === "assistant" || roleRaw === "bot";
          const canPlan = canPlanFromActivity && isAssistant && isPlanLikeText(entry.content || "");
          const planBtn = canPlan
            ? `
              <div class="activity-item__actions">
                <button class="commitment-btn plan-from-activity-btn" data-plan-text="${encodeURIComponent(entry.content || "")}">
                  Add to Current Plan
                </button>
              </div>
            `
            : "";
          contentHtml += `
            <div class="activity-item">
              <div class="activity-item__role">${escapeHtml(role)}</div>
              <div class="activity-item__text">${formatMessageText(entry.content || "")}</div>
              ${planBtn}
            </div>
          `;
        });

        contentHtml += `
            </div>
          </div>
        `;
      } else {
        contentHtml += `
          <div class="detail-section">
            <div class="detail-section__title">Activity Log</div>
            <div class="detail-section__body">No activity yet. Continue working on this goal to build your conversation history.</div>
          </div>
        `;
      }

      const planSteps = Array.isArray(goal.plan_steps) ? goal.plan_steps : [];
      const planText = typeof goal.plan === "string" ? goal.plan.trim() : "";
      if (planSteps.length > 0) {
        const sections = new Map();
        planSteps.forEach((step) => {
          const sectionLabel = (step.section || step.section_title || step.section_name || step.section_hint || "").trim();
          const sectionKey = sectionLabel || "Plan Steps";
          if (!sections.has(sectionKey)) {
            sections.set(sectionKey, []);
          }
          sections.get(sectionKey).push(step);
        });

        const sectionHtml = Array.from(sections.entries()).map(([sectionTitle, steps]) => {
          const safeTitle = escapeHtml(sectionTitle);
          const count = steps.length;
          const stepsHtml = steps.map(step => {
            const stepId = typeof step.id === "number" ? step.id : null;
            const goalId = goalIdNum != null ? goalIdNum : null;
            const stepIndex = typeof step.step_index === "number" ? step.step_index : null;
            const label = escapeHtml(step.description || step.label || "Step");
            const statusValue = (step.status || "pending").toString().toLowerCase();
            const statusLabel = escapeHtml(formatStepStatus(statusValue));
            const due = step.due_date ? ` | ${escapeHtml(`due ${step.due_date}`)}` : "";
            const detail = typeof step.detail === "string" ? step.detail.trim() : "";
            const hasDetail = detail.length > 0;
            const isDone = statusValue === "done";
            const labelClass = isDone ? "plan-step__label--done" : "";
            const checkboxAttrs = stepId && goalId ? "" : "disabled";
            const checkedAttr = isDone ? "checked" : "";
            const detailPreview = hasDetail
              ? `<div class="plan-step__detail-preview">${escapeHtml(detail)}</div>`
              : "";
            const detailBtnLabel = hasDetail ? "Edit details" : "Add details";
            const detailEditor = stepId && goalId
              ? `
                <div class="plan-step__detail-editor" data-step-id="${stepId}" data-goal-id="${goalId}" data-step-index="${stepIndex || ""}">
                  <textarea class="plan-step__detail-input" rows="3" placeholder="Add details...">${escapeHtml(detail)}</textarea>
                  <div class="plan-step__detail-actions">
                    <button class="plan-step__detail-save" data-step-id="${stepId}" data-goal-id="${goalId}" data-step-index="${stepIndex || ""}">Save</button>
                    <button class="plan-step__detail-cancel" data-step-id="${stepId}" data-goal-id="${goalId}" data-step-index="${stepIndex || ""}">Cancel</button>
                  </div>
                </div>
              `
              : "";
            return `
              <div class="planner-step plan-step" data-step-id="${stepId || ""}" data-goal-id="${goalId || ""}" data-step-index="${stepIndex || ""}">
                <label class="plan-step__toggle">
                  <input type="checkbox" class="plan-step__checkbox" data-step-id="${stepId || ""}" data-goal-id="${goalId || ""}" data-step-index="${stepIndex || ""}" ${checkedAttr} ${checkboxAttrs}>
                </label>
                <div class="plan-step__body">
                  <div class="planner-step__label ${labelClass}">${label}</div>
                  <div class="planner-step__meta">${statusLabel}${due}</div>
                  ${detailPreview}
                </div>
                <button class="plan-step__detail-btn" data-step-id="${stepId || ""}" data-goal-id="${goalId || ""}" data-step-index="${stepIndex || ""}" ${checkboxAttrs}>
                  ${detailBtnLabel}
                </button>
              </div>
              ${detailEditor}
            `;
          }).join("");

          return `
            <details class="plan-accordion" open>
              <summary class="detail-section__title">
                <span>${safeTitle}</span>
                <span class="plan-accordion__count">${count} step${count === 1 ? "" : "s"}</span>
              </summary>
              <div class="planner-steps">
                ${stepsHtml}
              </div>
            </details>
          `;
        }).join("");

        contentHtml += `
          <div class="detail-section">
            <div class="detail-section__title">Current Plan</div>
            ${sectionHtml}
          </div>
        `;
      } else if (planText) {
        contentHtml += `
          <div class="detail-section">
            <div class="detail-section__title">Current Plan</div>
            <div class="detail-section__body">${escapeHtml(planText)}</div>
          </div>
        `;
      } else {
        contentHtml += `
          <div class="detail-section">
            <div class="detail-section__title">Current Plan</div>
            <div class="detail-section__body">Plan tracking coming soon. Othello will help you break down this goal into actionable steps.</div>
          </div>
        `;
      }

      detailContent.innerHTML = contentHtml;
    }

    async function fetchGoalDetail(goalId) {
      if (!goalId) return;
      // Guard: Do not fetch drafts from the goals API
      if (String(goalId).startsWith("draft:")) return;

      try {
        const resp = await fetch(`/api/goals/${goalId}`, { credentials: "include" });
        if (resp.status === 401 || resp.status === 403) {
          await handleUnauthorized("goal-detail");
          return;
        }
        if (!resp.ok) throw new Error("Failed to fetch goal detail");
        const data = await resp.json();
        const goal = data && data.goal ? data.goal : null;
        if (!goal) return;
        const idx = othelloState.goals.findIndex(g => g.id === goal.id);
        if (idx >= 0) {
          othelloState.goals[idx] = goal;
        } else {
          othelloState.goals.push(goal);
        }
        renderGoalDetail(goal);
      } catch (err) {
        console.warn("[Othello UI] Failed to fetch goal detail:", err);
      }
    }

    async function refreshGoalDetail() {
      if (othelloState.currentDetailGoalId == null) return;
      await fetchGoalDetail(othelloState.currentDetailGoalId);
    }

    function showGoalDetail(goalId) {
      const goal = othelloState.goals.find(g => g.id === goalId);
      othelloState.currentDetailGoalId = goalId;

      if (goal) {
        if (goal.is_draft) {
             // Render Draft Detail
             detailGoalId.textContent = "Draft";
             detailGoalTitle.innerHTML = formatMessageText(goal.text || "New Draft");
             let contentHtml = "";
             
             // Intent/Body
             if (goal.draft_text) {
                contentHtml += `
                  <div class="detail-section">
                    <div class="detail-section__title">Description / Intent</div>
                    <div class="detail-section__body" style="white-space: pre-wrap;">${formatMessageText(goal.draft_text)}</div>
                  </div>
                  <div class="detail-actions" style="padding: 0 16px 16px 16px;">
                    <button class="action-btn clarify-intent-btn" data-goal-id="${goal.id}" style="font-size: 0.9em; padding: 6px 12px; border: 1px solid var(--border-color); background: var(--bg-secondary); border-radius: 4px; cursor: pointer; display: flex; align-items: center; gap: 6px;">
                       <span class="codicon codicon-question"></span> Clarify Intent
                    </button>
                  </div>
                `;
             }

             // Steps
             if (goal.checklist && goal.checklist.length > 0) {
                 const stepsHtml = goal.checklist.map((step, idx) => {
                    return `<div class="intent-item"><div class="intent-item__text">${idx + 1}. ${formatMessageText(step)}</div></div>`;
                 }).join("");
                  contentHtml += `
                  <div class="detail-section">
                    <div class="detail-section__title">Draft Steps</div>
                    <div class="intent-list">${stepsHtml}</div>
                  </div>`;
             } else {
                 contentHtml += `<div class="detail-section"><div class="detail-section__body" style="font-style:italic; opacity:0.7;">No steps generated yet. Use chat to "generate steps".</div></div>`;
             }
             
             // Actions (Confirm/Dismiss wrappers handled by chat usually, but we can add buttons here if needed)
             // Using data-draft-id for actions
             const realId = goal.real_draft_id;
             contentHtml += `
               <div class="detail-section" style="margin-top:20px; border-top:1px solid var(--border-color); padding-top:10px;">
                  <div style="display:flex; gap:10px;">
                      <button onclick="sendMessage('', {ui_action:'confirm_draft', draft_id:${realId}})" class="commitment-btn">Confirm Goal</button>
                      <button onclick="sendMessage('', {ui_action:'dismiss_draft', draft_id:${realId}})" style="background:var(--bg-secondary); border:1px solid var(--border-color); color:var(--text-color); padding:8px 16px; border-radius:4px; cursor:pointer;">Dismiss</button>
                  </div>
               </div>
             `;

             detailContent.innerHTML = contentHtml;
        } else {
             renderGoalDetail(goal);
        }
      } else {
        detailGoalId.textContent = `Goal #${goalId}`;
        detailGoalTitle.textContent = "Loading...";
        detailContent.innerHTML = `
          <div class="detail-section">
            <div class="detail-section__body">Loading goal details...</div>
          </div>
        `;
      }

      goalDetail.classList.add("visible");
      // Only fetch if it's a real goal, otherwise we have data in memory
      if (!goal || !goal.is_draft) {
          fetchGoalDetail(goalId);
      }
    }

    async function archiveGoal(goalId) {
      if (!goalId) return;
      if (archiveStatus) {
        archiveStatus.textContent = "Archiving.";
        archiveStatus.style.color = "";
      }
      if (archiveConfirmBtn) archiveConfirmBtn.disabled = true;
      try {
        const res = await fetch(`/api/goals/${goalId}/archive`, {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          credentials: "include"
        });
        if (res.status === 401 || res.status === 403) {
          await handleUnauthorized("goal-archive");
          return;
        }
        if (!res.ok) {
          let errMsg = "Unable to archive goal.";
          let reqId = null;
          const contentType = res.headers.get("content-type") || "";
          if (contentType.includes("application/json")) {
            const data = await res.json();
            errMsg = (data && (data.message || data.error)) || errMsg;
            reqId = data && data.request_id;
          } else {
            const text = await res.text();
            if (text) errMsg = text.slice(0, 200);
          }
          if (archiveStatus) {
            archiveStatus.textContent = reqId ? `${errMsg} (request_id: ${reqId})` : errMsg;
            archiveStatus.style.color = "#fca5a5";
          }
          return;
        }
        await res.json();
        closeArchiveModal();
        if (othelloState.activeGoalId === goalId) {
          othelloState.activeGoalId = null;
          updateFocusRibbon();
        }
        hideGoalDetail();
        await refreshGoals();
      } catch (err) {
        console.error("[Othello UI] archiveGoal error:", err);
        if (archiveStatus) {
          archiveStatus.textContent = "Network error.";
          archiveStatus.style.color = "#fca5a5";
        }
      } finally {
        if (archiveConfirmBtn) archiveConfirmBtn.disabled = false;
      }
    }

    function hideGoalDetail() {
      goalDetail.classList.remove("visible");
      othelloState.currentDetailGoalId = null;
    }

    backFromDetailBtn.addEventListener("click", hideGoalDetail);
    if (goalDetailRefreshBtn) {
      goalDetailRefreshBtn.addEventListener("click", refreshGoalDetail);
    }

    const detailContentEl = document.getElementById("detail-content");
    if (detailContentEl) {
      detailContentEl.addEventListener("click", async (e) => {
        const detailToggleBtn = e.target.closest(".plan-step__detail-btn");
        const detailSaveBtn = e.target.closest(".plan-step__detail-save");
        const detailCancelBtn = e.target.closest(".plan-step__detail-cancel");
        if (detailToggleBtn) {
          const stepId = parseInt(detailToggleBtn.getAttribute("data-step-id") || "0", 10);
          if (!stepId) return;
          const editor = detailContentEl.querySelector(`.plan-step__detail-editor[data-step-id="${stepId}"]`);
          if (!editor) return;
          const isOpen = editor.style.display === "block";
          editor.style.display = isOpen ? "none" : "block";
          if (!isOpen) {
            const input = editor.querySelector(".plan-step__detail-input");
            if (input) input.focus();
          }
          return;
        }
        if (detailSaveBtn) {
          const stepId = parseInt(detailSaveBtn.getAttribute("data-step-id") || "0", 10);
          const goalId = parseInt(detailSaveBtn.getAttribute("data-goal-id") || "0", 10);
          const stepIndex = parseInt(detailSaveBtn.getAttribute("data-step-index") || "", 10);
          const safeStepIndex = Number.isFinite(stepIndex) ? stepIndex : null;
          if (!stepId || !goalId) return;
          const editor = detailSaveBtn.closest(".plan-step__detail-editor");
          const input = editor ? editor.querySelector(".plan-step__detail-input") : null;
          const detailText = input ? input.value : "";
          const originalLabel = detailSaveBtn.textContent;
          detailSaveBtn.textContent = "Saving...";
          detailSaveBtn.disabled = true;
          try {
            if (BOOT_DEBUG) {
              console.log("[Plan Step Detail] save payload", {
                goalId,
                stepId,
                stepIndex: safeStepIndex,
                detailLength: detailText.length,
              });
            }
            await postPlanStepDetail(goalId, stepId, detailText, safeStepIndex);
            if (othelloState.currentDetailGoalId === goalId) {
              await refreshGoalDetail();
            }
            refreshGoals();
          } catch (err) {
            console.error("[Othello UI] plan step detail update failed:", err);
            detailSaveBtn.textContent = err && err.message ? err.message : "Failed";
            setTimeout(() => {
              detailSaveBtn.textContent = originalLabel;
            }, 1200);
          } finally {
            detailSaveBtn.disabled = false;
            if (detailSaveBtn.textContent === "Saving...") {
              detailSaveBtn.textContent = originalLabel;
            }
          }
          return;
        }
        if (detailCancelBtn) {
          const stepId = parseInt(detailCancelBtn.getAttribute("data-step-id") || "0", 10);
          if (!stepId) return;
          const editor = detailContentEl.querySelector(`.plan-step__detail-editor[data-step-id="${stepId}"]`);
          if (editor) {
            editor.style.display = "none";
          }
          return;
        }

        const clarifyBtn = e.target.closest(".clarify-intent-btn");
        if (clarifyBtn) {
            let goalId = clarifyBtn.getAttribute("data-goal-id");
            if (!goalId) return;
            
            // Handle draft IDs (e.g. "draft:123")
            if (goalId.startsWith("draft:")) {
                 const realId = goalId.split(":")[1];
                 hideGoalDetail();
                 sendMessage("", { ui_action: "clarify_goal_intent", draft_id: realId }); 
                 return;
            }

            // Phase 18: Clarify Intent Action
            hideGoalDetail(); // Close detail to show chat
            sendMessage("", { ui_action: "clarify_goal_intent", goal_id: goalId });
            return;
        }

        const btn = e.target.closest(".plan-from-activity-btn");
        const intentBtn = e.target.closest(".intent-plan-btn");
        if (btn) {
          const encoded = btn.getAttribute("data-plan-text") || "";
          let planText = "";
          try {
            planText = decodeURIComponent(encoded);
          } catch (err) {
            planText = "";
          }
          if (!planText) return;
          const originalLabel = btn.textContent;
          btn.textContent = "Adding.";
          btn.disabled = true;
          try {
            const data = await postPlanFromText(planText);
            btn.textContent = "Added";
            if (data && data.meta && data.meta.intent === "plan_steps_added") {
              if (othelloState.currentDetailGoalId === othelloState.activeGoalId) {
                refreshGoalDetail();
              }
              refreshGoals();
            }
          } catch (err) {
            btn.textContent = err && err.message ? err.message : "Failed";
          } finally {
            setTimeout(() => {
              btn.textContent = originalLabel;
              btn.disabled = false;
            }, 1500);
          }
          return;
        }
        if (intentBtn) {
          const intentIndex = parseInt(intentBtn.getAttribute("data-intent-index") || "0", 10);
          const rawGoalId = intentBtn.getAttribute("data-goal-id");
          const encodedText = intentBtn.getAttribute("data-intent-text") || "";
          let intentText = "";
          try {
            intentText = decodeURIComponent(encodedText);
          } catch (err) {
            intentText = "";
          }
          if (!intentIndex || !intentText) return;
          const resolvedGoalId = normalizeGoalId(rawGoalId || othelloState.currentDetailGoalId || othelloState.activeGoalId);
          if (resolvedGoalId == null) return;
          const activeIdNum = normalizeGoalId(othelloState.activeGoalId);
          if (activeIdNum !== resolvedGoalId) {
            setActiveGoal(resolvedGoalId);
            if (othelloState.currentDetailGoalId === resolvedGoalId) {
              await refreshGoalDetail();
            }
          }
          const originalLabel = intentBtn.textContent;
          intentBtn.textContent = "Building.";
          intentBtn.disabled = true;
          try {
            const data = await postPlanFromIntent(resolvedGoalId, intentIndex, intentText);
            intentBtn.textContent = "Built";
            if (data && data.reply) {
              addMessage("bot", data.reply);
            }
            if (data && data.meta && data.meta.intent === "plan_steps_added") {
              if (othelloState.currentDetailGoalId === othelloState.activeGoalId) {
                refreshGoalDetail();
              }
              refreshGoals();
            }
          } catch (err) {
            intentBtn.textContent = err && err.message ? err.message : "Failed";
          } finally {
            setTimeout(() => {
              intentBtn.textContent = originalLabel;
              intentBtn.disabled = false;
            }, 1500);
          }
        }
      });

      detailContentEl.addEventListener("change", async (e) => {
        const checkbox = e.target.closest(".plan-step__checkbox");
        if (!checkbox) return;
        const stepId = parseInt(checkbox.getAttribute("data-step-id") || "0", 10);
        const goalId = parseInt(checkbox.getAttribute("data-goal-id") || "0", 10);
        if (!stepId || !goalId) return;
        const newStatus = checkbox.checked ? "done" : "pending";
        checkbox.disabled = true;
        try {
          await postPlanStepStatus(goalId, stepId, newStatus);
          if (othelloState.currentDetailGoalId === goalId) {
            await refreshGoalDetail();
          }
          refreshGoals();
        } catch (err) {
          console.error("[Othello UI] plan step status update failed:", err);
          checkbox.checked = !checkbox.checked;
        } finally {
          checkbox.disabled = false;
        }
      });
    }

    continueWorkingBtn.addEventListener("click", () => {
      if (othelloState.currentDetailGoalId !== null) {
        setActiveGoal(othelloState.currentDetailGoalId);
        hideGoalDetail();
        switchView("chat");
        input.focus();
      }
    });

    if (archiveGoalBtn) {
      archiveGoalBtn.addEventListener("click", () => {
        const goalId = othelloState.currentDetailGoalId;
        const goal = othelloState.goals.find(g => g.id === goalId);
        if (goalId == null) return;
        openArchiveModal(goal);
      });
    }

    if (archiveConfirmBtn) {
      archiveConfirmBtn.addEventListener("click", () => {
        const goalId = othelloState.currentDetailGoalId;
        if (goalId == null) return;
        archiveGoal(goalId);
      });
    }

    // ===== ROUTINE PLANNER LOGIC =====
    const ROUTINES_API = "/api/routines";
    othelloState.routines = [];
    othelloState.activeRoutineId = null;

    function debounce(func, wait) {
      let timeout;
      return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
      };
    }

    function showToast(message, type = "info") {
      const container = document.getElementById("toast-container");
      if (!container) return;
      const toast = document.createElement("div");
      toast.className = `toast ${type}`;
      toast.textContent = message;
      container.appendChild(toast);
      setTimeout(() => {
        toast.style.animation = "fadeOut 0.3s ease-out forwards";
        setTimeout(() => toast.remove(), 300);
      }, 3000);
    }

    async function fetchRoutines() {
      if (othelloState.currentView !== "routine-planner") return;
      if (document.hidden) return;
      const listEl = document.getElementById("routine-list");
      // Only show loader if we don't have data yet to avoid flicker on refresh
      if (listEl && othelloState.routines.length === 0) {
         listEl.innerHTML = '<div class="routine-loader">Loading routines...</div>';
      }
      try {
        abortRoutineRequests("routines-reload");
        routinesAbort = new AbortController();
        const resp = await fetch(ROUTINES_API, { credentials: "include", signal: routinesAbort.signal });
        if (!resp.ok) throw new Error("Failed to fetch routines");
        const data = await resp.json();
        if (data.ok) {
          othelloState.routines = data.routines || [];
          // If we have an active routine, ensure we have the latest version of it
          if (othelloState.activeRoutineId) {
              const active = othelloState.routines.find(r => r.id === othelloState.activeRoutineId);
              if (!active) {
                  // Active routine disappeared (deleted elsewhere?)
                  othelloState.activeRoutineId = null;
              }
          }
        }
      } catch (err) {
        if (isAbortError(err)) {
          logPlannerDebug("[Routine Planner] fetch aborted", { reason: "routines-reload" });
          return;
        }
        console.error("fetchRoutines error:", err);
        showToast("Failed to load routines", "error");
        if (listEl && othelloState.routines.length === 0) {
            listEl.innerHTML = '<div class="planner-error" style="padding:1rem; text-align:center;">Failed to load routines.</div>';
        }
      }
    }

    async function loadRoutinePlanner() {
      if (othelloState.currentView !== "routine-planner") return;
      if (document.hidden) return;
      await fetchRoutines();
      renderRoutineList(othelloState.routines);
      
      // Deterministic selection logic
      if (othelloState.activeRoutineId) {
          // Try to select the previously active routine
          const exists = othelloState.routines.find(r => r.id === othelloState.activeRoutineId);
          if (exists) {
              selectRoutine(othelloState.activeRoutineId, true);
          } else {
              othelloState.activeRoutineId = null;
              if (othelloState.routines.length > 0) {
                  selectRoutine(othelloState.routines[0].id, false);
              } else {
                  renderEmptyState();
              }
          }
      } else if (othelloState.routines.length > 0) {
        selectRoutine(othelloState.routines[0].id, false);
      } else {
        renderEmptyState();
      }
    }

    function renderEmptyState() {
        document.getElementById("routine-editor").style.display = "none";
        document.getElementById("routine-empty-state").style.display = "flex";
        if (window.innerWidth <= 768) setRoutineMobileView("list");
    }

    function renderRoutineList(routines) {
      const listEl = document.getElementById("routine-list");
      listEl.innerHTML = "";

      // Update empty state text
      const emptyState = document.getElementById("routine-empty-state");
      if (emptyState) {
        if (routines.length === 0) {
            emptyState.textContent = "No routines yet — tap + to create your first routine.";
        } else if (!othelloState.activeRoutineId) {
            emptyState.textContent = "Select a routine to edit";
        }
      }

      routines.forEach(r => {
        const item = document.createElement("div");
        item.className = "routine-list-item";
        if (r.id === othelloState.activeRoutineId) item.classList.add("selected");
        item.dataset.routineId = r.id;

        item.style.padding = "0.8rem";
        item.style.borderBottom = "1px solid var(--border)";
        item.style.cursor = "pointer";
        if (r.id !== othelloState.activeRoutineId) {
            item.style.background = "transparent";
            item.style.borderLeft = "3px solid transparent";
        }
        item.style.position = "relative";
        
        const titleRow = document.createElement("div");
        titleRow.style.display = "flex";
        titleRow.style.justifyContent = "space-between";
        titleRow.style.alignItems = "center";
        
        const title = document.createElement("div");
        title.style.fontWeight = "600";
        title.style.color = r.enabled ? "var(--text-main)" : "var(--text-soft)";
        title.style.display = "flex";
        title.style.alignItems = "center";
        title.style.gap = "0.5rem";
        
        const nameSpan = document.createElement("span");
        nameSpan.textContent = r.title;
        title.appendChild(nameSpan);

        // Disabled badge if days=[]
        const sched = r.schedule_rule || {};
        if (sched.days && Array.isArray(sched.days) && sched.days.length === 0) {
           const badge = document.createElement("span");
           badge.textContent = "Disabled";
           badge.style.fontSize = "0.7rem";
           badge.style.background = "rgba(255,255,255,0.1)";
           badge.style.padding = "0.1rem 0.3rem";
           badge.style.borderRadius = "4px";
           title.appendChild(badge);
        }
        
        titleRow.appendChild(title);

        // Duplicate button (stop propagation)
        const dupBtn = document.createElement("button");
        dupBtn.innerHTML = "📋"; // Copy icon
        dupBtn.title = "Duplicate Routine";
        dupBtn.style.background = "none";
        dupBtn.style.border = "none";
        dupBtn.style.cursor = "pointer";
        dupBtn.style.fontSize = "0.9rem";
        dupBtn.style.opacity = "0.6";
        dupBtn.style.padding = "0.2rem";
        dupBtn.onclick = (e) => {
          e.stopPropagation();
          duplicateRoutine(r.id);
        };
        dupBtn.onmouseover = () => dupBtn.style.opacity = "1";
        dupBtn.onmouseout = () => dupBtn.style.opacity = "0.6";
        titleRow.appendChild(dupBtn);

        const meta = document.createElement("div");
        meta.style.fontSize = "0.8rem";
        meta.style.color = "var(--text-soft)";
        meta.style.marginTop = "0.2rem";
        const stepCount = (r.steps || []).length;
        
        let updatedText = "";
        if (r.updated_at) {
            try {
                const d = new Date(r.updated_at);
                updatedText = ` • ${d.toLocaleDateString()}`;
            } catch(e) {}
        }
        
        meta.textContent = `${stepCount} step${stepCount !== 1 ? 's' : ''}${updatedText}`;
        
        item.appendChild(titleRow);
        item.appendChild(meta);
        item.onclick = () => {
            othelloState.mobileEditorPinned = true;
            selectRoutine(r.id, true);
        };
        listEl.appendChild(item);
      });
    }

    // Mobile Navigation Helpers
    function setRoutineMobileView(view) {
      // Single source of truth for mobile view switching
      // view: "list" | "editor"
      const isMobile = window.innerWidth <= 768;
      const editor = document.getElementById("routine-editor");
      const listPanel = document.querySelector(".routine-list-panel");
      
      if (view === "editor") {
        document.body.classList.add("routine-editor-open");
        if (editor) editor.style.display = "flex";
        if (listPanel && isMobile) listPanel.style.display = "none";
      } else {
        document.body.classList.remove("routine-editor-open");
        if (editor && isMobile) editor.style.display = "none";
        if (listPanel) listPanel.style.display = "flex";
      }
    }

    function openMobileEditor() {
      if (Date.now() - (othelloState.mobileBackJustPressedAt || 0) < 750) return;
      if (window.innerWidth <= 768) {
        setRoutineMobileView("editor");
      }
    }

    function closeMobileEditor() {
      setRoutineMobileView("list");
      othelloState.mobileEditorPinned = false; // Unpin
      othelloState.mobileBackJustPressedAt = Date.now(); // Guard against immediate reopen
      othelloState.activeRoutineId = null; // Deselect
      renderRoutineList(othelloState.routines); // Refresh list selection state
    }
    
    const mobileBackBtn = document.getElementById("routine-mobile-back-btn");
    if (mobileBackBtn) {
      mobileBackBtn.onclick = (e) => {
          e.preventDefault();
          e.stopPropagation();
          closeMobileEditor();
      };
    }

    function selectRoutine(routineId, openOnMobile = false) {
      othelloState.activeRoutineId = routineId;
      // Always find the routine from the latest state
      const routine = othelloState.routines.find(r => r.id === routineId);
      renderRoutineList(othelloState.routines); // update selection style
      
      if (routine) {
        document.getElementById("routine-empty-state").style.display = "none";
        
        // Logic to determine if editor should be visible
        const isMobile = window.innerWidth <= 768;
        const shouldShow = !isMobile || (openOnMobile && othelloState.mobileEditorPinned);
        
        if (shouldShow) {
            document.getElementById("routine-editor").style.display = "flex";
            if (isMobile) setRoutineMobileView("editor");
        } else {
            // Pre-render but keep hidden on mobile if not pinned
            if (isMobile) {
                document.getElementById("routine-editor").style.display = "none";
                // Ensure list is visible
                document.querySelector(".routine-list-panel").style.display = "flex";
            } else {
                document.getElementById("routine-editor").style.display = "flex";
            }
        }

        renderRoutineEditor(routine);
      } else {
        renderEmptyState();
      }
    }

    async function saveRoutine(routineId) {
        const titleInput = document.getElementById("routine-title-input");
        const enabledToggle = document.getElementById("routine-enabled-toggle");
        const daysContainer = document.getElementById("routine-days");
        
        if (!titleInput || !enabledToggle || !daysContainer) return;
        
        // Gather days
        const days = [];
        daysContainer.querySelectorAll("input[type=checkbox]").forEach((cb, idx) => {
            const dayNames = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"];
            if (cb.checked) days.push(dayNames[idx]);
        });
        
        // Gather extra schedule info (part_of_day, time_window)
        // Note: These are updated via onchange in the UI, but we can re-read them if we want to be sure.
        // However, the DOM elements for them are dynamically created in renderRoutineEditor.
        // For simplicity, we'll trust the state or re-read if we can find them.
        // Since updateRoutine is called on change for these, the state *should* be consistent.
        // But the user wants "Save" to be the primary action or at least reliable.
        // Let's just send the title and enabled state and days explicitly, 
        // and rely on the fact that other fields triggered their own updates.
        // OR, better: read everything from the DOM to be sure.
        
        const extraContainer = document.getElementById("routine-schedule-extra");
        let part_of_day = "any";
        let time_window = { start: "", end: "" };
        
        if (extraContainer) {
            const selects = extraContainer.querySelectorAll("select");
            if (selects.length > 0) part_of_day = selects[0].value;
            
            const inputs = extraContainer.querySelectorAll("input[type=time]");
            if (inputs.length > 0) time_window.start = inputs[0].value;
            if (inputs.length > 1) time_window.end = inputs[1].value;
        }

        const patch = {
            title: titleInput.value,
            enabled: enabledToggle.checked,
            schedule_rule: {
                days: days,
                part_of_day: part_of_day,
                time_window: time_window
            }
        };
        
        const btn = document.getElementById("routine-save-btn");
        const originalText = btn ? btn.textContent : "Save";
        if (btn) {
            btn.textContent = "Saving...";
            btn.disabled = true;
        }

        try {
            await updateRoutine(routineId, patch, true);
            showToast("Routine saved", "success");
        } catch (err) {
            showToast("Save failed", "error");
        } finally {
            if (btn) {
                btn.textContent = originalText;
                btn.disabled = false;
            }
        }
    }

    function renderRoutineEditor(routine) {
      const debouncedUpdateRoutine = debounce((patch) => updateRoutine(routine.id, patch, false), 500);

      const titleInput = document.getElementById("routine-title-input");
      titleInput.value = routine.title;
      titleInput.oninput = (e) => debouncedUpdateRoutine({ title: e.target.value });
      
      const enabledToggle = document.getElementById("routine-enabled-toggle");
      enabledToggle.checked = routine.enabled;
      enabledToggle.onchange = (e) => updateRoutine(routine.id, { enabled: e.target.checked });
      
      const saveBtn = document.getElementById("routine-save-btn");
      if (saveBtn) {
          saveBtn.onclick = () => saveRoutine(routine.id);
      }
      
      const backBtn = document.getElementById("routine-mobile-back-btn");
      if (backBtn) {
          backBtn.onclick = (e) => {
              e.preventDefault();
              e.stopPropagation();
              closeMobileEditor();
          };
      }

      document.getElementById("routine-delete-btn").onclick = () => deleteRoutine(routine.id);
      
      // Schedule days
      const daysContainer = document.getElementById("routine-days");
      daysContainer.innerHTML = "";
      const days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"];
      const currentDays = (routine.schedule_rule || {}).days || [];
      
      days.forEach(day => {
        const label = document.createElement("label");
        label.style.display = "flex";
        label.style.alignItems = "center";
        label.style.gap = "0.3rem";
        label.style.fontSize = "0.85rem";
        label.style.cursor = "pointer";
        label.style.padding = "0.3rem 0.6rem";
        label.style.borderRadius = "4px";
        label.style.background = "var(--card-bg)";
        label.style.border = "1px solid var(--border)";
        
        const cb = document.createElement("input");
        cb.type = "checkbox";
        cb.checked = currentDays.includes(day);
        cb.onchange = () => {
          const newDays = days.filter(d => {
            if (d === day) return cb.checked;
            return currentDays.includes(d);
          });
          updateRoutine(routine.id, { schedule_rule: { days: newDays } });
        };
        
        label.appendChild(cb);
        label.appendChild(document.createTextNode(day.toUpperCase()));
        daysContainer.appendChild(label);
      });
      
      // Part of Day & Time Window
      const scheduleRule = routine.schedule_rule || {};
      const existingExtra = document.getElementById("routine-schedule-extra");
      if (existingExtra) existingExtra.remove();
      
      const extraContainer = document.createElement("div");
      extraContainer.id = "routine-schedule-extra";
      extraContainer.style.display = "flex";
      extraContainer.style.gap = "1rem";
      extraContainer.style.marginTop = "0.8rem";
      extraContainer.style.flexWrap = "wrap";
      
      // Part of Day
      const podWrap = document.createElement("div");
      podWrap.style.display = "flex";
      podWrap.style.flexDirection = "column";
      podWrap.style.gap = "0.3rem";
      const podLabel = document.createElement("label");
      podLabel.textContent = "Part of Day";
      podLabel.style.fontSize = "0.8rem";
      podLabel.style.color = "var(--text-soft)";
      const podSelect = document.createElement("select");
      podSelect.className = "login-input";
      podSelect.style.padding = "0.4rem";
      podSelect.style.fontSize = "0.9rem";
      ["any", "morning", "afternoon", "evening", "night"].forEach(p => {
         const opt = document.createElement("option");
         opt.value = p;
         opt.text = p;
         opt.selected = (scheduleRule.part_of_day || "any") === p;
         podSelect.appendChild(opt);
      });
      podSelect.onchange = (e) => {
         const current = (othelloState.routines.find(r => r.id === routine.id) || {}).schedule_rule || {};
         updateRoutine(routine.id, { schedule_rule: { ...current, part_of_day: e.target.value } });
      };
      podWrap.appendChild(podLabel);
      podWrap.appendChild(podSelect);
      extraContainer.appendChild(podWrap);
      
      // Time Window
      const timeWrap = document.createElement("div");
      timeWrap.style.display = "flex";
      timeWrap.style.flexDirection = "column";
      timeWrap.style.gap = "0.3rem";
      const timeLabel = document.createElement("label");
      timeLabel.textContent = "Time Window (Optional)";
      timeLabel.style.fontSize = "0.8rem";
      timeLabel.style.color = "var(--text-soft)";
      
      const timeInputs = document.createElement("div");
      timeInputs.style.display = "flex";
      timeInputs.style.gap = "0.5rem";
      timeInputs.style.alignItems = "center";
      
      const startInput = document.createElement("input");
      startInput.type = "time";
      startInput.className = "login-input";
      startInput.style.padding = "0.4rem";
      startInput.value = (scheduleRule.time_window || {}).start || "";
      startInput.onchange = (e) => {
         const current = (othelloState.routines.find(r => r.id === routine.id) || {}).schedule_rule || {};
         const win = current.time_window || {};
         updateRoutine(routine.id, { schedule_rule: { ...current, time_window: { ...win, start: e.target.value } } });
      };
      
      const endInput = document.createElement("input");
      endInput.type = "time";
      endInput.className = "login-input";
      endInput.style.padding = "0.4rem";
      endInput.value = (scheduleRule.time_window || {}).end || "";
      endInput.onchange = (e) => {
         const current = (othelloState.routines.find(r => r.id === routine.id) || {}).schedule_rule || {};
         const win = current.time_window || {};
         updateRoutine(routine.id, { schedule_rule: { ...current, time_window: { ...win, end: e.target.value } } });
      };
      
      timeInputs.appendChild(startInput);
      timeInputs.appendChild(document.createTextNode("-"));
      timeInputs.appendChild(endInput);
      
      timeWrap.appendChild(timeLabel);
      timeWrap.appendChild(timeInputs);
      extraContainer.appendChild(timeWrap);
      
      daysContainer.parentNode.insertBefore(extraContainer, daysContainer.nextSibling);
      
      // Steps Header
      const stepsHeader = document.getElementById("routine-steps-header");
      if (stepsHeader) {
          stepsHeader.innerHTML = "";
          
          const headerLeft = document.createElement("div");
          headerLeft.style.display = "flex";
          headerLeft.style.alignItems = "center";
          headerLeft.style.gap = "0.5rem";

          const stepsTitle = document.createElement("span");
          stepsTitle.style.fontSize = "0.95rem";
          stepsTitle.style.fontWeight = "600";
          stepsTitle.style.color = "var(--text-main)";
          stepsTitle.textContent = "Steps";
          headerLeft.appendChild(stepsTitle);

          const stepCountBadge = document.createElement("span");
          stepCountBadge.style.fontSize = "0.8rem";
          stepCountBadge.style.color = "var(--text-soft)";
          stepCountBadge.style.background = "var(--bg-1)";
          stepCountBadge.style.padding = "0.1rem 0.4rem";
          stepCountBadge.style.borderRadius = "10px";
          stepCountBadge.textContent = (routine.steps || []).length;
          headerLeft.appendChild(stepCountBadge);
          
          stepsHeader.appendChild(headerLeft);

          const headerRight = document.createElement("div");
          headerRight.style.display = "flex";
          headerRight.style.gap = "0.5rem";
          headerRight.style.alignItems = "center";

          // Reorder Hint
          if ((routine.steps || []).length > 1) {
              const hint = document.createElement("span");
              hint.textContent = "Use ▲/▼ to reorder";
              hint.style.fontSize = "0.75rem";
              hint.style.color = "var(--text-soft)";
              hint.style.marginRight = "0.5rem";
              headerRight.appendChild(hint);
          }

          // Save Order Button
          const saveOrderBtn = document.createElement("button");
          saveOrderBtn.id = "routine-save-order-btn";
          saveOrderBtn.textContent = "Save Order";
          saveOrderBtn.className = "settings-button";
          saveOrderBtn.style.fontSize = "0.8rem";
          saveOrderBtn.style.padding = "0.3rem 0.6rem";
          saveOrderBtn.style.display = "none"; // Hidden by default
          saveOrderBtn.onclick = () => saveStepOrder(routine.id);
          headerRight.appendChild(saveOrderBtn);

          // Add Step Button (Header)
          const addStepBtn = document.createElement("button");
          addStepBtn.id = "routine-add-step-btn"; // Ensure ID is present for fallback
          addStepBtn.textContent = "+ Add Step";
          addStepBtn.className = "login-button";
          addStepBtn.style.padding = "0.3rem 0.6rem";
          addStepBtn.style.fontSize = "0.8rem";
          addStepBtn.onclick = () => addStep(routine.id);
          headerRight.appendChild(addStepBtn);

          stepsHeader.appendChild(headerRight);
      }

      // Steps List
      const stepsContainer = document.getElementById("routine-steps");
      stepsContainer.innerHTML = "";
      
      if (!routine.steps || routine.steps.length === 0) {
          const emptySteps = document.createElement("div");
          emptySteps.className = "routine-empty-placeholder";
          emptySteps.style.padding = "1rem";
          emptySteps.textContent = "No steps yet — add your first step below.";
          stepsContainer.appendChild(emptySteps);
      }

      (routine.steps || []).forEach((step, idx) => {
        const debouncedUpdateStep = debounce((patch) => updateStep(step.id, patch, false), 500);
        const row = document.createElement("div");
        row.style.display = "flex";
        row.style.gap = "0.5rem";
        row.style.alignItems = "center";
        row.style.padding = "0.5rem";
        row.style.background = "var(--card-bg)";
        row.style.borderRadius = "6px";
        row.style.border = "1px solid var(--border)";
        
        // Order buttons
        const orderCol = document.createElement("div");
        orderCol.style.display = "flex";
        orderCol.style.flexDirection = "column";
        
        const upBtn = document.createElement("button");
        upBtn.innerHTML = "▲";
        upBtn.style.fontSize = "0.6rem";
        upBtn.style.background = "none";
        upBtn.style.border = "none";
        upBtn.style.color = "var(--text-soft)";
        upBtn.style.cursor = "pointer";
        upBtn.disabled = idx === 0;
        upBtn.onclick = () => moveStepLocal(routine.id, step.id, -1);
        
        const downBtn = document.createElement("button");
        downBtn.innerHTML = "▼";
        downBtn.style.fontSize = "0.6rem";
        downBtn.style.background = "none";
        downBtn.style.border = "none";
        downBtn.style.color = "var(--text-soft)";
        downBtn.style.cursor = "pointer";
        downBtn.disabled = idx === (routine.steps.length - 1);
        downBtn.onclick = () => moveStepLocal(routine.id, step.id, 1);
        
        orderCol.appendChild(upBtn);
        orderCol.appendChild(downBtn);
        row.appendChild(orderCol);
        
        // Title
        const sTitle = document.createElement("input");
        sTitle.type = "text";
        sTitle.value = step.title;
        sTitle.className = "login-input";
        sTitle.style.flex = "1";
        sTitle.style.padding = "0.3rem 0.5rem";
        sTitle.style.fontSize = "0.9rem";
        sTitle.oninput = (e) => debouncedUpdateStep({ title: e.target.value });
        row.appendChild(sTitle);
        
        // Duration
        const sDur = document.createElement("input");
        sDur.type = "number";
        sDur.value = step.est_minutes || "";
        sDur.placeholder = "min";
        sDur.className = "login-input";
        sDur.style.width = "60px";
        sDur.style.padding = "0.3rem 0.5rem";
        sDur.style.fontSize = "0.9rem";
        sDur.oninput = (e) => debouncedUpdateStep({ est_minutes: parseInt(e.target.value) || 0 });
        row.appendChild(sDur);
        
        // Energy
        const sEnergy = document.createElement("select");
        sEnergy.className = "login-input";
        sEnergy.style.width = "80px";
        sEnergy.style.padding = "0.3rem 0.5rem";
        sEnergy.style.fontSize = "0.9rem";
        ["low", "medium", "high"].forEach(e => {
          const opt = document.createElement("option");
          opt.value = e;
          opt.text = e;
          opt.selected = step.energy === e;
          sEnergy.appendChild(opt);
        });
        sEnergy.onchange = (e) => updateStep(step.id, { energy: e.target.value });
        row.appendChild(sEnergy);
        
        // Delete
        const delBtn = document.createElement("button");
        delBtn.innerHTML = "×";
        delBtn.style.background = "none";
        delBtn.style.border = "none";
        delBtn.style.color = "#fca5a5";
        delBtn.style.fontSize = "1.2rem";
        delBtn.style.cursor = "pointer";
        delBtn.onclick = () => deleteStep(step.id);
        row.appendChild(delBtn);
        
        stepsContainer.appendChild(row);
      });

      // Inline Add Step Row
      const addRow = document.createElement("div");
      addRow.style.display = "flex";
      addRow.style.gap = "0.5rem";
      addRow.style.alignItems = "center";
      addRow.style.padding = "0.5rem";
      addRow.style.marginTop = "0.5rem";
      
      const addInput = document.createElement("input");
      addInput.type = "text";
      addInput.placeholder = "New step title...";
      addInput.className = "login-input";
      addInput.style.flex = "1";
      addInput.style.padding = "0.4rem 0.6rem";
      addInput.style.fontSize = "0.9rem";
      
      const handleAdd = async () => {
        const val = addInput.value.trim();
        if (!val) return;
        
        addInput.disabled = true;
        addBtn.disabled = true;
        addBtn.textContent = "...";
        
        const success = await addStepInline(routine.id, val);
        
        addInput.disabled = false;
        addBtn.disabled = false;
        addBtn.textContent = "Add";
        
        if (success) {
            addInput.value = "";
            // Focus is lost because of re-render, but that's acceptable for now.
            // If we wanted to keep focus, we'd need to find the new input after render.
            setTimeout(() => {
                const newInputs = document.querySelectorAll("#routine-steps input[type=text]");
                // The last one is the add input, but we want to focus it? 
                // Actually renderRoutineEditor re-creates the DOM.
                // So we need to find the add input in the new DOM.
                // But this function (renderRoutineEditor) has finished.
                // The re-render happens inside addStepInline -> fetchRoutines -> selectRoutine -> renderRoutineEditor.
                // So the DOM is fresh.
                // We can try to auto-focus the add input if we can identify it.
                // For now, just clearing it is enough improvement.
            }, 100);
        } else {
            addInput.focus();
        }
      };

      addInput.onkeydown = (e) => {
        if (e.key === "Enter") {
            handleAdd();
        }
      };
      
      const addBtn = document.createElement("button");
      addBtn.textContent = "Add";
      addBtn.className = "settings-button";
      addBtn.style.padding = "0.4rem 0.8rem";
      addBtn.onclick = handleAdd;
      
      addRow.appendChild(addInput);
      addRow.appendChild(addBtn);
      stepsContainer.appendChild(addRow);
    }

    async function updateRoutine(id, patch, refresh = true) {
      try {
        const resp = await fetch(`${ROUTINES_API}/${id}`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(patch),
          credentials: "include"
        });
        if (resp.ok) {
          if (refresh) {
            await fetchRoutines();
            selectRoutine(id, true); // refresh view
          } else {
             // Optimistic update
             const r = othelloState.routines.find(r => r.id === id);
             if (r) {
                 Object.assign(r, patch);
                 if (patch.schedule_rule) {
                     r.schedule_rule = Object.assign(r.schedule_rule || {}, patch.schedule_rule);
                 }
             }
          }
        } else {
            throw new Error("Failed to update routine");
        }
      } catch (err) { 
          console.error(err);
          showToast("Failed to update routine", "error");
      }
    }

    async function deleteRoutine(id) {
      if (!confirm("Delete this routine?")) return;
      try {
        const resp = await fetch(`${ROUTINES_API}/${id}`, { method: "DELETE", credentials: "include" });
        if (resp.ok) {
          // Optimistic remove
          const wasActive = (othelloState.activeRoutineId === id);
          othelloState.routines = othelloState.routines.filter(r => r.id !== id);
          
          if (wasActive) {
              othelloState.activeRoutineId = null;
              closeMobileEditor();
              // Select next or empty
              if (othelloState.routines.length > 0) {
                  selectRoutine(othelloState.routines[0].id, false);
              } else {
                  renderEmptyState();
              }
          }
          renderRoutineList(othelloState.routines);
          console.debug("routineDeleted", { routineId: id, wasActive, remaining: othelloState.routines.length });

          // Reconcile
          await loadRoutinePlanner();
          showToast("Routine deleted", "success");
        } else {
            throw new Error("Failed to delete routine");
        }
      } catch (err) { 
          console.error(err);
          showToast("Failed to delete routine", "error");
      }
    }

    async function addRoutine() {
      if (othelloState.creatingRoutine) {
          showToast("Creating routine...", "info");
          return;
      }

      const title = prompt("Routine Name:");
      if (!title) return;

      othelloState.creatingRoutine = true;
      const btn = document.getElementById("routine-add-btn");
      if (btn) {
          btn.disabled = true;
          btn.style.opacity = "0.5";
      }
      showToast("Creating routine...", "info");

      try {
        const resp = await fetch(ROUTINES_API, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ title, enabled: true }),
          credentials: "include"
        });
        if (resp.ok) {
          const data = await resp.json();
          
          // Refresh list immediately
          await fetchRoutines();
          
          // Robust ID extraction
          const createdId = (data?.routine?.id) || data?.id || data?.routine_id || data?.routineId || null;
          
          // Find the new routine (by ID or fallback to title/last)
          let newRoutine = null;
          if (createdId) {
              newRoutine = othelloState.routines.find(r => r.id === createdId);
          }
          
          if (!newRoutine) {
              // Fallback: look for title match (newest first) or just take the last one
              newRoutine = othelloState.routines.slice().reverse().find(r => r.title === title) || othelloState.routines[othelloState.routines.length - 1];
          }
          
          if (newRoutine) {
              othelloState.activeRoutineId = newRoutine.id;
              renderRoutineList(othelloState.routines);
              
              // Mobile navigation logic
              othelloState.mobileEditorPinned = true;
              selectRoutine(newRoutine.id, true);
              
              // Scroll into view
              setTimeout(() => {
                  const item = document.querySelector(`.routine-list-item[data-routine-id="${newRoutine.id}"]`);
                  if (item) item.scrollIntoView({ behavior: "smooth", block: "center" });
              }, 100);
              
              showToast("Routine created", "success");
          } else {
              showToast("Routine created but not found after refresh", "warning");
          }
        } else {
            let msg = "Failed to create routine";
            try {
                const errData = await resp.json();
                if (errData.message) msg += `: ${errData.message}`;
            } catch (e) {}
            throw new Error(msg);
        }
      } catch (err) { 
          console.error(err);
          showToast(err.message || "Failed to create routine", "error");
      } finally {
          othelloState.creatingRoutine = false;
          if (btn) {
              btn.disabled = false;
              btn.style.opacity = "1";
          }
      }
    }
    document.getElementById("routine-add-btn").onclick = addRoutine;

    async function addStep(routineId) {
      try {
        const resp = await fetch(`${ROUTINES_API}/${routineId}/steps`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ title: "New Step", est_minutes: 5, energy: "low" }),
          credentials: "include"
        });
        if (resp.ok) {
          await fetchRoutines();
          selectRoutine(routineId);
        } else {
            throw new Error("Failed to add step");
        }
      } catch (err) { 
          console.error(err);
          showToast("Failed to add step", "error");
      }
    }

    async function updateStep(stepId, patch, refresh = true) {
      try {
        const resp = await fetch(`/api/steps/${stepId}`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(patch),
          credentials: "include"
        });
        if (resp.ok) {
          if (refresh) {
            await fetchRoutines();
            if (othelloState.activeRoutineId) {
                selectRoutine(othelloState.activeRoutineId);
            }
          } else {
             // Optimistic update
             const r = othelloState.routines.find(r => r.id === othelloState.activeRoutineId);
             if (r && r.steps) {
                 const s = r.steps.find(s => s.id === stepId);
                 if (s) Object.assign(s, patch);
             }
          }
        } else {
            throw new Error("Failed to update step");
        }
      } catch (err) { 
          console.error(err);
          showToast("Failed to update step", "error");
      }
    }

    async function deleteStep(stepId) {
      if (!confirm("Delete step?")) return;
      try {
        const resp = await fetch(`/api/steps/${stepId}`, { method: "DELETE", credentials: "include" });
        if (resp.ok) {
          await fetchRoutines();
          selectRoutine(othelloState.activeRoutineId);
        } else {
            throw new Error("Failed to delete step");
        }
      } catch (err) { 
          console.error(err);
          showToast("Failed to delete step", "error");
      }
    }

    async function duplicateRoutine(routineId) {
      const routine = othelloState.routines.find(r => r.id === routineId);
      if (!routine) return;
      const newTitle = routine.title + " (Copy)";
      try {
        const resp = await fetch(ROUTINES_API, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ title: newTitle, schedule_rule: routine.schedule_rule, enabled: false }),
          credentials: "include"
        });
        if (!resp.ok) throw new Error("Failed to create routine copy");
        const data = await resp.json();
        const newRoutine = data.routine;
        
        // Optimistic insert (without steps initially)
        othelloState.routines.push(newRoutine);
        renderRoutineList(othelloState.routines);
        
        // Copy steps
        if (routine.steps && routine.steps.length > 0) {
            for (const step of routine.steps) {
                await fetch(`${ROUTINES_API}/${newRoutine.id}/steps`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        title: step.title,
                        est_minutes: step.est_minutes,
                        energy: step.energy,
                        order_index: step.order_index,
                        tags: step.tags
                    }),
                    credentials: "include"
                });
            }
        }
        
        // Refresh and select
        await fetchRoutines();
        
        // Ensure we find the new routine in the fresh state
        const freshNewRoutine = othelloState.routines.find(r => r.id === newRoutine.id);
        if (freshNewRoutine) {
            othelloState.mobileEditorPinned = true;
            selectRoutine(freshNewRoutine.id, true);
            
            // Scroll into view
            setTimeout(() => {
                const item = document.querySelector(`.routine-list-item[data-routine-id="${freshNewRoutine.id}"]`);
                if (item) item.scrollIntoView({ behavior: "smooth", block: "center" });
            }, 100);
            
            showToast("Routine duplicated", "success");
            console.debug("routineDuplicated", { sourceId: routineId, newId: newRoutine.id });
        } else {
            showToast("Routine duplicated but not found in list", "warning");
        }
      } catch (err) {
        console.error("Duplicate routine error:", err);
        showToast("Failed to duplicate routine", "error");
      }
    }

    function moveStepLocal(routineId, stepId, direction) {
        const routine = othelloState.routines.find(r => r.id === routineId);
        if (!routine || !routine.steps) return;
        
        const idx = routine.steps.findIndex(s => s.id === stepId);
        if (idx === -1) return;
        const newIdx = idx + direction;
        if (newIdx < 0 || newIdx >= routine.steps.length) return;
        
        // Swap in local array
        const item = routine.steps.splice(idx, 1)[0];
        routine.steps.splice(newIdx, 0, item);
        
        // Re-render editor
        renderRoutineEditor(routine);
        
        // Show Save button
        const saveBtn = document.getElementById("routine-save-order-btn");
        if (saveBtn) {
            saveBtn.style.display = "inline-block";
            saveBtn.textContent = "Save Order";
            saveBtn.disabled = false;
        }
    }

    async function saveStepOrder(routineId) {
        const routine = othelloState.routines.find(r => r.id === routineId);
        if (!routine || !routine.steps) return;
        
        const saveBtn = document.getElementById("routine-save-order-btn");
        if (saveBtn) {
            saveBtn.textContent = "Saving...";
            saveBtn.disabled = true;
        }
        
        try {
            const updates = routine.steps.map((s, i) => {
                return updateStep(s.id, { order_index: i }, false);
            });
            await Promise.all(updates);
            if (saveBtn) {
                saveBtn.style.display = "none";
            }
            await fetchRoutines(); // Sync with server
            showToast("Order saved", "success");
        } catch (err) {
            console.error("Save order error:", err);
            showToast("Failed to save order", "error");
            if (saveBtn) {
                saveBtn.textContent = "Error";
                setTimeout(() => {
                    saveBtn.textContent = "Save Order";
                    saveBtn.disabled = false;
                }, 2000);
            }
        }
    }

    function routineStepsUrl(routineId) {
        return `${ROUTINES_API}/${encodeURIComponent(routineId)}/steps`;
    }

    async function addStepInline(routineId, title) {
      const url = routineStepsUrl(routineId);
      console.debug("createStep", { routineId, url });
      
      try {
        const resp = await fetch(url, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ title: title, est_minutes: 15, energy: "medium" }),
          credentials: "include"
        });
        
        console.debug("createStep response", { status: resp.status });

        if (resp.ok) {
          const data = await resp.json();
          
          // Optimistic update
          const routine = othelloState.routines.find(r => r.id === routineId);
          if (routine && data.step) {
              if (!routine.steps) routine.steps = [];
              routine.steps.push(data.step);
              // Sort by order_index if needed (usually new steps are last)
              routine.steps.sort((a, b) => (a.order_index || 0) - (b.order_index || 0));
              
              // Render via selectRoutine to ensure consistent state
              // But we can just call renderRoutineEditor if we are sure it's safe now.
              // The user requested: "Call selectRoutine(routineId, true) (NOT renderRoutineEditor(r) directly)."
              // This ensures we always render from othelloState.routines.
              selectRoutine(routineId, true);
              
              console.debug("stepCreated", { routineId, stepId: data.step.id, count: routine.steps.length });
          }

          // Reconcile
          await fetchRoutines();
          
          // Re-select to ensure fresh state
          const updatedRoutine = othelloState.routines.find(r => r.id === routineId);
          if (updatedRoutine) {
              selectRoutine(routineId, true);
          }
          return true;
        } else {
            let msg = "Failed to add step";
            try {
                const errData = await resp.json();
                console.error("createStep error data:", errData);
                if (errData.message) msg += `: ${errData.message}`;
                if (errData.request_id) msg += ` (Req: ${errData.request_id})`;
            } catch (e) {}
            throw new Error(msg);
        }
      } catch (err) { 
          console.error(err);
          showToast(err.message || "Failed to add step", "error");
          return false;
      }
    }

    // Preview Plan Logic
    const planPreviewOverlay = document.getElementById("plan-preview-overlay");
    const planPreviewClose = document.getElementById("plan-preview-close");
    const planPreviewContent = document.getElementById("plan-preview-content");
    const planPreviewBtn = document.getElementById("routine-preview-plan-btn");

    if (planPreviewBtn) {
        planPreviewBtn.onclick = async () => {
            if (planPreviewOverlay) planPreviewOverlay.style.display = "flex";
            if (planPreviewContent) planPreviewContent.innerHTML = '<div style="text-align: center; color: var(--text-soft); padding: 2rem;">Generating preview...</div>';
            
            try {
                const resp = await fetch("/api/today-plan", { credentials: "include" });
                if (!resp.ok) throw new Error("Failed to fetch plan");
                const data = await resp.json();
                renderPlanPreview(data.plan);
            } catch (err) {
                if (planPreviewContent) planPreviewContent.innerHTML = `<div class="planner-error">Failed to load plan: ${err.message}</div>`;
            }
        };
    }

    if (planPreviewClose) {
        planPreviewClose.onclick = () => {
            if (planPreviewOverlay) planPreviewOverlay.style.display = "none";
        };
    }

    function renderPlanPreview(plan) {
        if (!planPreviewContent) return;
        
        const sections = (plan && plan.sections) || {};
        const routines = sections.routines || [];
        const goalTasks = sections.goal_tasks || [];
        const optional = sections.optional || [];
        
        const allItems = [];
        
        // Flatten routines
        routines.forEach(r => {
            const rName = r.name || r.label || "Routine";
            (r.steps || []).forEach(s => {
                allItems.push({
                    title: s.label || s.title || "Step",
                    section: s.section_hint || r.section_hint || "any",
                    source: rName,
                    effort: s.approx_duration_min ? `${s.approx_duration_min}m` : "",
                    status: s.status || "planned"
                });
            });
        });
        
        // Goal tasks
        goalTasks.forEach(t => {
            allItems.push({
                title: t.label || t.description || "Task",
                section: t.section_hint || "any",
                source: "Goal Task",
                effort: t.effort || "",
                status: t.status || "planned"
            });
        });
        
        // Optional
        optional.forEach(o => {
            allItems.push({
                title: o.label || o.description || "Optional",
                section: "Optional",
                source: "Backlog",
                effort: o.effort || "",
                status: o.status || "planned"
            });
        });

        if (allItems.length === 0) {
            planPreviewContent.innerHTML = '<div class="planner-empty">No items in plan.</div>';
            return;
        }
        
        let html = `<div style="margin-bottom: 1rem; font-weight: 600; color: var(--accent);">Plan Date: ${plan.date || "Today"}</div>`;
        html += '<div class="planner-blocks">';
        
        // Group by section
        const grouped = {};
        const sectionOrder = ["morning", "afternoon", "evening", "night", "any", "Optional"];
        
        allItems.forEach(item => {
            let sec = item.section || "any";
            // Capitalize
            sec = sec.charAt(0).toUpperCase() + sec.slice(1);
            if (!grouped[sec]) grouped[sec] = [];
            grouped[sec].push(item);
        });
        
        // Sort sections
        const sortedKeys = Object.keys(grouped).sort((a, b) => {
            const ia = sectionOrder.indexOf(a.toLowerCase());
            const ib = sectionOrder.indexOf(b.toLowerCase());
            return (ia === -1 ? 99 : ia) - (ib === -1 ? 99 : ib);
        });
        
        for (const sec of sortedKeys) {
            const items = grouped[sec];
            html += `<div class="planner-block">
                <div class="planner-block__header"><div class="planner-block__title">${sec}</div></div>
                <div class="planner-steps">`;
            
            items.forEach(item => {
                html += `<div class="planner-step">
                    <div class="planner-step__body">
                        <div class="planner-step__label">${escapeHtml(item.title)}</div>
                        <div class="planner-step__meta" style="font-size: 0.75rem; color: var(--text-soft);">
                           ${item.source ? `<span style="opacity:0.8">${escapeHtml(item.source)}</span>` : ""}
                           ${item.effort ? ` • ${item.effort}` : ""}
                        </div>
                    </div>
                    <div class="planner-step__status">${item.status}</div>
                </div>`;
            });
            
            html += `</div></div>`;
        }
        html += '</div>';
        planPreviewContent.innerHTML = html;
    }

    // ===== INITIALIZATION =====
    // Boot sequence (bootUnified) handles auth + data fetches

// Phase 4: Hook scanner to existing status
(function() {
  const statusEl = document.getElementById('chat-status-text');
  // Use a more generic selector or id if available, but users instruction identified .chat-sheet in HTML
  // We need to wait for DOM maybe? No, script is at end of body.
  const chatSheet = document.querySelector('.chat-sheet');
  
  if (!statusEl || !chatSheet) {
    console.warn('[Othello UI] Scanner init skipped: elements not found.');
    return;
  }

  const observer = new MutationObserver(() => {
    const text = (statusEl.textContent || '').toLowerCase();
    // Signal 'is-thinking' if text contains active keywords and not just 'Online'/'Offline'
    // Keywords based on codebase grep: Thinking, Saving, Updating, Dismissing, Adding, Preparing
    const activeKeywords = ['thinking', 'working', 'saving', 'updating', 'dismissing', 'adding', 'preparing'];
    const isThinking = activeKeywords.some(k => text.includes(k));
    
    if (isThinking) {
      chatSheet.classList.add('is-thinking');
    } else {
      chatSheet.classList.remove('is-thinking');
    }
  });

  observer.observe(statusEl, { childList: true, characterData: true, subtree: true });
})();

