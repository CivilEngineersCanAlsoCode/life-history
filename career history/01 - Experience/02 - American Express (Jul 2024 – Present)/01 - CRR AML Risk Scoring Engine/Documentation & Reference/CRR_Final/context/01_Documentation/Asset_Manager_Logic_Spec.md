# Asset Manager: Logic Specification (Romanised Hindi)

Ye document Asset Manager ke logic ko simple bhasha mein samjhata hai. Isme SQL ya technical jargon nahi hai, bas seedha logic hai ki system kaam kaise karega.

## 1. Sandbox Awareness (kya dikhega?)
Asset Manager koi static page nahi hai. Ye depend karta hai ki tum abhi kahan khade ho (Sandbox mein ya bahar).

### A. View Only Mode (Jab tum Sandbox mein nahi ho)
*   **Context:** Jab tum "Asset Manager" khologe bina koi Sandbox open kiye.
*   **Primary Market Dropdown:** Yahan upar ek main dropdown hoga jahan tum Market select karoge (e.g. India).
    *   **Default Selection:** Jab page load hoga, to system user ke available markets mein se **Alphabetically First** market ko auto-select karega (e.g. agar access 'India' aur 'China' ka hai, to 'China' select hoga).
*   **Smart Filter (Zaroori):** Jab tum India select karoge, to list mein sab kuch nahi dikhega. Sirf wohi assets dikhenge jo **abhi India ke Rules mein actually use ho rahe hain**.
    *   Isme wo *Enterprise Assets* bhi aayenge jo India ne inherit kiye hain.
    *   Aur wo *Local Assets* bhi aayenge jo India ne khud banaye hain.
*   **Note:** Agar abhi tak kuch bhi live nahi hua hai (Zero State), to ye list bilkul khaali hogi. Drafts yahan nahi dikhenge.

### B. Sandbox Mode (Draft State)
*   **Context:** Jab tumne koi Sandbox open kiya hai (jaise "Enterprise V1").
*   **Kya dikhega:**
    1.  **Inherited Assets:** Jo pehle se Production mein hain (agar kuch hain to). Zero State mein ye khaali hoga.
    2.  **Draft Assets (Zaroori):** Jo bhi nayi cheezen tum *isi waqt* is sandbox mein bana rahe ho.
    3.  **Matlab:** Agar tum naye Asset banate ho Enterprise Sandbox mein, to wo tumhe turant dikhenge, bhale hi Production khaali ho.

## 2. Asset Kahan Bante Hain?
*   Tum Assets ko **Enterprise Sandbox** aur **Market Sandbox** dono jagah bana sakte ho.
*   **Fark kya hai:**
    *   Agar **Enterprise Sandbox** mein banaya -> To wo "Global Asset" banega (Sabko dikhega).
    *   Agar **Market Sandbox** (jaise India) mein banaya -> To wo "Local Asset" banega (Sirf India walon ko dikhega).

## 3. Database mein kya save hoga? (Simple Logic)
Jab Rebecca "High Risk Geo" list banati hai, to system peeche 2 cheezen note karta hai:
1.  **Header:**
    *   **Name:** List ka naam (e.g. "High Risk Geo").
    *   **Scope:** Ye list kis level ki hai? (Yaani "Enterprise" hai ya kisi specific "Market" ki hai).
2.  **Version:**
    *   **Data:** List ka content kya hai aur status kya hai (Draft v0.1).
    *   **Sandbox ID:** Ye specific version **kis Sandbox ID** se juda hai. (Matlab us specific Sandbox ki ID jisme ye draft banaya gaya hai).
    *   *Ye Sandbox ID hi wo link hai jisse system ko pata chalta hai ki ye draft kiske liye hai.*

## 4. Rule banate waqt Dropdown mein kya aayega?
Jab tum Rule likh rahe hoge (jaise `IF Country IN ...`), to dropdown mein kya dikhega?
*   **Logic:** System check karega ki tum kahan ho.
*   **Enterprise Sandbox:** Sirf Global/Enterprise wale assets dikhenge.
*   **Market Sandbox:** Global wale assets bhi dikhenge (kyunki wo inherit huye hain) + Local Market wale assets bhi dikhenge.

## 5. Edit kaun kar sakta hai?
*   **Rule:** Tum sirf unhi cheezon ko edit kar sakte ho jo **tumhare current Sandbox** ka hissa hain.
*   **Scenario 1 (Enterprise Sandbox):**
    *   Jo naya draft banaya hai -> Edit kar lo.
    *   Jo purana Production asset hai -> Direct edit nahi hoga. **"Versioning"** karni padegi (isme uska naya version ban jayega).
*   **Scenario 2 (Market Sandbox):**
    *   Market wale assets -> Edit kar lo full.
    *   Enterprise wale assets -> Edit **NAHI** kar sakte. Tum sirf unka logic override kar sakte ho, list ka content change nahi kar sakte.

## 6. Versioning Kaise Chalegi?
Simple flow hai:
1.  **v0.1 (Draft):** Jab pehli baar Sandbox mein banaya.
2.  **v1.0 (Active):** Jab Sandbox Promote ho gaya Production mein.
3.  **v1.1 (Draft):** Jab agli baar kisi ne edit karne ke liye Sandbox khola.

## 7. Agar Sandbox Reject ya Delete ho gaya to?
*   **Reject:** Agar Manager ne mana kar diya, to wo saare Drafts "Discarded" maane jayenge. Wo Production mein kabhi nahi jayenge.
*   **Delete:** Agar tumne galti se Sandbox delete kar diya, to uske andar banaye huye saare naye Assets bhi gayab ho jayenge. Production data safe rahega.
