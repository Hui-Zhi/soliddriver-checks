import click
import json
from ..api import analysis
from ..api.filter import check_filter
from ..api.km import KM_COLUMNS
from ..api.kmp import KMP_COLUMNS
from .terminal_logs import KMPTerminalOutput, single_kmp_output
from .kmp_report import KMPReporter
from .km_report import KMReporter
import os
import logging
import socket
from pathlib import Path
from ..version import __VERSION__


FORMAT_TYPES = {
    "html": ".html",
    "json": ".json",
}


class Check_Target:
    def __init__(self, target):
        if target is None:
            target = "system"

        self._target = target

    @property
    def system(self):
        target = Path(self._target)
        return target.name == "system" and not (target.is_file() or target.is_dir())

    @property
    def rpm(self):
        # need better check than this
        target = Path(self._target)
        if target.is_file() and target.name.endswith(".rpm"):
            return target
        return None

    @property
    def dir(self):
        target = Path(self._target)
        if target.is_dir():
            return target
        return None


def with_format_suffix(path, format_type):
    suffix = FORMAT_TYPES.get(format_type, None)

    if suffix is None:
        return path

    if path.suffix == suffix:
        return path

    return path.parent / (path.name + suffix)


def kmp_export(exporter, check_result, out_format, dst):
    dst = with_format_suffix(dst, out_format)
    if out_format == "html":
        exporter.to_html(check_result, dst)
    elif out_format == "json":
        exporter.to_json(check_result, dst)


def km_export(exporter, label, check_result, filter, out_format, dst):
    dst = with_format_suffix(dst, out_format)
    if out_format == "html":
        exporter.to_html(label, check_result, filter, dst)
    elif out_format == "json":
        exporter.to_json(label, check_result, filter, dst)


def dst_is_ok(dst):
    if dst.is_file():
        if not os.access(dst, os.W_OK):
            raise click.FileError(str(dst), hint="permission denied")
        return click.confirm("Overwrite %s?" % dst)
    return True


@click.command()
@click.argument("check_target", default="system")
@click.option(
    "--format",
    "-f",
    "out_format",
    type=click.Choice(FORMAT_TYPES),
    default="json",
    help="Specify output format",
)
@click.option(
    "--filter",
    "-i",
    default="",
    help="Only report the KMPs or kernel modules that match the filter "
    "expression, e.g. '\"level.level\" != \"PASS\"'. "
    "See README.md for the syntax.",
)
@click.option(
    "--output",
    "-o",
    default=".",
    help="Output destination. If it is an existing directory, or ends "
    "with '/', the report is written there as check_result.<format>. "
    "Otherwise it is used as the file name. The extension matching "
    "the output format is added if it is missing.",
)
@click.option("--version", is_flag=True)
def run(check_target, output, out_format, filter, version):
    """Run checks against CHECK_TARGET.

    \b
    CHECK_TARGET can be:
      KMP file
      directory containing KMP files
      "system" to check locally installed kernel modules
    """

    if version:
        print(__VERSION__)
        exit()

    logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
    logger = logging.getLogger("soliddriver-checks")

    target = Check_Target(check_target)

    if target.rpm:  # printed to the terminal, no report file.
        df = analysis.kmp_analysis(target.rpm)
        single_kmp_output(df)
        return

    if target.dir:
        columns = KMP_COLUMNS
    elif target.system:
        columns = KM_COLUMNS
    else:
        raise click.BadParameter(
            "%s is not a KMP file (.rpm), a directory or \"system\"" % check_target,
            param_hint="'CHECK_TARGET'",
        )

    try:
        check_filter(filter, columns)
    except ValueError as e:
        raise click.BadParameter(str(e), param_hint="'--filter'")

    dst = Path(output)
    if dst.is_dir() or output.endswith("/"):
        dst = dst / "check_result"
    dst = with_format_suffix(dst, out_format)

    if not dst_is_ok(dst):
        logger.error("Not overwriting %s, nothing was checked." % dst)
        exit(1)

    if target.dir:
        df = analysis.kmps_to_dataframe(target.dir, KMPTerminalOutput(), filter)
        reporter = KMPReporter()
        kmp_export(reporter, df, out_format, dst)

    elif target.system:
        try:
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
        except socket.gaierror as e:
            logger.warning(f"Get ip by hostname: {hostname} failed: {e}")
            ip = "127.0.0.1"

        label = "%s (%s)" % (hostname, ip)
        logger.info("Retrieving kernel module data for %s" % label)
        reporter = KMReporter()
        km_export(reporter, label, None, filter, out_format, dst)

    logger.info("Check is completed! The result has been saved to %s" % dst)


if __name__ == "__main__":
    run()
