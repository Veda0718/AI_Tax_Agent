"""
File: tax_logic.py
Description:
    Contains core tax computation logic for the AI Tax Return Agent prototype.
    Uses 2024 IRS federal tax brackets and standard deductions to compute
    taxable income, total tax owed, and refund or balance due.

Key Responsibilities:
    - Aggregate all income sources (wages, interest, nonemployee compensation)
    - Apply standard deduction based on filing status
    - Compute tax owed using progressive brackets
    - Return a clean numeric summary dictionary

Author: Veda Sahaja Bandi
"""

# --------------------------------------------------------------------
# IRS 2024 Standard Deductions (source: IRS.gov)
# --------------------------------------------------------------------
STANDARD_DEDUCTION = {
    "single": 14600,
    "married_filing_jointly": 29200,
    "married_filing_separately": 14600,
    "head_of_household": 21900
}

# --------------------------------------------------------------------
# IRS 2024 Federal Tax Brackets
# --------------------------------------------------------------------
TAX_BRACKETS_2024 = {
    "single": [
        (0, 11000, 0.10),
        (11000, 44725, 0.12),
        (44725, 95375, 0.22),
        (95375, 182100, 0.24),
        (182100, 231250, 0.32),
        (231250, 578125, 0.35),
        (578125, float('inf'), 0.37),
    ],
    "married_filing_jointly": [
        (0, 22000, 0.10),
        (22000, 89450, 0.12),
        (89450, 190750, 0.22),
        (190750, 364200, 0.24),
        (364200, 462500, 0.32),
        (462500, 693750, 0.35),
        (693750, float('inf'), 0.37),
    ],
    "married_filing_separately": [
        (0, 11000, 0.10),
        (11000, 44725, 0.12),
        (44725, 95375, 0.22),
        (95375, 182100, 0.24),
        (182100, 231250, 0.32),
        (231250, 346875, 0.35),
        (346875, float('inf'), 0.37),
    ],
    "head_of_household": [
        (0, 15700, 0.10),
        (15700, 59850, 0.12),
        (59850, 95350, 0.22),
        (95350, 182100, 0.24),
        (182100, 231250, 0.32),
        (231250, 578100, 0.35),
        (578100, float('inf'), 0.37),
    ]
}


# --------------------------------------------------------------------
# Core Computation Functions
# --------------------------------------------------------------------
def calculate_tax(income, filing_status):
    """Compute federal tax using progressive brackets."""
    if filing_status not in TAX_BRACKETS_2024:
        filing_status = "single"  # default fallback

    brackets = TAX_BRACKETS_2024[filing_status]
    tax = 0.0

    for low, high, rate in brackets:
        if income > high:
            tax += (high - low) * rate
        else:
            tax += (income - low) * rate
            break

    return round(tax, 2)


def compute_liability(filing_status, incomes, withheld):
    """Compute total income, deductions, tax owed, and refund."""
    filing_status = filing_status.lower().replace(" ", "_")
    total_income = sum(incomes)
    deduction = STANDARD_DEDUCTION.get(filing_status, STANDARD_DEDUCTION["single"])
    taxable_income = max(0, total_income - deduction)

    tax = calculate_tax(taxable_income, filing_status)
    refund = round(withheld - tax, 2)

    return {
        "Total Income": round(total_income, 2),
        "Standard Deduction": deduction,
        "Taxable Income": round(taxable_income, 2),
        "Federal Tax Owed": round(tax, 2),
        "Federal Tax Withheld": round(withheld, 2),
        "Refund or Balance Due": refund
    }
