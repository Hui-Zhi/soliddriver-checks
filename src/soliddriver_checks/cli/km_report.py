import os
import json
from jinja2 import Environment, FileSystemLoader
from ..config import SDCConf, get_version, generate_timestamp
from ..api.common import Evaluation
from ..api.analysis import kms_to_dataframe, kms_to_json


class KMReporter:
    def __init__(self):
        self._style = SDCConf()

    def _format_cell(self, value):
        if type(value) == dict:
            return value.get("value", "")
        else:
            return value

    def _row_style_in_html(self, row):
        # TODO: row style should be added
        def _get_cell_style(row_level, cell_level):
            style = ""
            cristyle = self._style.get_km_html_error()
            impstyle = self._style.get_km_html_warning()
            cri_bgcolor = cristyle["background-color"]
            cri_color = cristyle["color"]
            # cri_border = cristyle["border"]

            imp_bgcolor = impstyle["background-color"]
            # imp_border = impstyle["border"]

            if int(Evaluation.WARNING) == cell_level:
                style = f"background-color:{imp_bgcolor}"
            elif int(Evaluation.ERROR) == cell_level:
                style = f"background-color:{cri_bgcolor} color:{cri_color}"

            return style

        return [
            "",  # level style, no need for this.
            _get_cell_style(
                Evaluation(row["level"]["value"]),
                Evaluation(row["Module Name"]["level"]["value"]),
            ),
            _get_cell_style(
                Evaluation(row["level"]["value"]),
                Evaluation(row["File"]["level"]["value"]),
            ),
            _get_cell_style(
                Evaluation(row["level"]["value"]),
                Evaluation(row["License"]["level"]["value"]),
            ),
            _get_cell_style(
                Evaluation(row["level"]["value"]),
                Evaluation(row["Signature"]["level"]["value"]),
            ),
            _get_cell_style(
                Evaluation(row["level"]["value"]),
                Evaluation(row['"supported" Flag']["level"]["value"]),
            ),
            "",  # running style, no need for this.
            _get_cell_style(
                Evaluation(row["level"]["value"]),
                Evaluation(row["KMP"]["level"]["value"]),
            ),
        ]

    def _format_columns(self, df):
        return df.rename(
            columns={
                "modulename": "Module Name",
                "filename": "File",
                "license": "License",
                "signature": "Signature",
                "supported": '"supported" Flag',
                "running": "Running",
                "kmp": "KMP",
            }
        )

    def to_html(self, sys_info, df_format, filter, file):
        pkg_path = os.path.dirname(__file__)
        jinja_tmpl = f"{pkg_path}/../config/templates"
        file_loader = FileSystemLoader(jinja_tmpl)
        env = Environment(loader=file_loader)

        km_tmpl = env.get_template("km-report.html.jinja")

        if df_format is None:
            df_format = kms_to_dataframe(filter)  # read from local system.

        kms_in_total = len(df_format.index)
        if kms_in_total == 0:
            failed_kms_in_total = 0
        else:
            failed_kms_in_total = len(
                [
                    f
                    for f in df_format["level"].to_list()
                    if f["value"] != int(Evaluation.PASS)
                ]
            )

        df_format = self._format_columns(df_format)

        # Handle empty dataframe case
        if kms_in_total == 0:
            ts = df_format.style.hide(axis="index")
        else:
            ts = (
                df_format.style.hide(axis="index")
                .hide([("level")], axis="columns")
                .set_table_attributes('class="table_center"')
                .apply(self._row_style_in_html, axis=1)
                .format(self._format_cell)
            )

        # df["running"].loc[df.running == True] = "&#9989;"
        # df["running"].loc[df.running == False] = "&#9940;"
        # df["running"].loc[df.running == ""] = "N/A"

        # Will be easier to get the value if run this after reformat the values.
        if kms_in_total == 0:
            external_kms_in_total = 0
        else:
            external_kms_in_total = len(
                [sf for sf in df_format['"supported" Flag'].to_list() if sf == "external"]
            )

        kms_buffer = km_tmpl.render(
            version=get_version(),
            timestamp=generate_timestamp(),
            sysinfo=sys_info,
            kms_in_total=kms_in_total,
            external_kms_in_total=external_kms_in_total,
            failed_kms_in_total=failed_kms_in_total,
            kms_table=ts.to_html(),
        )

        with open(file, "w") as f:
            f.write(kms_buffer)

    def to_json(self, sys_info, df_format, filter, file):
        buffer = kms_to_json(df_format)

        # TODO: add sys_info to json output.
        with open(file, "w") as fp:
            json.dump(json.loads(buffer), fp)
