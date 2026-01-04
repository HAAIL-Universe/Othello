Cycle Status: COMPLETE
Todo Ledger:
Planned: Establish focus lock signal; add secondary suggestion capture + badge UI; wire focus lock into goal/routine panels; tighten routine draft guard messaging; update evidence log; Fix server-side goal prompt injection
Completed: Implemented secondary suggestions storage and UI; wired focus lock to goal/routine handlers; updated routine draft guard to capture secondary suggestions; updated routine confirm label; FIXED ReferenceError: refreshSecondarySuggestionUI is not defined; Removed forced goal prompt injection in api.py; Implemented conservative goal intent gating
Remaining: Runtime verification (deploy-required)
Next Action: Deploy and verify that "Want this saved as a goal..." no longer appears, and that goal suggestions appear as badges only when explicitly requested.

diff --git a/api.py b/api.py
index 0c90cd8c..c9338b7c 100644
--- a/api.py
+++ b/api.py
@@ -1325,6 +1325,47 @@ def _load_companion_context(
     return messages
 
 
+def should_offer_goal_intent(text: str) -> bool:
+    if not text:
+        return False
+    t = text.strip().lower()
+    if not t:
+        return False
+
+    # Question check
+    if "?" in t:
+        return False
+    question_words = ("what", "why", "how", "when", "where", "who", "can", "should", "do", "is", "are")
+    if any(t.startswith(w + " ") or t == w for w in question_words):
+        return False
+
+    # Routine signals
+    routine_signals = (
+        "every day", "each day", "daily", "weekly", "remind me", "alarm",
+        "routine", "habit", "meet at"
+    )
+    if any(s in t for s in routine_signals):
+        return False
+
+    # Time signals
+    if re.search(r"\b([01]?\d|2[0-3]):[0-5]\d\b", t):
+        return False
+    if re.search(r"\b([1-9]|1[0-2])\s*(a\.?m\.?|p\.?m\.?)\b", t):
+        return False
+    if re.search(r"\b(at|around|by)\s+([1-9]|1[0-2])\b", t):
+        return False
+
+    # Explicit goal phrasing
+    explicit_phrases = (
+        "goal:", "my goal is", "i want to", "i am going to", "i'm going to",
+        "i will", "new goal", "working towards", "need to achieve"
+    )
+    has_explicit = any(p in t for p in explicit_phrases)
+
+    # Return True only when explicit goal phrasing is present AND none of the disqualifiers matched.
+    return has_explicit
+
+
 def _goal_intent_prompt(active_goal_id: Optional[int]) -> str:
     if active_goal_id is not None:
         return "Want this saved as a goal, added to your focused goal, or broken into steps?"
@@ -6072,22 +6113,25 @@ def handle_message():
             if not isinstance(agent_status, dict):
                 agent_status = {}
 
-            if _is_placeholder_reply(agentic_reply) or (
-                goal_intent_detected and not (agentic_reply or "").strip()
-            ):
+            if not (agentic_reply or "").strip():
                 if effective_channel == "companion":
-                    agentic_reply = _goal_intent_prompt(active_goal.get("id"))
-                    if not goal_intent_suggestion:
-                        goal_intent_suggestion = _build_goal_intent_fallback(
-                            user_input,
-                            client_message_id,
-                            user_id,
-                        )
-                        goal_intent_detected = bool(goal_intent_suggestion)
+                    agentic_reply = "Noted."
                 else:
                     agentic_reply = "Please share a bit more detail so I can help you plan."
                 reply_source = "fallback"
 
+            if should_offer_goal_intent(user_input):
+                if not goal_intent_suggestion:
+                    goal_intent_suggestion = _build_goal_intent_fallback(
+                        user_input,
+                        client_message_id,
+                        user_id,
+                    )
+                goal_intent_detected = bool(goal_intent_suggestion)
+            else:
+                goal_intent_suggestion = None
+                goal_intent_detected = False
+
         if active_goal is None:
             logger.info("API: No active goal for this message; falling back to casual mode")
             reply_source = "fallback"
@@ -6137,22 +6181,25 @@ def handle_message():
             if not isinstance(agent_status, dict):
                 agent_status = {}
 
-            if _is_placeholder_reply(agentic_reply) or (
-                goal_intent_detected and not (agentic_reply or "").strip()
-            ):
+            if not (agentic_reply or "").strip():
                 if effective_channel == "companion":
-                    agentic_reply = _goal_intent_prompt(None)
-                    if not goal_intent_suggestion:
-                        goal_intent_suggestion = _build_goal_intent_fallback(
-                            user_input,
-                            client_message_id,
-                            user_id,
-                        )
-                        goal_intent_detected = bool(goal_intent_suggestion)
+                    agentic_reply = "Noted."
                 else:
                     agentic_reply = "Please share a bit more detail so I can help you plan."
                 reply_source = "fallback"
 
+            if should_offer_goal_intent(user_input):
+                if not goal_intent_suggestion:
+                    goal_intent_suggestion = _build_goal_intent_fallback(
+                        user_input,
+                        client_message_id,
+                        user_id,
+                    )
+                goal_intent_detected = bool(goal_intent_suggestion)
+            else:
+                goal_intent_suggestion = None
+                goal_intent_detected = False
+
             response = {
                 "reply": agentic_reply,
                 "agent_status": agent_status,
