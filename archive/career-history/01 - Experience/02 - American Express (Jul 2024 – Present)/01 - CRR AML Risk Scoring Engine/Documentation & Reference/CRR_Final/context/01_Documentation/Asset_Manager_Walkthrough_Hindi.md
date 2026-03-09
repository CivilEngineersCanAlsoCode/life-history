# Asset Manager Journey: Day 0 se Maturity tak (Romanised Hindi)

Ye document poora flow batata hai ki kaise hum **Zero State** se shuru karke ek complex multi-market setup tak pahunchenge.

Hum 3 main scenarios cover karenge:
1.  **Enterprise Assets:** Jo puri duniya ke liye common hain.
2.  **Market Specific Assets:** Jo sirf ek country ke liye hain.
3.  **Shared/Center Assets:** Jo multiple markets share karte hain (e.g., EU Region).

---

## Phase 1: Day 0 - The Beginning (Enterprise Assets)
*Scenario: System khaali hai. Pehla banda (Rebecca) login karta hai.*

### 1.1 Enterprise Sandbox Banana
*   Rebecca "Asset Manager" kholti hai -> **Empty View** (Kyunki Production mein kuch nahi hai).
*   System bolta hai: *"Bhai pehle Sandbox banao."* (View Only mode mein create allowed nahi hai).
*   **Step:** Rebecca "Create Sandbox" click karti hai -> Name: **"Foundation V1"** -> Scope: **Enterprise**.

### 1.2 Global List Create Karna
*   **Goal:** "Global High Risk Countries" list banani hai jo sab use karenge.
*   **Action:**
    1.  Sandbox ke andar, Rebecca click karti hai **"Create List"**.
    2.  Name: "Global Sanctions".
    3.  Scope: **Enterprise** (Ye automatic set hoga kyunki sandbox Enterprise hai).
    4.  Items add kiye: 'North Korea', 'Iran'.
*   **System State:**
    *   Ye asset abhi **DRAFT** hai.
    *   Sirf is "Foundation V1" sandbox mein dikhega.
    *   Production abhi bhi khaali hai.

### 1.3 Production Push
*   Rebecca "Promote" click karti hai. Jake (Manager) approve karta hai.
*   **Result:** Ab "Global Sanctions" list **Production** mein live hai.
*   **Impact:** Ab agar koyi bhi naya Sandbox banayega, to usko ye list "Read-Only" mode mein dikhegi.

---

## Phase 2: Day 1 - The First Local Market (Market Specific Assets)
*Scenario: India team (Alex) ko apni specific list chahiye.*

### 2.1 India Sandbox Banana
*   Alex login karta hai. Use "Global Sanctions" list dikh rahi hai View Only mode mein.
*   **Step:** Alex "Create Sandbox" click karta hai -> Name: **"India Launch"** -> Scope: **India**.

### 2.2 Local List Create Karna
*   **Goal:** India ke liye "Local Blacklisted Merchants" list banani hai.
*   **Action:**
    1.  India Sandbox ke andar, Alex click karta hai **"Create List"**.
    2.  Name: "Debit Card Blacklist".
    3.  Scope: **India** (Ye automatic set hoga kyunki sandbox India hai).
    4.  Items add kiye: 'Local Vendor A', 'Local Vendor B'.
*   **Dropdown Logic:**
    *   Jab Alex Rule likhega, to dropdown mein use **2 lists** dikhengi:
        1.  Global Sanctions (Inherited from Enterprise).
        2.  Debit Card Blacklist (Local India Asset).

### 2.3 Production Push (India)
*   Alex promote karta hai. Jake approve karta hai.
*   **Result:** India Market ke paas ab apni personal list hai.
*   **Privacy:** Agar kal ko "Canada" ka banda login karega, to use "Global Sanctions" dikhegi par "Debit Card Blacklist" **nahi dikhegi**.

---

## Phase 3: Day 2 - Shared Assets (Multiple Markets)
*Scenario: Europe ke saare countries (France, Germany, Italy) ko "GDPR High Risk List" share karni hai. Har koi alag alag nahi banana chahta.*

### 3.1 "Center" (Region) Sandbox Banana
*   Yahan hume ek **"Regional Sandbox"** chahiye.
*   **Step:** Regional Head (Pierre) "Create Sandbox" click karta hai -> Name: **"EU Regional Standad"** -> Scope: **Europe Center** (Center = Region).

### 3.2 Shared Asset Create Karna
*   **Action:**
    1.  Sandbox ke andar, Pierre asset banata hai.
    2.  Name: "GDPR Violators".
    3.  Scope: **Europe Center**.
    4.  Items add kiye: 'Company X', 'Company Y'.
*   **Promote:** Pierre isko Production mein promote kar deta hai.

### 3.3 Inheritance Logic (Germany vs France)
*   Ab jab **Germany** ka MCO apna sandbox banayega:
    *   Usko **Global Sanctions** dikhegi (Enterprise se).
    *   Usko **GDPR Violators** dikhegi (Europe Center se).
*   Ab jab **France** ka MCO apna sandbox banayega:
    *   Usko bhi same **Global + GDPR** lists dikhengi.
*   Lekin **India** wale ko GDPR list **nahi dikhegi** (Kyunki India Europe Center ka part nahi hai).

---

## Summary Table

| Asset Name | Scope | Kaun dekh sakta hai? | Kaun Edit kar sakta hai? |
| :--- | :--- | :--- | :--- |
| **Global Sanctions** | Enterprise | Sabhi (India, France, Germany) | Sirf Enterprise Admin (Versioning karke) |
| **Debit Card Blacklist** | India | Sirf India | Sirf India MCO |
| **GDPR Violators** | Europe Center | France, Germany, Italy (Poora Europe) | Europe Regional Head |

Ye approach ensure karti hai ki **"Create Once, Use Many"** principle follow ho, aur India ka kachra France mein na dikhe.
