# ISP Design Catalog
## American Express Design System Component Library

> [!NOTE]
> This catalog documents the ISP (Internal Style & Pattern) Design Library components used across American Express digital products. Each component includes its purpose, usage context, and real-world examples from common AmEx applications.

---

## Table of Contents

1. [Navigation Components](#navigation-components)
2. [Form Components](#form-components)
3. [Data Display Components](#data-display-components)
4. [Feedback & Messaging Components](#feedback--messaging-components)
5. [Interactive Components](#interactive-components)
6. [Layout Components](#layout-components)

---

## Navigation Components

### 1. **Breadcrumbs**
![Component](file:///Users/satvikjain/Downloads/CRR - American Express/ISP Design Library/Breadcrumbs.svg)

**Why It's Used:**
- Provides hierarchical navigation path
- Helps users understand their current location in the application
- Enables quick navigation to parent pages
- Reduces cognitive load by showing site structure

**Where It's Used:**

| Use Case | Example | Context |
|----------|---------|---------|
| **Account Management** | Home > My Account > Profile Settings | Multi-level account configuration pages |
| **Transaction Details** | Accounts > Credit Cards > Card Details > Transaction History | Deep navigation in financial products |
| **Statements & Documents** | Home > Statements > 2024 > January | Hierarchical document browsing |
| **Merchant Offers** | Home > Offers > Travel > Airlines | Category-based offer navigation |
| **Business Services** | Services > Payment Solutions > Corporate Cards > Apply | Complex business product flows |
| **Support Center** | Help > Account Issues > Card Activation > Step-by-Step Guide | Multi-tier help documentation |

---

### 2. **Tabs**
![Component](file:///Users/satvikjain/Downloads/CRR - American Express/ISP Design Library/Tabs.svg)

**Why It's Used:**
- Organizes related content into separate views
- Reduces page clutter and improves scanability
- Allows users to switch between different data sets without page reload
- Maintains context while exploring related information

**Where It's Used:**

| Use Case | Example | Context |
|----------|---------|---------|
| **Account Overview** | Summary | Activity | Statements | Rewards | Dashboard with multiple data views |
| **Credit Card Management** | Card Details | Transactions | Benefits | Offers | Comprehensive card information hub |
| **Membership Rewards** | Points Summary | Redeem | Transfer | Shop | Multi-functional rewards portal |
| **Business Analytics** | Overview | Spending | Employees | Reports | Business account dashboard |
| **Travel Booking** | Flights | Hotels | Car Rentals | Activities | Integrated travel services |
| **Payment Settings** | AutoPay | Payment Methods | Scheduled Payments | History | Payment configuration interface |

---

### 3. **Vertical Navigation**
![Component](file:///Users/satvikjain/Downloads/CRR - American Express/ISP Design Library/Vertical Nav.svg)

**Why It's Used:**
- Provides persistent navigation for complex applications
- Supports deep hierarchies with expandable sections
- Optimizes screen real estate on desktop views
- Enables quick access to main sections

**Where It's Used:**

| Use Case | Example | Context |
|----------|---------|---------|
| **Account Hub** | Dashboard, Cards, Rewards, Statements, Profile | Primary navigation for logged-in users |
| **Business Portal** | Home, Employees, Spending Controls, Reports, Settings | Enterprise account management |
| **Admin Console** | Users, Permissions, Billing, Integrations, Audit Logs | Internal admin tools |
| **Customer Service Portal** | Cases, Chat, Knowledge Base, Escalations | Support representative interface |
| **Partner Portal** | Overview, Offers, Analytics, Co-Brand Settings | Merchant/partner management |
| **Developer Console** | API Keys, Documentation, Sandbox, Usage, Support | API integration platform |

---

### 4. **Unauthenticated Navigation**
![Component](file:///Users/satvikjain/Downloads/CRR - American Express/ISP Design Library/Unauthenticated Navigation.svg)

**Why It's Used:**
- Guides non-logged-in users to key areas
- Promotes product discovery and conversion
- Provides clear call-to-action for login/signup
- Maintains brand consistency across public pages

**Where It's Used:**

| Use Case | Example | Context |
|----------|---------|---------|
| **Marketing Homepage** | Cards, Rewards, Travel, Business, About | Public-facing AmEx website |
| **Card Comparison** | Compare Cards, Apply Now, Login | Pre-authentication product browsing |
| **Travel Portal (Public)** | Destinations, Deals, Fine Hotels & Resorts, Login | Travel benefits showcase |
| **Business Solutions** | Small Business, Corporate, Merchant Services, Resources | B2B product information |
| **Support (Pre-Login)** | Help Topics, Contact Us, FAQs, Login | Public support resources |
| **Benefits Overview** | Travel, Shopping, Dining, Entertainment, Insurance | Membership benefits marketing |

---

### 5. **Vertical Secondary/Tertiary**
![Component](file:///Users/satvikjain/Downloads/CRR - American Express/ISP Design Library/Vertical Secondary.svg)

**Why It's Used:**
- Provides sub-navigation within a primary section
- Creates clear information hierarchy
- Enables granular navigation without overwhelming users
- Supports complex multi-level applications

**Where It's Used:**

| Use Case | Example | Context |
|----------|---------|---------|
| **Account Settings** | Security > Password, 2FA, Trusted Devices, Login History | Nested security configurations |
| **Rewards Management** | Redeem > Travel, Gift Cards, Statement Credit, Shop | Sub-categories within rewards |
| **Business Reporting** | Reports > Spending Analysis, Employee Activity, Tax Reports | Specialized report types |
| **Card Services** | Manage Card > Replace Card, Additional Cards, Card Lock | Specific card management actions |
| **Benefits Access** | Travel > Airline Credits, Hotel Status, Lounge Access | Benefit sub-categories |
| **Compliance Section** | Regulations > PCI DSS, GDPR, SOC 2, Audit Reports | Compliance documentation hierarchy |

---

### 6. **Pagination**
![Component](file:///Users/satvikjain/Downloads/CRR - American Express/ISP Design Library/Pagination.svg)

**Why It's Used:**
- Breaks large data sets into manageable chunks
- Improves page load performance
- Provides clear navigation through multi-page content
- Reduces cognitive overload

**Where It's Used:**

| Use Case | Example | Context |
|----------|---------|---------|
| **Transaction History** | Pages 1-50 of 200 transactions | Long transaction lists |
| **Statement Archive** | Viewing statements from past 7 years | Historical document browsing |
| **Search Results** | Card offer search returning 150+ results | Product search functionality |
| **Employee Management** | Corporate card holder list (1000+ employees) | Large-scale business account management |
| **Merchant Offers** | Browse 500+ available offers | Extensive offer catalog |
| **Help Articles** | Knowledge base with 300+ articles | Support documentation library |

---

## Form Components

### 7. **Text Input**
![Component](file:///Users/satvikjain/Downloads/CRR - American Express/ISP Design Library/Text Input.svg)

**Why It's Used:**
- Primary method for collecting user text data
- Supports validation and error messaging
- Provides clear field labels and helper text
- Maintains accessibility standards

**Where It's Used:**

| Use Case | Example | Context |
|----------|---------|---------|
| **Card Application** | First Name, Last Name, Email, SSN | New card enrollment forms |
| **Profile Update** | Update email address, phone number | Account information editing |
| **Payment Setup** | Account holder name, routing number | Bank account linking |
| **Merchant Search** | "Search for merchants near you" | Search functionality |
| **Travel Booking** | Passenger name, hotel preferences | Travel reservation forms |
| **Support Request** | Subject line, case description | Customer service inquiries |

---

### 8. **Password**
![Component](file:///Users/satvikjain/Downloads/CRR - American Express/ISP Design Library/Password.svg)

**Why It's Used:**
- Securely captures password input with masking
- Includes show/hide toggle for user convenience
- Supports password strength indicators
- Ensures sensitive data protection

**Where It's Used:**

| Use Case | Example | Context |
|----------|---------|---------|
| **User Login** | Password field with "Show" toggle | Authentication pages |
| **Account Creation** | Set password with strength meter | New account registration |
| **Password Reset** | Create new password, confirm password | Security flows |
| **Two-Factor Setup** | One-time password entry | Enhanced security configuration |
| **Business Admin** | Admin password verification | Sensitive business operations |
| **Payment Authorization** | Password confirmation for large transfers | High-value transaction security |

---

### 9. **Phone**
![Component](file:///Users/satvikjain/Downloads/CRR - American Express/ISP Design Library/Phone.svg)

**Why It's Used:**
- Standardizes phone number collection
- Supports international formats
- Enables auto-formatting for better UX
- Facilitates SMS verification

**Where It's Used:**

| Use Case | Example | Context |
|----------|---------|---------|
| **Account Setup** | Primary contact number | User registration |
| **Two-Factor Authentication** | SMS verification number | Security enhancement |
| **Travel Alerts** | Mobile number for fraud alerts | Notification preferences |
| **Business Contact** | Company phone, extension | Corporate account setup |
| **Card Activation** | Verification phone number | New card activation |
| **Support Callback** | Preferred callback number | Customer service scheduling |

---

### 10. **Select/Dropdown**
![Component](file:///Users/satvikjain/Downloads/CRR - American Express/ISP Design Library/Select.svg)

**Why It's Used:**
- Provides predefined options to reduce errors
- Ensures data consistency
- Saves screen space compared to radio buttons
- Supports searchable lists for long option sets

**Where It's Used:**

| Use Case | Example | Context |
|----------|---------|---------|
| **Address Forms** | State/Province, Country selection | Geographic information |
| **Card Application** | Annual income range, employment status | Financial questionnaires |
| **Travel Preferences** | Airline preference, seat type | Booking customization |
| **Statement Preferences** | Delivery method (Online/Paper), Language | Account settings |
| **Business Settings** | Expense category, cost center | Corporate card controls |
| **Filtering** | Time period (Last 30 days, Last 3 months) | Data filtering options |

---

### 11. **Multi-Select**
![Component](file:///Users/satvikjain/Downloads/CRR - American Express/ISP Design Library/Multi Select.svg)

**Why It's Used:**
- Allows selection of multiple options simultaneously
- Shows selected items with dismissible tags
- Efficient for category-based inputs
- Provides clear visual feedback

**Where It's Used:**

| Use Case | Example | Context |
|----------|---------|---------|
| **Offer Preferences** | Select interest categories (Travel, Dining, Shopping) | Personalization settings |
| **Alert Settings** | Choose alert types to receive | Notification management |
| **Report Customization** | Select data columns to include | Business intelligence tools |
| **Expense Categorization** | Multiple expense categories for review | Spending analysis filters |
| **Benefits Selection** | Enroll in multiple benefit programs | Membership benefit management |
| **Search Filters** | Filter by multiple card types, benefits | Advanced product search |

---

### 12. **Checkbox**
![Component](file:///Users/satvikjain/Downloads/CRR - American Express/ISP Design Library/Checkbox.svg)

**Why It's Used:**
- Enables binary (yes/no) choices
- Supports multi-selection in lists
- Provides clear visual state indication
- Accessible and familiar interaction pattern

**Where It's Used:**

| Use Case | Example | Context |
|----------|---------|---------|
| **Terms & Conditions** | "I agree to the terms of service" | Legal agreement acceptance |
| **Marketing Preferences** | "Send me promotional emails" | Opt-in/out settings |
| **AutoPay Setup** | "Enable automatic minimum payment" | Payment automation |
| **Transaction Selection** | Select multiple transactions to dispute | Batch operations |
| **Feature Enrollment** | "Enroll in paperless statements" | Service opt-in |
| **Privacy Settings** | Multiple data sharing checkboxes | Privacy preferences |

---

### 13. **Radio Button**
![Component](file:///Users/satvikjain/Downloads/CRR - American Express/ISP Design Library/Radio Button.svg)

**Why It's Used:**
- Forces single selection from multiple options
- Makes all options visible simultaneously
- Provides clear mutually exclusive choices
- Better than dropdown for 2-5 options

**Where It's Used:**

| Use Case | Example | Context |
|----------|---------|---------|
| **Payment Amount** | Minimum Payment | Statement Balance | Other Amount | Payment selection |
| **Card Delivery** | Standard Shipping | Express Delivery | In-Branch Pickup | Fulfillment options |
| **Contact Preference** | Email | Phone | SMS | Communication channels |
| **Statement Period** | Current | Last 3 Months | Last 6 Months | Last Year | Time range selection |
| **Travel Class** | Economy | Business | First Class | Booking preferences |
| **Dispute Reason** | Fraudulent | Did not recognize | Incorrect amount | Issue categorization |

---

### 14. **Toggle Switch**
![Component](file:///Users/satvikjain/Downloads/CRR - American Express/ISP Design Library/Toggle Switch.svg)

**Why It's Used:**
- Provides instant on/off state changes
- Gives immediate visual feedback
- Perfect for settings and preferences
- Mobile-friendly interaction

**Where It's Used:**

| Use Case | Example | Context |
|----------|---------|---------|
| **Card Controls** | Enable/disable international transactions | Real-time card security |
| **Notifications** | Turn on/off push notifications | Alert management |
| **Feature Activation** | Enable contactless payments | Card feature toggles |
| **Privacy Settings** | Share data with partners (On/Off) | Data privacy controls |
| **AutoPay** | Enable automatic payments | Payment automation |
| **Travel Mode** | Activate travel notification mode | Location-based settings |

---

### 15. **Date Picker**
![Component](file:///Users/satvikjain/Downloads/CRR - American Express/ISP Design Library/Date Picker.svg)

**Why It's Used:**
- Standardizes date input format
- Prevents invalid date entries
- Provides calendar interface for easy selection
- Supports date range constraints

**Where It's Used:**

| Use Case | Example | Context |
|----------|---------|---------|
| **Travel Booking** | Select departure date | Flight/hotel reservations |
| **Statement Download** | Choose statement date | Document retrieval |
| **Scheduled Payment** | Select payment date | Future payment scheduling |
| **Report Generation** | Start date for expense report | Business analytics |
| **Offer Redemption** | Book hotel stay dates | Rewards utilization |
| **Transaction Search** | Filter by transaction date | History exploration |

---

### 16. **Date Range Picker**
![Component](file:///Users/satvikjain/Downloads/CRR - American Express/ISP Design Library/Date Range Picker.svg)

**Why It's Used:**
- Selects start and end dates simultaneously
- Ideal for filtering time-based data
- Visual calendar interface shows range
- Prevents invalid range selection

**Where It's Used:**

| Use Case | Example | Context |
|----------|---------|---------|
| **Transaction History** | View transactions from Jan 1 - Jan 31 | Data filtering |
| **Expense Reporting** | Select expense period for report | Business reporting |
| **Travel Dashboard** | Show trips between March - June | Trip planning |
| **Rewards Activity** | Points earned from Q1 2024 | Loyalty program analysis |
| **Spending Analysis** | Analyze spending patterns over custom period | Financial insights |
| **Statement Search** | Download statements for date range | Document management |

---

### 17. **Calendar**
![Component](file:///Users/satvikjain/Downloads/CRR - American Express/ISP Design Library/Calendar.svg)

**Why It's Used:**
- Displays events and scheduled items
- Provides month/week/day views
- Enables date navigation and selection
- Shows availability and conflicts

**Where It's Used:**

| Use Case | Example | Context |
|----------|---------|---------|
| **Payment Calendar** | View upcoming payment due dates | Payment planning dashboard |
| **Travel Itinerary** | Show booked trips on calendar | Travel management |
| **Statement Calendar** | Statement closing dates visualization | Billing cycle awareness |
| **Offer Expiry** | Calendar view of expiring offers | Time-sensitive promotions |
| **Appointment Booking** | Bank branch appointment scheduler | Service booking |
| **Business Events** | Company expense deadlines, fiscal periods | Corporate timeline |

---

### 18. **Slider**
![Component](file:///Users/satvikjain/Downloads/CRR - American Express/ISP Design Library/Slider.svg)

**Why It's Used:**
- Enables selection from a continuous range
- Provides visual representation of value
- Great for adjustable parameters
- Intuitive touch/drag interaction

**Where It's Used:**

| Use Case | Example | Context |
|----------|---------|---------|
| **Payment Amount** | Slide to select payment amount between minimum and full balance | Flexible payment selection |
| **Spending Limits** | Set employee spending limit ($100 - $10,000) | Business card controls |
| **Price Filters** | Filter hotels by price range | Travel booking |
| **Credit Limit Request** | Request credit limit increase | Account customization |
| **Points Transfer** | Select number of points to transfer | Rewards management |
| **Budget Allocation** | Distribute budget across categories | Financial planning tools |

---

### 19. **Text Area**
![Component](file:///Users/satvikjain/Downloads/CRR - American Express/ISP Design Library/Text Area.svg)

**Why It's Used:**
- Allows multi-line text input
- Supports longer form content
- Character count and validation
- Resizable for user convenience

**Where It's Used:**

| Use Case | Example | Context |
|----------|---------|---------|
| **Dispute Details** | Explain the reason for transaction dispute | Fraud reporting |
| **Support Messages** | Describe issue in customer service form | Help requests |
| **Travel Notes** | Add special requests for hotel booking | Reservation customization |
| **Feedback Forms** | Share experience feedback | Customer satisfaction surveys |
| **Business Justification** | Expense report notes and justifications | Corporate compliance |
| **Profile Information** | Company description for business account | Business profile setup |

---

### 20. **Search**
![Component](file:///Users/satvikjain/Downloads/CRR - American Express/ISP Design Library/Search.svg)

**Why It's Used:**
- Enables quick content discovery
- Supports auto-complete and suggestions
- Filters large data sets efficiently
- Provides instant feedback

**Where It's Used:**

| Use Case | Example | Context |
|----------|---------|---------|
| **Transaction Search** | "Search transactions by merchant name" | Finding specific purchases |
| **Offer Discovery** | "Search for dining offers in NYC" | Personalized offer browsing |
| **Help Center** | "Search help articles" | Self-service support |
| **Merchant Locator** | "Find AmEx-accepting merchants nearby" | Location-based services |
| **Travel Destinations** | "Search for hotels in Paris" | Travel booking |
| **Employee Lookup** | Search corporate cardholders | Business admin tools |

---

### 21. **Currency Input**
![Component](file:///Users/satvikjain/Downloads/CRR - American Express/ISP Design Library/Currency.svg)

**Why It's Used:**
- Formats monetary values correctly
- Supports multiple currencies
- Prevents invalid decimal entries
- Shows currency symbols automatically

**Where It's Used:**

| Use Case | Example | Context |
|----------|---------|---------|
| **Payment Entry** | Enter custom payment amount | Bill payment |
| **Budget Setting** | Set monthly spending budget | Financial planning |
| **Transfer Amount** | Transfer amount between accounts | Account management |
| **Donation** | Enter donation amount | Charitable giving through AmEx |
| **Price Alerts** | Set price drop alert threshold | Shopping tools |
| **Expense Reporting** | Enter expense amount for reimbursement | Business expense management |

---

### 22. **Input Stepper**
![Component](file:///Users/satvikjain/Downloads/CRR - American Express/ISP Design Library/Input Stepper.svg)

**Why It's Used:**
- Provides increment/decrement controls
- Prevents invalid numeric input
- Better UX for small value ranges
- Clear minimum/maximum constraints

**Where It's Used:**

| Use Case | Example | Context |
|----------|---------|---------|
| **Traveler Count** | Number of travelers (1-9) | Travel booking |
| **Additional Cards** | Number of authorized users to add (0-99) | Account management |
| **Points Transfer** | Transfer points in 1,000-point increments | Rewards management |
| **Room Selection** | Number of hotel rooms needed | Accommodation booking |
| **Statement Copies** | Number of copies to mail | Document requests |
| **Credit Limit** | Increase limit in $500 increments | Credit management |

---

## Data Display Components

### 23. **Data Table**
![Component](file:///Users/satvikjain/Downloads/CRR - American Express/ISP Design Library/Data Table.svg)

**Why It's Used:**
- Presents complex data in organized rows/columns
- Supports sorting, filtering, and pagination
- Enables data comparison and analysis
- Scalable for large datasets

**Where It's Used:**

| Use Case | Example | Context |
|----------|---------|---------|
| **Transaction History** | Date | Merchant | Amount | Status | Category | Primary account activity view |
| **Employee Card Activity** | Employee | Card | Spend | Transactions | Status | Corporate account oversight |
| **Statement Details** | All charges and payments in current cycle | Billing information |
| **Rewards Activity** | Date | Activity | Points Earned | Points Redeemed | Balance | Loyalty program tracking |
| **Merchant Offers** | Merchant | Category | Discount | Expiry | Status | Available promotions |
| **Business Reports** | Spend by department, category, time period | Analytics dashboard |

---

### 24. **Card (Standard)**
![Component](file:///Users/satvikjain/Downloads/CRR - American Express/ISP Design Library/Card.svg)

**Why It's Used:**
- Groups related information visually
- Scannable and modular layout
- Supports images, text, and actions
- Mobile-responsive design

**Where It's Used:**

| Use Case | Example | Context |
|----------|---------|---------|
| **Account Overview** | Card showing current balance, available credit, payment due | Dashboard summary |
| **Rewards Summary** | Total points, cash back earned, redemption options | Loyalty benefits |
| **Benefit Highlights** | Airport lounge access, travel insurance, purchase protection | Membership perks |
| **Offer Cards** | Individual merchant offers with details and CTA | Promotions catalog |
| **Statement Summary** | Previous balance, payments, new charges, balance due | Billing snapshot |
| **Travel Bookings** | Upcoming trip details with booking reference | Trip management |

---

### 25. **Card Showcase**
![Component](file:///Users/satvikjain/Downloads/CRR - American Express/ISP Design Library/Card Showcase.svg)

**Why It's Used:**
- Highlights premium content prominently
- Large imagery for visual impact
- Drives engagement with featured items
- Perfect for hero sections

**Where It's Used:**

| Use Case | Example | Context |
|----------|---------|---------|
| **Featured Offers** | Premium travel offer with luxury hotel image | Homepage promotion |
| **Card Products** | Showcase new credit card with benefits | Product marketing |
| **Travel Experiences** | Fine Hotels & Resorts featured property | Premium travel portal |
| **Partner Spotlight** | Featured brand partnership with exclusive benefits | Marketing campaigns |
| **Event Promotion** | AmEx exclusive concert or dining experience | Entertainment offerings |
| **Seasonal Campaigns** | Holiday shopping bonuses, summer travel deals | Timely promotions |

---

### 26. **Card Actionable**
![Component](file:///Users/satvikjain/Downloads/CRR - American Express/ISP Design Library/Card Actionable.svg)

**Why It's Used:**
- Combines information display with clear actions
- Call-to-action buttons integrated
- Drives user engagement and conversion
- Task-oriented design

**Where It's Used:**

| Use Case | Example | Context |
|----------|---------|---------|
| **Offer Activation** | Offer details with "Add to Card" button | Merchant promotions |
| **Payment Due** | Amount due with "Make Payment" CTA | Account servicing |
| **Reward Redemption** | Available points with "Redeem Now" button | Loyalty engagement |
| **Card Application** | Card features with "Apply Now" action | Product acquisition |
| **Paperless Enrollment** | Benefits explanation with "Enroll" button | Service adoption |
| **Travel Booking** | Hotel details with "Book Now" action | Reservation flow |

---

### 27. **Accordion Panel**
![Component](file:///Users/satvikjain/Downloads/CRR - American Express/ISP Design Library/Accordion Panel.svg)

**Why It's Used:**
- Collapses/expands content progressively
- Reduces page length and clutter
- Shows summaries with details on demand
- Improves mobile experience

**Where It's Used:**

| Use Case | Example | Context |
|----------|---------|---------|
| **FAQ Section** | Collapsible questions and answers | Help center |
| **Transaction Details** | Expand to see full transaction information | Activity feed |
| **Benefits Information** | Card benefits with detailed descriptions | Product documentation |
| **Statement Sections** | Payments, Purchases, Fees & Interest | Detailed billing |
| **Travel Itinerary** | Flight details, hotel info, car rental | Trip summary |
| **Terms & Conditions** | Expandable legal sections | Cardmember agreements |

---

### 28. **Status**
![Component](file:///Users/satvikjain/Downloads/CRR - American Express/ISP Design Library/Status.svg)

**Why It's Used:**
- Communicates current state clearly
- Color-coded for quick recognition
- Shows progress or completion
- Reduces uncertainty

**Where It's Used:**

| Use Case | Example | Context |
|----------|---------|---------|
| **Application Status** | Approved | Pending | Under Review | Declined | Card application tracking |
| **Payment Status** | Paid | Scheduled | Processing | Failed | Payment confirmation |
| **Dispute Status** | Open | Under Investigation | Resolved | Closed | Fraud case management |
| **Shipping Status** | Ordered | Shipped | In Transit | Delivered | Card delivery tracking |
| **Offer Status** | Active | Expired | Redeemed | Inactive | Promotion management |
| **Account Status** | Active | Suspended | Closed | Under Review | Account health |

---

### 29. **Dismissible Tag**
![Component](file:///Users/satvikjain/Downloads/CRR - American Express/ISP Design Library/Dismissible Tag.svg)

**Why It's Used:**
- Shows selected items compactly
- Easy removal with close icon
- Great for filters and multi-select
- Maintains context while browsing

**Where It's Used:**

| Use Case | Example | Context |
|----------|---------|---------|
| **Applied Filters** | Category: Travel ✕ | Amount: $100+ ✕ | Active search filters |
| **Selected Categories** | Dining ✕ | Shopping ✕ | Entertainment ✕ | Preference tags |
| **Alert Subscriptions** | Payment Reminders ✕ | Fraud Alerts ✕ | Notification management |
| **Benefit Enrollments** | Lounge Access ✕ | Travel Protection ✕ | Active benefits |
| **Card Features** | Contactless ✕ | International ✕ | Enabled features |
| **Search Terms** | Recent searches with quick removal | Search history |

---

### 30. **Hero**
![Component](file:///Users/satvikjain/Downloads/CRR - American Express/ISP Design Library/Hero.svg)

**Why It's Used:**
- Creates strong first impression
- Communicates primary value proposition
- Drives key user actions
- Sets visual tone for page

**Where It's Used:**

| Use Case | Example | Context |
|----------|---------|---------|
| **Homepage Banner** | "Get 75K bonus points with the Platinum Card" | Marketing landing page |
| **Product Launch** | New card introduction with key benefits | Product announcement |
| **Seasonal Campaign** | Holiday shopping bonus promotion | Limited-time offer |
| **Travel Portal** | "Book now and earn 5X points on flights" | Travel services |
| **Benefits Showcase** | Membership benefits overview with imagery | Value communication |
| **Welcome Screen** | Post-login personalized welcome message | User engagement |

---

### 31. **Journey Completion**
![Component](file:///Users/satvikjain/Downloads/CRR - American Express/ISP Design Library/Journey Completion.svg)

**Why It's Used:**
- Confirms successful task completion
- Provides next steps guidance
- Reduces user anxiety
- Encourages continued engagement

**Where It's Used:**

| Use Case | Example | Context |
|----------|---------|---------|
| **Card Application** | "Application submitted! What's next?" | Application confirmation |
| **Payment Success** | "Payment processed successfully" | Transaction confirmation |
| **Account Setup** | "Welcome aboard! Your account is ready" | Onboarding completion |
| **Offer Enrollment** | "You're all set! Offer added to your card" | Feature activation |
| **Document Upload** | "Documents received. We'll review within 3 days" | Submission confirmation |
| **Dispute Filed** | "Dispute submitted. Track status in your account" | Case initiation |

---

### 32. **Multi-Step Tracker**
![Component](file:///Users/satvikjain/Downloads/CRR - American Express/ISP Design Library/Multi-Step Tracker.svg)

**Why It's Used:**
- Shows progress through multi-page flows
- Sets clear expectations
- Reduces abandonment
- Provides context and orientation

**Where It's Used:**

| Use Case | Example | Context |
|----------|---------|---------|
| **Card Application** | Personal Info > Financial Info > Review > Submit | Application funnel |
| **Dispute Process** | Select Transaction > Provide Details > Upload Evidence > Confirm | Multi-step workflow |
| **Travel Booking** | Search > Select > Passenger Info > Payment > Confirmation | Reservation process |
| **Account Upgrade** | Current Plan > Select New Plan > Review Changes > Confirm | Plan modification |
| **Authorized User Setup** | Add User > User Details > Spending Limits > Confirmation | User management |
| **Report Generation** | Select Type > Choose Dates > Customize Fields > Download | Report builder |

---

## Feedback & Messaging Components

### 33. **Alert**
![Component](file:///Users/satvikjain/Downloads/CRR - American Express/ISP Design Library/Alert.svg)

**Why It's Used:**
- Provides contextual feedback
- Communicates important information
- Different severity levels (info, warning, error, success)
- Inline with related content

**Where It's Used:**

| Use Case | Example | Context |
|----------|---------|---------|
| **Security Warning** | "Your password will expire in 7 days" | Account security |
| **Payment Reminder** | "Payment due in 3 days" | Billing alert |
| **Feature Update** | "New contactless payment now available" | Product announcements |
| **Form Validation** | "Please correct errors before submitting" | Error messaging |
| **Promotional** | "Limited time: earn 2X points on dining" | Marketing messages |
| **Service Notice** | "Scheduled maintenance on Sunday 2-4 AM" | System notifications |

---

### 34. **Alert Dialog**
![Component](file:///Users/satvikjain/Downloads/CRR - American Express/ISP Design Library/Alert Dialog.svg)

**Why It's Used:**
- Interrupts user for critical information
- Requires user acknowledgment
- Prevents unintended actions
- Focuses attention on important decisions

**Where It's Used:**

| Use Case | Example | Context |
|----------|---------|---------|
| **Destructive Actions** | "Are you sure you want to close this account?" | Account closure |
| **Payment Confirmation** | "Confirm payment of $1,500.00?" | High-value transactions |
| **Card Lock** | "Lock your card to prevent transactions?" | Security action |
| **Session Timeout** | "You'll be logged out in 2 minutes. Continue?" | Session management |
| **Terms Changes** | "Terms updated. Please review and accept" | Legal requirements |
| **Fraud Alert** | "Suspicious activity detected. Was this you?" | Security verification |

---

### 35. **Page Level Notification**
![Component](file:///Users/satvikjain/Downloads/CRR - American Express/ISP Design Library/Page Level Notification.svg)

**Why It's Used:**
- Communicates system-wide messages
- Appears at top of page
- Can be dismissed by user
- Persists across pages if needed

**Where It's Used:**

| Use Case | Example | Context |
|----------|---------|---------|
| **System Maintenance** | "Some services may be unavailable during maintenance" | Platform-wide notice |
| **Account Issues** | "Your account requires verification" | Account-level alerts |
| **Promotion Banner** | "Refer a friend and earn 10,000 bonus points" | Marketing campaigns |
| **Security Update** | "Enable two-factor authentication for enhanced security" | Security recommendations |
| **Regulatory Notice** | "New privacy policy effective March 1" | Compliance communications |
| **Service Disruption** | "Experiencing delays in payment processing" | Operational updates |

---

### 36. **Tooltip**
![Component](file:///Users/satvikjain/Downloads/CRR - American Express/ISP Design Library/Tooltip.svg)

**Why It's Used:**
- Provides additional context on hover/tap
- Doesn't clutter interface
- Explains unfamiliar terms
- Improves accessibility

**Where It's Used:**

| Use Case | Example | Context |
|----------|---------|---------|
| **Term Definitions** | Hover over "APR" to see definition | Financial terminology |
| **Feature Explanations** | Info icon explaining "Auto-Pay" benefits | Feature education |
| **Icon Meaning** | Hover over status icon for description | Visual clarification |
| **Input Help** | Format example for SSN field | Form assistance |
| **Benefits Details** | Quick explanation of "Purchase Protection" | Benefit summaries |
| **Data Points** | Graph data point details on hover | Analytics tooltips |

---

### 37. **Info Tooltip**
![Component](file:///Users/satvikjain/Downloads/CRR - American Express/ISP Design Library/Info Tooltip.svg)

**Why It's Used:**
- Dedicated information icon triggers
- Persistent on click (mobile-friendly)
- More detailed than standard tooltip
- Educational micro-content

**Where It's Used:**

| Use Case | Example | Context |
|----------|---------|---------|
| **Fee Explanations** | Click (i) next to "Foreign Transaction Fee" | Transparent pricing |
| **Calculation Details** | How interest is calculated | Financial education |
| **Eligibility Criteria** | Requirements for credit limit increase | Qualification info |
| **Points Value** | How points translate to dollar value | Rewards understanding |
| **Security Features** | Explanation of fraud protection | Trust building |
| **Business Terms** | Corporate card program details | B2B communication |

---

### 38. **Modal**
![Component](file:///Users/satvikjain/Downloads/CRR - American Express/ISP Design Library/Modal.svg)

**Why It's Used:**
- Focuses attention on specific task
- Overlays main content
- Contains forms or confirmations
- Maintains context without navigation

**Where It's Used:**

| Use Case | Example | Context |
|----------|---------|---------|
| **Quick Actions** | Make payment modal without leaving dashboard | Task completion |
| **Detail Views** | Transaction details overlay | Information display |
| **Offer Enrollment** | Add offer to card confirmation | Feature activation |
| **Address Update** | Edit address form in modal | Quick edits |
| **Image Gallery** | View receipt or document image | Media viewer |
| **Terms Acceptance** | Display and accept updated terms | Legal compliance |

---

### 39. **Loaders**
![Component](file:///Users/satvikjain/Downloads/CRR - American Express/ISP Design Library/Loaders.svg)

**Why It's Used:**
- Indicates processing or loading state
- Prevents user confusion during delays
- Builds trust through transparency
- Reduces perceived wait time

**Where It's Used:**

| Use Case | Example | Context |
|----------|---------|---------|
| **Payment Processing** | Spinner while payment is being processed | Transaction submission |
| **Data Loading** | Loading transactions or statements | Content retrieval |
| **Application Submit** | Processing card application | Form submission |
| **Search Results** | Loading search results | Query execution |
| **Page Transitions** | Loading next page content | Navigation |
| **Document Generation** | Creating PDF statement | File creation |

---

### 40. **Assistance**
![Component](file:///Users/satvikjain/Downloads/CRR - American Express/ISP Design Library/Assistance.svg)

**Why It's Used:**
- Provides contextual help
- Guides users through complex tasks
- Reduces support requests
- Improves user confidence

**Where It's Used:**

| Use Case | Example | Context |
|----------|---------|---------|
| **Form Help** | Inline guidance for card application fields | Application assistance |
| **Feature Introduction** | First-time user walkthroughs | Onboarding |
| **Error Recovery** | Suggested actions when error occurs | Problem resolution |
| **Best Practices** | Tips for maximizing rewards | User education |
| **Security Guidance** | How to protect account information | Security awareness |
| **Process Explanation** | Step-by-step dispute filing help | Complex workflows |

---

## Interactive Components

### 41. **Buttons (Base)**
![Component](file:///Users/satvikjain/Downloads/CRR - American Express/ISP Design Library/ButtonsBase.svg)

**Why It's Used:**
- Primary interaction element
- Clear call-to-action
- Multiple styles (primary, secondary, tertiary)
- Consistent across platform

**Where It's Used:**

| Use Case | Example | Context |
|----------|---------|---------|
| **Form Submission** | "Submit Application", "Continue", "Save" | Action completion |
| **Navigation** | "Back", "Next", "Cancel" | Flow control |
| **Transactions** | "Make Payment", "Transfer Funds" | Financial actions |
| **Feature Actions** | "Add to Card", "Redeem", "Activate" | Feature engagement |
| **Account Management** | "Update Profile", "Change Password" | Settings modification |
| **Content Actions** | "Download Statement", "Print", "Share" | Content operations |

---

### 42. **Links**
![Component](file:///Users/satvikjain/Downloads/CRR - American Express/ISP Design Library/Links.svg)

**Why It's Used:**
- Lightweight navigation
- Connects related content
- Less prominent than buttons
- Supports text flow naturally

**Where It's Used:**

| Use Case | Example | Context |
|----------|---------|---------|
| **Navigation** | "View all transactions", "See more offers" | Content discovery |
| **Help Resources** | "Learn more about this benefit" | Educational links |
| **Related Actions** | "Forgot password?", "Update preferences" | Secondary actions |
| **External Resources** | "Read terms and conditions" | Document access |
| **Cross-selling** | "Compare other cards" | Product exploration |
| **Support** | "Contact customer service" | Help access |

---

### 43. **Overflow Menu**
![Component](file:///Users/satvikjain/Downloads/CRR - American Express/ISP Design Library/Overflow Menu.svg)

**Why It's Used:**
- Hides secondary actions
- Saves screen space
- Organizes multiple options
- Reduces visual clutter

**Where It's Used:**

| Use Case | Example | Context |
|----------|---------|---------|
| **Transaction Actions** | Dispute, Download Receipt, Categorize, Add Note | Row-level actions |
| **Card Management** | Report Lost, Request Replacement, View PIN, Lock Card | Card controls |
| **Account Options** | Settings, Help, Logout, Switch Account | User menu |
| **Content Actions** | Share, Download, Print, Email | Document operations |
| **List Item Actions** | Edit, Delete, Duplicate, Archive | Data management |
| **Offer Actions** | Save for Later, Share, Hide, Report Issue | Promotion management |

---

### 44. **Select Menu**
![Component](file:///Users/satvikjain/Downloads/CRR - American Express/ISP Design Library/Select Menu.svg)

**Why It's Used:**
- Dropdown with rich formatting
- Supports icons and descriptions
- Better UX for complex options
- Searchable for long lists

**Where It's Used:**

| Use Case | Example | Context |
|----------|---------|---------|
| **Account Selection** | Choose from multiple cards with icons | Multi-card holders |
| **Payment Method** | Select payment source with last 4 digits | Payment options |
| **Redemption Options** | Points redemption types with values | Rewards management |
| **Report Types** | Business report templates with descriptions | Analytics tools |
| **Benefit Selection** | Available benefits with eligibility status | Membership features |
| **Transfer Partners** | Airline partners with transfer ratios | Points transfer |

---

### 45. **Filters**
![Component](file:///Users/satvikjain/Downloads/CRR - American Express/ISP Design Library/Filters.svg)

**Why It's Used:**
- Refines large data sets
- Multiple filter criteria
- Shows active filters clearly
- Improves content discovery

**Where It's Used:**

| Use Case | Example | Context |
|----------|---------|---------|
| **Transaction Filtering** | By date, amount, category, merchant | Activity exploration |
| **Offer Discovery** | By category, location, expiry | Promotion browsing |
| **Statement Search** | By year, account, type | Document retrieval |
| **Travel Search** | Destination, dates, price, amenities | Booking tools |
| **Employee Reports** | By department, date range, status | Business analytics |
| **Help Articles** | By topic, product, issue type | Knowledge base |

---

### 46. **Copy Link**
![Component](file:///Users/satvikjain/Downloads/CRR - American Express/ISP Design Library/CopyLink.svg)

**Why It's Used:**
- Easy sharing functionality
- One-click copy to clipboard
- Confirmation feedback
- Improves viral sharing

**Where It's Used:**

| Use Case | Example | Context |
|----------|---------|---------|
| **Referral Programs** | Copy referral link to share | Customer acquisition |
| **Transaction Sharing** | Share transaction details with accountant | Financial management |
| **Offer Sharing** | Copy offer link to share with friend | Promotion distribution |
| **Travel Itinerary** | Copy booking confirmation link | Trip coordination |
| **Payment Links** | Share payment request link | Bill splitting |
| **Support Cases** | Copy case reference number | Customer service |

---

## Layout Components

### 47. **Divider**
![Component](file:///Users/satvikjain/Downloads/CRR - American Express/ISP Design Library/Divider.svg)

**Why It's Used:**
- Separates content sections
- Creates visual hierarchy
- Improves scannability
- Subtle wayfinding aid

**Where It's Used:**

| Use Case | Example | Context |
|----------|---------|---------|
| **Section Separation** | Between dashboard widgets | Content organization |
| **List Items** | Between transaction rows | Data presentation |
| **Form Sections** | Between Personal and Financial info | Form structure |
| **Menu Items** | Between different action groups | Navigation clarity |
| **Statement Sections** | Between Payments and Purchases | Document organization |
| **Settings Groups** | Between different preference categories | Settings UI |

---

### 48. **Bars (Progress/Status)**
![Component](file:///Users/satvikjain/Downloads/CRR - American Express/ISP Design Library/Bars.svg)

**Why It's Used:**
- Visual progress indication
- Shows proportions clearly
- Gamifies goals and milestones
- Quick status comprehension

**Where It's Used:**

| Use Case | Example | Context |
|----------|---------|---------|
| **Spending vs Budget** | Show percentage of budget used | Spending tracking |
| **Credit Utilization** | Visual of credit used vs available | Credit health |
| **Points Progress** | Progress toward bonus threshold | Rewards motivation |
| **Profile Completion** | Account setup progress | Onboarding encouragement |
| **Application Status** | Steps completed in application | Process transparency |
| **Goal Tracking** | Savings or points goals | Financial objectives |

---

### 49. **Chevron (Navigation)**
![Component](file:///Users/satvikjain/Downloads/CRR - American Express/ISP Design Library/Chevron.svg)

**Why It's Used:**
- Indicates expandable content
- Shows navigation direction
- Universal wayfinding symbol
- Minimal design footprint

**Where It's Used:**

| Use Case | Example | Context |
|----------|---------|---------|
| **Accordion Triggers** | Expand/collapse transaction details | Content reveal |
| **Navigation Indicators** | Menu item has submenu | Depth indication |
| **Carousel Controls** | Next/previous slide arrows | Content browsing |
| **Breadcrumb Separators** | Home > Account > Settings | Path visualization |
| **Dropdowns** | Open select menu indicator | Interaction cue |
| **List Navigation** | Navigate to detail page | Forward movement |

---

### 50. **Unauthenticated Footer**
![Component](file:///Users/satvikjain/Downloads/CRR - American Express/ISP Design Library/Unauthenticated Footer.svg)

**Why It's Used:**
- Provides legal and secondary links
- Consistent brand presence
- SEO and accessibility
- Contact and social information

**Where It's Used:**

| Use Case | Example | Context |
|----------|---------|---------|
| **Marketing Pages** | Terms, Privacy, About, Contact, Careers | Public website footer |
| **Product Pages** | Card disclosure, rates & fees, important terms | Transparency requirements |
| **Help Center** | Support topics, contact options, site map | Service access |
| **Pre-Login** | Login, apply now, explore cards | Conversion prompts |
| **Legal Pages** | Copyright, accessibility, privacy notice | Compliance |
| **Global Navigation** | International sites, language selection | Localization |

---

## Summary & Best Practices

### Component Selection Guidelines

> [!IMPORTANT]
> **Accessibility First**: All ISP components are designed to meet WCAG 2.1 AA standards. Always maintain color contrast, keyboard navigation, and screen reader support.

> [!TIP]
> **Mobile-First Approach**: ISP components are responsive by default. Consider mobile interactions first, then enhance for desktop.

> [!WARNING]
> **Consistency is Critical**: Using ISP components consistently across AmEx products ensures:
> - Brand cohesion
> - Reduced development time
> - Better user experience through familiarity
> - Easier maintenance and updates

---

### Common Component Combinations

**Dashboard Layout:**
- Hero (welcome banner) + Cards (account summaries) + Data Table (recent transactions) + Page Level Notification (alerts)

**Application Flow:**
- Multi-Step Tracker + Form Components (Text Input, Select, Radio, Checkbox) + Alert Dialog + Journey Completion

**Search & Browse:**
- Search + Filters + Data Table/Card Grid + Pagination + Dismissible Tags

**Account Management:**
- Tabs + Vertical Navigation + Cards + Toggle Switches + Modals

**Mobile Optimization:**
- Accordion Panels + Overflow Menus + Toggle Switches + Floating Action Buttons

---

### ISP Design Principles

1. **Clarity**: Components communicate purpose clearly
2. **Efficiency**: Reduce user effort and cognitive load
3. **Consistency**: Familiar patterns across all touchpoints
4. **Trust**: Professional, secure, reliable experience
5. **Accessibility**: Inclusive design for all users

---

## Document Information

**Version**: 1.0  
**Last Updated**: December 2024  
**Maintained By**: ISP Design Systems Team  
**For Questions**: Contact the AmEx UX Design team

---

*This catalog is a living document and will be updated as new components are added or existing ones are enhanced.*
