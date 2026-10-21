import click


LEVEL_COLORS = {"PASS": "green", "WARNING": "yellow", "ERROR": "red"}


def styled_level(level):
    # click drops the colors when the output is not a terminal.
    return click.style(level, fg=LEVEL_COLORS.get(level), bold=level == "ERROR")


class KMPTerminalOutput:
    """Print one line per checked KMP to stderr."""

    def prepartion(self, kmps):
        self._total = len(kmps)
        self._done = 0
        click.echo("Checking %d KMP(s)..." % self._total, err=True)

    def process(self, data):
        self._done += 1
        width = len(str(self._total))
        level = data["level"]["level"]
        click.echo(
            "[%*d/%d] %s%s %s"
            % (
                width,
                self._done,
                self._total,
                styled_level(level),
                " " * (7 - len(level)),
                data["path"]["value"],
            ),
            err=True,
        )

    def complete(self):
        pass


def single_kmp_output(df):
    for __, row in df.iterrows():
        click.echo(
            "%s: %s" % (row["name"]["value"], styled_level(row["level"]["level"]))
        )
        columns = [col for col in df.columns if col != "level"]
        width = max(len(col) for col in columns)
        for col in columns:
            level = row[col]["level"]["level"]
            value = row[col]["value"]
            # pad before styling, the color codes would break the alignment.
            click.echo(
                "  %s  %s%s  %s"
                % (
                    col.ljust(width),
                    styled_level(level),
                    " " * (7 - len(level)),
                    "" if value is None else value,
                )
            )
