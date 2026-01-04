Cycle Status: COMPLETE
Todo Ledger:
Planned: Establish focus lock signal; add secondary suggestion capture + badge UI; wire focus lock into goal/routine panels; tighten routine draft guard messaging; update evidence log; Fix server-side goal prompt injection; Fix "It isn't saved yet" default response; Add intent markers to UI; Show intent markers on first routine/goal turn via client hints; Add chat background gradient; Add focus mode bubble borders; Fix chat scrolling and focus glow reliability; Fix chat scroll drift and ensure CSS loading
Completed: Implemented secondary suggestions storage and UI; wired focus lock to goal/routine handlers; updated routine draft guard to capture secondary suggestions; updated routine confirm label; FIXED ReferenceError: refreshSecondarySuggestionUI is not defined; Removed forced goal prompt injection in api.py; Implemented conservative goal intent gating; Made "It isn't saved yet" system instruction conditional; Added intent markers to UI; Implemented client-side intent hints for immediate marker rendering; Added chat background gradient; Added focus mode bubble borders; Fixed chat scrolling by changing overflow to overflow-x: hidden; Improved focus glow reliability by using getActiveFocusKind; Extracted CSS to static/othello.css; Fixed chat scroll drift by removing unconditional smooth scroll; Added cache buster to CSS link
Remaining: Runtime verification (deploy-required)
Next Action: Deploy and verify that the chat background is visible, scrolling works correctly (no drift), and message bubbles get a glow/border when a goal is active or a routine draft is pending.

diff --git a/othello_ui.html b/othello_ui.html
index 66a75996..12345678 100644
--- a/othello_ui.html
+++ b/othello_ui.html
@@ -4,7 +4,7 @@
 <head>
-    <link rel="stylesheet" href="/static/othello.css">
+    <link rel="stylesheet" href="/static/othello.css?v=2">
   <meta charset="UTF-8" />
   <title>Othello — Personal Goal Architect</title>
@@ -4170,7 +4170,14 @@
             const text = msg && msg.transcript ? String(msg.transcript) : "";
             if (!text.trim()) return;
             const role = msg && msg.source === "assistant" ? "bot" : "user";
-            addMessage(role, text);
+            // Skip individual scrolls during history load to prevent drift
+            addMessage(role, text, { skipScroll: true });
           });
+          // Final instant scroll to bottom after history load
+          const chatView = document.getElementById("chat-view");
+          if (chatView) {
+            requestAnimationFrame(() => {
+              chatView.scrollTop = chatView.scrollHeight;
+            });
+          }
         };
         if (renderedCount > 0) {
@@ -4293,13 +4300,15 @@
         refreshSecondarySuggestionUI(othelloState.messagesByClientId[clientMessageId]);
       }
 
-      // Scroll to latest message
-      requestAnimationFrame(() => {
+      // Smart Scroll: Only scroll if user is near bottom or it's their own message.
+      // Avoids "drift" from repeated smooth scrolls.
+      if (!options.skipScroll) {
         const chatView = document.getElementById("chat-view");
         if (chatView) {
-          chatView.scrollTo({
-            top: chatView.scrollHeight,
-            behavior: "smooth"
-          });
+          const nearBottom = (chatView.scrollTop + chatView.clientHeight) >= (chatView.scrollHeight - 120);
+          if (role === "user" || nearBottom) {
+            requestAnimationFrame(() => {
+              chatView.scrollTo({
+                top: chatView.scrollHeight,
+                behavior: options.smoothScroll ? "smooth" : "auto"
+              });
+            });
+          }
         }
-      });
+      }
       return { row, bubble };
     }
 
diff --git a/static/othello.css b/static/othello.css
index 12345678..87654321 100644
--- a/static/othello.css
+++ b/static/othello.css
@@ -984,6 +984,7 @@
   position: relative;
   isolation: isolate;
   overflow-x: hidden;
+  overflow-y: auto;
 }
 
 #chat-view::before {
