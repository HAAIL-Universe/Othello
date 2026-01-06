diff --git a/static/othello.js b/static/othello.js
index 4319420a..b162b6e9 100644
--- a/static/othello.js
+++ b/static/othello.js
@@ -36,6 +36,7 @@
     const archiveStatus = document.getElementById('archive-status');
     const archiveGoalLabel = document.getElementById('archive-goal-label');
     let settingsWarningLogged = false;
+    let pendingChatRequests = 0; // Moved to top-level to avoid TDZ errors
     const BOOT_STATE = {
       CHECKING_AUTH: "checking_auth",
       NEEDS_LOGIN: "needs_login",
@@ -5740,7 +5741,6 @@
     }
 
     // KITT Scanner Logic
-    let pendingChatRequests = 0;
     function setChatThinking(isThinking) {
         const sheet = document.querySelector('.chat-sheet');
         if(sheet) {
@@ -5749,10 +5749,12 @@
         }
     }
     function beginThinking() {
+        if (typeof pendingChatRequests !== 'number') pendingChatRequests = 0;
         pendingChatRequests++;
         setChatThinking(true);
     }
     function endThinking() {
+        if (typeof pendingChatRequests !== 'number') pendingChatRequests = 0;
         pendingChatRequests = Math.max(0, pendingChatRequests - 1);
         if (pendingChatRequests === 0) setChatThinking(false);
     }
