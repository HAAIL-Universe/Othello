# Cycle Status: DIAGNOSING

## Todo Ledger
Completed:
- [x] Duet Chat Debugging

## Next Action
Confirm Fix

diff --git a/othello_ui.html b/othello_ui.html
index 398bb638..de5229af 100644
--- a/othello_ui.html
+++ b/othello_ui.html
@@ -10,7 +10,6 @@
 </head>
 
 <body>
-    <div style="background:#ff000033;color:white;text-align:center;font-size:10px;position:fixed;top:0;left:0;right:0;z-index:9999;pointer-events:none;">DEBUG BUILD: Duet V1 - Checked</div>
     <div id="connect-overlay" class="waking-overlay" style="display:none;">
       <div class="waking-overlay__spinner" id="connect-spinner"></div>
       <div id="connect-status" class="waking-overlay__status" style="margin-top:1.2rem;">Connecting to serverÔÇª</div>
@@ -327,6 +326,7 @@
   <div id="global-chat-overlay" class="global-chat-overlay">
     <div class="chat-sheet">
       <div class="chat-sheet__header">
+        <div id="duet-build-marker" style="color:red;font-size:10px;margin-right:8px;font-weight:bold;">DUET_V1_MARKER</div>
         <div class="kitt-scanner" aria-hidden="true"></div>
         <div id="chat-status-pill" class="status-pill" style="margin-right: auto;">
           <div class="dot"></div>
