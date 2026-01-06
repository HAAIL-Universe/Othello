diff --git a/static/othello.js b/static/othello.js
index 2a82f107..4319420a 100644
--- a/static/othello.js
+++ b/static/othello.js
@@ -1,4 +1,6 @@
     console.log("Othello UI boot OK");
+    console.info("[build] othello.js", "v2026-01-06-A", new Date().toISOString());
+
     // DOM element bindings for globals that may be missing
     const modeToggle = document.getElementById('mode-toggle');
     const inputBar = document.getElementById('input-bar');
@@ -4152,8 +4154,17 @@
         await refreshGoals();
       } catch (err) {
         console.error("[Othello UI] goal edit error:", err);
-        addMessage("bot", "[Connection error: backend unreachable]");
-        statusEl.textContent = "Offline";
+        const isNetwork = err instanceof TypeError && (
+             err.message === "Failed to fetch" ||
+             err.message.includes("NetworkError") ||
+             err.message.includes("Network request failed")
+        );
+        if (isNetwork) {
+             addMessage("bot", `[Network error] backend unreachable: ${err.message}`);
+             updateConnectivity('offline');
+        } else {
+             addMessage("bot", `[Client error] Goal edit failed: ${err.message || String(err)}`);
+        }
       }
     }
 
@@ -6248,9 +6259,18 @@
            refreshGoalDetail();
         }
       } catch (err) {
-        console.error("[Othello UI] sendMessage error:", err);
-        addMessage("bot", "[Connection error: backend unreachable]");
-        statusEl.textContent = "Offline";
+        console.error("[sendMessage] outer exception:", err);
+        const isNetwork = err instanceof TypeError && (
+             err.message === "Failed to fetch" ||
+             err.message.includes("NetworkError") ||
+             err.message.includes("Network request failed")
+        );
+        if (isNetwork) {
+             addMessage("bot", `[Network error] backend unreachable: ${err.message}`);
+             updateConnectivity('offline');
+        } else {
+             addMessage("bot", `[Client error] ${err.message || String(err)}`);
+        }
       } finally {
         endSendUI(sendUiState);
       }
