"""
Compare Cape Town IPP Solar/Wind (and Eskom IPP) settings across the 4
'Updated' scenarios in Full Scenario Excel LEAP.xlsx.

Goal: find which Variables differ between Pro Solar / UP and BAU / LMI on the
centralized renewable processes — to identify what got broken when Pro-solar
and UP were rebuilt on the Updated BAU Area.
"""

import os
import openpyxl
import csv

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "Full Scenario Excel LEAP.xlsx")

SCENARIOS = [
    "Updated BAU GHS",
    "Updated LMI GHS",
    "Updated Pro Solar",
    "Updated Utility Protection",
]
SHORT = {
    "Updated BAU GHS": "BAU",
    "Updated LMI GHS": "LMI",
    "Updated Pro Solar": "ProSolar",
    "Updated Utility Protection": "UP",
}

BRANCH_FILTERS = [
    "Cape Town IPP Solar",
    "Cape Town IPP Wind",
    "Eskom IPP Solar",
    "Eskom IPP Wind",
    "Eskom Wind",
    "Eskom IPP Renewables",
    "Eskom IPP Non Renewable",
    "Eskom IPP OCGT",
]

YEAR_COLS = list(range(12, 45))  # 2018-2050
META_COLS = {
    "Branch Path": 4,
    "Variable": 5,
    "Scenario": 6,
    "Units": 9,
    "Method": 11,
}


def load_rows():
    wb = openpyxl.load_workbook(SRC, data_only=True, read_only=True)
    ws = wb["Export"]
    out = []
    for i, row in enumerate(ws.iter_rows(values_only=True), 1):
        if i < 4:
            continue
        bp = row[4] or ""
        scen = row[6] or ""
        if scen not in SCENARIOS:
            continue
        if not any(f in bp for f in BRANCH_FILTERS):
            continue
        out.append(row)
    wb.close()
    return out


def values_signature(row):
    """Compact representation of (Method, year-values) for comparison."""
    method = row[11]
    yrs = tuple(row[c] for c in YEAR_COLS)
    return (method, yrs)


def fmt_value(row):
    """Human-readable value: if all years equal, show single value; else show
    year-pair summary."""
    method = row[11]
    vals = [row[c] for c in YEAR_COLS]
    non_none = [v for v in vals if v is not None]
    if not non_none:
        return f"[{method}] (empty)"
    # All identical?
    unique = set(non_none)
    if len(unique) == 1:
        return f"[{method}] {non_none[0]}"
    # Show first / mid / last year that has a value
    pairs = [(2018 + i, v) for i, v in enumerate(vals) if v is not None]
    first, last = pairs[0], pairs[-1]
    mid = pairs[len(pairs) // 2]
    return f"[{method}] {first[0]}={first[1]} ... {mid[0]}={mid[1]} ... {last[0]}={last[1]}"


def main():
    rows = load_rows()
    # Group by (Branch Path, Variable)
    grouped = {}
    for r in rows:
        key = (r[4], r[5])
        grouped.setdefault(key, {})[r[6]] = r

    diffs = []
    same = []
    only_some = []

    for (bp, var), by_scen in sorted(grouped.items()):
        sigs = {s: values_signature(by_scen[s]) for s in SCENARIOS if s in by_scen}
        unique_sigs = set(sigs.values())
        # Categorize
        present = set(sigs.keys())
        if len(present) < len(SCENARIOS):
            only_some.append((bp, var, by_scen, present))
        elif len(unique_sigs) == 1:
            same.append((bp, var, by_scen))
        else:
            diffs.append((bp, var, by_scen))

    # ------ Print report ------
    print("=" * 100)
    print(f"IPP SETTINGS DIFF — {len(grouped)} (Branch, Variable) combinations across 4 scenarios")
    print(f"  All 4 scenarios identical:  {len(same)}")
    print(f"  Only some scenarios have it: {len(only_some)}")
    print(f"  At least one scenario DIFFERS: {len(diffs)}  <-- focus here")
    print("=" * 100)

    if diffs:
        print("\n### A. VARIABLES THAT DIFFER ACROSS SCENARIOS")
        print("    (these are the candidates for what broke Pro-solar / UP)\n")
        for bp, var, by_scen in diffs:
            print(f"--- {bp}")
            print(f"    Variable: {var}")
            for s in SCENARIOS:
                if s in by_scen:
                    print(f"      {SHORT[s]:<10}: {fmt_value(by_scen[s])}")
            # Tag pattern: do ProSolar+UP agree but differ from BAU+LMI?
            sigs = {s: values_signature(by_scen[s]) for s in SCENARIOS if s in by_scen}
            if all(s in sigs for s in SCENARIOS):
                bau, lmi, ps, up = (sigs["Updated BAU GHS"], sigs["Updated LMI GHS"],
                                    sigs["Updated Pro Solar"], sigs["Updated Utility Protection"])
                if bau == lmi and ps == up and bau != ps:
                    print(f"      *** PATTERN: BAU=LMI vs ProSolar=UP — likely the rebuild bug ***")
                elif bau == lmi == ps and ps != up:
                    print(f"      *** PATTERN: only UP differs ***")
                elif bau == lmi == up and bau != ps:
                    print(f"      *** PATTERN: only ProSolar differs ***")
            print()

    if only_some:
        print("\n### B. VARIABLES PRESENT IN SOME SCENARIOS BUT NOT OTHERS")
        for bp, var, by_scen, present in only_some:
            missing = [SHORT[s] for s in SCENARIOS if s not in present]
            print(f"  {bp} :: {var}  --  missing in: {', '.join(missing)}")

    # ------ CSV output (full dump for browsing) ------
    out_csv = os.path.join(os.path.dirname(__file__), "ipp_settings_diff.csv")
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Branch Path", "Variable", "Scenario", "Method", "Units"]
                   + list(range(2018, 2051)) + ["DIFFERS_FROM_BAU"])
        for (bp, var), by_scen in sorted(grouped.items()):
            bau_sig = (values_signature(by_scen["Updated BAU GHS"])
                       if "Updated BAU GHS" in by_scen else None)
            for s in SCENARIOS:
                if s not in by_scen:
                    continue
                r = by_scen[s]
                differs = (bau_sig is not None and values_signature(r) != bau_sig)
                w.writerow([r[4], r[5], r[6], r[11], r[9]]
                           + [r[c] for c in YEAR_COLS]
                           + ["YES" if differs else ""])
    print(f"\nFull CSV dump: {out_csv}")


if __name__ == "__main__":
    main()
