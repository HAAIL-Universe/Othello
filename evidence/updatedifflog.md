diff --git a/static/othello.css b/static/othello.css
index 6b0b2d80..908a47d0 100644
--- a/static/othello.css
+++ b/static/othello.css
@@ -2114,16 +2114,16 @@ body.chat-open #global-chat-fab {
 /* KITT Scanner (Knight Rider) Effect */
 .kitt-scanner {
   position: absolute;
-  top: 0;
+  bottom: 0; /* Anchor to bottom of header */
   left: 0;
   right: 0;
-  height: 4px;
+  height: 3px; /* Thin line */
   overflow: hidden;
-  border-radius: 4px 4px 0 0;
+  border-radius: 0;
   opacity: 0;
   transition: opacity 0.3s ease;
   pointer-events: none;
-  z-index: 50; /* Below controls */
+  z-index: 105; /* Above header border/controls if needed, but safe */
 }
 
 .chat-sheet.is-thinking .kitt-scanner {
@@ -2137,10 +2137,11 @@ body.chat-open #global-chat-fab {
   top: 0;
   bottom: 0;
   width: 15%;
-  background: var(--accent, #e5e7eb); /* Fallback color */
-  box-shadow: 0 0 10px var(--accent, #e5e7eb), 0 0 5px var(--accent, #e5e7eb);
+  /* Red KITT scanner style */
+  background: rgba(255, 60, 60, 0.9);
+  box-shadow: 0 0 10px rgba(255, 60, 60, 0.8), 0 0 5px rgba(255, 80, 80, 0.6);
   border-radius: 2px;
-  opacity: 0.8;
+  opacity: 0.9;
   will-change: left, right;
 }
 
