# VYNTRIX — Voice-of-Store Intelligence Engine
**Track R5: “Turning Store Chatter Into Action: The Voice-of-Store Engine”**  
*Talent AP Mega Hackathon 2026*

---

## 1. Project Overview & Architectural Vision

Retail businesses receive thousands of unstructured customer reviews, in-app comments, shift notes, and support transcripts every week. This raw store chatter contains spelling mistakes, slang, emojis, truncated sentences, and mixed expressions. Critical operational hazards—such as undeclared food allergens, unattended physical slips, sanitation failures, or acute checkout bottlenecks—frequently remain buried in volume until legal action, brand damage, or customer attrition occurs.

**VYNTRIX** bridges the gap between raw store chatter and operational resolution:
1. **Intelligent Issue Classification:** Maps messy, unstructured comments to 8 canonical operational categories.
2. **Deterministic Severity & Statutory Escalation:** Enforces mandatory High priority and incident escalation for all Safety, Hygiene, and Allergen risks, ensuring zero regulatory compliance slip-through regardless of feedback frequency.
3. **Departmental Ownership Routing:** Automatically directs feedback to the responsible team (`Store Safety Team`, `Food Safety Team`, `Quality Team`, `Store Operations`, `Inventory Team`, `Customer Experience`).
4. **Store-Level Trend Intelligence:** Compares weekly store-normalized rates against historical baselines, applying configurable evidence thresholds to detect emerging localized spikes without false alarms.
5. **Evidence-Backed Regional Briefs:** Autonomously compiles executive-ready reports with verbatim quotes, trend trajectories, and risk-weighted recommendations with one-click Markdown and CSV export.

---

## 2. Technology Stack & Design Decisions

- **Web Interface:** **Streamlit** (`app.py`) featuring an enterprise dark navy, white, and teal SaaS palette, responsive KPI metric cards, sidebar navigation, reactive filters, and one-click report downloads.
- **Data Engineering:** **Pandas** & **NumPy** for vectorised data manipulation, column alias mapping, and time-series aggregation.
- **Visualisation:** **Plotly Express** & **Graph Objects** for interactive category bars, channel donut charts, and time-series distributions.
- **NLP & Classification:** Deterministic, regex-powered rule engine with statutory escalation logic and extensible TF-IDF + Logistic Regression architecture.
- **Theme & Palette:** Enterprise Dark Navy (`#0F172A`), Slate (`#1E293B`), Teal Accent (`#0D9488`), and Cyan (`#06B6D4`).

---

## 3. Quick-Start Local Installation & Launch

### Prerequisites
- Python 3.9+ installed on your laptop or workstation
- Standard virtual environment tools

### Step 1: Clone or Navigate to Project Directory
```bash
cd vyntrix
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run the Streamlit Web Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 4. Five-Minute Hackathon Live Demonstration Script

Follow this 6-step walkthrough for an impactful live demonstration to judges:

### Step 1: Open Executive Dashboard (Minute 0:00 - 1:00)
- Navigate to the **Executive Dashboard**.
- Show the 4 top KPI cards: **Total Feedback (265 records)**, **High-Priority Issues (46.4%)**, **Escalations Mandated (123)**, and **Monitored Stores (6 locations)**.
- Highlight the **Issue Category Distribution** bar chart and **Channel Breakdown** (Reviews, In-App, Shift Notes, Support Transcripts).
- Point out the **Recent Critical Alerts** banner showing urgent incidents flagged for immediate escalation.

### Step 2: Filter and Audit in Feedback Explorer (Minute 1:00 - 1:45)
- Switch to **Feedback Explorer**.
- In the search bar, type `peanut` or `slip` or `expired`.
- Show how the table instantly filters records while displaying the original raw text, assigned category, severity badge, and owning department.
- Select any record ID in the **Deep-Dive Inspector** to reveal the full audit trail: original text, trigger cues, and recommended action.

### Step 3: Test Interactive Feedback Analyzer (Minute 1:45 - 2:45)
- Open the **Interactive Feedback Analyzer**.
- Click the preset button **🥜 Allergen Violation**:
  > *"Bakery cookies contain undeclared peanuts, my child with nut allergy had severe hives! 🥜"*
- Click **Run Operational Analysis**:
  - Show that it immediately classifies as:
    - **Category:** `Allergen Concern`
    - **Severity:** `High` (Red badge)
    - **Department:** `Food Safety Team`
    - **Escalation Required:** `YES — MANDATORY` (Statutory Policy)
  - Review the tactical recommended action: immediate SKU quarantine, cross-contact audit, and regional QA alert.
- Now click **⏱️ Long Checkout Queue**:
  > *"Waited 40 mins in line with only 1 register open on Saturday afternoon rush! 😡"*
  - Show dynamic reclassification:
    - **Category:** `Long Queue`
    - **Severity:** `High` (>30 min wait trigger)
    - **Department:** `Store Operations`
    - **Escalation Required:** `YES — ESCALATE` (Code Green checkout backup)

### Step 4: Explore Store-Level Trend Intelligence (Minute 2:45 - 3:45)
- Switch to **Store-Level Trend Intelligence**.
- Select target evaluation week `2026-W09` (or `2026-W08`).
- Highlight how the engine detects **emerging operational spikes** normalized against each store's baseline:
  - **Store STR-103 (Metro North Express):** `Allergen Concern` spiked to 35.7% vs historical baseline of 2.6% (+33.1 pp, 13.9x baseline).
  - **Store STR-101 (Downtown Flagship):** `Stock Availability` out-of-stock rate spiked to 58.3% vs baseline 10.8% (+47.5 pp).
- Show the **Insufficient Baseline Data** notice:
  - **Store STR-106 (Harbor Point):** Brand new store opened in week 8 with 0 prior baseline weeks. Explain that VYNTRIX transparently suppresses false alarm statistical spikes until 2 baseline weeks exist.

### Step 5: Generate & Download Weekly Regional Brief (Minute 3:45 - 4:30)
- Go to **Weekly Regional Brief**.
- Show the live rendered executive summary with Top 5 issues, severity mix, affected store distribution, and customer quotes.
- Click **📥 Download Regional Brief (Markdown .md)** and open the downloaded report.
- Click **📥 Download Regional Summary (CSV)** to demonstrate seamless data export.

### Step 6: Verify Data Import & Template Management (Minute 4:30 - 5:00)
- Navigate to **Data Import & Dataset Management**.
- Click **📄 Download Sample CSV Template** to demonstrate how store managers can format custom chatter data.
- Mention flexible column alias mapping (`comment` -> `original_text`, `location` -> `store_id`).
- Click **🔄 Reset to Benchmark Demonstration Dataset** to show instant system restoration.

---

## 5. Sample Feedback Messages to Test in Analyzer

| # | Sample Text | Expected Category | Expected Severity | Owning Department | Escalation? |
|---|---|---|---|---|---|
| 1 | *"Water leaking from refrigeration unit puddle on floor without any yellow warning sign 🚨"* | Safety | High | Store Safety Team | Yes |
| 2 | *"Bakery cookies contain undeclared peanuts, my son had severe allergic reaction! 🥜"* | Allergen Concern | High | Food Safety Team | Yes |
| 3 | *"Saw a live rat crawling behind the bakery display case 🐀 disgusting"* | Hygiene | High | Food Safety / Store Operations | Yes |
| 4 | *"Waited 45 mins in line with only 1 cashier open on Saturday"* | Long Queue | High | Store Operations | Yes |
| 5 | *"Bought milk that expired 4 days ago, smelled sour and curdled milkkkk! 🤢"* | Product Quality | Medium | Quality Team | No |
| 6 | *"Shelves completely empty in dairy section, no 2% milk or butter for 3 days"* | Stock Availability | High | Inventory Team | Yes |
| 7 | *"Cashier was extremely rude, rolled her eyes and threw my change on counter"* | Staff Service | Medium | Customer Experience | No |
| 8 | *"Receipt printer ink was faint and hard to read"* | Other / Unclear | Low | Manual Review | No |

---

## 6. Core Business Logic & Rule Engine Transparency

### Operational Mappings
- `Product Quality` → **Quality Team**
- `Hygiene` → **Food Safety / Store Operations**
- `Safety` → **Store Safety Team**
- `Allergen Concern` → **Food Safety Team**
- `Stock Availability` → **Inventory Team**
- `Long Queue` → **Store Operations**
- `Staff Service` → **Customer Experience**
- `Other / Unclear` → **Manual Review**

### Mandatory Statutory Escalation Rule
Safety, hygiene, and allergen issues automatically receive **High priority** and **Immediate Escalation**, regardless of feedback volume. In retail operations, a single customer reporting an anaphylactic allergen reaction or a physical slip hazard carries statutory regulatory liability and potential bodily harm. VYNTRIX guarantees these issues can never be masked by high-volume minor complaints.

### Rules vs Machine Learning Transparency
- **Operational Classification Engine:** VYNTRIX utilizes a transparent, deterministic pattern and regular-expression engine with statutory overrides. This provides 100% explainability, zero-shot operation without costly training pipelines, and guaranteed SLA adherence for compliance issues.
- **ML Baseline Architecture:** The codebase includes a modular `FeedbackClassifier` design supporting scikit-learn `TfidfVectorizer` + `LogisticRegression`. In strict adherence to hackathon evaluation guidelines, **we do not claim an ML model is trained without verified human ground-truth labels**. The deterministic rule engine serves as the reliable operational foundation.

---

## 7. Automated Testing & Verification

Run the comprehensive test suite validating all 12 track requirements:
```bash
python3 tests/test_vyntrix.py
```

### Test Suite Coverage (12 Core Validations):
1. `test_01_modules_initialization`: Verifies core modules and department dictionaries load.
2. `test_02_demo_data_loading`: Validates synthetic benchmark dataset integrity (265 records).
3. `test_03_filtering_functionality`: Tests multi-variable filtering across store, channel, severity.
4. `test_04_feedback_analyzer_dynamic_output`: Verifies dynamic classification output for new user input.
5. `test_05_safety_mandatory_high_and_escalation`: Verifies 100% High severity & escalation for safety.
6. `test_06_hygiene_mandatory_high_and_escalation`: Verifies 100% High severity & escalation for hygiene.
7. `test_07_allergen_mandatory_high_and_escalation`: Verifies 100% High severity & escalation for allergens.
8. `test_08_department_ownership_mappings`: Verifies correct department routing for all 8 categories.
9. `test_09_store_trends_insufficient_history`: Validates suppression of false alerts for stores with < 2 baseline weeks.
10. `test_10_csv_upload_and_validation`: Tests CSV alias mapping and missing column detection.
11. `test_11_weekly_regional_brief_generation`: Validates Markdown and CSV report generation.
12. `test_12_empty_and_invalid_input_handling`: Verifies graceful error handling for empty or malformed inputs.

---

## 8. Known Limitations & Future Roadmap

1. **Multi-Language Chatter:** Current classification focuses on English retail chatter with slang and emojis. Future releases will integrate multilingual tokenizers (e.g. XLM-RoBERTa) for regional Indian languages (Telugu, Hindi, Tamil).
2. **Automated Ticketing Webhooks:** Integration with enterprise ticketing systems (Jira Service Management, ServiceNow, Zendesk) to auto-dispatch incident tickets upon escalation trigger.
3. **Computer Vision Integration:** Combining photo attachments (e.g. photos of broken glass, receipt barcodes, expired expiration dates) with text chatter for multi-modal verification.
4. **Historical Auto-Clustering:** Unsupervised DBSCAN / HDBSCAN clustering on embeddings to surface net-new operational categories previously unknown to store operations.

---
*Developed for Talent AP Mega Hackathon 2026 • Track R5*
