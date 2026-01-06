# Cycle Status: COMPLETE

## Todo Ledger
- [x] Phase 0: Evidence + Location
- [x] Phase 1: Server: Pending Draft Storage
- [x] Phase 2: Client: Draft Focus UI + Payload Wiring
- [x] Phase 3: Quality Gates
- [x] Phase 5: Runtime Fix (Fixed sendMessage event arg bug)
- [x] Audit Persona Sources
- [x] Trace Persona/Prompt Logic
- [x] Separate Chat/Work Prompts
- [x] Tighten Prompt Routing (Word Boundary + Ask Guard)
- [x] Add chat_persona prompt + wire to router
- [x] Fix IndentationError (Backend)
- [x] Fix setMode null crash (Frontend)
- [x] Ensure Mic Click Toggle (Frontend)

## Next Action
Stop and commit.

diff --git a/core/architect_brain.py b/core/architect_brain.py
index 9aa1707f..a56669e3 100644
--- a/core/architect_brain.py
+++ b/core/architect_brain.py
@@ -577,16 +577,6 @@ class Architect:
             
             # Build XML-only planning prompt
             system_prompt = load_prompt("strict_planning_xml")
-                "<category>health|career|finance|learning|relationship|other</category>\n"
-                "<plan_steps>\n"
-                "<step index=\"1\" status=\"pending\">First actionable step</step>\n"
-                "<step index=\"2\" status=\"pending\">Second actionable step</step>\n"
-                "<!-- Add more steps as needed -->\n"
-                "</plan_steps>\n"
-                "<next_action>The most important immediate next step</next_action>\n"
-                "</goal_update>\n\n"
-                "OUTPUT ONLY THE XML. NO OTHER TEXT.\n"
-            )
             
             # Build messages
             messages = [
diff --git a/static/othello.js b/static/othello.js
index 9ba7d838..6efeb39d 100644
--- a/static/othello.js
+++ b/static/othello.js
@@ -3906,8 +3906,11 @@
       if (!MODE_LABELS[mode]) return;
       othelloState.currentMode = mode;
       persistMode(mode);
-      modeLabel.textContent = MODE_LABELS[mode];
-      modeSubtitle.textContent = MODE_SUBTITLES[mode] || "";
+      
+      if (modeLabel) modeLabel.textContent = MODE_LABELS[mode];
+      else console.warn("[UI] setMode called but modeLabel missing");
+
+      if (modeSubtitle) modeSubtitle.textContent = MODE_SUBTITLES[mode] || "";
 
       if (modeOptions && modeOptions.length) {
         modeOptions.forEach(opt => {
