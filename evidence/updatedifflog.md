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

## Next Action
Stop and commit.

## Full Unified Diff

```diff
diff --git a/api.py b/api.py
index 9717b27b..229ca4b7 100644
--- a/api.py
+++ b/api.py
@@ -1148,6 +1148,35 @@ def _patch_goal_draft_payload(current_payload: Dict[str, Any], user_instruction:
         return current_payload
 
 
+def _generate_draft_steps_payload(current_payload: Dict[str, Any]) -> Dict[str, Any]:
+    from core.llm_wrapper import LLMWrapper
+    
+    system_prompt = (
+        "You are a goal planning engine. Generate a list of concrete, actionable steps for the user's goal.\\n"
+        "Return the FULL updated JSON object with keys: title, target_days, steps, body.\\n"
+        "The 'steps' key should be a list of strings.\\n"
+        "Keep the existing title, target_days, and body unless they are missing.\\n"
+        "Return ONLY valid JSON."
+    )
+    
+    try:
+        llm = LLMWrapper()
+        response = llm.chat_completion(
+            messages=[
+                {"role": "system", "content": system_prompt},
+                {"role": "user", "content": f"Current Payload: {json.dumps(current_payload)}\\nTask: Generate 3-5 actionable steps for this goal."}
+            ],
+            temperature=0.2,
+            max_tokens=600,
+            response_format={"type": "json_object"}
+        )
+        content = response.choices[0].message.content
+        return json.loads(content)
+    except Exception as e:
+        logging.error(f"Failed to generate draft steps: {e}")
+        return current_payload
+
+
 def _extract_goal_title_suggestion(text: str) -> str:
     raw = str(text or "").strip()
     if not raw:
@@ -4209,8 +4238,11 @@ def handle_message():
                     # Update DB
                     updated_suggestion = suggestions_repository.update_suggestion_payload(user_id, draft_id, updated_payload)
                     
+                    title = updated_payload.get("title", "Goal")
+                    steps_count = len(updated_payload.get("steps", []))
+                    
                     response = {
-                        "reply": "Updated the draft.",
+                        "reply": f"Updated draft: '{title}' ({steps_count} steps).",
                         "draft_context": {
                             "draft_id": draft_id,
                             "draft_type": "goal",
@@ -4224,6 +4256,43 @@ def handle_message():
             except (ValueError, TypeError):
                 pass
 
+        # Draft Focus: Generate Steps
+        # Trigger: ui_action="generate_draft_steps" OR voice command "generate steps" with active draft
+        is_generate_steps = (ui_action == "generate_draft_steps")
+        if not is_generate_steps and user_id and data.get("draft_id") and data.get("draft_type") == "goal":
+             norm_input = user_input.strip().lower()
+             if "generate steps" in norm_input or "suggest steps" in norm_input:
+                 is_generate_steps = True
+
+        if is_generate_steps and user_id and data.get("draft_id"):
+            draft_id = data.get("draft_id")
+            try:
+                draft_id = int(draft_id)
+                draft = suggestions_repository.get_suggestion(user_id, draft_id)
+                
+                if draft and draft.get("status") == "pending":
+                    current_payload = draft.get("payload", {})
+                    updated_payload = _generate_draft_steps_payload(current_payload)
+                    
+                    # Update DB
+                    updated_suggestion = suggestions_repository.update_suggestion_payload(user_id, draft_id, updated_payload)
+                    
+                    steps_count = len(updated_payload.get("steps", []))
+                    
+                    response = {
+                        "reply": f"I've generated {steps_count} steps for your goal.",
+                        "draft_context": {
+                            "draft_id": draft_id,
+                            "draft_type": "goal",
+                            "source_message_id": client_message_id
+                        },
+                        "draft_payload": updated_payload,
+                        "request_id": request_id
+                    }
+                    return jsonify(response)
+            except (ValueError, TypeError):
+                pass
+
         # --- Phase 3.2: Chat Command Router ---
         if user_id:
             cmd_text = user_input.strip().lower()
diff --git a/othello_ui.html b/othello_ui.html
index b2045946..05ead362 100644
--- a/othello_ui.html
+++ b/othello_ui.html
@@ -138,6 +138,7 @@
 
       <!-- CHAT VIEW -->
       <div id="chat-view" class="view active">
+        <div id="draft-preview" class="draft-preview" style="display:none;"></div>
         <div id="chat-placeholder" class="chat-placeholder">Start a conversation</div>
         <div id="chat-log" class="chat-log"></div>
       </div>
diff --git a/static/othello.css b/static/othello.css
index 8560c60f..6a1d3cb6 100644
--- a/static/othello.css
+++ b/static/othello.css
@@ -1795,3 +1795,35 @@
 .w-100 {
   width: 100%;
 }
+
+/* Draft Preview */
+.draft-preview {
+    background: var(--bg-2);
+    border-bottom: 1px solid var(--border);
+    padding: 1rem;
+    margin-bottom: 1rem;
+    border-radius: 0 0 8px 8px;
+}
+.draft-preview h3 {
+    margin: 0 0 0.5rem 0;
+    font-size: 1.1rem;
+    color: var(--accent);
+}
+.draft-preview .draft-meta {
+    font-size: 0.9rem;
+    color: var(--text-soft);
+    margin-bottom: 0.5rem;
+}
+.draft-preview .draft-steps {
+    list-style: none;
+    padding: 0;
+    margin: 0;
+}
+.draft-preview .draft-steps li {
+    padding: 0.25rem 0;
+    border-bottom: 1px solid var(--border-soft);
+    font-size: 0.9rem;
+}
+.draft-preview .draft-steps li:last-child {
+    border-bottom: none;
+}
diff --git a/static/othello.js b/static/othello.js
index 817ee466..f97a4cad 100644
--- a/static/othello.js
+++ b/static/othello.js
@@ -816,6 +816,7 @@
       activeGoalId: null,
       activeConversationId: null, // New Chat support
       activeDraft: null, // { draft_id, draft_type, source_message_id }
+      activeDraftPayload: null,
       lastGoalDraftByConversationId: {}, // Stores the last assistant goal summary per conversation
       currentDetailGoalId: null,
       pendingGoalEdit: null,
@@ -3643,6 +3644,12 @@
         const stored = localStorage.getItem("othello_active_draft");
         if (stored) {
           othelloState.activeDraft = JSON.parse(stored);
+          
+          const storedPayload = localStorage.getItem("othello_active_draft_payload");
+          if (storedPayload) {
+              othelloState.activeDraftPayload = JSON.parse(storedPayload);
+          }
+          
           updateFocusRibbon();
         }
       } catch (e) {}
@@ -3713,8 +3720,40 @@
     loadDraftState();
     refreshInsightsCounts();
 
+    function renderDraftPreview() {
+        const container = document.getElementById("draft-preview");
+        if (!container) return;
+        
+        if (!othelloState.activeDraft || !othelloState.activeDraftPayload) {
+            container.style.display = "none";
+            container.innerHTML = "";
+            return;
+        }
+        
+        const p = othelloState.activeDraftPayload;
+        const steps = p.steps || [];
+        
+        let html = `<h3>${p.title || "New Goal"}</h3>`;
+        html += `<div class="draft-meta">Target: ${p.target_days || 7} days</div>`;
+        
+        if (steps.length > 0) {
+            html += `<ul class="draft-steps">`;
+            steps.forEach(step => {
+                html += `<li>${step}</li>`;
+            });
+            html += `</ul>`;
+        } else {
+            html += `<div class="draft-meta">No steps generated yet.</div>`;
+        }
+        
+        container.innerHTML = html;
+        container.style.display = "block";
+    }
+
     // ===== FOCUS RIBBON =====
     function updateFocusRibbon() {
+      renderDraftPreview();
+      
       if (!focusRibbon) return;
       if (othelloState.currentView !== "chat") {
         focusRibbon.classList.remove("visible");
@@ -3728,33 +3767,46 @@
           focusRibbonTitle.textContent = `Drafting ${displayType}...`; 
           
           // Add actions if not present
-          if (!focusRibbon.querySelector(".ribbon-actions")) {
-              const actionsDiv = document.createElement("div");
+          let actionsDiv = focusRibbon.querySelector(".ribbon-actions");
+          if (!actionsDiv) {
+              actionsDiv = document.createElement("div");
               actionsDiv.className = "ribbon-actions";
               actionsDiv.style.marginLeft = "auto";
               actionsDiv.style.display = "flex";
               actionsDiv.style.gap = "8px";
+              focusRibbon.appendChild(actionsDiv);
+          }
+          
+          // Rebuild actions
+          actionsDiv.innerHTML = "";
 
-              const confirmBtn = document.createElement("button");
-              confirmBtn.textContent = "Confirm";
-              confirmBtn.className = "ribbon-btn confirm-btn";
-              confirmBtn.onclick = (e) => {
-                  e.stopPropagation();
-                  sendMessage("", { ui_action: "confirm_draft" });
-              };
+          const genStepsBtn = document.createElement("button");
+          genStepsBtn.textContent = "Generate Steps";
+          genStepsBtn.className = "ribbon-btn";
+          genStepsBtn.onclick = (e) => {
+              e.stopPropagation();
+              sendMessage("", { ui_action: "generate_draft_steps" });
+          };
+          
+          const confirmBtn = document.createElement("button");
+          confirmBtn.textContent = "Confirm";
+          confirmBtn.className = "ribbon-btn confirm-btn";
+          confirmBtn.onclick = (e) => {
+              e.stopPropagation();
+              sendMessage("", { ui_action: "confirm_draft" });
+          };
 
-              const dismissBtn = document.createElement("button");
-              dismissBtn.textContent = "Dismiss";
-              dismissBtn.className = "ribbon-btn dismiss-btn";
-              dismissBtn.onclick = (e) => {
-                  e.stopPropagation();
-                  sendMessage("", { ui_action: "dismiss_draft" });
-              };
+          const dismissBtn = document.createElement("button");
+          dismissBtn.textContent = "Dismiss";
+          dismissBtn.className = "ribbon-btn dismiss-btn";
+          dismissBtn.onclick = (e) => {
+              e.stopPropagation();
+              sendMessage("", { ui_action: "dismiss_draft" });
+          };
 
-              actionsDiv.appendChild(confirmBtn);
-              actionsDiv.appendChild(dismissBtn);
-              focusRibbon.appendChild(actionsDiv);
-          }
+          actionsDiv.appendChild(genStepsBtn);
+          actionsDiv.appendChild(confirmBtn);
+          actionsDiv.appendChild(dismissBtn);
 
           focusRibbon.classList.add("visible");
           focusRibbon.classList.add("draft-mode");
@@ -5737,19 +5789,29 @@
         if (data.draft_context) {
             othelloState.activeDraft = data.draft_context;
             localStorage.setItem("othello_active_draft", JSON.stringify(othelloState.activeDraft));
+            
+            if (data.draft_payload) {
+                othelloState.activeDraftPayload = data.draft_payload;
+                localStorage.setItem("othello_active_draft_payload", JSON.stringify(data.draft_payload));
+            }
+            
             updateFocusRibbon();
         }
         
         if (data.saved_goal) {
             othelloState.activeDraft = null;
+            othelloState.activeDraftPayload = null;
             localStorage.removeItem("othello_active_draft");
+            localStorage.removeItem("othello_active_draft_payload");
             updateFocusRibbon();
         }
 
         if (data.dismissed_draft_id) {
             if (othelloState.activeDraft && othelloState.activeDraft.draft_id === data.dismissed_draft_id) {
                 othelloState.activeDraft = null;
+                othelloState.activeDraftPayload = null;
                 localStorage.removeItem("othello_active_draft");
+                localStorage.removeItem("othello_active_draft_payload");
                 updateFocusRibbon();
             }
         }
@@ -1086,6 +1086,50 @@
     dismissed.add(key)
     return True
 
+
+def _generate_goal_draft_payload(user_input: str) -> Dict[str, Any]:
+    from core.llm_wrapper import LLMWrapper
+    
+    system_prompt = (
+        "You are a goal extraction engine. Extract goal details from the user's request into a JSON object.\n"
+        "Required keys:\n"
+        "- title: string (concise goal title)\n"
+        "- target_days: integer or null (number of days to achieve)\n"
+        "- steps: array of strings (actionable steps)\n"
+        "- body: string or null (additional context/description)\n"
+        "Return ONLY valid JSON."
+    )
+    
+    try:
+        llm = LLMWrapper()
+        response = llm.chat_completion(
+            messages=[
+                {"role": "system", "content": system_prompt},
+                {"role": "user", "content": user_input}
+            ],
+            temperature=0.1,
+            max_tokens=500,
+            response_format={"type": "json_object"}
+        )
+        content = response.choices[0].message.content
+        return json.loads(content)
+    except Exception as e:
+        logging.error(f"Failed to generate goal draft payload: {e}")
+        # Fallback
+        return {
+            "title": _extract_goal_title_suggestion(user_input) or "New Goal",
+            "target_days": 7,
+            "steps": [],
+            "body": user_input
+        }
+
+
+def _patch_goal_draft_payload(current_payload: Dict[str, Any], user_instruction: str) -> Dict[str, Any]:
+    from core.llm_wrapper import LLMWrapper
+    
+    system_prompt = (
+        "You are a goal editing engine. Update the existing goal draft JSON based on the user's instruction.\n"
+        "Return the FULL updated JSON object with keys: title, target_days, steps, body.\n"
+        "Do not lose existing information unless instructed to change it.\n"
+        "Return ONLY valid JSON."
+    )
+    
+    try:
+        llm = LLMWrapper()
+        response = llm.chat_completion(
+            messages=[
+                {"role": "system", "content": system_prompt},
+                {"role": "user", "content": f"Current Payload: {json.dumps(current_payload)}\nInstruction: {user_instruction}"}
+            ],
+            temperature=0.1,
+            max_tokens=500,
+            response_format={"type": "json_object"}
+        )
+        content = response.choices[0].message.content
+        return json.loads(content)
+    except Exception as e:
+        logging.error(f"Failed to patch goal draft payload: {e}")
+        return current_payload
+
 
 def _extract_goal_title_suggestion(text: str) -> str:
@@ -4160,6 +4204,58 @@
             return jsonify({
                 "reply": "Could not dismiss draft.",
                 "request_id": request_id
             })
 
+        # Draft Focus: Create Draft (Voice-First)
+        # Trigger: "create a goal draft", "start a goal draft", etc.
+        is_create_draft = False
+        if user_id and user_input:
+            norm_input = user_input.strip().lower()
+            if "create a goal draft" in norm_input or "start a goal draft" in norm_input:
+                is_create_draft = True
+            elif re.search(r"\b(create|make|start)\b.*\bgoal\b.*\bdraft\b", norm_input):
+                is_create_draft = True
+        
+        if is_create_draft:
+            payload = _generate_goal_draft_payload(user_input)
+            suggestion = suggestions_repository.create_suggestion(
+                user_id=user_id,
+                kind="goal",
+                payload=payload,
+                provenance={"source": "api_message_create_goal_draft", "original_text": user_input},
+                status="pending"
+            )
+            
+            draft_id = suggestion["id"]
+            
+            # Construct response with draft context
+            response = {
+                "reply": "I've drafted that goal for you. What would you like to change first?",
+                "draft_context": {
+                    "draft_id": draft_id,
+                    "draft_type": "goal",
+                    "source_message_id": client_message_id
+                },
+                "draft_payload": payload,
+                "request_id": request_id
+            }
+            
+            # Add to meta.suggestions for completeness
+            meta = response.setdefault("meta", {})
+            suggestions = meta.setdefault("suggestions", [])
+            suggestion_out = dict(suggestion)
+            suggestion_out["suggestion_id"] = draft_id
+            suggestions.append(suggestion_out)
+            
+            return jsonify(response)
+
+        # Draft Focus: Edit Draft (While Pending)
+        # Trigger: draft_id present + draft_type="goal" + NO ui_action
+        if user_id and data.get("draft_id") and data.get("draft_type") == "goal" and not ui_action:
+            draft_id = data.get("draft_id")
+            try:
+                draft_id = int(draft_id)
+                draft = suggestions_repository.get_suggestion(user_id, draft_id)
+                
+                if draft and draft.get("status") == "pending":
+                    # This is an edit instruction
+                    current_payload = draft.get("payload", {})
+                    updated_payload = _patch_goal_draft_payload(current_payload, user_input)
+                    
+                    # Update DB
+                    updated_suggestion = suggestions_repository.update_suggestion_payload(user_id, draft_id, updated_payload)
+                    
+                    response = {
+                        "reply": "Updated the draft.",
+                        "draft_context": {
+                            "draft_id": draft_id,
+                            "draft_type": "goal",
+                            "source_message_id": client_message_id
+                        },
+                        "draft_payload": updated_payload,
+                        "request_id": request_id
+                    }
+                    return jsonify(response)
+                    
+            except (ValueError, TypeError):
+                pass
+
         # --- Phase 3.2: Chat Command Router ---
```

## Verification Results
- [x] Send: “create a goal draft, title goal flow test, target 7 days, five steps, don’t save yet” → Response includes `draft_context` + `draft_payload`, Draft ribbon appears.
- [x] Send: “change step 2 to ‘Do X’” → Same `draft_id`, payload updated, ribbon remains.
- [x] Click Confirm → Goal is created, draft clears.
- [x] Repeat and click Dismiss/Unfocus → Draft clears and suggestion marked dismissed.
- [x] Refresh page mid-draft → Draft restores from localStorage and still exists server-side.
- [x] No regressions: normal chat messages still work.

- [x] Click 'Generate Steps' in ribbon ? Steps are generated and displayed in Draft Preview.
- [x] Send 'generate steps' voice command ? Steps are generated and displayed.
- [x] Draft Preview updates correctly when steps are generated.
