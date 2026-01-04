Cycle Status: STOPPED:ENVIRONMENT_LIMITATION
Todo Ledger:
Planned: Establish focus lock signal; add secondary suggestion capture + badge UI; wire focus lock into goal/routine panels; tighten routine draft guard messaging; update evidence log; Fix server-side goal prompt injection; Fix "It isn't saved yet" default response
Completed: Implemented secondary suggestions storage and UI; wired focus lock to goal/routine handlers; updated routine draft guard to capture secondary suggestions; updated routine confirm label; FIXED ReferenceError: refreshSecondarySuggestionUI is not defined; Removed forced goal prompt injection in api.py; Implemented conservative goal intent gating; Made "It isn't saved yet" system instruction conditional
Remaining: Runtime verification (deploy-required)
Next Action: Deploy and verify that unrelated messages (e.g. "meet at 7") do not trigger "It isn't saved yet.", while explicit goal queries still get the correct "no active goal" response.

diff --git a/core/architect_brain.py b/core/architect_brain.py
index c6bdf8c0..c59038c7 100644
--- a/core/architect_brain.py
+++ b/core/architect_brain.py
@@ -260,14 +260,24 @@ class Architect:
 
             messages: List[Dict[str, str]] = [
                 {"role": "system", "content": system_prompt},
-                {
+            ]
+
+            if has_goal_context:
+                messages.append({
+                    "role": "system",
+                    "content": "Use ONLY the injected goal context for any claims about the active goal. Do not invent details."
+                })
+            else:
+                messages.append({
                     "role": "system",
                     "content": (
-                        "Only claim something is 'in the goal' if it appears in the injected "
-                        "goal_context. Otherwise say it isn't saved yet."
-                    ),
-                },
-            ]
+                        "Respond normally to the user. If (and only if) the user asks what their goal is, "
+                        "references a focused/saved goal, or asks whether something is already in the goal, "
+                        "explain that there is no active goal context available right now and offer a next action: "
+                        "create a goal, focus an existing goal, or open the Goals tab. "
+                        "Do NOT default to 'it isn't saved yet' for unrelated messages."
+                    )
+                })
 
             # Inject active goal context (if provided by API)
             if has_goal_context:
