FEATURE 1: UNIFIED SANDBOX JOURNEY
Note: Authorization/permissions management is explicitly OUT OF SCOPE for this feature and will be addressed in a separate effort.

Story 1.1: Dynamic Sandbox Scope Selection with Mutual Exclusion
Description:
As a CRR Business User,
I want to see only the sandbox scope options that I'm allowed to create based on what already exists in the system,
so that I don't accidentally create invalid sandbox combinations and I understand why certain options are unavailable.
Acceptance Criteria:
AC1 - First Time Setup (No Production Exists)
Given I'm on the Sandbox list page and no production configuration exists yet,
When I click "Add Risk Assessment" and the scope dropdown opens,
Then I see only "Enterprise" option available in the dropdown,
And all market options (India, France, Spain, Belgium, etc.) are completely hidden from the dropdown (not visible at all),
And I can only select Enterprise to create my first sandbox.
AC2 - Production Exists, No Active Sandboxes
Given production configuration exists and I'm on the Sandbox list page with no active sandboxes,
When I click "Add Risk Assessment" and open the scope dropdown,
Then I see "Enterprise" option available,
And I see all market options (India, France, Spain, Belgium, etc.) available,
And I can select any scope to create a new sandbox.
AC3 - Enterprise Sandbox Active, Creation Blocked
Given an Enterprise sandbox exists in any state (Draft, In Progress, Testing Completed, Pending Approval 1, or Pending Approval 2),
When I view the Sandbox list page,
Then "Add Risk Assessment" button is disabled and grayed out,
And hovering over the button shows tooltip "Cannot create Market sandbox while Enterprise sandbox is active",
And I cannot create any new sandbox until the Enterprise sandbox is implemented or rejected.
AC4 - Market Sandbox Active, Enterprise Hidden
Given an India Market sandbox exists in Draft state,
When I click "Add Risk Assessment" and open the scope dropdown,
Then "Enterprise" option is completely hidden from the dropdown (not present in the list),
And India option is disabled with tooltip "India sandbox already exists",
And other market options (France, Spain, Belgium) remain enabled,
And I can create sandboxes for France, Spain, or Belgium but not Enterprise or another India sandbox.
AC5 - Multiple Market Sandboxes Allowed
Given India and France Market sandboxes already exist,
When I open the scope dropdown,
Then India and France options are disabled with tooltips showing they already exist,
And remaining market options (Spain, Belgium, etc.) are enabled,
And "Enterprise" option is completely hidden from the dropdown,
And I can create additional market sandboxes (up to the system limit) but not duplicate markets or Enterprise.
AC6 - After Sandbox Promotion, Options Re-Enable
Given an Enterprise sandbox was just promoted to production and removed from active list,
When I return to Sandbox list page and click "Add Risk Assessment",
Then both "Enterprise" and all market options are enabled again,
And I can create either Enterprise or Market sandboxes.

Story 1.4: Complete Configuration Snapshot on Version Creation
Description:
As a CRR Business User,
I want to ensure that every sandbox version captures exactly what I configured across all areas (Rules, Assets, and Fundamental Assessment),
so that I have a complete, traceable record of what was simulated and eventually promoted to production.
Acceptance Criteria:
AC1 - Snapshot Captures All Three Configuration Types
Given I'm in a Draft sandbox and I've made changes to Rules (added 2 rulesets), Assets (modified 3 assets), and Fundamental Assessment (changed 1 override),
When I click "Submit for Simulation" and confirm,
Then the system creates Version 1 as an immutable snapshot,
And the snapshot includes all my rule changes with exact rule logic, weights, and multipliers,
And the snapshot includes all my asset changes linked to specific asset version numbers,
And the snapshot includes all my FA override changes with Q&A answers,
And I can later review exactly what was in Version 1.
AC2 - Snapshot Links to Specific Component Versions
Given I'm submitting a sandbox that references Asset "High_Risk_Countries" version 3,
When Version 1 snapshot is created,
Then the snapshot explicitly links to asset_id + asset_vsn_no = 3,
And if that asset is later updated to version 4 in another sandbox,
And my Version 1 still points to version 3,
And I can trace back exactly which asset version was used in my simulation.
AC3 - Snapshot is Immutable After Creation
Given Version 1 has been created and saved,
When I try to edit any configuration,
Then a new version (Version 2) is created for my edits,
And Version 1 remains unchanged,
And Version 1 can never be modified,
And I can always see the original Version 1 configuration in version history.
AC4 - Multiple Versions Build on Previous
Given I submitted Version 1, reviewed results, and clicked "Create New Version",
When Version 2 is created,
Then Version 2 starts with Version 1's configuration as the baseline,
And I can make edits to Version 2 without affecting Version 1.
AC5 - Version History Navigation with Horizontal Switcher
Given my sandbox has progressed through 3 versions,
When I view the sandbox detail page,
Then I see horizontal navigation controls (back and forward arrows) to move between versions,
And current version is clearly indicated,
And I can navigate to Version 1, Version 2, or Version 3 using the arrows,
And each version shows: version number, creation date, created by user, status, and justification comment,
And I can view what was configured in each version.
AC6 - Snapshot Creation Fails Atomically
Given I click "Submit for Simulation",
When the system starts creating the snapshot but encounters an error (database timeout, validation failure),
Then no partial snapshot is saved,
And I see error message "Failed to create version snapshot. Please try again",
And my sandbox remains in Draft state,
And I can fix issues and retry submission.

Story 1.5: Submit Confirmation with Hierarchical Change Summary
Description:
As a CRR Business User,
I want to see exactly where my changes have impacted the CRR configuration before submitting for simulation,
so that I can validate I'm testing the right scope of changes and provide appropriate justification.
Acceptance Criteria:
AC1 - Enterprise Sandbox Shows Three-Level Pivot Structure
Given I'm in an Enterprise sandbox and made changes across multiple Risk Categories and Risk Elements,
When I click "Submit for Simulation",
Then confirmation modal opens with title "Confirm Submission for Simulation",
And modal shows "Rules Changes" section with three-level expandable pivot structure:

Level 1: Risk Category names (expandable)
Level 2: Risk Element names under each category (expandable)
Level 3: Ruleset descriptions under each element (leaf nodes showing actual changes),
And I can expand/collapse each level to see where changes occurred,
And this provides clear visibility into which parts of the CRR framework were modified.

AC2 - Market Sandbox Shows Four-Level Pivot Structure
Given I'm in a Market sandbox (e.g., India) and made changes to assets affecting multiple markets,
When I click "Submit for Simulation" and view "Asset Changes" section,
Then modal shows four-level expandable pivot structure:

Level 1: Scope/Market names (India, Poland, etc.) (expandable)
Level 2: Risk Category names under each market (expandable)
Level 3: Risk Element names under each category (expandable)
Level 4: Ruleset descriptions under each element (leaf nodes showing which rulesets were impacted),
And same four-level structure applies to "FA Changes" section,
And I can see which markets and framework components are affected by my changes.

AC3 - Summary Shows Impact Scope, Not Detailed Changes
Given confirmation modal is displaying change summary,
Then pivot structure shows WHERE changes have been made (which categories, elements, rulesets),
And pivot structure does NOT show exact before/after values or detailed change content,
And detailed change export is available separately in simulation results (future story),
And this summary helps me understand scope without overwhelming detail.
AC4 - Justification Required to Proceed
Given confirmation modal is open,
When I view the modal,
Then I see text area labeled "Justification (Required)" below the change summary,
And [Confirm and Submit] button is present,
And I must enter justification text before submission can proceed.

Story 1.9: Atomic Promotion with Complete Rollback on Any Failure
Description:
As a CRR Business User,
I want to have confidence that when I promote a sandbox to production, either all my changes go live together or none of them do,
so that production never ends up in a broken or partial state that wasn't tested.
Acceptance Criteria:
AC1 - All Components Merge in Single Operation
Given my sandbox contains rule changes, asset updates, and FA override changes,
When I click "Implement" after all approvals are complete,
Then the system merges all three types of changes (Rules + Assets + FA) in a single operation,
And the operation either completes fully or fails completely,
And I never see a state where rules are in production but assets are not.
AC2 - Successful Promotion Updates Everything
Given implementation starts and all components merge successfully,
When the operation completes,
Then all my rule changes are live in production,
And all my asset version updates are live in production,
And all my FA override changes are live in production,
And sandbox status changes to "Production",
And sandbox is removed from my active sandbox list.
AC3 - Partial Failure Triggers Complete Rollback
Given implementation starts successfully and rules merge to production,
When asset merge encounters a database error halfway through,
Then the system automatically rolls back the rule changes that were already merged,
And production returns to its exact state before implementation started,
And sandbox status changes to "Rejected",
And rejection comments field shows error message "Implementation failed due to system error. Please contact support."
AC4 - Enterprise Asset Versions Propagate to Markets
Given my Enterprise sandbox contains updated asset "Global_Products" from version 2 to version 3,
When implementation succeeds,
Then India Market production rules automatically reference "Global_Products" version 3,
And France Market production rules automatically reference "Global_Products" version 3,
And Spain Market production rules automatically reference "Global_Products" version 3,
And asset version 2 is marked as "Archived" in the system,
And audit log shows "Asset Global_Products upgraded from v2 to v3 in markets: [India, France, Spain]."
AC5 - Markets That Stopped Using Asset Are Skipped
Given India Market previously used "Global_Products" v2 but later created local copy "India_Products" and switched rules to use it,
When Enterprise promotes "Global_Products" v3,
Then France and Spain get version 3 updates,
And India rules are NOT updated (they're using "India_Products" instead),
And audit log shows "Global_Products v3 applied to: [France, Spain]. Skipped: [India - using different asset]."
AC7 - Transaction Timeout Triggers Rollback
Given implementation transaction starts but takes longer than timeout limit to complete,
When timeout limit is reached,
Then transaction is automatically rolled back,
And sandbox status changes to "Rejected",
And rejection comments show "Implementation timeout. Transaction exceeded time limit. No changes applied. Contact support",
And production remains in original state,
And no partial data exists.

Story 1.10: Rollback to Historical Version
Description:
As a CRR Business User,
I want to go back to a previous version of my sandbox configuration when simulation results aren't what I expected,
so that I can quickly restart from a known-good state instead of manually undoing all my changes.
Acceptance Criteria:
AC1 - Version Navigation with Horizontal Controls
Given my sandbox has progressed through 5 versions,
When I view the sandbox detail page,
Then I see horizontal navigation controls (back and forward arrows),
And I can move between versions using these arrows,
And current version number is clearly displayed (e.g., "Version 3 of 5"),
And each version shows creation date, created by user, status, and justification comment,
And non-current versions show [Rollback] button.
AC2 - Rollback from Non-Editable State Creates New Version
Given my sandbox is at Version 3 in "Testing Completed" state (non-editable),
When I navigate to Version 1 and click [Rollback],
Then confirmation modal appears: "Create new version based on Version 1? Current Version 3 will remain unchanged",
And modal shows [Create New Version] and [Cancel] buttons,
When I click [Create New Version],
Then system creates Version 4 as an exact copy of Version 1's configuration,
And Version 4 opens in Draft state (editable),
And I can now edit Version 4 starting from Version 1's baseline,
And Version 3 remains unchanged in history.
AC3 - Rollback Behavior Consistent Across Configuration Types
Given rollback functionality currently works for Rules configuration,
When rollback is performed from any version,
Then rollback applies to Rules, Assets, and Fundamental Assessment configuration together,
And all three configuration types are restored to the selected historical version,
And rollback behavior remains consistent with how it currently works for Rules (same warnings, confirmations, and state transitions apply).
AC4 - Cancel Rollback Preserves Current State
Given rollback confirmation modal is displayed,
When I click [Cancel],
Then modal closes,
And no rollback happens,
And my current version and any uncommitted changes remain exactly as they were.

FEATURE 2: ASSET MANAGER
Note: Authorization/permissions management is explicitly OUT OF SCOPE for this feature and will be addressed in a separate effort.

Story 2.1: Asset Database Model with Versioning
Description:
As a CRR Business User,
I want to have assets properly tracked with complete version history and usage information,
so that I can always trace which version of an asset was used in any simulation and who made changes when.
Acceptance Criteria:
AC1 - New Asset Creation Stores All Core Fields
Given I create a new asset named "High_Risk_Industries" with description "Industries requiring enhanced due diligence", linked to reference table "Industry_Code", and upload CSV with 10 valid values,
When I save the asset,
Then system creates asset record with unique asset ID, stores my name, description, list name, creation timestamp, creation user, version number = 1, and status = "Draft",
And system creates 10 separate value records linking the asset ID to each of the 10 values,
And I can retrieve the complete asset with all its values later.
AC2 - Asset Edits Accumulate Until Submit
Given asset "High_Risk_Industries" currently has version 1 in Draft state within my sandbox,
When I edit the asset first time (add 3 values), version updates to version 2,
And I continue making additional edits (remove 1 value, add 2 more values),
Then all my edits keep accumulating without creating new versions,
And version remains at version 2 throughout my editing session,
When I click "Submit for Simulation",
Then version 2 is frozen as immutable snapshot,
And all accumulated changes since version 1 are captured in version 2.
AC3 - Usage Metadata Tracks Where Asset Is Used
Given asset "High_Risk_Industries" is selected in Rule R-500 within Ruleset RS-200 in India Market,
When rule is saved,
Then system creates usage record linking asset ID to rule ID, ruleset ID, risk element ID, and market code (IN),
And I can later query "Where is this asset used?" and see India Market, Ruleset RS-200, Rule R-500,
And this information displays in the References section when I view asset details.
AC4 - Multiple Markets Using Same Asset Tracked Separately
Given asset "APAC_Countries" is used in India Market Rule R-100 and France Market Rule R-200,
When I retrieve usage information,
Then system returns two separate usage records: one for India (IN) and one for France (FR),
And system can determine asset is "shared" (used in multiple markets),
And this shared status affects editability rules later.
AC5 - Version History Preserved Indefinitely
Given asset "High_Risk_Products" has progressed through 5 versions over 6 months,
When I query version history,
Then system returns all 5 versions with: version number, creation date, creation user, value count, status (Draft/Sandbox/Production/Archived),
And I can see version 1 created 6 months ago even though we're now on version 5,
And all versions are retained for compliance and audit purposes.
AC6 - Asset Deletion Only for Unused Draft Assets
Given asset "Test_Asset_123" has status "Draft" and no usage records (not referenced by any rules),
When I attempt to delete it,
Then deletion succeeds,
And asset and all its value records are permanently removed from database.
AC7 - Delete Option Only Available for Draft Status
Given I'm viewing the asset list,
When I look at assets with different statuses,
Then [Delete] action is visible only for assets with status "Draft",
And [Delete] action is hidden for assets with status "Sandbox", "Production", or "Archived",
And users cannot attempt deletion of non-Draft assets.

Story 2.2: Asset Creation Within Sandbox
Description:
As a CRR Business User,
I want to create new assets directly within my sandbox work session,
so that I can immediately use those assets in my rules without switching screens or workflows.
Acceptance Criteria:
AC1 - Create Asset Button Available in Sandbox
Given I'm inside a Draft sandbox and clicked on the "Assets" sub-navigation tab,
When the asset list view loads,
Then I see a [Create Asset] button at the top of the screen,
And clicking it opens the Create Asset modal.
AC2 - Create Asset Modal Contains All Required Fields
Given the Create Asset modal is open,
Then I see form fields:

Asset Name (text input, required)
Description (text area, optional)
List Name (dropdown, required)
CSV File Upload (file selector, required),
And List Name dropdown is populated with available reference data tables (Industry_Code, Country_Code, Occupation_Type, Product_Type, etc.),
And all fields are initially empty/unselected,
And [Save] button is visible but disabled until required fields are filled.

AC3 - Real-Time Duplicate Name Validation
Given I'm filling out the Create Asset form,
When I type asset name "Existing_Asset" that already exists in the system,
Then inline error appears below Asset Name field indicating duplicate name,
And [Save] button remains disabled,
When I change name to "New_Unique_Asset",
Then error clears,
And [Save] button becomes enabled (if other required fields are valid).
AC4 - Asset Creation Follows Existing Validation Rules
Given I'm creating a new asset,
When I fill form fields and upload CSV,
Then all existing validation rules that apply to asset creation are enforced (reference data validation, file format checks, required field validation),
And validation behavior matches current asset creation functionality,
And appropriate error messages display for validation failures.
AC5 - Successful Asset Creation
Given I filled all required fields with valid data (unique name, selected list name, uploaded valid CSV),
When I click [Save],
Then asset is created with status "Draft" and version 1,
And modal closes,
And success message displays,
And new asset appears in the asset list immediately,
And asset is visible in all sandboxes (Enterprise and Market) because it's in Draft status.
AC7 - Cancel Without Creating Asset
Given Create Asset modal is open and I've partially filled some fields,
When I click [Cancel] or click outside the modal,
Then modal closes,
And no asset is created,
And no data is saved,
And I return to the asset list view.

Story 2.3: Asset Status Transition When Used in Rules
Description:
As a CRR Business User,
I want to assets to automatically track when they start being used in rules,
so that the system can prevent accidental changes to assets that are actively part of risk calculations.
Acceptance Criteria:
AC1 - Draft Asset Selected in Rule Triggers Status Change
Given asset "High_Risk_Countries" exists with status "Draft",
When I'm configuring a rule and select this asset from the value dropdown as the rule value,
And I save the rule,
Then asset status automatically changes from "Draft" to "Sandbox",
And usage record is created linking asset to the rule, ruleset, and market,
And I don't need to manually update asset status.
AC2 - Usage Metadata Populated Automatically
Given I selected asset "Restricted_Industries" (asset_id = 100) in Rule R-500 of Ruleset RS-200 in India Market,
When rule is saved,
Then usage metadata table contains record: asset_id = 100, rule_id = 500, ruleset_id = 200, market_code = "IN", usage_start_timestamp = [current time],
And I can later query this asset and see it's used in "India Market, Ruleset RS-200, Rule R-500."
AC3 - Second Rule Using Same Asset Updates Usage, Not Status
Given asset "APAC_Countries" already has status "Sandbox" (used in one rule),
When I select this asset in a different rule and save,
Then new usage record is created for the second rule,
And asset status remains "Sandbox" (doesn't change again),
And asset now shows 2 usage locations in its References.
AC4 - Asset Used Across Markets Creates Multiple Usage Records
Given I'm in India Market sandbox and select asset "Global_Products" in Rule R-100,
And later another user in France Market sandbox selects same asset in Rule R-200,
When both rules are saved,
Then asset has two usage records: one for India (IN) and one for France (FR),
And system detects asset is "shared" (used in multiple markets).
AC5 - Removing All References Reverts Status to Draft
Given asset "Test_Asset" has status "Sandbox" and is used in Rule R-300 and Rule R-400,
When both Rule R-300 and Rule R-400 are deleted,
Then both usage records are removed,
And asset status automatically reverts from "Sandbox" back to "Draft",
And asset becomes globally editable again.
AC6 - Draft Asset Visible in Rule Value Dropdown
Given I'm configuring a rule with datapoint "Industry" (linked to Industry_Code reference table),
When I open the value dropdown to select an asset,
Then dropdown shows all assets with List Name = "Industry_Code",
And this includes Draft assets, Sandbox assets, and Production assets,
And I can select any of them regardless of status.

Story 2.4: Asset List with Visual Indicators for Shared Assets
Description:
As a CRR Business User,
I want to see all assets in one place with clear visual indicators showing which ones are shared across markets,
so that I know which assets need special care when editing and can avoid accidentally impacting other markets.
Acceptance Criteria:
AC1 - All Assets Visible Regardless of Scope
Given I'm in India Market sandbox viewing the Assets tab,
When asset list loads,
Then I see ALL assets in the system (Draft, Sandbox, Production),
And this includes assets used only in India,
And this includes assets used only in France or other markets,
And this includes assets used in Enterprise,
And complete visibility helps me understand full asset inventory.
AC2 - Shared Assets Have Visual Color Indicator
Given asset "APAC_Countries" is used in India, France, and Spain markets (shared),
When I view the asset list,
Then "APAC_Countries" row has subtle color accent (light yellow background or colored border),
And this visual indicator is NOT a text label saying "Shared",
And visual indicator immediately signals this asset requires special handling.
AC3 - Local Assets Have No Special Indicator
Given asset "India_Specific_Products" is used ONLY in India Market rules,
When I view the asset list in India Market sandbox,
Then "India_Specific_Products" row has standard/default styling (no color accent),
And absence of indicator signals this asset is safe to edit directly.
AC5 - Draft Assets Have No Indicator
Given asset "New_Draft_Asset" has status "Draft" and isn't used anywhere yet,
When I view the asset list,
Then "New_Draft_Asset" has no color indicator,
And I know this asset is freely editable everywhere.
AC6 - Shared Indicator Works in Both Enterprise and Market Sandboxes
Given asset "Global_Products" is shared across markets,
When I view it in Enterprise sandbox,
Then it has color indicator,
When I view it in India Market sandbox,
Then it also has color indicator,
And visual treatment is consistent across all sandbox scopes.
AC7 - Asset List Loads Without Indicators If Usage Data Unavailable
Given I load asset list but usage metadata API fails or times out,
When assets are displayed,
Then all assets show warning icon indicating usage scope cannot be determined,
And users can still see asset list,
And system assumes shared (safest assumption) when data is unavailable.

Story 2.5: Asset Edit Permission Based on Status and Scope
Description:
As a CRR Business User,
I want to see edit buttons enabled or disabled based on whether I'm allowed to edit an asset,
so that I don't accidentally try to edit assets I don't have permission for and understand the rules governing asset changes.
Acceptance Criteria:
AC1 - Draft Asset Editable Everywhere
Given I'm in any sandbox (Enterprise or India Market or France Market) and viewing asset "New_Asset" with status "Draft",
When I look at the asset in the list,
Then [Edit] button is enabled and clickable,
And clicking it opens Edit Asset modal allowing direct changes.
AC2 - Local Sandbox Asset Editable in Home Market
Given asset "India_Products" has status "Sandbox" and is used ONLY in India Market rules,
When I'm in India Market sandbox,
Then [Edit] button is enabled,
And clicking it opens Edit Asset modal with versioning (saves create new version).
AC3 - Shared Sandbox Asset Blocked in Market Sandbox
Given asset "APAC_Countries" has status "Sandbox" and is used in India, France, and Spain (shared),
When I'm in India Market sandbox and click [Edit],
Then instead of Edit Asset modal, I see confirmation prompt "This asset is used across multiple markets: India, France, Spain. Would you like to create a copy and customize?" with [Create a Copy] [Cancel] buttons,
And direct editing is prevented to avoid cross-market impact.
AC4 - All Sandbox Assets Editable in Enterprise Sandbox
Given I'm in Enterprise sandbox viewing asset "Any_Asset" with status "Sandbox" or "Production",
When I look at any asset,
Then [Edit] button is enabled,
And clicking it opens Edit Asset modal with versioning,
And changes will propagate to all markets upon promotion.
AC5 - Production Asset Not Editable Outside Sandbox
Given I'm viewing standalone Asset Manager tab (not inside a sandbox) and looking at asset with status "Production",
When I look at the asset row,
Then [Edit] button is hidden or disabled,
And only [Export] action is available.
AC6 - Asset Not Editable in Non-Draft Sandbox States
Given I'm in a sandbox with status "Testing Completed" or "Pending Approval" (not "Draft"),
When I view the Assets tab,
Then all [Edit] buttons are disabled for all assets,
And I must wait for sandbox to return to Draft or create new version.

Story 2.6: Copy-on-Write for Shared Assets
Description:
As a CRR Business User,
I want to create a customized copy of a shared asset when I need market-specific changes,
so that my changes only affect my market and don't accidentally impact other markets using the same asset.
Acceptance Criteria:
AC1 - Shared Asset Edit Triggers Copy Confirmation
Given I'm in India Market sandbox and asset "APAC_Countries" is used in India, Singapore, and France,
When I click [Edit] on this asset,
Then confirmation modal appears with message "This asset has been used across multiple markets: India, Singapore, France. Would you like to create a copy and customize?",
And modal shows [Create a Copy] and [Cancel] buttons,
And direct editing is prevented.
AC2 - Create Copy Opens Pre-Filled Modal
Given copy confirmation modal is displayed,
When I click [Create a Copy],
Then Edit Asset modal opens with pre-filled fields:

Asset Name = "APAC_Countries_copy"
Description = copied from original asset description
List Name = "Country_Code" (disabled, grayed out, cannot change)
CSV file = original values pre-loaded,
And [Save] button is initially enabled IF default name is unique.

AC3 - Duplicate Name Validation Uses Existing Error
Given default copy name "APAC_Countries_copy" already exists (someone created this copy before),
When Edit Asset modal opens,
Then existing duplicate name validation error appears below Asset Name field,
And [Save] button is disabled,
And I must rename before proceeding.
AC4 - Real-Time Duplicate Validation as User Types
Given Edit Asset modal is open with duplicate name error,
When I change name to "APAC_Countries_India",
Then validation API is called,
And if "APAC_Countries_India" is unique, error clears and [Save] button enables,
And if name is still duplicate, error remains and Save stays disabled.
AC5 - Successful Copy Creation
Given I renamed copy to unique name "APAC_Countries_India", optionally modified description and CSV,
When I click [Save],
Then NEW asset is created with:

New unique asset_id
Name = "APAC_Countries_India"
Status = "Draft"
Version = 1
Values from my modified CSV,
And original asset "APAC_Countries" remains unchanged,
And existing asset creation success message displays,
And modal closes,
And new asset appears in asset list.

AC6 - User Can Modify Values Before Saving Copy
Given Edit Asset modal is open for creating copy,
When I upload a different CSV file with modified values,
Then new CSV values are used for the copy,
And original asset values remain unchanged,
And I can customize the copy before saving.
AC7 - Cancel Copy Workflow Returns to Asset List
Given confirmation modal or Edit Asset modal is displayed during copy workflow,
When I click [Cancel],
Then modal closes,
And no copy is created,
And original shared asset remains unchanged,
And I return to asset list with no changes made.

Story 2.7: Enterprise Asset Version Propagation on Promotion
Description:
As a CRR Business User,
I want to have enterprise-wide asset updates automatically apply to all markets when I promote from Enterprise sandbox,
so that global policy changes are consistently enforced everywhere without manual market-by-market updates.
Acceptance Criteria:
AC1 - Enterprise Edit Creates New Asset Version
Given I'm in Enterprise sandbox editing asset "Global_Products" which is currently version 2,
When I add 3 new values and save,
Then system creates version 3 of "Global_Products",
And version 2 is preserved as historical record,
And version 3 is captured in sandbox snapshot when I submit for simulation.
AC2 - Sandbox Snapshot Links to Specific Asset Version
Given my Enterprise sandbox Version 1 contains asset "Global_Products" version 3,
When I submit for simulation creating snapshot,
Then snapshot explicitly records: asset_id + asset_vsn_no = 3,
And simulation uses version 3 for risk calculations,
And I can later trace that this sandbox used exactly version 3.
AC3 - Promotion Propagates Asset to All Markets
Given India Market production uses "Global_Products" v2, France uses v2, Spain uses v2,
When my Enterprise sandbox containing "Global_Products" v3 is successfully promoted,
Then India's production rules automatically reference v3,
And France's production rules automatically reference v3,
And Spain's production rules automatically reference v3,
And v2 is marked "Archived" (hidden from UI but retained for audit).
AC4 - Audit Log Shows Propagation Details
Given Enterprise promotion propagated "Global_Products" v3 to all markets,
When I view audit log,
Then I see entry: "Asset Global_Products upgraded from v2 to v3 in markets: [India, France, Spain]. Triggered by Enterprise Sandbox Implementation (sandbox_id = 500). Implemented by: [user name] at [timestamp]."
AC5 - Markets Using Custom Copy Are Skipped
Given India previously created custom copy "Global_Products_India" and switched their rules to use it,
When Enterprise promotes "Global_Products" v3,
Then France and Spain receive v3 update,
And India rules are NOT updated (they're using "Global_Products_India" with different asset_id),
And audit log notes: "Global_Products v3 applied to: [France, Spain]. Skipped: [India - using different asset]."
AC6 - Promotion Failure Prevents Version Propagation
Given Enterprise sandbox promotion encounters error during asset version update,
When transaction rolls back (per atomic promotion),
Then all markets remain on version 2,
And version 3 stays in sandbox (not promoted),
And audit log shows failed promotion attempt with error details.
AC7 - Version History Preserves Enterprise Linkage
Given "Global_Products" v3 was created in Enterprise Sandbox 500,
When I query version history for this asset,
Then version 3 record shows: version_no = 3, sandbox_id = 500, status = "Production",
And I can trace that v3 came from Enterprise Sandbox 500.

Story 2.8: Asset Export with Values and References
Description:
As a CRR Business User,
I want to export assets to Excel showing both the asset values and where they're being used,
so that I have documentation for auditors showing what's in the asset and which rules depend on it.
Acceptance Criteria:
AC1 - Export Button Available for All Assets
Given I'm viewing asset list (in sandbox or standalone Asset Manager),
When I look at any asset row,
Then [Export] action button is visible and enabled,
And clicking it triggers export generation.
AC2 - Export Generates Two-Sheet Workbook
Given I clicked [Export] on asset "High_Risk_Products",
When file generation completes,
Then Excel workbook downloads with filename "High_Risk_Products_v2.xlsx" (includes version number),
And workbook contains exactly two sheets: "Values" and "References".
AC3 - Values Sheet Contains Only Data Rows
Given asset has 25 values (CASINO, ARMS_DEALER, CRYPTO_EXCHANGE, etc.),
When I open "Values" sheet,
Then I see 25 data rows with one value per row,
And there is NO header row in Values sheet,
And values are listed in order as they appear in the asset.
AC4 - References Sheet Shows Where Asset Is Used
Given asset is used in 3 rulesets across 2 markets,
When I open "References" sheet,
Then I see column headers (bold, with background): Scope, Status, Risk Category, Risk Element, Ruleset, Rule,
And I see 3 data rows (one per ruleset),
And each row shows:

Scope = "India Market" or "France Market" (human-readable label, not "IN" or "FR")
Status = "Production" (current asset status)
Risk Category = "Product Risk" (category name, not category_id)
Risk Element = "Product Type" (element name, not element_id)
Ruleset = "High-risk product screening rules" (description, not RS-301)
Rule = "Product IN High_Risk_Products" (rule logic text, not rule_id).

AC5 - Asset Not Used Shows Empty References
Given asset "Draft_Test_Asset" has no usage records (not used in any rules),
When I export it,
Then "Values" sheet contains asset values as normal,
And "References" sheet contains only header row,
And cell A2 shows message "This asset is not currently used in any rules."

Story 2.9: Standalone Asset Manager Read-Only View
Description:
As a Market Compliance Officer,
I want to view which assets are actively used in my market's production configuration without ability to edit them,
so that I have clear reference documentation of current risk policy lists without risk of accidentally changing production.
Acceptance Criteria:
AC1 - Standalone Asset Manager Tab Accessible
Given I navigate to main application menu,
When I access the standalone Assets section (not CRR tab, separate Assets tab),
Then standalone Asset Manager view loads,
And I see market dropdown at top of page,
And I see read-only asset list (no create or edit capabilities).
AC2 - Market Dropdown Filters Production Assets
Given I'm on standalone Asset Manager view,
When I select "Belgium" from market dropdown,
Then asset list displays only Production assets currently used in Belgium's production rulesets,
And Draft assets are hidden,
And Sandbox assets are hidden,
And Assets used in other markets but not Belgium are hidden,
And this provides clear view of "what's active in Belgium right now."
AC3 - Asset List Shows Read-Only Information
Given asset list is displayed for selected market,
Then I see columns: Asset Name, Description, List Name, Last Updated,
And I see Actions column containing only [Export] button,
And [Edit] and [Delete] buttons are not present,
And [Create Asset] button is not present,
And this enforces read-only access.
AC4 - Asset Detail View is Read-Only
Given I click on asset name "High_Risk_Industries" in the list,
When detail view or modal opens,
Then all fields display as read-only text (no input fields or edit controls),
And I can see asset values listed,
And I can see usage metadata (References section showing which rules use this asset),
And only action available is [Export] button.
AC5 - Empty State Uses Existing Blank Screen Placeholder
Given I select a market which has no production assets,
When asset list loads,
Then existing blank screen placeholder displays (consistent with other empty states in CRR application),
And no custom empty state message is needed.
AC6 - Export Works from Standalone View
Given I'm viewing asset in standalone Asset Manager,
When I click [Export],
Then Excel workbook generates and downloads with same format as described in Story 2.8 (Values + References sheets),
And export functionality is identical whether I'm in sandbox or standalone view.