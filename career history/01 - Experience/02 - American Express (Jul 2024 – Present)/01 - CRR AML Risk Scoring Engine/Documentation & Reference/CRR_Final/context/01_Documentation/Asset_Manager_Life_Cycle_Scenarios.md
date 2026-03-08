# Asset Manager: Complete Life Cycle Scenarios (Romanised Hindi)

Ye document Asset Manager ke poore life cycle ko detail mein samjhata hai. Har scenario mein **3-4 paragraphs** hain taaki sab kuch crystal clear ho jaye.

**Statuses jo use honge:**
- **DRAFT:** Asset banaya par kisi rule mein link nahi kiya
- **SANDBOX:** Asset kisi rule mein linked hai (sandbox ke andar)
- **PRODUCTION:** Sandbox promote ho gaya, live hai
- **ARCHIVED:** Purana version jo ab active nahi hai

**Key Rules (Corrected):**
1. **Pehla Sandbox sirf Enterprise:** Jab tak Enterprise production nahi hai, Market sandbox create nahi ho sakta
2. **Enterprise + Market Sath Mein:** Ek baar Enterprise production ho jaaye, Enterprise aur Market sandboxes sath mein exist kar sakte hain
3. **No Copy-on-Write:** Agar Market ko apna version chahiye, to use NAYA local asset banana padega
4. **Rebase Concept:** Jab Enterprise update ho, Markets ko manually rebase karna padega
5. **Sandbox Version Limit:** Max 10 versions per sandbox, uske baad sandbox delete karke naya banana padega

---

## **PHASE 1: ZERO STATE - JAB KUCH BHI NAHI HAI**

### Scenario 1: System bilkul khaali hai - Rebecca pehli baar login karti hai

**Context aur Problem:**
Rebecca pehli baar CRR system mein login karti hai. Abhi tak kisine bhi koi sandbox nahi banaya, koi asset nahi banaya, kuch bhi production mein nahi hai. System literally "Day 0" pe hai. Rebecca Asset Manager page kholti hai aur dekhna chahti hai ki kya available hai.

**User Experience - View Only Mode:**
Jab Rebecca Asset Manager tab pe click karti hai, use "View Only" mode dikhta hai. Is screen mein:
1. **Primary Market Dropdown (Upar):** Is dropdown mein **saare markets dikhte hain jinke access Rebecca ke paas hai** (e.g., Enterprise, India, Belgium, UK). Ye dropdown KHAALI nahi hai - user ke accessible markets hamesha dikhte hain. Default selection **Alphabetically First** market hota hai.
2. **Asset List (Neeche):** Ye list **KHAALI** hai kyunki abhi Production mein koi asset hai hi nahi. Dropdown mein market select karne se kuch nahi dikhega - list empty rahegi.
3. **Create Button:** View Only mode mein Create button **DIKHTA HI NAHI HAI** - wo GAYAB hai. Disabled nahi, bas UI mein exist hi nahi karta. Ye ensure karta hai ki user ko confuse na ho.

**System ka Logic:**
Dropdown mein markets dikhna aur list mein assets dikhna ye 2 ALAG cheezein hain. Dropdown user ke access rights se populate hota hai (ye hamesha bhara rehta hai). List Production assets se populate hoti hai (ye abhi khaali hai kyunki kuch promote nahi hua). View Only mode mein creation ka koi option hi nahi dikhta.

**Rebecca ka Next Step:**
Rebecca ko **"Sandbox" tab** mein jaana padega. Wahan se **"Create New" button click** karegi. Ek form khulega jisme sandbox details fill karni hongi. **Important:** Is stage pe Scope dropdown mein sirf **"Enterprise"** option dikhega - Market options (India, Belgium, UK) **GAYAB** honge, disabled nahi. Jab Enterprise production exist karegi tabhi Market options visible honge.

Jab Rebecca sandbox create kar legi, wo sandbox **list mein appear** hoga. Rebecca us sandbox ko **click** karegi, tab wo uske andar jayegi aur Asset Manager mein Create button visible hoga.

---

## **PHASE 2: ENTERPRISE SANDBOX BANANA AUR CONFIGURE KARNA**

### Scenario 2: Rebecca Enterprise Sandbox banati hai (Pehla aur Only Option)

**Context aur Goal:**
Rebecca ne decide kiya ki ab system setup karni hai. Wo **"Sandbox" tab** pe jaati hai.

**Step-by-Step Actions:**

**Step 1: Sandbox Tab pe Jaana**
Rebecca left navigation mein "Sandbox" tab click karti hai. Abhi sandbox list **KHAALI** hai (koi sandbox nahi banaya abhi tak).

**Step 2: Create New Click**
Rebecca **"Create New"** button click karti hai. Ek form/modal khulta hai jisme fields hain:
- **Name:** Rebecca likhti hai "Enterprise Foundation v1"
- **Description:** Rebecca likhti hai "Global baseline - common rules for all markets"
- **Scope Dropdown:** Is dropdown mein **SIRF "Enterprise (XX)" dikhta hai**. Market options (India, Belgium, UK) **GAYAB hain** - disabled nahi, simply option hi nahi dikh raha. Ye isliye kyunki abhi tak koi Enterprise production nahi hai.

Rebecca "Enterprise" select karti hai (only option) aur **"Add"** button click karti hai.

**Step 3: Sandbox List mein Appear**
System sandbox create karta hai. Ab **Sandbox list mein** ek entry dikhti hai:
```
┌───────────────────────────────────────────────────┐
│ Enterprise Foundation v1 | Status: WORKING | ... │
└───────────────────────────────────────────────────┘
```

**Step 4: Sandbox Click karke Andar Jaana**
Rebecca is sandbox entry ko **click** karti hai. Tab wo sandbox ke andar chali jaati hai. Ab:
- Screen change hoti hai - upar banner dikhta hai: "Currently in: Enterprise Foundation v1 (Status: WORKING)"
- **Configuration Selector dropdown** dikhta hai (options: Rules, Assets, Fundamental Assessment)
- Rebecca **Configuration Selector** mein se **"Assets"** select karti hai
- Ab Assets screen khulti hai jahan **Create button VISIBLE** hota hai

**State Summary:**
- Sandbox Status: **WORKING** (Draft, abhi simulate bhi nahi kiya)
- Assets inside Sandbox: Zero (Abhi tak koi asset nahi banaya)
- Enterprise Production: Does not exist yet
- Market Sandboxes: Cannot be created yet (disabled)

---

### Scenario 3: Rebecca sandbox ke andar Assets banati hai - CORRECT ASSET CREATION FLOW

**Context:**
Ab Rebecca "Enterprise Foundation v1" sandbox ke andar hai. Wo Reference Lists banana chahti hai.

---

**Asset 1 - "Global High Risk Countries" List Banana (Step-by-Step Correct Flow):**

**Step 1: Create Asset Button Click**
Rebecca Asset Manager mein jaati hai aur **"Create Asset"** button click karti hai. Ek modal/form khulta hai.

**Step 2: Basic Details Fill Karna**
Modal mein Rebecca ye fields fill karti hai:
- **Name:** "Global High Risk Countries"
- **Description:** "Countries with sanctions or high ML/TF risk"
- **Reference Data Table:** Dropdown se "Countries" select karti hai (ye master list hai jisme ALL valid countries hain)

**Step 3: File Upload**
Rebecca apni CSV file upload karti hai jisme wo countries hain jo wo is list mein daalna chahti hai:
```
high_risk_countries.csv
-----------------------
Iran
North Korea
Syria
Afghanistan
```

**Step 4: Add Button Click**
Rebecca **"Add"** button click karti hai.

**Step 5: System Validation (Reference Data Table Check)**
System har uploaded value ko **Reference Data Table "Countries"** ke against validate karta hai:
- "Iran" → ✅ Valid (Countries table mein hai)
- "North Korea" → ✅ Valid
- "Syria" → ✅ Valid
- "Afghanistan" → ✅ Valid

**Agar Sab Valid:**
System asset create kar deta hai:
- Asset Name: "Global High Risk Countries"
- Status: **DRAFT** (kyunki abhi kisi rule se linked nahi)
- Values: [Iran, North Korea, Syria, Afghanistan]
- Message: "Asset created successfully"

**Agar Koi Invalid:**
Let's say Rebecca ne "Narnia" bhi daal diya file mein:
- "Narnia" → ❌ INVALID (Countries table mein nahi hai)
- **ENTIRE FILE REJECTED**
- Error Message: "Upload failed. Invalid value: 'Narnia' is not found in Reference Data Table 'Countries'. Please correct and re-upload."
- Asset create NAHI hota, Rebecca ko file fix karke dubara upload karna padega

---

**Asset 2 - "Industry Codes" List Banana:**
Rebecca same process follow karti hai:
1. "Create Asset" click
2. Name: "Industry Codes", Description fill, Reference Table: "Industries" select
3. `industry_codes.csv` upload (500 rows)
4. "Add" click
5. System validates all 500 values against "Industries" reference table
6. Agar sab valid → Asset created, Status **DRAFT**
7. Agar koi invalid → File reject, error message

---

**Asset 3 - Fundamental Assessment (FA) - Alag Workflow:**
FA ka workflow different hai. FA mein file upload nahi hoti. Yahan:
1. 6 Gates hain (Geography, Industry, Product, Structure, Occupation, Acquisition Channel)
2. Har gate mein Attributes hain (e.g., Geography gate mein "Venezuela", "Iran", etc.)
3. Har attribute ke liye 10 Questions answer karne hote hain (Yes/No)
4. Rebecca "Venezuela" select karti hai aur questions answer karti hai
5. "Calculate" button click karti hai → Score compute hota hai
6. Save karti hai → Status **DRAFT**

---

**Current State After Asset Creation:**
- Sandbox: "Enterprise Foundation v1" - Status **WORKING**
- Asset 1: "Global High Risk Countries" - Status **DRAFT** (Not linked to any rule yet)
- Asset 2: "Industry Codes" - Status **DRAFT** (Not linked to any rule yet)
- Asset 3: FA Changes - Status **DRAFT**
- Enterprise Production: Does not exist

**Key Insight:**
Asset creation flow hai: Create → Name/Desc/RefTable → File Upload → Add → Validate → Success/Error. Validation Reference Data Table ke against hoti hai. Invalid values se poori file reject ho jaati hai.

---

### Scenario 4: Rebecca Rule banati hai jo Asset ko link karta hai - Status DRAFT se SANDBOX banta hai

**Context:**
Rebecca ne 3 assets bana liye hain. Ab wo ek rule banana chahti hai jo "Global High Risk Countries" list use kare.

**Rule Creation Process:**
Rebecca Rule Configuration section mein jaati hai. Wo navigate karti hai: Geographic Risk → Country of Residence → Add New Ruleset. Ruleset create karne ke baad, wo Add Rule click karti hai. Rule builder mein:
1. **Datapoint:** "Customer_Jurisdiction" (customer ka data field)
2. **Operator:** "IN" (is one of)
3. **Value:** Dropdown se "Global High Risk Countries" (Asset A001) select karti hai

Rebecca "Save Rule" click karti hai.

**Status Change Magic:**
Jaise hi ye rule save hota hai, kuch important hota hai peeche:
- Asset "Global High Risk Countries" link ho gaya ek active rule se
- **Status change:** DRAFT → **SANDBOX**
- Ab ye asset is sandbox ka official part ban gaya

**Why This Matters:**
DRAFT status ka matlab tha "orphan asset, kisi ke kaam nahi aa raha". SANDBOX status ka matlab hai "is sandbox mein actively use ho raha hai". Agar sandbox promote hoga, to ye asset bhi promote hoga. Agar sandbox reject/delete hoga, to is asset ka future uncertain hai.

**State After Linking:**
- Asset "Global High Risk Countries" - Status **SANDBOX** (linked to Rule RS001)
- Asset "Industry Codes" - Status **DRAFT** (still not used)
- Sandbox - Status **WORKING**

---

### Scenario 5: Rebecca Simulation submit karti hai - Snapshot liya jaata hai

**Context:**
Rebecca ne framework complete kar liya hai - rules banaye, assets link kiye. Ab wo test karna chahti hai ki ye configuration real customers pe kaise behave karegi.

**User Action:**
Rebecca "Submit for Simulation" button click karti hai. Ek confirmation modal aata hai jo summary dikhata hai:
- Rules Created: 15
- Assets Used: 2 (High Risk Countries, Industry Codes)
- FA Changes: 3 attributes updated
- Status will change to: IN_PROGRESS

Rebecca comment likhti hai: "Initial Enterprise setup for AML compliance" aur Submit click karti hai.

**System Response - Snapshot Mechanism:**
Ye bahut important step hai. Jaise hi Submit hota hai:
1. System current configuration ka **SNAPSHOT** le leta hai
2. Is snapshot mein EXACTLY record hota hai ki kaunse asset versions, kaunsi rules use ho rahi hain
3. Sandbox status: WORKING → **IN_PROGRESS**
4. Ab tak sab kuch FROZEN hai - Rebecca kuch edit nahi kar sakti jab tak simulation complete na ho

**Why Snapshot at Submit Time, Not Simulation Start Time?**
Kyunki simulation queue mein lag sakti hai. Agar snapshot tab lein jab simulation actually run hota hai, to beech ke time mein koi aur change kar sakta tha. Submit time pe snapshot ensure karta hai ki jo tumne click kiya wahi test hoga.

**State During Simulation:**
- Sandbox: "Enterprise Foundation v1" - Status **IN_PROGRESS**
- All editing: **DISABLED** (frozen)
- Assets Status: Unchanged (still SANDBOX)
- Simulation: Running on full customer population

---

### Scenario 6: Simulation Complete - Rebecca Results Review karti hai

**Context:**
Simulation complete ho gayi. Rebecca ko results dikhte hain.

**Results Summary:**
- Total customers scored: 5,00,000
- High Risk: 15,000 (3%)
- Medium Risk: 85,000 (17%)
- Low Risk: 4,00,000 (80%)
- Breakdown by rule available

Rebecca results dekh ke satisfied hai. Wo "Implement" click karti hai.

**Approval Flow:**
- Status: IN_PROGRESS → **PENDING_APPROVAL_1**
- Jake (First Approver) ko notification jaati hai
- Jake review karke "Approve" click karta hai
- Status: PENDING_APPROVAL_1 → **PENDING_APPROVAL_2**
- Sarah (Second Approver) ko notification jaati hai
- Sarah approve karti hai

**Final Action - Promote to Production:**
Sarah "Approve and Implement" click karti hai.

---

### Scenario 7: Enterprise Sandbox Promote hota hai - Everything Goes PRODUCTION

**The Big Moment:**
Jab second approval milti hai, system ek **ATOMIC TRANSACTION** execute karta hai. Matlab ye sab kuch ek hi operation mein hota hai - agar koi ek step fail ho, to sab rollback ho jaata hai.

**What Happens in Atomic Promotion:**
1. **All Rules** jo sandbox mein the → Enterprise Production mein jaate hain
2. **All Assets** jo SANDBOX status mein the → **PRODUCTION** status mein jaate hain
3. **FA Changes** → Production mein reflect hote hain
4. **Sandbox Status:** WORKING → **IMPLEMENTED** (historical record ban jaata hai)

**Asset Status Changes:**
| Asset | Before Promotion | After Promotion |
|-------|-----------------|-----------------|
| Global High Risk Countries | SANDBOX | **PRODUCTION** |
| Industry Codes (if linked) | SANDBOX | **PRODUCTION** |
| Industry Codes (if NOT linked) | DRAFT | DRAFT (unchanged) |

**Critical Result:**
Ab Enterprise Production **EXISTS**. Ye bahut important hai kyunki:
- Ab "View Only" mode mein ye assets sabko dikhenge
- Ab Market sandbox creation ka option **ENABLED** ho jaayega
- Ye assets ab "Global Truth" hain jo sab inherit karenge

**State After Promotion:**
- Enterprise Production: **ACTIVE** (Live, scoring customers)
- Sandbox: "Enterprise Foundation v1" - Status **IMPLEMENTED** (Read-only history)
- Assets in Production: High Risk Countries v1, Industry Codes v1 (if used)
- Market Sandboxes: Now **AVAILABLE** for creation

---

## **PHASE 3: MARKET SANDBOX CREATION (JAB ENTERPRISE PRODUCTION HAI)**

### Scenario 8: Alex (India MCO) pehla Market Sandbox banata hai

**Context - System State:**
- Enterprise Production: **EXISTS** ✓
- Enterprise Sandbox: None (previous one was implemented)
- Available for Sandbox Creation: Enterprise ✓, India ✓, Belgium ✓, UK ✓ (all enabled now)

**User Action:**
Alex login karta hai. Wo "Create New Sandbox" click karta hai. Ab dropdown mein sab options available hain! Alex "India (IN)" select karta hai.
- Name: "India Framework v1"
- Scope: India

Alex "Add" click karta hai.

**System Response - Inheritance:**
Jab India sandbox create hota hai, kuch automatic hota hai:
1. System Enterprise Production se saari rules COPY karta hai (as baseline)
2. System Enterprise Production ke assets ko **REFERENCE** karta hai (not copy)
3. India sandbox ab Enterprise ka "child" hai - parent ki properties inherit karti hai

**Alex ka View in Sandbox:**
Jab Alex Asset Manager kholega:
- "Global High Risk Countries" dikhega - par **READONLY** (Gray icon, Edit disabled)
- "Industry Codes" dikhega - par **READONLY**
- Ye Enterprise Production ke assets hain - Alex inhe directly edit nahi kar sakta

**Why Readonly?**
Kyunki ye Enterprise ke assets hain. Agar Alex inhe edit kare, to wo Enterprise Production pe impact daalega jo allowed nahi hai. India ke paas 2 options hain:
1. **Use as-is:** Enterprise asset ko reference karo apni rules mein
2. **Create Local:** Apna separate India-only asset banao

**State After India Sandbox Creation:**
- Enterprise Production: Unchanged (still active)
- India Sandbox: "India Framework v1" - Status **WORKING**
- Inherited Enterprise Assets: Visible but Readonly in India Sandbox
- India's Own Assets: Zero (not created yet)

---

### Scenario 9: Alex NAYA Local Asset banata hai (instead of Copy-on-Write)

**Context:**
Alex ko ek India-specific list chahiye - "India Local PEP List" (Politically Exposed Persons). Ye list sirf India ke liye relevant hai, doosre countries ko nahi chahiye.

**Important Design Decision - No Copy-on-Write:**
Humara system Copy-on-Write support NAHI karta. Iska matlab:
- Alex Enterprise ke "Global High Risk Countries" asset ka copy nahi bana sakta
- Agar Alex ko different values chahiye, to use **NAYA ALAG ASSET** banana padega
- Ye new asset India-scoped hoga

**User Action:**
Alex Asset Manager mein jaata hai aur "Create New List" click karta hai:
- Name: "India Local PEP List"
- Description: "Politically Exposed Persons specific to India"
- Reference Table: "Customer Names" (or appropriate)
- Scope: **India** (automatically set kyunki sandbox India ka hai)

Alex names add karta hai aur Save click karta hai.

**Status Flow:**
1. Asset created: Status = **DRAFT**
2. Alex is asset ko ek India-specific rule mein link karta hai
3. Status change: DRAFT → **SANDBOX**

**Key Insight - No Relationship with Enterprise Asset:**
"India Local PEP List" ka "Global High Risk Countries" se koi connection nahi hai. Ye completely independent assets hain. Agar kal ko Enterprise apna asset update kare, India ke local asset pe koi impact nahi padega (aur vice versa).

**State After Local Asset Creation:**
- Enterprise Assets (in India sandbox): Readonly (Global High Risk Countries, etc.)
- India Local Asset: "India Local PEP List" - Status **SANDBOX** (linked to rule)
- Visibility: India's asset sirf India ko dikhega, Enterprise/UK/Belgium ko nahi

---

### Scenario 10: Concurrent Work - Enterprise aur India Sandbox Sath Mein Exist Karte Hain

**Context - This is Now Allowed:**
Humara updated system Enterprise aur Market sandboxes ko sath mein exist karne deta hai. Ye production environments ke parallel development allow karta hai.

**Current State:**
- Enterprise Production: Active
- India Sandbox: "India Framework v1" - Status WORKING (Alex working)
- Enterprise Sandbox: Rebecca wants to create one

**Rebecca Creates Enterprise Sandbox:**
Rebecca "Create New Sandbox" click karti hai:
- Name: "Enterprise Update - Q2 Regulatory Changes"
- Scope: Enterprise

System sandbox create karta hai. Ab dono sandboxes sath mein exist karte hain!

**What Each User Sees:**
| User | Sandbox | Enterprise Assets (Prod v1) | India Local Assets |
|------|---------|---------------------------|-------------------|
| Rebecca (Enterprise SB) | Enterprise Update | Edit allowed (create new version) | Not visible |
| Alex (India SB) | India Framework v1 | Readonly | Edit allowed |

**No Immediate Conflict:**
Jab tak koi promote nahi karta, dono apne apne sandboxes mein peacefully kaam kar sakte hain. Par jab promotion hogi, tab situation interesting hogi (Scenario 14-16 mein dekhenge).

---

### Scenario 11: Alex Enterprise Asset ko Rule mein USE karta hai (Reference, not Edit)

**Context:**
Alex ko "Global High Risk Countries" list use karni hai apni India-specific rule mein. Wo edit nahi karna chahta, sirf reference karna chahta hai.

**User Action:**
Alex Rule Configuration mein jaata hai. Naya rule banata hai:
- Datapoint: "Customer_Jurisdiction"
- Operator: "IN"
- Value: Dropdown se **"Global High Risk Countries"** select karta hai

**This is Allowed!**
Enterprise asset ko reference karna (read-only use) allowed hai. Alex basically keh raha hai "mere rule mein check karo ki customer ka country Enterprise ki list mein hai ya nahi".

**Status Nuance:**
- Enterprise Asset "Global High Risk Countries": Status **PRODUCTION** (unchanged)
- Ye asset ab India sandbox mein bhi referenced hai, par ownership Enterprise ki hai

**What Happens if Enterprise Updates This Asset?**
Ye interesting hai. Agar Rebecca Enterprise sandbox mein is asset ka new version (v2) banaye aur promote kare:
- Enterprise Production: Uses v2
- India Sandbox: **STALE** ho jaayega - wo abhi bhi v1 reference kar raha tha

Ye **REBASE** scenario hai - Scenario 14 mein detail mein dekhenge.

---

## **PHASE 4: PARALLEL EDITING AUR VERSIONING**

### Scenario 12: Rebecca Enterprise Asset ka new version banati hai (Versioning)

**Context:**
Rebecca "Enterprise Update" sandbox mein hai. Wo "Global High Risk Countries" mein "Russia" add karna chahti hai.

**Versioning Process:**
Enterprise Production mein asset hai: "Global High Risk Countries" v1 (Status: PRODUCTION)
Rebecca is asset pe click karti hai → "Edit" ya "Create New Version" button dikhta hai

Rebecca click karti hai. System peeche ye karta hai:
1. v1 ka content copy karta hai
2. New version create karta hai: **v2** (Status: **DRAFT**)
3. v2 ko Rebecca ke Enterprise sandbox se link karta hai
4. v1 unchanged rehta hai (still PRODUCTION, still being used everywhere)

**Important Status Point:**
New version v2 abhi DRAFT hai, SANDBOX nahi. Kyunki wo abhi kisi rule se linked nahi hai - Rebecca ne sirf content copy kiya.

**Rebecca Edits and Links:**
1. Rebecca v2 mein "Russia" add karti hai
2. Rebecca rule update karti hai to point to v2 (implicit, rule automatically uses sandbox version)
3. v2 Status: DRAFT → **SANDBOX** (now linked to rule in sandbox)

**State Summary:**
| Asset | Version | Status | Used By |
|-------|---------|--------|---------|
| Global High Risk Countries | v1 | PRODUCTION | Enterprise Prod, India Sandbox (reference) |
| Global High Risk Countries | v2 | SANDBOX | Enterprise Sandbox (Rebecca's) |

**Two Versions Exist Simultaneously:**
v1 (Production) aur v2 (Sandbox) sath mein exist kar rahe hain. Real customers abhi bhi v1 pe score ho rahe hain. v2 sirf testing/development ke liye hai.

---

### Scenario 13: Rebecca Enterprise Sandbox Promote karti hai - Old Version Archived

**Context:**
Rebecca ne v2 complete kar liya. Simulation pass. Approvals mil gayi. Ab promote karna hai.

**Promotion Process:**
1. Jake aur Sarah approve karte hain
2. System **ATOMIC TRANSACTION** execute karta hai:
   - "Global High Risk Countries" v2: Status SANDBOX → **PRODUCTION**
   - "Global High Risk Countries" v1: Status PRODUCTION → **ARCHIVED**
   - Enterprise Sandbox: WORKING → **IMPLEMENTED**

**ARCHIVED Status Explained:**
v1 ab archived hai. Iska matlab:
- v1 ab active nahi hai
- Koi rule v1 use nahi karegi (automatically v2 pe switch)
- v1 abhi bhi database mein hai for audit trail
- UI mein v1 hidden hai by default (but "Show Archived" se dikh sakta hai)

**Critical Impact - Single Active Version Rule:**
Ab sirf v2 PRODUCTION hai. **Saare scopes** (Enterprise, India, Belgium, UK) jo is asset ko reference kar rahe the, wo ab automatically v2 use karenge. Koi choice nahi hai - latest PRODUCTION version hi active hota hai.

**State After Promotion:**
| Asset | Version | Status |
|-------|---------|--------|
| Global High Risk Countries | v1 | ARCHIVED |
| Global High Risk Countries | v2 | PRODUCTION |

---

## **PHASE 5: REBASE SCENARIOS (JAB ENTERPRISE UPDATE HO AUR MARKET STALE HO)**

### Scenario 14: India Sandbox STALE ho jaata hai - Rebase Required

**Context - The Problem:**
- India Sandbox "India Framework v1" created on Day 1
- At that time, Enterprise had "Global High Risk Countries" v1
- India sandbox references v1
- On Day 5, Enterprise promoted v2 (added Russia)
- India sandbox is now **STALE** - it was based on v1, but v2 is now PRODUCTION

**What Alex Sees:**
Jab Alex apna India sandbox kholega, system use warning dikhayega:
```
⚠️ BASE CONFIGURATION CHANGED

The Enterprise Production has been updated since this sandbox was created.
Your sandbox is based on an outdated version.

Changed Items:
- Global High Risk Countries: v1 → v2 (Russia added)

[REBASE NOW]    [CONTINUE ANYWAY]    [VIEW CHANGES]
```

**Option 1 - Continue Anyway (Not Recommended):**
Alex ignore kar sakta hai aur kaam continue kar sakta hai. Par jab wo promote karega:
- System warning dega: "Your sandbox uses outdated Enterprise assets"
- Approver ko ye information dikhegi
- Risk hai ki India production outdated ho jayega

**Option 2 - Rebase (Recommended):**
Alex "REBASE NOW" click karta hai. System kya karta hai:
1. India sandbox ki baseline update hoti hai to v2
2. India ke local assets/rules unchanged rehte hain
3. Jo rules Enterprise assets reference kar rahi thi, wo ab v2 use karengi
4. Alex ko verify karna chahiye ki rebase ke baad sab sahi hai

**After Rebase:**
- India Sandbox: Now based on Enterprise v2 (current)
- India's local assets: Unchanged
- Status: WORKING (can continue working)

**Technical Nuance:**
Rebase sirf "reference update" hai. India ka koi local asset copy nahi ho raha - wo sirf enterprise ke latest version ko point kar raha hai ab.

---

### Scenario 15: Multiple Markets Stale - Coordinated Rebase

**Context:**
- Enterprise promoted v2
- India Sandbox: Created before v2, needs rebase
- UK Sandbox: Created before v2, needs rebase
- Belgium Sandbox: Created AFTER v2, already on latest

**Each Market Team's Responsibility:**
Har market MCO ko apna apna rebase karna padega. Enterprise team sirf notify kar sakti hai, force nahi kar sakti.

**Communication Flow:**
1. Enterprise promotes v2
2. System automatically sab active Market sandboxes ko check karta hai
3. Jo stale hain unhe flag karta hai
4. Market MCOs ko notification jaati hai

**Worst Case - Market Ignores Rebase:**
Agar India rebase nahi karta aur promote kar deta hai:
- India Production: Based on v1 (outdated)
- Enterprise Production: Based on v2 (current)
- **INCONSISTENCY** - India customers different rules pe score ho rahe hain

Ye allowed hai (system force nahi karta), par highly discouraged hai.

---

## **PHASE 6: CONCURRENT EDITING CONFLICTS**

### Scenario 16: Two Users Same Sandbox, Same Asset - Edit Conflict

**Context:**
Rebecca aur Sarah dono "Enterprise Update v2" sandbox mein kaam kar rahe hain. Dono same asset "Global High Risk Countries" edit karna chahte hain.

**Timeline:**
- T1 (10:00 AM): Rebecca asset kholti hai, sees v2 content
- T2 (10:05 AM): Sarah asset kholti hai, sees v2 content (same as Rebecca)
- T3 (10:10 AM): Sarah "Cuba" add karti hai aur Save click karti hai → v3 created, Status SANDBOX
- T4 (10:15 AM): Rebecca "Myanmar" add karti hai aur Save click karti hai → **CONFLICT!**

**System Detection (Optimistic Locking):**
System detect karta hai ki Rebecca ne v2 pe edit kiya, par ab v3 exist karta hai. Rebecca ka expected version (v2) actual version (v3) se match nahi karta.

**Conflict Resolution UI:**
```
┌─────────────────────────────────────────────────────────────────┐
│                    CONFLICT DETECTED!                            │
│                                                                  │
│  This asset was modified by Sarah at 10:10 AM.                  │
│                                                                  │
│  YOUR CHANGES:              CURRENT STATE (Sarah's):            │
│  + Added: Myanmar           + Added: Cuba                        │
│                                                                  │
│  [MERGE BOTH]    [KEEP MINE]    [USE CURRENT]    [CANCEL]       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Options Explained:**
1. **MERGE BOTH:** System creates v4 with both Cuba AND Myanmar. Best option when changes are non-overlapping.
2. **KEEP MINE:** Discard Sarah's Cuba, keep only Myanmar. Creates v4 with Myanmar only. Sarah ka kaam gayab.
3. **USE CURRENT:** Discard my Myanmar, accept Sarah's Cuba. Rebecca ka kaam gayab.
4. **CANCEL:** Go back to editing, decide later.

---

### Scenario 17: Two Users Different Sandboxes, Same Enterprise Asset - No Conflict Initially

**Context:**
- Rebecca: Enterprise Sandbox, editing "Global High Risk Countries"
- Alex: India Sandbox, editing... wait, Alex can't edit Enterprise assets!

**Reminder - No Copy-on-Write:**
Alex cannot create a version of Enterprise asset. Alex can only:
1. Reference it as-is (readonly)
2. Create a completely NEW India-scoped asset

**So This Conflict Cannot Happen:**
Enterprise assets sirf Enterprise sandbox mein edit ho sakte hain. Market sandboxes mein ye readonly hain. Isliye "two users editing same asset in different sandboxes" scenario possible hi nahi hai for Enterprise assets.

**But What About Market Assets?**
Agar India creates asset "India PEP List", aur UK bhi use karna chahta hai:
- UK can reference India's PRODUCTION asset (if India promoted it)
- UK cannot edit India's asset (it's India-scoped)
- UK would need to create their own "UK PEP List"

---

### Scenario 18: Same User, Multiple Browser Tabs - Self Conflict

**Context:**
Rebecca ne 2 browser tabs khol rakhe hain. Dono mein same asset open hai.

**Timeline:**
- Tab 1: Rebecca opens asset v2
- Tab 2: Rebecca opens same asset v2
- Tab 1: Rebecca adds "Iran", saves → v3 created
- Tab 2: Rebecca adds "Cuba", saves → CONFLICT (same as Scenario 16)

**System Behavior:**
System doesn't care ki same user hai ya different. Conflict detection mechanism same hai. Rebecca ko same resolution UI dikhega.

**Prevention Tip:**
System could show: "You have this asset open in another tab/window" as a warning. But it's not a blocker.

---

### Scenario 19: Asset Edit vs Asset Delete - Race Condition

**Context:**
- Rebecca is editing asset "Industry Codes" (creating v2)
- Sarah wants to DELETE this asset entirely

**Sarah's Delete Attempt:**
Sarah "Industry Codes" pe right-click → Delete. System checks:
1. Is this asset linked to any rule? → Yes (let's say RS005)
2. **BLOCKED:** "Cannot delete - asset is used in rule RS005"

**Even if Not Linked to Rule:**
If "Industry Codes" was DRAFT status (not used anywhere):
- Sarah could potentially delete it
- But Rebecca is actively editing it
- System should track "editing sessions" and block delete during active edit

**Resolution:**
- Rule-linked assets: Always blocked from deletion
- DRAFT assets: Blocked if someone is actively editing

---

### Scenario 20: Promotion Race - Two Sandboxes Try to Promote Same Asset Version

**Context:**
Rare but possible:
- Enterprise Sandbox A: Created v2 of "Global High Risk Countries", ready to promote
- Enterprise Sandbox B: Also created v2 of same asset (different changes), ready to promote

Wait - can two Enterprise sandboxes exist simultaneously?

**Answer - No (One Sandbox Per Scope Rule):**
At any given time, only ONE sandbox can exist per scope. You cannot have two Enterprise sandboxes active simultaneously. Same for each market.

**So This Scenario is IMPOSSIBLE:**
If Rebecca has Enterprise Sandbox, Sarah cannot create another Enterprise Sandbox until Rebecca's sandbox is either:
1. Promoted (becomes IMPLEMENTED)
2. Rejected/Deleted (goes away)

**Market Sandboxes - Different Rule:**
Multiple market sandboxes CAN exist (India + UK + Belgium simultaneously). But they don't edit same assets, so no conflict.

---

## **PHASE 7: DELETION AUR SANDBOX LIFECYCLE**

### Scenario 21: Asset ko Delete karna - Blocking Rules

**Context:**
Rebecca wants to delete "Industry Codes" asset.

**Case A - Asset is PRODUCTION and Linked to Rules:**
- Delete button click
- System: "Cannot delete. This asset is used in 3 active rules."
- List of rules shown
- **BLOCKED** - Rebecca must first unlink from all rules

**Case B - Asset is PRODUCTION but Not Linked:**
This is rare (promoted but not used? Shouldn't happen). But if it does:
- Delete button click
- Confirmation: "This asset is in PRODUCTION. Deleting will archive it."
- Rebecca confirms → Status: PRODUCTION → **ARCHIVED**

**Case C - Asset is DRAFT:**
- Not linked to any rule
- Delete button click
- Confirmation: "Delete this draft asset?"
- Rebecca confirms → Asset record deleted (hard delete since never used)

**Case D - Asset is SANDBOX:**
- Linked to rule in current sandbox only
- Delete button click
- System: "This will also remove the asset from linked rules in this sandbox."
- Rebecca confirms → Asset unlinked from rules, then deleted

**No Auto-Archive for Orphaned Assets:**
Humara system automatically orphaned assets ko archive NAHI karta. Agar koi asset bahut time se unused hai, wo waise hi DRAFT status mein pada rahega jab tak manually delete na karo.

---

### Scenario 22: Sandbox Version Limit - 10 Versions, Phir Delete

**Context:**
Sandbox "India Framework v1" mein bahut iterations hui hain:
- V1: Initial creation
- V2: First simulation submit
- V3: Changes after feedback
- ... continues ...
- V10: Final changes

**What Happens at V11 Attempt:**
```
┌─────────────────────────────────────────────────────────────────┐
│                    VERSION LIMIT REACHED                        │
│                                                                  │
│  This sandbox has reached the maximum of 10 versions.           │
│                                                                  │
│  To continue working, you must:                                 │
│  1. Delete this sandbox (changes will be lost)                  │
│  2. Create a new sandbox                                        │
│                                                                  │
│  [DELETE AND CREATE NEW]    [CANCEL]                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**What Happens on Delete:**
1. Current sandbox v10 → Status: **DELETED**
2. All draft assets that were only in this sandbox → DELETED
3. Alex creates new sandbox "India Framework v2"
4. New sandbox starts fresh from Enterprise Production baseline
5. Alex will need to recreate his India-specific changes

**Why This Limit?**
10 versions ensure ki sandboxes don't become cluttered. Agar 10 iterations mein final state nahi mili, to shayad approach re-think karna chahiye.

---

### Scenario 23: Sandbox Rejection ka Impact on Assets

**Context:**
Alex ne "India Framework v1" sandbox submit kiya. Jake review karke **REJECT** karta hai (maybe compliance issue).

**System Actions on Rejection:**
1. Sandbox Status: TESTING_COMPLETED → **REJECTED**
2. All assets that were SANDBOX status in this sandbox: **Remain SANDBOX** (not auto-deleted)
3. Alex can either:
   - Make changes and re-submit (if within 10 version limit)
   - Delete sandbox and start fresh

**Important - Assets Don't Auto-Delete on Rejection:**
Rejection ka matlab "not approved", deletion nahi. Assets abhi bhi exist karte hain sandbox mein. Alex unhe edit karke dubara submit kar sakta hai.

---

### Scenario 24: Sandbox Delete karne pe Assets ka kya hota hai

**Context:**
Alex decides to delete "India Framework v1" sandbox (maybe starting fresh).

**Case A - Assets were ONLY used in this sandbox:**
- "India Local PEP List" was created in this sandbox
- Status was SANDBOX
- On sandbox delete: Asset gets **DELETED** (hard delete, it was never promoted)

**Case B - Assets were Enterprise (referenced):**
- "Global High Risk Countries" was referenced from Enterprise Production
- On sandbox delete: **NO IMPACT** on Enterprise asset (it's still PRODUCTION, owned by Enterprise)

**Case C - Assets were DRAFT in sandbox:**
- Some unused asset existed
- On sandbox delete: Depends on scope
  - If India-scoped DRAFT: Gets deleted (orphan cleanup)
  - If Enterprise-scoped DRAFT: Remains (belongs to Enterprise)

**Key Point:**
Sandbox delete sirf sandbox-specific cheezein delete karta hai. Production assets completely safe rehte hain.

---

## **PHASE 8: ADVANCED SCENARIOS**

### Scenario 25: Rollback Within Sandbox - Go Back to Previous Version

**Context:**
India Sandbox v5 mein Alex ne kuch galti kar di. Wo v3 pe wapas jaana chahta hai.

**User Action:**
Alex "Version History" button click karta hai. Timeline dikhti hai:
- v5: Current (buggy)
- v4: Previous attempt
- v3: Stable version
- v2: Initial simulation
- v1: Creation

Alex v3 select karke "Rollback to This Version" click karta hai.

**System Response:**
```
┌─────────────────────────────────────────────────────────────────┐
│                    ROLLBACK CONFIRMATION                        │
│                                                                  │
│  You are about to rollback to Version 3.                        │
│                                                                  │
│  This will:                                                      │
│  - Restore configuration state from v3                          │
│  - Create a new version v6 (rollback always creates new)        │
│  - Changes in v4 and v5 will remain in history                  │
│                                                                  │
│  [ROLLBACK TO V3]    [CANCEL]                                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Result:**
- v6 created with v3's content
- v4 and v5 still exist in history (not deleted)
- Alex is now working on v6

---

### Scenario 26: Enterprise Rollback - Impact on Markets

**Context:**
Enterprise promoted v3, but it caused issues. Rebecca wants to rollback to v2.

**Process:**
1. Rebecca creates new Enterprise Sandbox
2. Opens "Global High Risk Countries" version history
3. Selects v2 and clicks "Rollback to v2"
4. System creates v4 with v2's content
5. Rebecca promotes sandbox
6. v4 becomes PRODUCTION, v3 becomes ARCHIVED

**Impact on Markets:**
- All markets were using v3
- After promotion, all markets automatically use v4 (which has v2's content)
- Markets don't need to do anything - automatic switch

**Key Insight:**
Rollback is technically "forward promotion of old content". Version numbers always go forward (v4, not back to v2).

---

### Scenario 27: Audit Trail - Who Changed What When

**Context:**
Jake (Compliance Officer) wants to investigate who added "Russia" to High Risk Countries.

**System Feature - Audit Log:**
Jake goes to Asset → "Global High Risk Countries" → Audit History tab

```
VERSION HISTORY:
─────────────────────────────────────────────────────────────────
v4 | 2025-01-20 | Rebecca | Rollback to v2 content
v3 | 2025-01-15 | Rebecca | Added: Russia, Belarus | ARCHIVED
v2 | 2025-01-10 | Rebecca | Added: Afghanistan | ARCHIVED  
v1 | 2025-01-01 | Rebecca | Initial creation | ARCHIVED

DETAILED LOG FOR v3:
─────────────────────────────────────────────────────────────────
2025-01-15 09:00 | Rebecca | Created version v3 from v2
2025-01-15 09:15 | Rebecca | Added value: Russia
2025-01-15 09:16 | Rebecca | Added value: Belarus
2025-01-15 10:00 | Rebecca | Submitted for simulation
2025-01-15 14:00 | Jake    | Approved
2025-01-15 14:01 | Sarah   | Approved (final)
2025-01-15 14:02 | SYSTEM  | Promoted to Production
```

---

## **SUMMARY: KEY PRINCIPLES**

**1. Enterprise First, Always:**
- First sandbox must be Enterprise
- Markets cannot exist without Enterprise Production

**2. Coexistence Allowed:**
- Enterprise Sandbox + Market Sandboxes can exist simultaneously
- But only ONE sandbox per scope at any time

**3. Clear Status Flow:**
```
DRAFT ──(link to rule)──► SANDBOX ──(promote)──► PRODUCTION
                              │                       │
                              │                       └──(new version)──► ARCHIVED
                              │
                              └──(unlink all)──► Back to DRAFT (rare)
```

**4. No Copy-on-Write:**
- Markets cannot copy Enterprise assets
- Markets must create NEW local assets if they need different values

**5. Rebase is Manual:**
- When Enterprise updates, Markets become STALE
- Markets must manually REBASE to get updates
- System warns but doesn't force

**6. Production Safety:**
- Sandbox delete/reject doesn't affect Production
- Only successful promotion changes Production

**7. Sandbox Limits:**
- Maximum 10 versions per sandbox
- After 10, must delete and create new
