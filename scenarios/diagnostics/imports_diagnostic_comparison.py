"""
Diagnostic comparison of Energy Balance trends across scenarios.

Goal: figure out why Pro-solar and Utility Protection don't follow BAU's
declining-imports trend, and which UP file (UUTI vs Updated UT) is more
plausible.

Plots Production / Imports / Unmet Requirements for all 4 scenarios
(BAU, LMI, Pro-solar, UP) plus both candidate UP files side by side.
"""

import os
import openpyxl
import matplotlib.pyplot as plt

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def extract_bau_year_total(books=("Book7.xlsx", "Book8.xlsx", "Book9.xlsx")):
    """BAU files are per-year sheets, fuel columns. Use the 'Total' column."""
    out = {"Production": {}, "Imports": {}, "Unmet Requirements": {}}
    for fname in books:
        path = os.path.join(REPO, fname)
        if not os.path.exists(path):
            continue
        wb = openpyxl.load_workbook(path, data_only=True)
        for sn in wb.sheetnames:
            try:
                year = int(sn.split("|")[1])
            except (IndexError, ValueError):
                continue
            ws = wb[sn]
            # Find the 'Total' column index
            total_col = None
            for c in range(1, ws.max_column + 1):
                if ws.cell(row=3, column=c).value == "Total":
                    total_col = c
                    break
            if total_col is None:
                continue
            for r in range(1, ws.max_row + 1):
                label = ws.cell(row=r, column=1).value
                if label in out:
                    out[label][year] = ws.cell(row=r, column=total_col).value
    return out


def extract_single_sheet(filename, sheet_name=None):
    """Single-sheet 'Fuels: All' files — years are columns 2-34, label rows."""
    path = os.path.join(REPO, filename)
    if not os.path.exists(path):
        # also try Desktop directly
        alt = os.path.join(r"C:\Users\lxlms\OneDrive\Desktop", filename)
        if os.path.exists(alt):
            path = alt
        else:
            return None
    wb = openpyxl.load_workbook(path, data_only=True)
    sn = sheet_name or wb.sheetnames[0]
    if sn not in wb.sheetnames:
        return None
    ws = wb[sn]
    out = {"Production": {}, "Imports": {}, "Unmet Requirements": {}}
    for r in range(1, ws.max_row + 1):
        label = ws.cell(row=r, column=1).value
        if label not in out:
            continue
        for c in range(2, ws.max_column + 1):
            year = 2018 + (c - 2)
            if year > 2050:
                break
            v = ws.cell(row=r, column=c).value
            if v is not None:
                out[label][year] = v
    return out


def to_xy(d):
    if not d:
        return [], []
    yrs = sorted(d.keys())
    return yrs, [d[y] for y in yrs]


def main():
    series = {
        "BAU":              extract_bau_year_total(),
        "LMI":              extract_single_sheet("LMI Energy Balance.xlsx"),
        "Pro-solar (Updated Pro Solar.xlsx)":
                            extract_single_sheet("Updated Pro Solar.xlsx"),
        # Two UP candidates
        "UP-A (UUTI Energy Balance.xlsx)":
                            extract_single_sheet("UUTI Energy Balance.xlsx")
                            or extract_single_sheet("../UUTI Energy Balance.xlsx"),
        "UP-B (Updated UT.xlsx — repo, single sheet)":
                            extract_single_sheet("Updated UT.xlsx"),
        # Older Apr 3 files for reference
        "UP-old (Utility Protection Energy Balance.xlsx)":
                            extract_single_sheet("Utility Protection Energy Balance.xlsx"),
    }
    # Pull UUTI from Desktop if missing in repo
    if not series["UP-A (UUTI Energy Balance.xlsx)"]:
        series["UP-A (UUTI Energy Balance.xlsx)"] = extract_single_sheet(
            "UUTI Energy Balance.xlsx"
        )

    colors = {
        "BAU":                                                      "#666666",
        "LMI":                                                      "#2A9D8F",
        "Pro-solar (Updated Pro Solar.xlsx)":                       "#E9C46A",
        "UP-A (UUTI Energy Balance.xlsx)":                          "#E76F51",
        "UP-B (Updated UT.xlsx — repo, single sheet)":              "#9B2226",
        "UP-old (Utility Protection Energy Balance.xlsx)":          "#BBB",
    }
    linestyles = {
        "UP-A (UUTI Energy Balance.xlsx)":                          "--",
        "UP-B (Updated UT.xlsx — repo, single sheet)":              "-",
        "UP-old (Utility Protection Energy Balance.xlsx)":          ":",
    }

    fig, axes = plt.subplots(3, 1, figsize=(12, 13), sharex=True)
    metrics = ["Production", "Imports", "Unmet Requirements"]
    titles = [
        "Production (GWh) — SSEG + utility-scale generation",
        "Imports (GWh) — should DECREASE as DER grows (BAU shows the right trend)",
        "Unmet Requirements (GWh) — positive = deficit, negative = surplus",
    ]

    for ax, metric, title in zip(axes, metrics, titles):
        for name, data in series.items():
            if not data:
                continue
            x, y = to_xy(data[metric])
            if not x:
                continue
            ax.plot(
                x, y,
                color=colors.get(name, "#000"),
                linestyle=linestyles.get(name, "-"),
                linewidth=2.0,
                label=name,
                marker="o" if name.startswith("UP") else None,
                markersize=3,
            )
        ax.axhline(0, color="#999", linewidth=0.5)
        ax.set_title(title, fontsize=11, loc="left")
        ax.set_ylabel(metric)
        ax.grid(alpha=0.3)
        ax.set_xlim(2018, 2050)

    axes[-1].set_xlabel("Year")
    axes[0].legend(fontsize=8, loc="upper left", ncol=1, framealpha=0.9)
    fig.suptitle(
        "Energy Balance diagnostic: which UP file follows the expected trend?",
        fontsize=13, y=0.995,
    )
    fig.tight_layout()
    out = os.path.join(os.path.dirname(__file__), "imports_diagnostic_comparison.png")
    fig.savefig(out, dpi=140, bbox_inches="tight")
    print(f"Saved: {out}")

    # Print summary table
    print("\n=== End-of-period values (2050) ===")
    print(f"{'Scenario/file':<55} {'Production':>12} {'Imports':>10} {'Unmet':>10}")
    print("-" * 90)
    for name, data in series.items():
        if not data:
            continue
        last = max(data["Imports"].keys()) if data["Imports"] else None
        if last is None:
            continue
        prod = data["Production"].get(last, "n/a")
        imp = data["Imports"].get(last, "n/a")
        unmet = data["Unmet Requirements"].get(last, "n/a")
        prod_s = f"{prod:>12,.0f}" if isinstance(prod, (int, float)) else f"{prod:>12}"
        imp_s = f"{imp:>10,.0f}" if isinstance(imp, (int, float)) else f"{imp:>10}"
        unmet_s = f"{unmet:>10,.0f}" if isinstance(unmet, (int, float)) else f"{unmet:>10}"
        print(f"{name[:55]:<55} {prod_s} {imp_s} {unmet_s}")


if __name__ == "__main__":
    main()
