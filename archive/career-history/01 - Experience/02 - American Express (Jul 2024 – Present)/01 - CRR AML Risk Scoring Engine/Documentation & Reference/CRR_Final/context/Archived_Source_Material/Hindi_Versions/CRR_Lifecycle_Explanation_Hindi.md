# CRR Lifecycle ki Poori Kahani (Detailed Explanation)

**Document Version:** 1.0
**Created:** 2026-01-21
**Purpose:** CRR ke pure process ko detail mein samjhna, ekdum simple bhasa mein.

---

# PART 1: SYSTEM KAISE KAAM KARTA HAI (Detailed Kahani) ✅

## 1.1 Core System Architecture (Buniyadi Dhancha)

Dekho bhai, CRR system ko tum ek bade **Ped (Tree)** ki tarah samjho. Iska structure upar se neeche aise chalta hai:

1.  **Risk Framework:** Ye sabse upar hai. Ye decide karta hai ki hum kis "Market" (Country) ki baat kar rahe hain. Jaise India ka risk framework alag ho sakta hai aur Belgium ka alag.
2.  **Risk Categories:** Har framework ke andar 5 moti-moti categories hoti hain jahan se risk aa sakta hai:
    *   **Customer:** Grahak kaisa hai?
    *   **Geography:** Wo kahan rehta hai ya business karta hai?
    *   **Transactions:** Paise ka len-den kaisa hai?
    *   **Products & Services:** Wo humse kya khareed raha hai?
    *   **ARFs & HROs:** Ye kuch special high-risk indicators hote hain.
3.  **Risk Elements:** Categories ke andar specific chizein hoti hain. Jaise "Geography" category mein ek element ho sakta hai "Country of Residence".
4.  **Rulesets:** Har element ke andar kuch rules ka group hota hai.
5.  **Rules:** Ye wo actual logic hai. Jaise: "Agar Customer ki country = 'Iran' hai, toh High Risk maano".

### Scope Model (Matlab ye kiske liye hai?)
Har cheez ka ek "Scope" hota hai, yani wo kahan lagu hoga:
*   **`XX` (Enterprise/Global):** Ye "Bhagwan" rules hain. Ye sab jagah lagu hote hain jab tak koi market apna khud ka rule na bana le.
*   **`IN` (India):** Sirf India ke liye.
*   **`BE` (Belgium):** Sirf Belgium ke liye.

---

## 1.2 Sandbox Lifecycle (Sandbox ki Kahani)

**Sandbox kya hai?**
Socho tumhe ek drawing banani hai, lekin tum original painting kharab nahi karna chahte. Toh tum ek **Tracing Paper (Sandbox)** lete ho. Wahan jo marzi changes karo, original (Production) safe rahega. Jab tumhari drawing final ho jaye, tabhi hum use original pe chapenge.

**Process kaise chalta hai:**

1.  **WORKING (Draft):** Kacha kaam. Yahan koi rok-tok nahi.
2.  **SUBMIT (Simulation ke liye bhejna):** "Test karo". Comment likhna zaroori hai.
3.  **IN_PROGRESS (Simulation chal Rahi hai):** System naye rules ko purane data pe test karta hai.
4.  **TESTING COMPLETED:** Result dekho. Kharab hai toh naya version dalo, acha hai toh "Implement" karo.
5.  **APPROVALS (Boss ki manzoori):** Pehle Level 1, phir Level 2. Dono haan bolenge tabhi Production mein jayega.

---

## 1.3 Asset Lifecycle (Lists ki Kahani)

**Asset matlab?** Asset bas ek "List" hoti hai (Jaise "High Risk Countries"). Rules inhi lists ko padhke decision lete hain.

**Editability Matrix (Kab edit kar sakte hain?):**
*   **Agar tum Enterprise mein ho:** Sab kuch edit kar lo (Versioning hogi).
*   **Agar tum Market (India) mein ho:**
    *   Agar Asset **sirf tumhare market** mein use ho raha hai -> Edit kar lo.
    *   Agar Asset **dusre markets** mein bhi use ho raha hai -> **STOP!** Tum edit nahi kar sakte. Uski Copy banao.

---

## 1.4 Localisation Flow (Apna Rule Banana)

**Example:**
Enterprise (`XX`) ka rule hai: *"Income < 5000 = High Risk"*
India (`IN`) chahta hai: *"Income < 10000 = High Risk"*

Jab India wala us rule ko edit karega:
1.  System Enterprise waale rule ko **Copy** karke India (`IN`) ka naya rule bana dega.
2.  Ab India ke liye 2 rules hain: Ek Global, ek India wala.
3.  Lekin system hamesha **Local (India)** wala rule pehle maanega.

---

## 1.5 Concurrent Edit (Jab 2 log ek saath kaam karein)

Imagine karo tum aur tumhara dost same time pe ek hi file edit kar rahe ho.
1. Tumne file kholi (Version 5). Dost ne bhi wahi kholi (Version 5).
2. Dost ne save kar diya (File huyi Version 6).
3. Ab tum save karne gaye... **System bolega:** "Ruko! Tumhare paas purana version hai."
4. Tumhe pucha jayega: **Merge** (Mila dein?), **Overwrite** (Tumhara rakhein?), ya **Reload**?

---

# PART 2: SARE EDGE CASES KI KAHANIA (EC1 - EC20) ✅ & 🔶

Ab aate hain main mudde pe. Ye wo 20 situations hain jahan system phas sakta tha, par humne unki kahani likh di hai.

### EC1: Asset Chhin Gaya (Shared -> Exclusive)
*   **Kahani:** Tum "High Risk Countries" ki list edit kar rahe ho. Ye list India aur Belgium dono use kar rahe hain (Shared). Edit karte waqt India ne is list ko use karna band kar diya. Ab ye list *sirf* Belgium (tumhare) paas bachi.
*   **Kya hoga:** Jab tum Save karoge, system dekhega "Arre wah, ab toh ye sirf tumhari hai!" Aur wo save ho jayegi (Inline update). Tumhe Copy banane ki zaroorat nahi padegi.

### EC2: Status Badal Gaya (Draft -> Sandbox)
*   **Kahani:** Tum ek list edit kar rahe the jo "Sandbox" status mein thi (locked). Achanak kisi ne us list ko saare rules se hata diya. Ab wo wapas "Draft" ban gayi.
*   **Kya hoga:** Tumhara edit aaram se save ho jayega kyunki Draft lists mein koi rok-tok nahi hoti.

### EC3: Ek Asset, Do Sandbox
*   **Kahani:** "High Risk Countries" list India aur Belgium dono ke sandboxes mein use ho rahi hai.
*   **Kya hoga:** Har sandbox ke paas apna-apna version track hoga. India wala edit karega toh V2 banega (sirf India ke liye). Belgium wala V1 pe hi rahega jab tak wo update na maange.

### EC4: Ek Saath Edit (Concurrent Edit)
*   **Kahani:** (Upar bataya tha) Tum aur dost ek hi asset edit kar rahe ho.
*   **Kya hoga:** Jo baad mein save karega, use roka jayega aur pucha jayega "Merge karna hai kya?".

### EC5: Enterprise ki Manmaani
*   **Kahani:** Enterprise ne head office se naya rule bana diya. Lekin tum India market mein apna kaam kar rahe ho.
*   **Kya hoga:** Enterprise ka naya rule tumhare chhalte kaam ko nahi bigadega. Tumhe "Stale" (Baasi) badge dikhega. Jab tum chahoge, tab "Refresh" dabake naya rule le lena.

### EC6: Simulation mein cheating nahi
*   **Kahani:** Tumne Simulation chalayi. Usi waqt Production mein kuch naya changes aa gaya.
*   **Kya hoga:** Tumhari Simulation wahi purane (copied) data pe chalegi jo shuru mein tha. Beech mein production change hone se result nahi bigdega. (Isolation).

### EC7: Draft ban gaya Production
*   **Kahani:** Tumne 'India' sandbox mein ek Asset banaya (Draft). Kisi aur ne wohi Asset 'Enterprise' sandbox mein use karke Production mein bhej diya.
*   **Kya hoga:** Ab wo Asset "Production" ban gaya. Tum (India wale) ab use edit nahi kar paoge. Tumhe uska naya version banana padega.

### EC8: Enterprise deletion rokna
*   **Kahani:** Enterprise chahta hai "Customer Risk" category uda de. Lekin India walon ne usme apne rules banaye hue hain.
*   **Kya hoga:** System Enterprise ko rokega: "Ruko! India walon ne isme kaam kiya hai. Pehle unse baat karo." (Delete Blocked).

### EC9: Refresh mein Jhagda
*   **Kahani:** Enterprise ne Asset V2 banaya. Tumne India mein Asset V3 banaya. Tumne Refresh dabaya.
*   **Kya hoga:** Conflict! System puchega: "Kiska rakhna hai? Enterprise ka V2 ya tumhara V3?"

### EC10: Version Cap aur Assets
*   **Kahani:** Tumhara sandbox version 10 limits hit kar gaya. Tum naya sandbox banate ho.
*   **Kya hoga:** Tumhare banaye hue saare Asset versions naye sandbox mein **carry over** ho jayenge. Mehnat bekaar nahi jayegi.

---
### **AB WO 10 NAYE CASES (Jinpe Faisla Lena Hai) 🔶**

### EC11: Asset Naya, Rule Purana
*   **Kahani:** Tumne Asset update karke V2 bana diya. Lekin Rule abhi bhi V1 ko point kar raha hai.
*   **Sawal:** Kya Rule apne aap V2 ko point karne lage? Ya user khud kare?

### EC12: Kachra Jama Hona (Orphan Assets)
*   **Kahani:** 1 saal mein hazaron aisi lists jama ho jayengi jo koi use nahi kar raha. Dhoondhna mushkil ho jayega.
*   **Sawal:** Kya 90 din baad inhein archive kar dein?

### EC13: Merge kaise karein?
*   **Kahani:** Do logon ne same list edit ki. Ek ne [A, B] dala, dusre ne [C, D].
*   **Sawal:** Merge karne pe kya [A, B, C, D] ban jaye (Union)?

### EC14: Refresh aur 10 Version ki Limit
*   **Kahani:** Tumhara sandbox version 9 pe hai. Tumne Refresh dabaya. Kya ye Version 10 mana jayega?
*   **Sawal:** Agar haan, toh refresh karte hi tumhari limit khatam ho jayegi. Iska kya karein?

### EC15: Enterprise ne change kiya, Markets ko pata nahi
*   **Kahani:** Enterprise ne naya rule bana diya. India aur Belgium abhi bhi purana rule use kar rahe hain (Stale).
*   **Sawal:** Kya unhein zabardasti batana chahiye? Ya unka merge rok dena chahiye jab tak wo refresh na karein?

### EC16: Simulation Queue ka Pangaa
*   **Kahani:** Tumne Simulation submit ki. Wo 2 ghante queue mein lagi rahi. Us beech Production change ho gaya.
*   **Sawal:** Simulation kis data pe chalegi? Us waqt ke jab submit kiya tha? Ya jab 2 ghante baad shuru hui?

### EC17: Copy ka Naam
*   **Kahani:** India wale "High Risk" asset ki copy banate hain.
*   **Sawal:** Kya uska naam `High_Risk_IN` rakh dein? Ya user se puchein?

### EC18: Purane pe Rollback
*   **Kahani:** Production aage badh gaya (P2). Tum purane version (V1 jo P1 pe tha) pe rollback karna chahte ho.
*   **Sawal:** Kya rollback karne dein? Bhale hi wo 'Baasi' (Stale) ho jaye?

### EC19: Versions ka Pahad
*   **Kahani:** Tum roz Asset edit karte ho par submit nahi karte. Hazaron versions ban gaye.
*   **Sawal:** Kya koi limit honi chahiye? Jaise max 50 versions?

### EC20: Gate Delete karna
*   **Kahani:** Enterprise "Geography Check" gate uda deta hai. Lekin markets ne usme apne overrides lagaye hain.
*   **Sawal:** Kya Markets ke overrides bhi uda dein? Ya Enterprise ko rokein?

---

# PART 3: TUMSE SAWAL (OPEN QUESTIONS) 🔴

Bhai, bas inka Jawab de do (Part 4 wale) taaki hum final plan bana sakein:

*   **FQ7 (EC11):** Kya Asset V2 banne pe Rule auto-update ho? (Haan/Nahi)
*   **FQ8 (EC12):** Orphan assets kitne din rakhein? (30 din / 90 din / Hamesha)
*   **FQ9 (EC13):** Merge = Union? (Haan/Nahi)
*   **FQ12 (EC16):** Simulation Data kab copy ho? (Submit dabate hi / Job start hote hi)

Batao, kya lagta hai?
