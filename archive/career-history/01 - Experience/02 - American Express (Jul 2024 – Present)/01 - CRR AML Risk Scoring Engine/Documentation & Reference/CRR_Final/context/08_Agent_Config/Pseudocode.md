# Asset Manager - Edit Asset API Database Changes

## Overview
This document describes the database table changes when Edit Asset APIs are triggered in the CRR Asset Manager.

---

## Database Tables Involved

### 1. ASSET (Core Metadata)
- Stores asset name, reference table link, creator info

### 2. ASSET_VERSION (Version History)
- Tracks all versions (V1, V2, V3...)
- Status: Draft → Sandbox → Production → Archived

### 3. ASSET_VALUES (Value Storage)
- Actual values in each asset version
- Values can only be modified based on asset status

### 4. ASSET_USAGE_MAP (Usage Tracking)
- Tracks which markets/rulesets use each asset
- Determines if asset is "shared" or "exclusive"

### 5. SANDBOX (Assessment Metadata)
- Sandbox name, scope, type (Market/Enterprise)

### 6. SANDBOX_VERSION (Sandbox History)
- Version tracking with status transitions

### 7. SANDBOX_ASSET_MAPPING (Linkage)
- Maps sandbox versions to asset versions used

### 8. SANDBOX_HISTORY (Audit Trail)
- All actions logged with user, timestamp, comments

---

## Scenario Pseudocode

### Scenario 1: Create New Asset
```
REF-1.1: User clicks +Add Asset in Sandbox
REF-1.2: INSERT INTO ASSET (asset_id, asset_name, ...) 
REF-1.3: INSERT INTO ASSET_VERSION (version_id, asset_id, version_num='V1', status='Draft')
REF-1.4: INSERT INTO ASSET_VALUES (value_id, version_id, value, is_active='Y')
REF-1.5: INSERT INTO SANDBOX_HISTORY (action='CREATE_ASSET')
```

### Scenario 2: Edit Draft Asset
```
REF-2.1: User selects asset with status='Draft'
REF-2.2: UPDATE ASSET_VALUES SET value=new_value WHERE version_id=current_version
REF-2.3: INSERT INTO SANDBOX_HISTORY (action='EDIT_ASSET')
Note: No version increment - inline update allowed for Draft
```

### Scenario 3: Edit Asset in Sandbox (First Edit - Versioning)
```
REF-3.1: User edits asset where status='Production' in sandbox
REF-3.2: INSERT INTO ASSET_VERSION (asset_id, version_num='V2', status='Sandbox')
REF-3.3: COPY values from V1 to V2 in ASSET_VALUES
REF-3.4: APPLY user edits to V2 values
REF-3.5: INSERT INTO SANDBOX_ASSET_MAPPING (sb_ver_id, asset_id, asset_ver_id=V2)
REF-3.6: INSERT INTO SANDBOX_HISTORY (action='EDIT_ASSET')
Note: Subsequent edits before Submit update V2 inline
```

### Scenario 4: Copy Shared Asset (Cross-Market Protection)
```
REF-4.1: User tries to edit asset used in multiple markets
REF-4.2: CHECK ASSET_USAGE_MAP: COUNT(DISTINCT scope) > 1 OR is_enterprise='Y'
REF-4.3: IF shared THEN BLOCK edit, PROMPT "Create Copy?"
REF-4.4: IF yes:
    REF-4.4.1: INSERT INTO ASSET (new_asset_id, name=original_name + '_' + market_scope)
    REF-4.4.2: INSERT INTO ASSET_VERSION (new_asset_id, V1, status='Draft')
    REF-4.4.3: COPY values to new asset
    REF-4.4.4: INSERT INTO ASSET_USAGE_MAP (new_asset_id, current_market_scope)
    REF-4.4.5: INSERT INTO SANDBOX_HISTORY (action='COPY_ASSET')
```

### Scenario 5: Promote to Production
```
REF-5.1: Sandbox approved by two approvers
REF-5.2: UPDATE ASSET_VERSION SET status='Archived' WHERE asset_id=X AND status='Production'
REF-5.3: UPDATE ASSET_VERSION SET status='Production' WHERE version_id=sandbox_version
REF-5.4: UPDATE SANDBOX_VERSION SET status='Production'
REF-5.5: INCREMENT CRR_PRODUCTION_VERSION
REF-5.6: INSERT INTO SANDBOX_HISTORY (action='IMPLEMENT')
```

---

## Key Business Rules

1. **Draft Assets**: Editable anywhere, inline updates
2. **Sandbox Assets**: Version on first edit, inline until Submit
3. **Production Assets**: Read-only outside sandbox
4. **Shared Assets**: Copy-on-write in market sandboxes
5. **Enterprise Sandbox**: Can edit all assets (versioning)
6. **Market Sandbox**: Can only edit exclusive assets or copy shared

## Status Transitions
```
Draft → Sandbox (when linked to ruleset)
Sandbox → Production (after promotion)
Production → Archived (when newer version promoted)
```
