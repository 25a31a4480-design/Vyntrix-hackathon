"""
VYNTRIX Configuration & Domain Knowledge Definitions
Track R5: Voice-of-Store Intelligence Engine
"""

CAT_PRODUCT_QUALITY = "Product Quality"
CAT_HYGIENE = "Hygiene"
CAT_SAFETY = "Safety"
CAT_ALLERGEN = "Allergen Concern"
CAT_STOCK = "Stock Availability"
CAT_QUEUE = "Long Queue"
CAT_STAFF = "Staff Service"
CAT_OTHER = "Other / Unclear"

ALL_CATEGORIES = [
    CAT_PRODUCT_QUALITY,
    CAT_HYGIENE,
    CAT_SAFETY,
    CAT_ALLERGEN,
    CAT_STOCK,
    CAT_QUEUE,
    CAT_STAFF,
    CAT_OTHER
]

DEPARTMENT_MAPPING = {
    CAT_PRODUCT_QUALITY: "Quality Team",
    CAT_HYGIENE: "Food Safety / Store Operations",
    CAT_SAFETY: "Store Safety Team",
    CAT_ALLERGEN: "Food Safety Team",
    CAT_STOCK: "Inventory Team",
    CAT_QUEUE: "Store Operations",
    CAT_STAFF: "Customer Experience",
    CAT_OTHER: "Manual Review"
}

MANDATORY_HIGH_CATEGORIES = {
    CAT_SAFETY,
    CAT_HYGIENE,
    CAT_ALLERGEN
}

SEV_HIGH = "High"
SEV_MEDIUM = "Medium"
SEV_LOW = "Low"

SEVERITY_LEVELS = [SEV_HIGH, SEV_MEDIUM, SEV_LOW]

COLORS = {
    "primary_dark": "#0F172A",
    "secondary_dark": "#1E293B",
    "accent_teal": "#0D9488",
    "accent_cyan": "#06B6D4",
    "accent_light_teal": "#14B8A6",
    "bg_light": "#F8FAFC",
    "card_bg": "#FFFFFF",
    "border": "#E2E8F0",
    "text_dark": "#0F172A",
    "text_muted": "#64748B",
    "sev_high": "#DC2626",
    "sev_med": "#D97706",
    "sev_low": "#16A34A",
    "badge_high_bg": "#FEE2E2",
    "badge_med_bg": "#FEF3C7",
    "badge_low_bg": "#DCFCE7",
}

CANONICAL_COLUMNS = [
    "feedback_id",
    "original_text",
    "store_id",
    "date",
    "channel",
    "category",
    "severity",
    "department",
    "escalation_required"
]

COLUMN_ALIASES = {
    "feedback_id": ["feedback_id", "id", "ticket_id", "review_id", "record_id"],
    "original_text": ["original_text", "feedback_text", "feedback", "text", "comment", "review", "customer_feedback", "content"],
    "store_id": ["store_id", "store", "store_code", "location", "store_number", "unit_id"],
    "date": ["date", "timestamp", "created_at", "feedback_date", "time", "date_time"],
    "channel": ["channel", "source", "source_channel", "feedback_channel", "origin", "type"],
    "category": ["category", "issue_category", "topic", "predicted_category"],
    "severity": ["severity", "priority", "severity_level", "urgency"],
    "department": ["department", "owning_department", "responsible_dept", "team"],
    "escalation_required": ["escalation_required", "escalate", "escalation", "needs_escalation"]
}

FEEDBACK_CHANNELS = [
    "Google Review",
    "In-App Feedback",
    "Store Shift Notes",
    "Customer Support Transcript"
]

DEMO_STORES = {
    "STR-101": "Downtown Flagship",
    "STR-102": "Westside Galleria",
    "STR-103": "Metro North Express",
    "STR-104": "Suburban Center",
    "STR-105": "Airport Plaza",
    "STR-106": "Harbor Point (New Store)"
}
