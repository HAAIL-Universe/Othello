/* static/pingpong_mode.js */

(function () {
  "use strict";

  const DEFAULTS = {
    // Required (provided by init):
    getDuetBackgroundEl: null,  // () => HTMLElement
    isParked: null,             // () => boolean
    getUserRow: null,           // () => HTMLElement|null
    getAssistantRow: null,      // () => HTMLElement|null

    // Optional:
    excludeClosestSelectors: [], // selectors that, if matched via closest(), should NOT count as a tap
    disableControls: null,       // () => void
    enableControls: null,        // () => void

    // Gameplay:
    ballSpeedPxPerSec: 520,
    aiSmoothing: 0.12,
    tapWindowMs: 650
  };

  function clamp(v, min, max) {
    return Math.max(min, Math.min(max, v));
  }

  function nowMs() {
    return (typeof performance !== "undefined" && performance.now) ? performance.now() : Date.now();
  }

  class PingPongMode {
    constructor(cfg) {
      this.cfg = cfg;

      this.active = false;
      this.overlay = null;
      this.loading = null;
      this.exitHint = null;

      this.userPaddleWrap = null;
      this.aiPaddleWrap = null;

      this.ball = null;
      this.raf = null;

      this.lastFrame = 0;

      this.ballX = 0;
      this.ballY = 0;
      this.ballVX = 0;
      this.ballVY = 0;

      this.userPaddleX = 0;
      this.aiPaddleX = 0;

      this.dragging = false;

      this.tapCount = 0;
      this.tapT0 = 0;
      this.overlayTapCount = 0;
      this.overlayTapT0 = 0;

      this.boundOnTap = (e) => this.onTap(e);
    }

    init() {
      const bg = this.cfg.getDuetBackgroundEl && this.cfg.getDuetBackgroundEl();
      if (!bg) return;

      // Single listener: background gets triple-tap.
      bg.addEventListener("pointerdown", this.boundOnTap, { passive: true });
    }

    isActive() {
      return this.active;
    }

    onTap(e) {
      const bg = this.cfg.getDuetBackgroundEl && this.cfg.getDuetBackgroundEl();
      if (!bg) return;

      // Only accept taps from inside the configured background element.
      if (!bg.contains(e.target)) return;

      // Block taps originating from excluded zones (bubble/header/input etc.), using closest().
      if (Array.isArray(this.cfg.excludeClosestSelectors) && this.cfg.excludeClosestSelectors.length) {
        for (const sel of this.cfg.excludeClosestSelectors) {
          try {
            if (e.target && e.target.closest && e.target.closest(sel)) return;
          } catch (_) {
            // ignore invalid selector; integration should pass correct selectors
          }
        }
      }

      // Require parked state always.
      if (!(this.cfg.isParked && this.cfg.isParked())) return;

      const t = nowMs();
      if (this.tapCount === 0) {
        this.tapT0 = t;
        this.tapCount = 1;
        return;
      }

      // Reset if too slow
      if ((t - this.tapT0) > this.cfg.tapWindowMs) {
        this.tapT0 = t;
        this.tapCount = 1;
        return;
      }

      this.tapCount += 1;

      if (this.tapCount >= 3) {
        this.tapCount = 0;
        if (this.active) this.stop();
        else this.start();
      }
    }

    overlayTapMaybeExit() {
      if (!this.active) return false;

      const t = nowMs();
      if (this.overlayTapCount === 0) {
        this.overlayTapT0 = t;
        this.overlayTapCount = 1;
        return false;
      }

      if ((t - this.overlayTapT0) > this.cfg.tapWindowMs) {
        this.overlayTapT0 = t;
        this.overlayTapCount = 1;
        return false;
      }

      this.overlayTapCount += 1;

      if (this.overlayTapCount >= 3) {
        this.overlayTapCount = 0;
        this.stop();
        return true;
      }

      return false;
    }

    start() {
      if (this.active) return;

      const bg = this.cfg.getDuetBackgroundEl && this.cfg.getDuetBackgroundEl();
      if (!bg) return;
      if (!(this.cfg.isParked && this.cfg.isParked())) return;

      const userRow = this.cfg.getUserRow && this.cfg.getUserRow();
      const aiRow = this.cfg.getAssistantRow && this.cfg.getAssistantRow();
      if (!userRow || !aiRow) return;

      this.active = true;

      const chatView = this.cfg.getDuetBackgroundEl && this.cfg.getDuetBackgroundEl();
      if (chatView) chatView.classList.add("pp-parked-boost");

      // Freeze controls (optional hooks from integration).
      try { this.cfg.disableControls && this.cfg.disableControls(); } catch (_) {}

      this.overlay = document.createElement("div");
      this.overlay.className = "pp-overlay";

      // capture all pointer events above chat
      this.overlay.addEventListener("pointerdown", (e) => this.onOverlayPointerDown(e), { passive: false });
      this.overlay.addEventListener("pointermove", (e) => this.onOverlayPointerMove(e), { passive: false });
      this.overlay.addEventListener("pointerup", () => this.onOverlayPointerUp(), { passive: true });
      this.overlay.addEventListener("pointercancel", () => this.onOverlayPointerUp(), { passive: true });

      // Add a faint hint (optional, no interaction)
      this.exitHint = document.createElement("div");
      this.exitHint.className = "pp-exit-hint";
      this.exitHint.textContent = "Triple tap to exit";
      this.overlay.appendChild(this.exitHint);

      // Loading bar at center (stops once paddles placed + ball launched)
      this.loading = document.createElement("div");
      this.loading.className = "pp-loading";
      this.overlay.appendChild(this.loading);

      // Clone paddles
      this.aiPaddleWrap = this.clonePaddle(aiRow, true);
      this.aiPaddleWrap.classList.add("pp-top");
      this.overlay.appendChild(this.aiPaddleWrap);

      this.userPaddleWrap = this.clonePaddle(userRow, false);
      this.userPaddleWrap.classList.add("pp-bottom");
      this.overlay.appendChild(this.userPaddleWrap);

      // Ball
      this.ball = document.createElement("div");
      this.ball.className = "pp-ball";
      this.overlay.appendChild(this.ball);

      document.body.appendChild(this.overlay);

      // Align paddles vertically with their source message rows.
      const aiRowRect = aiRow.getBoundingClientRect();
      const userRowRect = userRow.getBoundingClientRect();
      if (this.aiPaddleWrap) {
        this.aiPaddleWrap.style.top = Math.round(aiRowRect.top) + "px";
      }
      if (this.userPaddleWrap) {
        const paddleH = this.userPaddleWrap.getBoundingClientRect().height || 22;
        const userOffset = 6;
        this.userPaddleWrap.style.top = Math.round(userRowRect.bottom - paddleH + userOffset) + "px";
        this.userPaddleWrap.style.bottom = "auto";
      }

      // Layout: place paddles and spawn ball from center
      const w = window.innerWidth;
      const h = window.innerHeight;

      this.userPaddleX = w / 2;
      this.aiPaddleX = w / 2;

      this.ballX = w / 2;
      this.ballY = h / 2;

      // Initial velocity: toward user (down)
      const speed = this.cfg.ballSpeedPxPerSec;
      this.ballVX = speed * 0.35;
      this.ballVY = speed * 0.94;

      // Small delay to let transform “feel” like it completes, then stop loading and start loop
      setTimeout(() => {
        if (!this.active) return;
        if (this.loading && this.loading.parentNode) this.loading.parentNode.removeChild(this.loading);
        this.loading = null;

        this.lastFrame = nowMs();
        this.raf = requestAnimationFrame(() => this.tick());
      }, 420);
    }

    stop() {
      if (!this.active) return;

      this.active = false;

      if (this.raf) cancelAnimationFrame(this.raf);
      this.raf = null;

      this.dragging = false;

      // Remove overlay
      if (this.overlay && this.overlay.parentNode) {
        this.overlay.parentNode.removeChild(this.overlay);
      }

      this.overlay = null;
      this.loading = null;
      this.exitHint = null;

      this.userPaddleWrap = null;
      this.aiPaddleWrap = null;
      this.ball = null;

      const chatView = this.cfg.getDuetBackgroundEl && this.cfg.getDuetBackgroundEl();
      if (chatView) chatView.classList.remove("pp-parked-boost");

      try { this.cfg.enableControls && this.cfg.enableControls(); } catch (_) {}
    }

    clonePaddle(rowEl, isAi) {
      const wrap = document.createElement("div");
      wrap.className = "pp-paddle-row";

      // Clone the msg-row so existing gradients/borders remain (bubble styles preserved)
      const clone = rowEl.cloneNode(true);

      // Force only the bubble shell to display as a bar
      const bubble = clone.querySelector && clone.querySelector(".bubble");
      if (bubble) {
        // Remove text content without altering bubble shell styles
        bubble.innerHTML = "";
        wrap.__ppBubble = bubble;
      }

      wrap.appendChild(clone);
      wrap.dataset.pp = isAi ? "ai" : "user";
      return wrap;
    }

    onOverlayPointerDown(e) {
      if (this.overlayTapMaybeExit()) return;
      e.preventDefault();
      this.dragging = true;
      this.setUserPaddleToPointer(e);
    }

    onOverlayPointerMove(e) {
      if (!this.dragging) return;
      e.preventDefault();
      this.setUserPaddleToPointer(e);
    }

    onOverlayPointerUp() {
      this.dragging = false;
    }

    setUserPaddleToPointer(e) {
      const x = (e && typeof e.clientX === "number") ? e.clientX : (window.innerWidth / 2);
      this.userPaddleX = x;
    }

    tick() {
      if (!this.active) return;

      const t = nowMs();
      const dt = clamp((t - this.lastFrame) / 1000, 0.0, 0.04);
      this.lastFrame = t;

      const w = window.innerWidth;
      const h = window.innerHeight;

      const ballR = 6;

      // Get paddle bounds from rendered nodes
      const aiBoundsEl = this.aiPaddleWrap.__ppBubble || this.aiPaddleWrap;
      const userBoundsEl = this.userPaddleWrap.__ppBubble || this.userPaddleWrap;
      const aiRect = aiBoundsEl.getBoundingClientRect();
      const userRect = userBoundsEl.getBoundingClientRect();

      // Move AI paddle toward ball x
      const targetAiX = this.ballX;
      this.aiPaddleX = this.aiPaddleX + (targetAiX - this.aiPaddleX) * this.cfg.aiSmoothing;

      // Clamp paddles within viewport
      const paddleW = userRect.width;
      const minX = paddleW / 2 + 8;
      const maxX = w - paddleW / 2 - 8;

      this.userPaddleX = clamp(this.userPaddleX, minX, maxX);
      this.aiPaddleX = clamp(this.aiPaddleX, minX, maxX);

      // Apply paddle positions
      this.aiPaddleWrap.style.left = this.aiPaddleX + "px";
      this.aiPaddleWrap.style.transform = "translateX(-50%)";
      this.userPaddleWrap.style.left = this.userPaddleX + "px";
      this.userPaddleWrap.style.transform = "translateX(-50%)";

      // Move ball
      this.ballX += this.ballVX * dt;
      this.ballY += this.ballVY * dt;

      // Wall collisions (left/right)
      if (this.ballX - ballR <= 0) {
        this.ballX = ballR;
        this.ballVX *= -1;
      } else if (this.ballX + ballR >= w) {
        this.ballX = w - ballR;
        this.ballVX *= -1;
      }

      // Top collision via AI paddle
      if (this.ballVY < 0 && (this.ballY - ballR) <= (aiRect.bottom)) {
        const hit = this.checkPaddleHit(aiRect);
        if (hit) {
          this.ballY = aiRect.bottom + ballR + 1;
          this.ballVY = Math.abs(this.ballVY);
          this.ballVX += hit * 180;
        }
      }

      // Bottom collision via User paddle
      if (this.ballVY > 0 && (this.ballY + ballR) >= (userRect.top)) {
        const hit = this.checkPaddleHit(userRect);
        if (hit !== null) {
          this.ballY = userRect.top - ballR - 1;
          this.ballVY = -Math.abs(this.ballVY);
          this.ballVX += hit * 220;
        }
      }

      // Miss condition (ball past bottom or top)
      if (this.ballY - ballR > h + 20 || (this.ballY + ballR) < -20) {
        this.stop();
        return;
      }

      // Apply ball position
      this.ball.style.left = (this.ballX - ballR) + "px";
      this.ball.style.top = (this.ballY - ballR) + "px";

      this.raf = requestAnimationFrame(() => this.tick());
    }

    checkPaddleHit(rect) {
      const ballR = 6;
      const withinX = (this.ballX + ballR) >= rect.left && (this.ballX - ballR) <= rect.right;
      const withinY = (this.ballY + ballR) >= rect.top && (this.ballY - ballR) <= rect.bottom;

      if (!(withinX && withinY)) return null;

      // normalized hit position [-1..1] (left..right)
      const mid = (rect.left + rect.right) / 2;
      const half = (rect.right - rect.left) / 2;
      if (half <= 1) return 0;
      return clamp((this.ballX - mid) / half, -1, 1);
    }
  }

  let INSTANCE = null;

  window.OthelloPingPong = {
    init: function (config) {
      const cfg = Object.assign({}, DEFAULTS, config || {});
      if (!cfg.getDuetBackgroundEl || !cfg.isParked || !cfg.getUserRow || !cfg.getAssistantRow) {
        return;
      }
      INSTANCE = new PingPongMode(cfg);
      INSTANCE.init();
    },
    start: function () {
      if (INSTANCE) INSTANCE.start();
    },
    stop: function () {
      if (INSTANCE) INSTANCE.stop();
    },
    isActive: function () {
      return INSTANCE ? INSTANCE.isActive() : false;
    }
  };
})();
