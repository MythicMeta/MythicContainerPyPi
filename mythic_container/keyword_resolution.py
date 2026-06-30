import json


class PTTaskKeywordResolution:
    def __init__(
        self,
        raw: str = "",
        keyword: str = "",
        selector: str = "",
        field: str = "",
        value_type: str = "",
        expanded_value: str = "",
        parameter_names: list[str] = None,
        **kwargs,
    ):
        self.Raw = raw
        self.Keyword = keyword
        self.Selector = selector
        self.Field = field
        self.ValueType = value_type
        self.ExpandedValue = expanded_value
        self.ParameterNames = parameter_names if parameter_names is not None else []

    def to_json(self):
        return {
            "raw": self.Raw,
            "keyword": self.Keyword,
            "selector": self.Selector,
            "field": self.Field,
            "value_type": self.ValueType,
            "expanded_value": self.ExpandedValue,
            "parameter_names": self.ParameterNames,
        }


def NormalizeKeywordResolution(keyword_resolution) -> list[PTTaskKeywordResolution]:
    normalized = []
    for entry in keyword_resolution or []:
        if isinstance(entry, PTTaskKeywordResolution):
            normalized.append(entry)
        elif isinstance(entry, dict):
            normalized.append(PTTaskKeywordResolution(**entry))
    return normalized


def RevertKeywords(parameter, keyword_resolution=None, parameter_name: str = "") -> str:
    reverted = _keyword_parameter_to_string(parameter)
    normalized = NormalizeKeywordResolution(keyword_resolution)
    if len(normalized) == 0:
        return reverted
    if parameter_name:
        for entry in normalized:
            if entry.ValueType == "structured" and parameter_name in entry.ParameterNames:
                return entry.Raw
        updated = _apply_keyword_resolution_string_entries(
            reverted,
            _filter_keyword_resolution_entries(normalized, parameter_name=parameter_name),
        )
        if updated != reverted:
            return updated
        return _apply_keyword_resolution_string_entries(
            reverted,
            _filter_keyword_resolution_entries(normalized, globals_only=True),
        )
    return _apply_keyword_resolution_string_entries(reverted, normalized)


def _keyword_parameter_to_string(parameter) -> str:
    if isinstance(parameter, str):
        return parameter
    try:
        return json.dumps(parameter, separators=(",", ":"))
    except TypeError:
        return str(parameter)


def _filter_keyword_resolution_entries(
    keyword_resolution: list[PTTaskKeywordResolution],
    parameter_name: str = "",
    globals_only: bool = False,
) -> list[PTTaskKeywordResolution]:
    filtered = []
    for entry in keyword_resolution:
        if entry.ValueType != "string":
            continue
        if globals_only:
            if len(entry.ParameterNames) == 0:
                filtered.append(entry)
            continue
        if parameter_name in entry.ParameterNames:
            filtered.append(entry)
    return filtered


def _apply_keyword_resolution_string_entries(
    parameter: str,
    keyword_resolution: list[PTTaskKeywordResolution],
) -> str:
    reverted = parameter
    sorted_entries = sorted(
        keyword_resolution,
        key=lambda entry: len(entry.ExpandedValue),
        reverse=True,
    )
    placeholders = {}
    for index, entry in enumerate(sorted_entries):
        if entry.ValueType != "string" or entry.ExpandedValue == "":
            continue
        placeholder = f"\x00MYTHIC_KEYWORD_{index}\x00"
        placeholders[placeholder] = entry.Raw
        reverted = reverted.replace(entry.ExpandedValue, placeholder)
    for placeholder, raw in placeholders.items():
        reverted = reverted.replace(placeholder, raw)
    return reverted
