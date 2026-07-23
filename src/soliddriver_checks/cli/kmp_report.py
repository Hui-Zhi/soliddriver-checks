import pandas as pd
import os
from dominate.tags import tr, td, th, table
from dominate.util import raw
from jinja2 import Environment, FileSystemLoader
from ..config import SDCConf, get_version, generate_timestamp
from ..api.common import Evaluation


class KMPReporter:
    def __init__(self):
        self._style = SDCConf()

    def _summary(self, df):
        summary = df.copy()
        # we need to do this for unique() since unhashable type: 'dict'.
        for i, row in summary.iterrows():
            row["vendor"] = row["vendor"]["value"]

        def failed_len(col):
            counter = 0
            for v in col:
                eval = v.get("level")
                if eval["value"] != int(Evaluation.PASS):
                    counter += 1
            return counter

        def format_cell(number, total):
            return f"{number} ({number/total * 100:.2f}%)"

        vendors = summary["vendor"].unique()
        sum_table = pd.DataFrame()
        for v in vendors:
            vendor_df = summary.loc[summary["vendor"] == v]
            total = len(vendor_df.index)
            sig_failed = failed_len(vendor_df["signature"])
            license_failed = failed_len(vendor_df["license"])
            supported_failed = failed_len(vendor_df["supported_flag"])
            wm2_invoked_failed = failed_len(vendor_df["wm2_invoked"])
            km_sigs_failed = failed_len(vendor_df["km_signatures"])
            km_license_failed = failed_len(vendor_df["km_licenses"])
            symbols_failed = failed_len(vendor_df["symbols"])
            alias_failed = failed_len(vendor_df["modalias"])

            new_row = pd.Series(
                {
                    "Vendor": v,
                    "Total KMPs": total,
                    "License": format_cell(license_failed, total),
                    "KMP Signature": format_cell(sig_failed, total),
                    "Weak Module Invoked": format_cell(wm2_invoked_failed, total),
                    "Supported Flag": format_cell(supported_failed, total),
                    "KM Signatures": format_cell(km_sigs_failed, total),
                    "KM Licenses": format_cell(km_license_failed, total),
                    "Symbols": format_cell(symbols_failed, total),
                    "Modalias": format_cell(alias_failed, total),
                }
            )

            sum_table = pd.concat([sum_table, new_row.to_frame().T], ignore_index=True)

        return sum_table

    def _summary_to_html(self, df):
        tb = table()
        with tb:
            tb.set_attribute("class", "summary_table")
            summary = self._summary(df)
            with tr():
                cols = summary.columns
                for col in cols:
                    if col == "Vendor":
                        t = th(col)
                        t.set_attribute("class", "summary_vendor")
                    else:
                        th(col)

            def _pass(item):
                return int(item.split(" ")[0]) == 0

            for __, row in summary.iterrows():
                vendor = row["Vendor"]
                total = row["Total KMPs"]
                sig = row["KMP Signature"]
                license = row["License"]
                supported = row["Supported Flag"]
                wm2_invoked = row["Weak Module Invoked"]
                km_sigs = row["KM Signatures"]
                km_license = row["KM Licenses"]
                symbols = row["Symbols"]
                alias = row["Modalias"]

                row_passed = False
                if (
                    vendor != ""
                    and _pass(sig)
                    and _pass(license)
                    and _pass(supported)
                    and _pass(wm2_invoked)
                    and _pass(km_sigs)
                    and _pass(km_license)
                    and _pass(symbols)
                    and _pass(alias)
                ):
                    row_passed = True
                with tr() as r:
                    if row_passed:
                        r.set_attribute("class", "summary_great_row")
                    if vendor != "":
                        td(vendor)
                    else:
                        tv = td("no vendor information")
                        tv.set_attribute("class", "important_failed")
                    with td(total) as t:
                        t.set_attribute("class", "summary_total")
                    with td(license) as t:
                        if _pass(license):
                            t.set_attribute("class", "summary_number")
                        else:
                            t.set_attribute("class", "important_failed summary_number")
                    with td(sig) as t:
                        if _pass(sig):
                            t.set_attribute("class", "summary_number")
                        else:
                            t.set_attribute("class", "important_failed summary_number")
                    with td(wm2_invoked) as t:
                        if _pass(wm2_invoked):
                            t.set_attribute("class", "summary_number")
                        else:
                            t.set_attribute("class", "critical_failed summary_number")
                    with td(supported) as t:
                        if _pass(supported):
                            t.set_attribute("class", "summary_number")
                        else:
                            t.set_attribute("class", "critical_failed summary_number")
                    with td(km_sigs) as t:
                        if _pass(km_sigs):
                            t.set_attribute("class", "summary_number")
                        else:
                            t.set_attribute("class", "important_failed summary_number")
                    with td(km_license) as t:
                        if _pass(km_license):
                            t.set_attribute("class", "summary_number")
                        else:
                            t.set_attribute("class", "important_failed summary_number")
                    with td(symbols) as t:
                        if _pass(symbols):
                            t.set_attribute("class", "summary_number")
                        else:
                            t.set_attribute("class", "critical_failed summary_number")
                    with td(alias) as t:
                        if _pass(alias):
                            t.set_attribute("class", "summary_number")
                        else:
                            t.set_attribute("class", "critical_failed summary_number")

        return tb

    def _detail_to_html(self, df):
        def _create_cell(ana_val, is_path=False):
            level, value = ana_val.get("level"), ana_val.get("value")
            if value is None:
                value = ""

            # Determine status class for individual cell coloring
            css_class = ""
            if level["value"] == int(Evaluation.PASS):
                css_class = "status-pass"
            elif level["value"] == int(Evaluation.WARNING):
                css_class = "status-warning"
            elif level["value"] == int(Evaluation.ERROR):
                css_class = "status-error"

            # Add mono class for paths
            if is_path:
                css_class += " mono"

            # Truncate long error messages and make them expandable
            if len(str(value)) > 100 and css_class in ["status-warning", "status-error"]:
                short_value = str(value)[:97] + "..."
                cell = td(raw(f'<div>{short_value}</div><span class="expandable-trigger">Show more</span><div class="expandable-content"><pre>{value}</pre></div>'))
                cell.set_attribute("class", css_class + " expandable")
                return cell
            else:
                cell = td(value)
                if css_class:
                    cell.set_attribute("class", css_class)
                return cell

        tb = table()
        with tb:
            tb.set_attribute("class", "table_center")
            with tr():
                th("KMP Checks", colspan=6).set_attribute("class", f"detail_rpm")
                th("Kernel Module Checks", colspan=5).set_attribute(
                    "class", f"detail_kernel_module"
                )
            with tr():
                th("Name").set_attribute("class", f"detail_0 sortable")
                th("Path").set_attribute("class", f"detail_1 sortable")
                th("Vendor").set_attribute("class", f"detail_2 sortable")
                th(
                    raw(
                        'Signature<span class="tooltiptext">Only check there\'s a signature or not.</span>'
                    )
                ).set_attribute("class", f"detail_3 tooltip sortable")
                th(
                    raw(
                        'License<span class="tooltiptext">KMP and it\'s kernel modules should use open source licenses.</span>'
                    )
                ).set_attribute("class", f"detail_4 tooltip sortable")
                th(
                    raw(
                        'Weak Module Invoked<span class="tooltiptext">Weak Module is necessary to make 3rd party kernel modules installed for one kernel available to KABI-compatible kernels. </span>'
                    )
                ).set_attribute("class", f"detail_5 tooltip sortable")
                th(
                    raw(
                        'Licenses<span class="tooltiptext">KMP and it\'s kernel modules should use open source licenses.</span>'
                    )
                ).set_attribute("class", f"detail_6 tooltip sortable km-check")
                th(
                    raw(
                        'Signatures<span class="tooltiptext">Module signature check - verifies kernel module is properly signed</span>'
                    )
                ).set_attribute("class", f"detail_7 tooltip sortable km-check")
                th(
                    raw(
                        'Supported Flag<span class="tooltiptext">"supported" flag: <br/>  "yes": Only supported by SUSE<br/>  "external": supported by both SUSE and vendor</span>'
                    )
                ).set_attribute("class", f"detail_8 tooltip sortable km-check")
                th(
                    raw(
                        'Symbols<span class="tooltiptext">Symbols check is to check whether the symbols in kernel modules matches the symbols in its package.</span>'
                    )
                ).set_attribute("class", f"detail_9 tooltip sortable km-check")
                th(
                    raw(
                        'Modalias<span class="tooltiptext">Modalias check is to check whether the modalias in kernel modules matches the modalias in its package.</span>'
                    )
                ).set_attribute("class", f"detail_10 tooltip sortable km-check")

            for __, row in df.iterrows():
                with tr() as r:
                    if row["level"]["value"] == int(Evaluation.WARNING):
                        r.set_attribute("class", "important_failed_row")
                    elif row["level"]["value"] == int(Evaluation.ERROR):
                        r.set_attribute("class", "critical_failed_row")

                    _create_cell(row["name"], is_path=False)
                    _create_cell(row["path"], is_path=True)
                    _create_cell(row["vendor"], is_path=False)
                    _create_cell(row["signature"], is_path=False)
                    _create_cell(row["license"], is_path=False)
                    _create_cell(row["wm2_invoked"], is_path=False)
                    _create_cell(row["km_licenses"], is_path=False)
                    _create_cell(row["km_signatures"], is_path=False)
                    _create_cell(row["supported_flag"], is_path=False)
                    _create_cell(row["symbols"], is_path=False)
                    _create_cell(row["modalias"], is_path=False)

        return tb

    def to_html(self, df, file):
        pkg_path = os.path.dirname(__file__)
        jinja_tmpl = f"{pkg_path}/../config/templates"
        file_loader = FileSystemLoader(jinja_tmpl)
        env = Environment(loader=file_loader)

        kmp_tmpl = env.get_template("kmp-report.html.jinja")

        kmp_checks = kmp_tmpl.render(
            version=get_version(),
            timestamp=generate_timestamp(),
            summary_table=self._summary_to_html(df),
            rpm_details=self._detail_to_html(df),
        )

        with open(file, "w") as f:
            f.write(kmp_checks)

    def to_json(self, df, file):
        df.to_json(file, orient="records")
