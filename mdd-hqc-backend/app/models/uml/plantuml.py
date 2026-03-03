"""PlantUML renderer for UML class diagrams.

This module converts `UmlModel` into a PlantUML class diagram string.

Conventions:
- Classes are always declared with a quoted display name and an alias (C1, C2, ...).
- Relationships use aliases to avoid referencing names with spaces/accents/symbols.
"""

from .uml import UmlClass, UmlDependency, UmlModel


# ============ CLASS RENDERING ============
def _render_class(uml_class: UmlClass, alias: str) -> list[str]:
    lines: list[str] = []

    header = _render_class_header(uml_class, alias)
    lines.append(header)

    lines.extend(_render_class_comments(uml_class))
    lines.extend(_render_class_tagged_values(uml_class))
    lines.extend(_render_class_attributes(uml_class))
    lines.extend(_render_class_methods(uml_class))

    lines.append("}")
    return lines


def _render_class_header(uml_class: UmlClass, alias: str) -> str:
    name = _escape_quoted(uml_class.name)
    stereotypes = _format_stereotypes(uml_class.stereotypes)
    return f'class "{name}" as {alias}{stereotypes} {{'


def _render_class_comments(uml_class: UmlClass) -> list[str]:
    lines: list[str] = []
    for comment in uml_class.comments:
        text = _clean_line(comment)
        if text:
            lines.append(f"  ' {text}")
    return lines


def _render_class_tagged_values(uml_class: UmlClass) -> list[str]:
    lines: list[str] = []

    keys = list(uml_class.tagged_values.keys())
    keys.sort()

    for key in keys:
        value = uml_class.tagged_values.get(key)
        if value is None:
            continue

        k = _clean_line(key)
        v = _clean_line(value)
        if k and v:
            lines.append(f"  ' {k}={v}")

    return lines


def _render_class_attributes(uml_class: UmlClass) -> list[str]:
    lines: list[str] = []

    for attr in uml_class.attributes:
        attr_name = _clean_line(attr.name)
        if not attr_name:
            continue

        attr_type = _clean_line(attr.type)
        if not attr_type:
            attr_type = "String"

        default_suffix = ""
        if attr.default is not None:
            default_value = _clean_line(attr.default)
            if default_value:
                default_suffix = f" = {default_value}"

        lines.append(f"  {attr_name} : {attr_type}{default_suffix}")

    return lines


def _render_class_methods(uml_class: UmlClass) -> list[str]:
    lines: list[str] = []

    for method in uml_class.methods:
        method_name = _clean_line(method.name)
        if not method_name:
            continue

        params_text = _render_parameters(method.parameters)

        return_type = _clean_line(method.return_type)
        if not return_type:
            return_type = "void"

        stereotypes = _format_stereotypes(method.stereotypes)
        lines.append(f"  {method_name}({params_text}) : {return_type}{stereotypes}")

    return lines


# ============ PARAMETERS / STEREOTYPES ============
def _render_parameters(parameters) -> str:
    parts: list[str] = []

    for p in parameters:
        p_name = _clean_line(p.name)
        if not p_name:
            continue

        p_type = _clean_line(p.type)
        if not p_type:
            p_type = "String"

        parts.append(f"{p_name}: {p_type}")

    return ", ".join(parts)


def _format_stereotypes(stereotypes) -> str:
    cleaned: list[str] = []

    if stereotypes is None:
        return ""

    for s in stereotypes:
        text = _clean_line(s)
        if text:
            cleaned.append(text)

    if not cleaned:
        return ""

    joined = ",".join(cleaned)
    return f" <<{joined}>>"


# ============ DEPENDENCY RENDERING ============
def _render_dependency(dep: UmlDependency, alias_by_name: dict[str, str]) -> str:
    source = _clean_line(dep.source)
    target = _clean_line(dep.target)
    if not source or not target:
        return ""

    source_alias = alias_by_name.get(source)
    target_alias = alias_by_name.get(target)
    if not source_alias or not target_alias:
        return ""

    label_parts: list[str] = []
    stereotype = _clean_line(dep.stereotype)
    if stereotype:
        label_parts.append(stereotype)
    label = _clean_line(dep.label)
    if label:
        label_parts.append(label)

    label_suffix = ""
    if label_parts:
        label_suffix = " : " + " ".join(label_parts)

    return f"{source_alias} ..> {target_alias}{label_suffix}"


# ============ TEXT HELPERS ============
def _escape_quoted(text) -> str:
    if text is None:
        return ""
    s = str(text)
    s = s.replace("\\", "\\\\")
    s = s.replace('"', '\\"')
    s = s.replace("\n", " ")
    s = s.replace("\r", " ")
    return s


def _clean_line(text) -> str:
    if text is None:
        return ""
    s = str(text)
    s = s.replace("\n", " ")
    s = s.replace("\r", " ")
    return s.strip()


# ============ PUBLIC API ============
def render(model: UmlModel) -> str:
    lines: list[str] = []
    lines.append("@startuml")

    title = _clean_line(model.name)
    if title:
        lines.append(f"title {title}")

    for comment in model.comments:
        text = _clean_line(comment)
        if text:
            lines.append(f"' {text}")

    class_names = list(model.classes.keys())
    class_names.sort()

    alias_by_name: dict[str, str] = {}
    i = 1
    for name in class_names:
        alias_by_name[name] = f"C{i}"
        i += 1

    for name in class_names:
        uml_class = model.classes[name]
        alias = alias_by_name[name]
        lines.extend(_render_class(uml_class, alias))

    for dep in model.dependencies:
        line = _render_dependency(dep, alias_by_name)
        if line:
            lines.append(line)

    lines.append("@enduml")
    return "\n".join(lines) + "\n"
