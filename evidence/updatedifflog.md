diff --git a/static/othello.js b/static/othello.js
index 7cd186ce..2a82f107 100644
--- a/static/othello.js
+++ b/static/othello.js
@@ -6032,10 +6032,21 @@
             }
 
         } catch (err) {
-             console.error("[sendMessage] network failure", err, err?.stack);
-             addMessage("bot", `[Network error] backend unreachable: ${err?.message || String(err)}`);
-             updateConnectivity('offline');
-             statusEl.textContent = "Offline";
+             console.error("[sendMessage] exception:", err, err?.stack);
+             
+             // Detect genuine network failures from fetch()
+             const isNetwork = err instanceof TypeError && (
+                 err.message === "Failed to fetch" ||
+                 err.message.includes("NetworkError") ||
+                 err.message.includes("Network request failed")
+             );
+
+             if (isNetwork) {
+                 addMessage("bot", `[Network error] backend unreachable: ${err.message}`);
+                 updateConnectivity('offline');
+             } else {
+                 addMessage("bot", `[Client error] ${err.message || String(err)}`);
+             }
              return;
         } finally {
             endThinking();
