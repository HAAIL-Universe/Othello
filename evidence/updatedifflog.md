# Cycle Status: COMPLETE

## Todo Ledger
- [x] Phase 0: Evidence + Location
- [x] Phase 1: Server: Pending Draft Storage
- [x] Phase 2: Client: Draft Focus UI + Payload Wiring
- [x] Phase 3: Quality Gates
- [x] Phase 5: Runtime Fix (Fixed sendMessage event arg bug)
- [x] Phase 6: Draft Focus Polish (Fix 400 error, Unfocus behavior, Bubble cleanup)
- [x] Phase 7: Goal Draft Persistence & Edit Lane (Voice-first creation + editing)
- [x] Phase 8: Draft Visibility + Step Generation (Deterministic steps + UI preview)
- [x] Phase 9: Fix Generate Steps (0 steps) + Continuous Draft Editing
- [x] Phase 10: Fix Draft Steps Visibility (Ribbon Overlay + Reply Steps)

## Next Action
Stop and commit.

## Full Unified Diff

```diff
diff --git a/api.py b/api.py
index af9e2f5b..12345678 100644
--- a/api.py
+++ b/api.py
@@ -4282,19 +4282,23 @@ def handle_message():
                     
                     # Fallback Logic
                     steps = updated_payload.get("steps", [])
+                    if not isinstance(steps, list):
+                        steps = []
+                    
+                    # Sanitize steps
+                    steps = [str(s) for s in steps if s]
+                    
                     used_fallback = False
                     if not steps:
                         used_fallback = True
                         steps = [
                             "Define success criteria",
                             "Break down into sub-tasks",
                             f"Schedule daily work for {updated_payload.get('target_days', 7)} days",
                             "Execute and track progress",
                             "Review and adjust"
                         ]
-                        updated_payload["steps"] = steps
                         logging.warning(f"Used fallback steps for draft {draft_id}")
+                    
+                    updated_payload["steps"] = steps
 
                     # Update DB
                     updated_suggestion = suggestions_repository.update_suggestion_payload(user_id, draft_id, updated_payload)
                     
-                    steps_count = len(updated_payload.get("steps", []))
+                    steps_count = len(steps)
+                    reply_text = f"I've generated {steps_count} steps for your goal:"
+                    for i, s in enumerate(steps, 1):
+                        reply_text += f"\\n{i}) {s}"
                     
                     response = {
-                        "reply": f"I've generated {steps_count} steps for your goal.",
+                        "reply": reply_text,
                         "draft_context": {
                             "draft_id": draft_id,
                             "draft_type": "goal",
                             "source_message_id": client_message_id
                         },
                         "draft_payload": updated_payload,
-                        "request_id": request_id,
-                        "meta": {"used_fallback_steps": used_fallback}
+                        "request_id": request_id
                     }
+                    
+                    meta = response.setdefault("meta", {})
+                    meta["used_fallback_steps"] = used_fallback
+                    
                     return jsonify(response)
             except (ValueError, TypeError):
                 pass
diff --git a/static/othello.css b/static/othello.css
index 6a1d3cb6..12345678 100644
--- a/static/othello.css
+++ b/static/othello.css
@@ -1803,6 +1803,8 @@
     padding: 1rem;
     margin-bottom: 1rem;
     border-radius: 0 0 8px 8px;
+    max-height: 40vh;
+    overflow: auto;
 }
 .draft-preview h3 {
     margin: 0 0 0.5rem 0;
diff --git a/static/othello.js b/static/othello.js
index 65a36732..12345678 100644
--- a/static/othello.js
+++ b/static/othello.js
@@ -3729,12 +3729,22 @@
             return;
         }
         
+        // Dynamic offset for ribbon
+        if (focusRibbon && focusRibbon.classList.contains("visible")) {
+            const h = focusRibbon.offsetHeight || 0;
+            container.style.marginTop = h ? (h + 8) + "px" : "0px";
+        } else {
+            container.style.marginTop = "0px";
+        }
+        
         const p = othelloState.activeDraftPayload;
         const steps = p.steps || [];
         
+        console.debug("[Othello UI] Draft preview steps:", steps.length);
+        
         let html = `<h3>${p.title || "New Goal"}</h3>`;
         html += `<div class="draft-meta">Target: ${p.target_days || 7} days</div>`;
         
@@ -5792,12 +5802,13 @@
         if (data.draft_context) {
             othelloState.activeDraft = data.draft_context;
             localStorage.setItem("othello_active_draft", JSON.stringify(othelloState.activeDraft));
-            
-            if (data.draft_payload) {
-                othelloState.activeDraftPayload = data.draft_payload;
-                localStorage.setItem("othello_active_draft_payload", JSON.stringify(data.draft_payload));
-            }
-            
+        }
+
+        if (data.draft_payload) {
+            othelloState.activeDraftPayload = data.draft_payload;
+            localStorage.setItem("othello_active_draft_payload", JSON.stringify(data.draft_payload));
+            updateFocusRibbon();
+        } else if (data.draft_context) {
             updateFocusRibbon();
         }
```

## Evidence Bundle

### A) Backend Verification (verify_phase10.py)
Ran `verify_phase10.py` to test the "Generate Steps" reply format.
- **Input**: `ui_action="generate_draft_steps"` (Mock LLM failure to trigger fallback)
- **Output Reply**:
```
I've generated 5 steps for your goal:
1) Define success criteria
2) Break down into sub-tasks
3) Schedule daily work for 7 days
4) Execute and track progress
5) Review and adjust
```
- **Meta Check**: `used_fallback_steps` is True.
- **Result**: PASS

### B) Frontend Logic
- **Ribbon Overlay Fix**: `renderDraftPreview` now dynamically sets `marginTop` based on `focusRibbon.offsetHeight`.
- **Scrollable Preview**: Added `max-height: 40vh; overflow: auto;` to `.draft-preview`.
- **Payload Update**: Response handler now updates `activeDraftPayload` and calls `updateFocusRibbon` (which calls `renderDraftPreview`) whenever `draft_payload` is present, ensuring the UI stays in sync.

