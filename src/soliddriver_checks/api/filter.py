from lark import Lark, Transformer
from lark.exceptions import LarkError, VisitError
import re
import pandas as pd


grammar = r"""
?start: expression
expression: disjunction
| conjunction
| operation
disjunction: conjunction ("or" conjunction)+ | conjunction
conjunction: group ("and" group)+ | group
group : "(" disjunction ")" | operation
operation : nil | match | equal | notequal
nil : "no" STRING
match : STRING "match" STRING
equal : STRING "=" STRING
notequal: STRING "!=" STRING

%import common.ESCAPED_STRING -> STRING
%import common.WS
%ignore WS
"""


class KernelModuleListFilter(Transformer):
    """Evaluate the parsed filter to a boolean mask over the rows of data.

    Every cell in data is {"level": {"level": "PASS", ...}, "value": ...},
    except the "level" column, which holds the row evaluation
    {"level": "PASS", "value": 1}.
    """

    LEVEL_SUFFIX = ".level"

    def __init__(self, data):
        super().__init__()
        self.data = data

    @staticmethod
    def _unquote(token):
        return str(token)[1:-1]

    def _cells(self, key):
        key = self._unquote(key)

        if key == "level" + self.LEVEL_SUFFIX:  # row evaluation
            column, get = "level", lambda cell: cell["level"]
        elif key.endswith(self.LEVEL_SUFFIX):  # evaluation of a field
            column = key[: -len(self.LEVEL_SUFFIX)]
            get = lambda cell: cell["level"]["level"]
        else:  # content of a field
            column, get = key, lambda cell: cell["value"]

        if column not in self.data.columns:
            keys = [c for c in self.data.columns if c != "level"]
            raise ValueError(
                "Unknown filter key: \"%s\". Valid keys: %s"
                % (key, ", ".join(keys))
            )

        # compare as strings, so "True" matches a boolean True.
        return self.data[column].apply(
            lambda cell: "" if get(cell) is None else str(get(cell))
        )

    def equal(self, vals):
        return self._cells(vals[0]) == self._unquote(vals[1])

    def notequal(self, vals):
        return self._cells(vals[0]) != self._unquote(vals[1])

    def match(self, vals):
        pattern = re.compile(self._unquote(vals[1]))
        return self._cells(vals[0]).apply(lambda v: pattern.search(v) is not None)

    def nil(self, vals):
        return self._cells(vals[0]) == ""

    def conjunction(self, vals):
        mask = vals[0]
        for val in vals[1:]:
            mask = mask & val
        return mask

    def disjunction(self, vals):
        mask = vals[0]
        for val in vals[1:]:
            mask = mask | val
        return mask

    def expression(self, vals):
        return vals[0]

    group = expression
    operation = expression


def _evaluate(filter, data):
    try:
        tree = Lark(grammar).parse(filter)
    except LarkError as e:
        raise ValueError("Invalid filter: %s" % str(e).strip()) from None

    try:
        return KernelModuleListFilter(data).transform(tree)
    except VisitError as e:  # unwrap errors raised inside the transformer
        if isinstance(e.orig_exc, re.error):
            raise ValueError(
                "Invalid regular expression in filter: %s" % e.orig_exc
            ) from None
        raise e.orig_exc from None


def check_filter(filter, columns):
    """Raise ValueError if filter isn't valid for data with these columns."""
    if filter:
        _evaluate(filter, pd.DataFrame(columns=columns))


def km_filter(filter, data):
    if filter == "" or len(data.index) == 0:
        return data

    mask = _evaluate(filter, data)

    return data[mask].reset_index(drop=True)
