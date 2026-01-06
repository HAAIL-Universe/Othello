diff --git a/static/othello.js b/static/othello.js
index b7f43936..7cd186ce 100644
--- a/static/othello.js
+++ b/static/othello.js
@@ -5970,63 +5970,73 @@
         let data;
         let res;
         try {
-            console.log(`[Othello UI] Fetching ${API}...`);
-            try {
-                res = await fetch(API, {
+            console.log(`[sendMessage] Fetching ${API}...`);
+            res = await fetch(API, {
                   method: "POST",
                   headers: {"Content-Type": "application/json"},
                   credentials: "include",
                   body: JSON.stringify(payload)
-                });
-            } catch (netErr) {
-                console.error("[Othello UI] Network failure:", netErr);
-                addMessage("bot", "[Connection error: backend unreachable]");
-                updateConnectivity('offline');
-                statusEl.textContent = "Offline";
-                return; // Finally will still run to clear thinking
-            }
+            });
 
-            console.log("[Othello UI] /api/message status", res.status);
+            console.log("[sendMessage] /api/message status", res.status);
 
             if (!res.ok) {
               updateConnectivity('degraded', `Error ${res.status}`);
               const contentType = res.headers.get("content-type") || "";
+              
               if (contentType.includes("application/json")) {
                 let errorData = null;
                 try {
                   errorData = await res.json();
                 } catch (e) {
-                  console.warn("[Othello UI] Could not parse JSON error body:", e);
+                  console.warn("[sendMessage] Could not parse JSON error body:", e);
                 }
-                console.error("[Othello UI] sendMessage HTTP error:", res.status, errorData);
+                console.error("[sendMessage] HTTP error:", res.status, errorData);
                 const errMsg = (errorData && (errorData.message || errorData.error)) || "Unable to process your message.";
-                const reqId = errorData && errorData.request_id;
-                if (reqId) {
-                  console.error("[Othello UI] sendMessage request_id:", reqId);
-                }
-                const detailSuffix = reqId ? ` (request_id: ${reqId})` : "";
-                addMessage("bot", `[Error ${res.status}]: ${errMsg}${detailSuffix}`);
+                addMessage("bot", `[Server error ${res.status}]: ${errMsg}`);
               } else {
                 let errorText = "";
                 try {
                   errorText = await res.text();
                 } catch (e) {
-                  console.warn("[Othello UI] Could not read error response body:", e);
+                  console.warn("[sendMessage] Could not read error response body:", e);
                 }
                 const preview = (errorText || "").slice(0, 200);
-                console.error("[Othello UI] sendMessage non-JSON error:", res.status, preview);
-                addMessage("bot", `[Error ${res.status}]: Unable to process your message. Please try again.`);
+                console.error("[sendMessage] HTTP error (non-JSON):", res.status, preview);
+                addMessage("bot", `[Server error ${res.status}]: Unable to process your message.`);
               }
-              // Do NOT set statusEl to "Error" blindly if we want connectivity state to rule. 
-              // But for immediate feedback, "Error" is fine, assuming it reverts to connectivity state later?
-              // Logic: updateConnectivity sets the pill text.
-              // So we should let updateConnectivity win or specifically set it here.
-              // We already called updateConnectivity('degraded').
               return;
             }
 
             updateConnectivity('online');
-            data = await res.json();
+            
+            const contentType = res.headers.get("content-type") || "";
+            if (contentType.includes("application/json")) {
+                const clone = res.clone();
+                try {
+                    data = await res.json();
+                } catch (parseErr) {
+                    let textBody = "";
+                    try { textBody = await clone.text(); } catch(e) {}
+                    console.error("[sendMessage] JSON parse error:", parseErr, "Body:", textBody);
+                    addMessage("bot", `[Parse error] Invalid JSON from server.`);
+                    return;
+                }
+            } else {
+                console.warn("[sendMessage] Unexpected Content-Type:", contentType);
+                let textBody = "";
+                try { textBody = await res.text(); } catch(e) {}
+                console.error("[sendMessage] Unexpected response type. Body:", textBody);
+                addMessage("bot", `[Parse error] Unexpected response type (${contentType}).`);
+                return;
+            }
+
+        } catch (err) {
+             console.error("[sendMessage] network failure", err, err?.stack);
+             addMessage("bot", `[Network error] backend unreachable: ${err?.message || String(err)}`);
+             updateConnectivity('offline');
+             statusEl.textContent = "Offline";
+             return;
         } finally {
             endThinking();
         }
