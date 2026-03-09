# CRR Lifecycle Complete Analysis & Edge Case "Stories"

**Document Version:** 1.3 (Complete Narrative Edition)
**Created:** 2026-01-21
**Purpose:** To explain every single nuanced scenario in the CRR lifecycle as a detailed story, answering "What happens?", "Why is it a conflict?", and "How do we solve it?" for the best user experience.

---

# PART 1: CONTEXT & BASICS

*   **System:** A hierarchy of Rules referencing Assets (Lists).
*   **Sandbox:** A safe "tracing paper" environment. You create a version, edit, simulate, and promote. Max 10 versions.
*   **Assets:** Can be Shared (Enterprise/Multiple Markets) or Exclusive (One Market).

---

# PART 2: THE FOUNDATIONAL STORIES (User Confirmed Questions) ✅

*These are the 6 basic scenarios we confirmed first (FQ1-FQ6). They set the stage for how the system handles day-to-day operations.*

## FQ1: The "New Life" (Sandbox Version Cap)
**👥 The User Story:**
**User Raj** has been working hard in his sandbox. He has created 10 versions of experiments. He tries to create the 11th version.
System says: *"Limit Reached. Please Archive."*
Raj worries: *"What about my 50 custom new assets? Will I lose them?"*

**⚙️ System Perspective:**
We need to clear the history stack (versions 1-10) but keep the *current state*.

**✅ Solution:**
Raj clicks "Archive & Star New".
System creates a **Brand New Sandbox (Version 1)**.
It copies the **Latest Version** of every single asset and rule from the old sandbox.
Raj finds all his work waiting for him, just with a clean history slate.

---

## FQ2: The "Double Click" (Concurrent Edit Conflict)
**👥 The User Story:**
**User Sarah** and **User Mike** both see a list of "Banned ID Types". It has `[Passport, DriverLicense]`.
Sarah opens it to add `VoterID`.
Mike opens it to add `PanCard`.
Mike saves first. The list is now `[Passport, DriverLicense, PanCard]`.
Sarah saves a second later. Her screen still shows the old list without PanCard.

**⚙️ System Perspective:**
If Sarah overwrites, `PanCard` is lost forever (Lost Update).

**✅ Solution:**
System stops Sarah: *"Wait! Someone else edited this."*
It shows her a **Side-by-Side View**: *"You added VoterID. Mike added PanCard."*
She clicks **Merge**, and the final list becomes `[Passport, DriverLicense, PanCard, VoterID]`. Peace is maintained.

---

## FQ3: The "Lucky Break" (Asset Unlinking Mid-Edit)
**👥 The User Story:**
**User Raj** wants to edit a Shared Asset. The system blocks him: *"It's shared! You must Copy."*
He leaves the window open.
Meanwhile, the other market unlinks the asset. Now it's effectively Raj's private property.
He clicks Save.

**✅ Solution:**
System re-checks ownership at the moment of saving.
It sees Raj is now the sole owner.
It **allows the save** directly to the asset. No copy needed. Raj is pleasantly surprised.

---

## FQ4: The "Stale Sandbox" (Enterprise Updates)
**👥 The User Story:**
**User Sarah** is testing a new Belgium rule.
Overnight, Enterprise updates the global "High Risk Scoring" model and pushes it to Production.
Sarah logs in. Her sandbox is now "Stale" (using yesterday's global model).

**⚙️ System Perspective:**
If we auto-update her sandbox, her test results might jump 20% today without her doing anything. That's confusing.

**✅ Solution:**
We **DO NOT** auto-update.
We show a **Yellow Badge**: *"Production has changed."*
Sarah can finish her current test. When *she* is ready, she clicks **Refresh** to pull in the new Enterprise model.

---

## FQ5: The "Isolated Lab" (Scoring Engine)
**👥 The User Story:**
Same as above. Sarah runs a simulation while Enterprise is changing production.
She clicks "Simulate" at 10:00 AM.
Enterprise changes Production at 10:05 AM.
Simulation finishes at 10:30 AM.

**✅ Solution:**
The simulation uses the **Copied Rules** inside her sandbox. It completely ignores what Enterprise is doing in Production. Her lab is sealed and safe.

---

## FQ6: The "Orphanage" (Archive Cleanup)
**👥 The User Story:**
**User Raj** deletes a sandbox he worked on for 2 months.
Inside that sandbox, he had created 20 new Assets.
He worries: *"Did I just delete those assets? I might need them later."*

**✅ Solution:**
Deleting a sandbox **does not delete** the Assets created inside it.
Those assets become **"Orphans"**.
They sit in the system status `SANDBOX`, waiting. Raj can find them later using a "Show Orphans" filter and revive them if needed.

---

# PART 3: RESOLVED EDGE CASES (The Complex Stories) ✅

*Here we detail the 10 trickier scenarios we resolved.*

## EC1: The "Disappearing Shared Link" (Asset Unlinked Mid-Edit)
*(See FQ3 above - this is the same scenario, resolved identically).*

## EC2: The "Sandbox to Draft" Reversion

**👥 The User Story:**
**User Mike** edits a `SANDBOX` status list (locked).
His colleague removes the rule using it. The list auto-reverts to `DRAFT`.
Mike clicks Save.

**✅ Solution:**
System sees it is now `DRAFT`. It allows the save instantly. No version check needed because Drafts are flexible.

## EC3: The "Multi-Sandbox Split" (Shared Asset, Different Versions)

**👥 The User Story:**
**Raj (India)** edits Asset A1, creating **Version 2**.
**Sarah (Belgium)** is using Asset A1 in her sandbox too.

**✅ Solution:**
Raj's sandbox updates to link to **Version 2**.
Sarah's sandbox stays linked to **Version 1**.
They see different truths because they are in different "timelines" (sandboxes).

## EC4: The "Race Condition" (Concurrent Edit)
*(See FQ2 above).*

## EC5: The "Enterprise God Mode" vs "Market Reality"
*(See FQ4 above - Enterprise changes don't auto-propagate).*

## EC6: The "Frozen Simulation" (Isolation)
*(See FQ5 above).*

## EC7: The "Draft to Production" Leapfrog

**👥 The User Story:**
**Raj** creates a Draft asset.
**Enterprise** promotes it to Production.
Raj tries to edit his "Draft".

**✅ Solution:**
It is no longer his draft. It is **Global Production Data**.
Raj is blocked from editing. He must treat it like any other system asset now (make a copy or new version).

## EC8: The "Blocked Deletion" (Dependency Hell)

**👥 The User Story:**
**Enterprise** tries to delete "Geography Risk".
**India and Belgium** have overrides inside it.

**✅ Solution:**
**BLOCK**. System tells Enterprise: *"You cannot delete this. Markets are using it."*
Enterprise must negotiate with markets first.

## EC9: The "Merge Conflict" (Refresh Hell)

**👥 The User Story:**
Enterprise makes **Version 2**.
India makes **Version 3** (based on V1).
India clicks Refresh.

**✅ Solution:**
System asks India:
1. **Take Enterprise V2** (Lose your V3).
2. **Keep My V3** (Ignore Enterprise).
3. **Merge** manually.

## EC10: The "Version Cap" (The 11th Version)
*(See FQ1 above).*

---

# PART 4: NEW EDGE CASES (The Sequel - EC11 to EC20) 🔶

*These are the finer, trickier scenarios discovered during deep analysis.*

## EC11: The "Lazy Reference" (Optimistic Locking Cascade)

**👥 The User Story:**
**User X** updates an Asset list `HighRisk` from V1 to V2.
**User Y** is editing a Rule `R1` that points to `HighRisk`.
User Y submits the rule. Does the rule point to V1 (which Y saw on screen) or V2 (which X just saved)?

**✅ Solution:**
**NO Auto-Update**.
User Y sees a **Badge** on Rule R1: *"Underlying asset has a newer version."*
User Y must explicitly click **"Update"**. We never silently swap data sources in a risk system.

## EC12: The "Digital Hoarding" (Orphan Assets)

**👥 The User Story:**
Users accumulate 5,000 draft lists over 3 years. Search is slow.

**✅ Solution:**
**Auto-Archive (Soft Hide)**.
If an asset is untouched and unused for **90 Days**, it moves to `ARCHIVED` status.
It is hidden from search unless you tick `[x] Include Archived`.

## EC13: The "Merge Logic Mystery"

**👥 The User Story:**
Two users merge lists.
A: `[Apple, Banana]`
B: `[Carrot, Banana]`

**✅ Solution:**
**Set Union**.
Result: `[Apple, Banana, Carrot]`. Duplicates removed automatically.

## EC14: The "Stale Refresh" Loop

**👥 The User Story:**
Sandbox is full (Version 10) AND Stale.
Refresh needs a new version, but can't create one.

**✅ Solution:**
**Forced Archive**.
System prompts: *"Sandbox full. Creating a NEW refreshed sandbox for you."*

## EC15: The "Silent Breakage" (Enterprise Edit)

**👥 The User Story:**
Enterprise edits a global asset used by 20 markets.

**✅ Solution:**
**Warning Modal**.
System tells Enterprise: *"Warning: This change will mark 20 sandboxes as STALE."*
Enterprise can proceed, but they are warned.

## EC16: The "Phantom Simulation" (Queue Timing)

**👥 The User Story:**
User clicks Submit at 12:00. Job runs at 14:00.
Production changed at 13:00.

**✅ Solution:**
**Copy on SUBMIT**.
We capture the state at 12:00 exactly. That is what we test.

## EC17: The "Name Collision" (Copy-on-Write)

**👥 The User Story:**
India copies "Global_List". Belgium copies "Global_List".

**✅ Solution:**
**Suffix Scoping**.
Auto-name them `Global_List_IN` and `Global_List_BE`.

## EC18: The "Zombie Rollback"

**👥 The User Story:**
User rolls back to a version based on 6-month-old production data.

**✅ Solution:**
**Allow with Warning**.
We let them rollback, but immediately flag the sandbox as **"STALE"** so they know to refresh eventually.

## EC19: The "Version Explosion" (Storage Hog)

**👥 The User Story:**
Asset has 500 versions. Dropdown is infinite.

**✅ Solution:**
**Soft Cap in UI**.
Dropdown shows **Last 10**. User clicks "See All" to view history.

## EC20: The "Orphan Override" (FA Gate Deletion)

**👥 The User Story:**
Enterprise deletes a Gate "G1" that India has overridden.

**✅ Solution:**
**Cascade Soft Delete**.
Enterprise delete marks G1 as deleted.
System automatically marks India's override as **Inactive/Hidden**. It doesn't break, it just disappears gracefully.

---

# PART 5: OPEN QUESTIONS (Confirmed Directions)

Based on the stories above, we have effectively answered the open questions:
*   **FQ7:** Rules Auto-Update? → **NO** (Manual is safer).
*   **FQ9:** Merge = Union? → **YES**.
*   **FQ12:** Copy Timestamp? → **ON SUBMIT**.

---
*End of Detailed Narrative Document*
