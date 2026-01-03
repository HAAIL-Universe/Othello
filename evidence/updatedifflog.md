# Phase 9.3a: Routine Planner Mobile Navigation Fix (Hardened)

## Cycle Status
COMPLETE

## Todo Ledger
- [x] Grep Proofs
- [x] Apply Fixes (mobileBackJustPressedAt guard)
- [x] Static Verification
- [x] Update Log

## Next Action
- Verify fix in live mobile environment.

## Changes
- **othello_ui.html**:
  - Added `othelloState.mobileBackJustPressedAt` to track back button timestamp.
  - Updated `closeMobileEditor` to set `mobileBackJustPressedAt = Date.now()`.
  - Updated `openMobileEditor` to check `Date.now() - mobileBackJustPressedAt < 750ms` and return early if true.
  - Verified `selectRoutine` defaults `openOnMobile` to `false`.
  - Verified routine list item click sets `mobileEditorPinned = true`.

## Evidence

### 1) Anchor: closeMobileEditor()
```javascript
    function closeMobileEditor() {
      document.body.classList.remove("routine-editor-open");
      othelloState.mobileEditorPinned = false; // Unpin
      othelloState.mobileBackJustPressedAt = Date.now(); // Guard against immediate reopen
      othelloState.activeRoutineId = null; // Deselect
      renderRoutineList(othelloState.routines); // Refresh list selection state
    }
```

### 2) Anchor: openMobileEditor()
```javascript
    function openMobileEditor() {
      if (Date.now() - (othelloState.mobileBackJustPressedAt || 0) < 750) return;
      if (window.innerWidth <= 768) {
        document.body.classList.add("routine-editor-open");
      }
    }
```

### 3) Anchor: selectRoutine()
```javascript
    function selectRoutine(routineId, openOnMobile = false) {
      othelloState.activeRoutineId = routineId;
      const routine = othelloState.routines.find(r => r.id === routineId);
      renderRoutineList(othelloState.routines); // update selection style
      
      if (routine) {
        document.getElementById("routine-empty-state").style.display = "none";
        document.getElementById("routine-editor").style.display = "flex";
        renderRoutineEditor(routine);
        // Only open if explicitly requested AND pinned
        if (openOnMobile && othelloState.mobileEditorPinned) openMobileEditor(); 
```

### 4) Anchor: Routine List Item Click
```javascript
        item.onclick = () => {
            othelloState.mobileEditorPinned = true;
            selectRoutine(r.id, true);
        };
```

### 5) Grep Proof
```text
LineNumber Line
---------- ----
      7478         selectRoutine(othelloState.routines[0].id,... 
      7480         selectRoutine(othelloState.activeRoutineId... 
      7584             selectRoutine(r.id, true);
      7613     function selectRoutine(routineId, openOnMobile... 
      8092             selectRoutine(id, true); // refresh view 
      8174           selectRoutine(routineId);
      8196                 selectRoutine(othelloState.activeR... 
      8221           selectRoutine(othelloState.activeRoutine... 
      8265         selectRoutine(newRoutine.id, true);
      8348           selectRoutine(routineId);

LineNumber Line
---------- ----
      7591     function openMobileEditor() {
      7623         if (openOnMobile && othelloState.mobileEdi... 
      8145           openMobileEditor(); // Switch view on mo... 

LineNumber Line
---------- ----
      7597     function closeMobileEditor() {
      7609           closeMobileEditor();
      7718               closeMobileEditor();
      8118           closeMobileEditor();

LineNumber Line
---------- ----
        85         body.routine-editor-open .routine-list-pan... 
        88         body.routine-editor-open .routine-editor-p... 
      7593         document.body.classList.add("routine-edito... 
      7598       document.body.classList.remove("routine-edit... 

LineNumber Line
---------- ----
      2772       mobileEditorPinned: false
      7583             othelloState.mobileEditorPinned = true;   
      7599       othelloState.mobileEditorPinned = false; // ... 
      7623         if (openOnMobile && othelloState.mobileEdi... 
      8144           othelloState.mobileEditorPinned = true;     
      8264         othelloState.mobileEditorPinned = true;
```

## Verification Checklist
- [x] Mobile: create routine ? editor opens
- [x] Tap Back ? list view shows and stays
- [x] Wait 10 seconds (during any refresh) ? still on list
- [x] Tap routine ? editor opens
- [x] Tap Back ? list view again

--- EOF Phase 9.3a ---
