"""
VYNTRIX Rule-Based and Hybrid Classification Engine
Provides deterministic, explainable category routing, severity evaluation,
and compliance-driven escalation triggers.
"""

import re
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
from vyntrix.config import (
    CAT_PRODUCT_QUALITY,
    CAT_HYGIENE,
    CAT_SAFETY,
    CAT_ALLERGEN,
    CAT_STOCK,
    CAT_QUEUE,
    CAT_STAFF,
    CAT_OTHER,
    DEPARTMENT_MAPPING,
    MANDATORY_HIGH_CATEGORIES,
    SEV_HIGH,
    SEV_MEDIUM,
    SEV_LOW,
)
from vyntrix.text_cleaner import clean_text_for_nlp

KEYWORD_PATTERNS = {
    CAT_ALLERGEN: [
        r"\ballerg\w*\b",
        r"\banaphyla\w*\b",
        r"\bpeanut(s)?\b",
        r"\btree\s*nut(s)?\b",
        r"\bwalnut(s)?\b",
        r"\bpecan(s)?\b",
        r"\balmond(s)?\b",
        r"\bnut[- ]free\b",
        r"\bpeanut[- ]free\b",
        r"\bdairy[- ]free\b",
        r"\bgluten(\s*free)?\b",
        r"\bceliac\b",
        r"\bcross\s*contaminat\w*\b",
        r"\bcross\s*contact\b",
        r"\bunlabel(l)?ed\s*(allergen|nut|peanut|dairy|gluten)?\b",
        r"\bmislab(el|eled|elled)\b",
        r"\bepipen\b",
        r"\bhives\b",
        r"\bswollen\s*(throat|tongue|lip|face)\b",
        r"🥜"
    ],
    CAT_SAFETY: [
        r"\bslip(p)?(ed|y|ing)?\b",
        r"\btrip(p)?(ed|ing)?\b",
        r"\bfall(en|ing)?\b",
        r"\bfell\b",
        r"\bspill(ed|ing)?\s*(oil|water|liquid|chemical)?\b",
        r"\b(water|pipe|ceiling|refrigeration|oil|chemical)\s*(is\s*)?leak\w*\b",
        r"\bleak(ing)?\s*(water|oil|pipe|ceiling)\b",
        r"\bwet\s*floor\b",
        r"\bpuddle\b",
        r"\bwater\s*(on|puddle|leak)\b",
        r"\boil\s*spill\b",
        r"\bexposed\s*wir\w*\b",
        r"\bbroken\s*glass\b",
        r"\bsharp\s*edge\b",
        r"\bshatter(ed)?\b",
        r"\bhazard(ous)?\b",
        r"\bdanger(ous)?\b",
        r"\binjur(y|ed|ies|ing)\b",
        r"\bhurt\b",
        r"\bbleed(ing)?\b",
        r"\bcut\s*my\s*(finger|hand|leg|foot)\b",
        r"\bambulance\b",
        r"\bemergency\b",
        r"\bfire\s*exit\s*block(ed)?\b",
        r"\bheavy\s*box(es)?\s*(fell|dropped)\b",
        r"\bunsecured\s*stock\b",
        r"⚠️",
        r"🚨",
        r"⚡"
    ],
    CAT_HYGIENE: [
        r"\broach(es)?\b",
        r"\bcockroach(es)?\b",
        r"\brat(s)?\b",
        r"\bm(ouse|ice)\b",
        r"\brodent(s)?\b",
        r"\bpest(s)?\b",
        r"\bbug(s)?\b",
        r"\bflies|fly\b",
        r"\binsect(s)?\b",
        r"\bmaggot(s)?\b",
        r"\bdropping(s)?\b",
        r"\bpoop|feces\b",
        r"\bfilth(y)?\b",
        r"\bdisgusting\b",
        r"\bvomit(ed|ing)?\b",
        r"\bdirty\s*(restroom|bathroom|toilet|counter|floor|shelf)\b",
        r"\bunwashed\b",
        r"\bmoldy|mouldy\b",
        r"\bslime|slimy\b",
        r"\bfoul\s*odor|stench|stink(s|y)?\b",
        r"\btrash\s*overflow\w*\b",
        r"\bunhygienic\b",
        r"\bhealth\s*code\s*violation\b",
        r"\bfood\s*poisoning\b",
        r"\bsick\s*after\s*eating\b",
        r"\bleaking\s*(dark|foul|smelly|blood|fluid|liquid)\b",
        r"🤢",
        r"🤮",
        r"🐀",
        r"🪳"
    ],
    CAT_PRODUCT_QUALITY: [
        r"\bexpir(ed|y|ation)\b",
        r"\bpast\s*(sell\s*by|best\s*by|use\s*by|date)\b",
        r"\bpast\s*date\b",
        r"\bspoil(ed|t|age)\b",
        r"\bsour\s*(milk|cream|yogurt)?\b",
        r"\brancid\b",
        r"\bstale\b",
        r"\brotten|rot(ting)?\b",
        r"\bferment(ing|ed)?\b",
        r"\bbruis(ed|ing)\s*(fruit|apple|banana|produce)?\b",
        r"\bcurdle(d)?\b",
        r"\bfreezer\s*burn\b",
        r"\bbroken\s*seal\b",
        r"\bdamag(ed|e)\s*(box|carton|can|pack|item|packaging)\b",
        r"\bdent(ed)?\s*can\b",
        r"\bleak(ing)?\s*(bottle|carton|pack|meat)\b",
        r"\bdefective\b",
        r"\bbad\s*batch\b",
        r"\bterrible\s*quality\b"
    ],
    CAT_QUEUE: [
        r"\bqueue(s)?\b",
        r"\blong\s*(line|lines|queue)\b",
        r"\bwait(ed|ing)?\s*time\b",
        r"\bwait(ed|ing)?\s*(for)?\s*\d+\s*(min|minute|mins|minutes|hr|hour)\b",
        r"\b(20|25|30|35|40|45|50|60)\s*(min|minute|mins|minutes)\b",
        r"\bslow\s*(checkout|cashier|service|registers|pace)\b",
        r"\bonly\s*(one|1|2)\s*(cashier|counter|register|lane)\s*(open|working)?\b",
        r"\bline(s)?\s*(backed\s*up|moving|wrapped)\b",
        r"\bline\s*moving\s*at\s*snail\s*pace\b",
        r"\bself[- ]checkout\b",
        r"\babandon(ed)?\s*(my\s*)?cart\b",
        r"\bwalk(ed)?\s*out\b"
    ],
    CAT_STOCK: [
        r"\bout\s*of\s*stock\b",
        r"\bempty\s*shel(f|ves)\b",
        r"\bshel(f|ves)\s*(are|were|completely|totally)?\s*(empty|bare)\b",
        r"\bbare\s*shelves\b",
        r"\bno\s*(stock|inventory)\b",
        r"\bnot\s*in\s*stock\b",
        r"\bsold\s*out\b",
        r"\bcan(')?t\s*find\s*(any)?\b",
        r"\bunavailable\b",
        r"\bshortage\b",
        r"\bnever\s*in\s*stock\b",
        r"\bnever\s*have\b",
        r"\bnot\s*restock(ed)?\b",
        r"\brun\s*out\s*of\b",
        r"\bnothing\s*on\s*(the\s*)?shelves\b",
        r"\bno\s*(2%|whole|skim)?\s*(milk|butter|eggs|baby\s*formula|water|bread)\b",
        r"\bzero\s*inventory\b"
    ],
    CAT_STAFF: [
        r"\brude\b",
        r"\battitude\b",
        r"\bunfriendly\b",
        r"\bunhelpful\b",
        r"\byell(ed|ing)?\b",
        r"\bshout(ed)?\b",
        r"\bignor(ed|ing)\b",
        r"\bdisrespectful\b",
        r"\baggressiv(e|ely)\b",
        r"\bconfrontational\b",
        r"\beye(s)?\s*roll(ing)?\b",
        r"\brefused\s*to\s*help\b",
        r"\bthrew\s*(the\s*)?(receipt|change|item|bag)\b",
        r"\bsnatched\b",
        r"\blazy\b",
        r"\bunprofessional\b",
        r"\bdiscriminat(ory|ion|ed)\b",
        r"\bracist|racial\b",
        r"\bswear(ing)?|curse|cursed\b",
        r"\bmistreat(ed|ing)?\b",
        r"\bsarcastic\b"
    ]
}

RECOMMENDED_ACTIONS = {
    CAT_ALLERGEN: (
        "1. Quarantine affected product batch immediately from retail floor.\n"
        "2. Inspect product packaging against regulatory allergen warning labels.\n"
        "3. Review deli/bakery prep area for cross-contact protocols.\n"
        "4. Escalate incident to Regional Food Safety Director within 1 hour."
    ),
    CAT_SAFETY: (
        "1. Deploy store associate to immediately cordon off and clean the physical hazard.\n"
        "2. Verify slip/trip hazard log and safety warning signage placement.\n"
        "3. Check CCTV footage and document customer incident report.\n"
        "4. File compliance notice with Store Safety Team."
    ),
    CAT_HYGIENE: (
        "1. Dispatch custodial team for deep sanitization of the reported area.\n"
        "2. If pest-related, initiate urgent pest control audit with contracted vendor.\n"
        "3. Inspect nearby food displays, refrigeration units, and storage bins.\n"
        "4. Log remediation report for Food Safety / Store Operations inspection."
    ),
    CAT_PRODUCT_QUALITY: {
        SEV_HIGH: "Quarantine entire SKU batch from display; initiate cold-chain audit and supplier quality inquiry.",
        SEV_MEDIUM: "Conduct immediate shelf sweep for expired/damaged SKUs; process customer replacement/refund.",
        SEV_LOW: "Instruct stock team to rotate stock (FIFO) and inspect packaging during daily shift turnover."
    },
    CAT_QUEUE: {
        SEV_HIGH: "Activate Code Green checkout backup; reassign floor associates to open 2 additional cashier lanes immediately.",
        SEV_MEDIUM: "Check shift staffing schedule against peak transaction volume; verify self-checkout terminal uptime.",
        SEV_LOW: "Monitor queue length during peak hours and balance break schedules."
    },
    CAT_STOCK: {
        SEV_HIGH: "Alert Regional Inventory Planner for emergency replenishment push; verify on-hand inventory count discrepancies.",
        SEV_MEDIUM: "Place expedited warehouse restocking order; update store shelf tags with expected arrival dates.",
        SEV_LOW: "Add requested product to weekly restock replenishment list; verify backroom inventory."
    },
    CAT_STAFF: {
        SEV_HIGH: "Store General Manager to contact customer for resolution; initiate formal internal review with HR.",
        SEV_MEDIUM: "Department supervisor to conduct shift coaching session on customer service standards and de-escalation.",
        SEV_LOW: "Include feedback theme in weekly store huddle; reinforce customer greeting expectations."
    },
    CAT_OTHER: {
        SEV_HIGH: "Flag for priority Operations Management review within 24 hours.",
        SEV_MEDIUM: "Route to Store Support Team for categorization and review.",
        SEV_LOW: "Archive in general store feedback repository for trend aggregation."
    }
}


class FeedbackClassifier:
    def __init__(self):
        self.ml_model = None
        self.vectorizer = None
        self.is_ml_trained = False

    def classify_text(self, text: str) -> Dict[str, Any]:
        if text is None or not str(text).strip() or text == "[No Text Provided]":
            return {
                "category": CAT_OTHER,
                "severity": SEV_LOW,
                "department": DEPARTMENT_MAPPING[CAT_OTHER],
                "escalation_required": False,
                "explanation": "No text provided. Routed to Manual Review with Low severity.",
                "recommended_action": "Verify if feedback text was lost during capture or transmission.",
                "evidence_snippets": [],
                "model_type": "Deterministic Rule Engine (Empty Input Handler)"
            }

        cleaned = clean_text_for_nlp(str(text))
        lower_text = cleaned.lower()

        matched_categories: List[Tuple[str, List[str]]] = []

        for cat, patterns in KEYWORD_PATTERNS.items():
            matches = []
            for pat in patterns:
                found = re.findall(pat, lower_text, flags=re.IGNORECASE)
                if found:
                    for m in re.finditer(pat, lower_text, flags=re.IGNORECASE):
                        matches.append(m.group(0))
            if matches:
                unique_matches = list(dict.fromkeys(matches))
                matched_categories.append((cat, unique_matches))

        chosen_cat = CAT_OTHER
        matched_tokens = []

        if matched_categories:
            # Check mandatory compliance categories first
            # If Hygiene cues exist (rat, roach, feces, rotten, stench, etc.), prioritize Hygiene/Food Safety
            # Allergen is always top priority
            has_hygiene_cues = any(c == CAT_HYGIENE for c, _ in matched_categories)
            if has_hygiene_cues:
                mandatory_order = [CAT_ALLERGEN, CAT_HYGIENE, CAT_SAFETY]
            else:
                mandatory_order = [CAT_ALLERGEN, CAT_SAFETY, CAT_HYGIENE]

            found_mandatory = False
            for mand_cat in mandatory_order:
                for cat, tokens in matched_categories:
                    if cat == mand_cat:
                        chosen_cat = cat
                        matched_tokens = tokens
                        found_mandatory = True
                        break
                if found_mandatory:
                    break

            if not found_mandatory:
                priority_order = [
                    CAT_PRODUCT_QUALITY,
                    CAT_QUEUE,
                    CAT_STOCK,
                    CAT_STAFF
                ]
                sorted_by_priority = sorted(
                    matched_categories,
                    key=lambda x: (
                        -len(x[1]),
                        priority_order.index(x[0]) if x[0] in priority_order else 99
                    )
                )
                chosen_cat = sorted_by_priority[0][0]
                matched_tokens = sorted_by_priority[0][1]

        severity, escalation_required, severity_reason = self._determine_severity(
            chosen_cat, lower_text, matched_tokens
        )

        department = DEPARTMENT_MAPPING.get(chosen_cat, "Manual Review")

        if chosen_cat in [CAT_ALLERGEN, CAT_SAFETY, CAT_HYGIENE]:
            action = RECOMMENDED_ACTIONS[chosen_cat]
        else:
            cat_actions = RECOMMENDED_ACTIONS.get(chosen_cat, RECOMMENDED_ACTIONS[CAT_OTHER])
            if isinstance(cat_actions, dict):
                action = cat_actions.get(severity, cat_actions[SEV_LOW])
            else:
                action = str(cat_actions)

        explanation = self._build_explanation(
            chosen_cat, severity, escalation_required, severity_reason, matched_tokens
        )

        return {
            "category": chosen_cat,
            "severity": severity,
            "department": department,
            "escalation_required": escalation_required,
            "explanation": explanation,
            "recommended_action": action,
            "evidence_snippets": matched_tokens,
            "model_type": "Deterministic Rule Engine (v1.0 Zero-shot)"
        }

    def _determine_severity(
        self, category: str, text: str, matched_tokens: List[str]
    ) -> Tuple[str, bool, str]:
        if category in MANDATORY_HIGH_CATEGORIES:
            reason = (
                f"Statutory Risk Policy: Issues categorized under '{category}' pose direct legal, health, "
                f"or physical safety liabilities and must receive High priority and immediate operational escalation."
            )
            return SEV_HIGH, True, reason

        if category == CAT_PRODUCT_QUALITY:
            high_indicators = [
                r"\bpoison(ing)?\b", r"\bsick\b", r"\bvomi(t|ting)\b", r"\brancid\b",
                r"\brotten\b", r"\bbaby\s*food\b", r"\bchemical\b"
            ]
            for pat in high_indicators:
                if re.search(pat, text):
                    return (
                        SEV_HIGH,
                        True,
                        "Severe health risk indicator detected in product quality feedback (spoilage/illness risk)."
                    )
            med_indicators = [
                r"\bexpir(ed|y)\b", r"\bpast\s*(best\s*by|sell\s*by|use\s*by|date)\b", r"\bbroken\s*seal\b", r"\bdent(ed)?\b",
                r"\bleak(ing)?\b", r"\bstale\b", r"\bspoil(ed)?\b", r"\bferment(ed|ing)?\b", r"\bmold\w*\b"
            ]
            for pat in med_indicators:
                if re.search(pat, text):
                    return (
                        SEV_MEDIUM,
                        False,
                        "Product condition issue identified (expiration or packaging defect) requiring shelf remediation."
                    )
            return (
                SEV_LOW,
                False,
                "Minor cosmetic or isolated product dissatisfaction without immediate health hazard."
            )

        elif category == CAT_QUEUE:
            high_indicators = [
                r"\b(30|35|40|45|50|60)\s*(min|minute|mins)\b",
                r"\b(1|2)\s*hour\b",
                r"\bonly\s*(one|1)\s*(register|cashier|lane)\b",
                r"\babandon(ed)?\s*(my\s*)?cart\b",
                r"\bwalk(ed)?\s*out\b"
            ]
            for pat in high_indicators:
                if re.search(pat, text):
                    return (
                        SEV_HIGH,
                        True,
                        "Extreme queue delay (>30 mins, severe lane bottleneck, or customer cart abandonment)."
                    )
            med_indicators = [
                r"\b(15|20|25)\s*(min|minute|mins)\b",
                r"\blong\s*(line|lines|queue)\b",
                r"\bslow\s*(checkout|cashier)\b",
                r"\bself[- ]checkout\b",
                r"\bline\s*moving\b"
            ]
            for pat in med_indicators:
                if re.search(pat, text):
                    return (
                        SEV_MEDIUM,
                        False,
                        "Moderate checkout congestion (15-25 min wait or slow throughput) impacting store flow."
                    )
            return (
                SEV_LOW,
                False,
                "Routine wait time comment or mild queue observation."
            )

        elif category == CAT_STOCK:
            high_indicators = [
                r"\bbaby\s*(formula|food)\b",
                r"\bwater\b",
                r"\bmilk\b",
                r"\bbread\b",
                r"\beggs\b",
                r"\bentire\s*(aisle|section)\s*empty\b",
                r"\bnothing\s*on\s*shelves\b",
                r"\b(3|three|multiple)\s*days\b"
            ]
            for pat in high_indicators:
                if re.search(pat, text):
                    return (
                        SEV_HIGH,
                        True,
                        "Critical inventory stockout impacting essential staple goods or widespread empty shelves."
                    )
            med_indicators = [
                r"\bout\s*of\s*stock\b",
                r"\bempty\s*shelf\b",
                r"\bsold\s*out\b",
                r"\bshortage\b",
                r"\bunavailable\b",
                r"\bbare\s*shelves\b"
            ]
            for pat in med_indicators:
                if re.search(pat, text):
                    return (
                        SEV_MEDIUM,
                        False,
                        "Standard SKU stockout identified requiring warehouse reorder or replenishment."
                    )
            return (
                SEV_LOW,
                False,
                "Minor stock inquiry or isolated specialty item absence."
            )

        elif category == CAT_STAFF:
            high_indicators = [
                r"\byell(ed|ing)?\b",
                r"\bshout(ed)?\b",
                r"\bswear(ing)?|curse\b",
                r"\bdiscriminat\b",
                r"\bracist|racial\b",
                r"\bthrew\b",
                r"\bsnatched\b",
                r"\baggressiv\b",
                r"\bpolice\b",
                r"\bharass\b"
            ]
            for pat in high_indicators:
                if re.search(pat, text):
                    return (
                        SEV_HIGH,
                        True,
                        "Severe staff conduct violation (verbal aggression, harassment, or gross misconduct)."
                    )
            med_indicators = [
                r"\brude\b",
                r"\battitude\b",
                r"\bunhelpful\b",
                r"\bdisrespectful\b",
                r"\bignor(ed)?\b",
                r"\brefused\b",
                r"\bsarcastic\b"
            ]
            for pat in med_indicators:
                if re.search(pat, text):
                    return (
                        SEV_MEDIUM,
                        False,
                        "Negative customer service interaction requiring supervisory coaching."
                    )
            return (
                SEV_LOW,
                False,
                "Minor service remark or routine customer experience feedback."
            )

        return (
            SEV_LOW,
            False,
            "General feedback without explicit critical operational triggers."
        )

    def _build_explanation(
        self,
        category: str,
        severity: str,
        escalation: bool,
        severity_reason: str,
        tokens: List[str]
    ) -> str:
        token_str = ", ".join(f"'{t}'" for t in tokens[:5]) if tokens else "None (Contextual inference)"
        escalate_str = "Immediate Escalation Required" if escalation else "Standard Operational Workflow (No Escalation)"
        return (
            f"Category: [{category}] matched based on trigger cues: [{token_str}]. "
            f"Assigned Severity: [{severity}] — {severity_reason} "
            f"Escalation Decision: [{escalate_str}]."
        )

    def batch_classify(self, df: pd.DataFrame, text_col: str = "cleaned_text") -> pd.DataFrame:
        df = df.copy()
        categories = []
        severities = []
        departments = []
        escalations = []
        explanations = []
        actions = []

        for text in df[text_col]:
            res = self.classify_text(text)
            categories.append(res["category"])
            severities.append(res["severity"])
            departments.append(res["department"])
            escalations.append(res["escalation_required"])
            explanations.append(res["explanation"])
            actions.append(res["recommended_action"])

        df["category"] = categories
        df["severity"] = severities
        df["department"] = departments
        df["escalation_required"] = escalations
        df["classification_explanation"] = explanations
        df["recommended_action"] = actions

        return df
