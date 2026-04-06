"""Services that render UML models into PlantUML text artifacts."""

import logging
from pathlib import Path
from app.models.uml import UmlClass, UmlDependency, UmlModel

logger = logging.getLogger(__name__)


# ====== Private Helpers ======
# Internal methods below render individual UML fragments before the full artifact is written.


# ------------ Class Rendering ------------
# Methods below render UML classes, their members, and their attached notes.
def _render_class(uml_class: UmlClass, alias: str) -> list[str]:
    """Renders one UML class block and its visible notes.

    This helper assembles the class header, members, and class notes before the final
    PlantUML document is joined into one artifact.
    """
    lines: list[str] = []

    header = _render_class_header(uml_class, alias)
    lines.append(header)

    lines.extend(_render_class_attributes(uml_class))
    lines.extend(_render_class_methods(uml_class))

    lines.append("}")
    lines.extend(_render_class_notes(uml_class, alias))
    return lines


def _render_class_header(uml_class: UmlClass, alias: str) -> str:
    """Builds the PlantUML header line for one class.

    This helper keeps the class declaration formatting consistent before attributes and
    methods are rendered under the same block.
    """
    name = _escape_quoted(uml_class.name)
    stereotypes = _format_stereotypes(uml_class.stereotypes)
    return f'class "{name}" as {alias}{stereotypes} {{'


def _render_class_notes(uml_class: UmlClass, alias: str) -> list[str]:
    """Renders the UML notes attached to one class.

    This helper collects the visible class annotations so the generated PlantUML output
    preserves notes added during the transformation stage.
    """
    lines: list[str] = []
    note_lines = _get_class_note_lines(uml_class)
    if not note_lines:
        return lines

    lines.append(f"note right of {alias}")
    for note_line in note_lines:
        lines.append(f"  {note_line}")
    lines.append("end note")
    return lines


def _get_class_note_lines(uml_class: UmlClass) -> list[str]:
    """Returns the note lines that must be attached to one class.

    This helper consolidates class notes and visible method notes before they are drawn
    as one PlantUML note block.
    """
    lines: list[str] = []

    lines.extend(_get_note_lines(uml_class.notes))

    method_contributions = _get_method_contribution_lines(uml_class)
    for contribution in method_contributions:
        if contribution in lines:
            continue
        lines.append(contribution)

    method_groups = _get_method_group_lines(uml_class)
    for group_line in method_groups:
        if group_line in lines:
            continue
        lines.append(group_line)

    return lines


def _render_class_attributes(uml_class: UmlClass) -> list[str]:
    """Renders the attributes declared in one UML class.

    This helper turns the stored attribute models into PlantUML member lines for the
    class block currently being generated.
    """
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
    """Renders the methods declared in one UML class.

    This helper converts stored UML methods into PlantUML operation lines so the class
    behavior appears in the generated artifact.
    """
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


def _get_note_lines(notes) -> list[str]:
    """Returns the visible note lines stored in one notes collection.

    This helper filters and normalizes note text before it is emitted in the PlantUML
    output.
    """
    lines: list[str] = []

    for note in notes:
        text = _clean_line(note)
        if text:
            lines.append(text)

    return lines


def _get_method_contribution_lines(uml_class: UmlClass) -> list[str]:
    """Returns contribution notes declared by the methods of one class.

    This helper keeps contribution annotations visible at class-note level when the UML
    methods carry those notes internally.
    """
    lines: list[str] = []

    for method in uml_class.methods:
        for note in method.notes:
            text = _clean_line(note)
            if not text:
                continue
            if not text.startswith("contribution:"):
                continue
            lines.append(text)

    return lines


def _get_method_group_lines(uml_class: UmlClass) -> list[str]:
    """Returns group notes for methods so they can be shown in the class note.

    This helper preserves method-level mandatory and `or` information in a form that can
    still be displayed in the rendered PlantUML note block.
    """
    lines: list[str] = []

    for method in uml_class.methods:
        method_name = _clean_line(method.name)
        if not method_name:
            continue

        group_lines = _get_group_note_lines(method.notes)
        for group_line in group_lines:
            lines.append(f"{method_name}(): {group_line}")

    return lines


def _get_group_note_lines(notes) -> list[str]:
    """Returns only the mandatory or `or` notes that should stay visible.

    This helper filters the notes collection so the renderer keeps only the group-related
    annotations that matter in the final UML view.
    """
    lines: list[str] = []

    for note in notes:
        text = _clean_line(note)
        if not text:
            continue
        if text.startswith("mandatory:") or text.startswith("or:"):
            lines.append(text)

    return lines


# ------------ Parameters and Stereotypes ------------
# Methods below render reusable textual fragments for methods and stereotypes.
def _render_parameters(parameters) -> str:
    """Renders the textual parameter list of one UML method.

    This helper formats method parameters once so every rendered operation follows the
    same PlantUML signature style.
    """
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
    """Formats a stereotype list using PlantUML class or method syntax.

    This helper centralizes stereotype formatting so classes and methods render those
    markers consistently in the final artifact.
    """
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


# ------------ Dependency Rendering ------------
# Methods below render the links between UML classes once aliases are known.
def _render_dependency(dep: UmlDependency, alias_by_name: dict[str, str]) -> str:
    """Renders one UML dependency between two previously rendered classes.

    This helper turns stored class relationships into PlantUML dependency lines after
    the class aliases have already been assigned.
    """
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


# ------------ Text Helpers ------------
# Methods below normalize raw text before it is written into PlantUML output.
def _escape_quoted(text) -> str:
    """Escapes text that will be written inside double quotes in PlantUML.

    This helper prevents the generated artifact from breaking when class names contain
    special characters or line breaks.
    """
    if text is None:
        return ""
    s = str(text)
    s = s.replace("\\", "\\\\")
    s = s.replace('"', '\\"')
    s = s.replace("\n", " ")
    s = s.replace("\r", " ")
    return s


def _clean_line(text) -> str:
    """Normalizes one text fragment into a single safe PlantUML line.

    This helper keeps emitted lines compact and valid before the final document is
    assembled.
    """
    if text is None:
        return ""
    s = str(text)
    s = s.replace("\n", " ")
    s = s.replace("\r", " ")
    return s.strip()


# ====== Public API ======
# Methods below expose the PlantUML rendering operations used by the backend.


def render(model: UmlModel) -> str:
    """Renders the complete UML model as PlantUML text.

    This function is the main rendering entry point used when the backend needs the UML
    model as a textual artifact.
    """
    lines: list[str] = []
    lines.append("@startuml")

    title = _clean_line(model.name)
    if title:
        lines.append(f"title {title}")

    for note in model.notes:
        text = _clean_line(note)
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


class PlantumlService:
    """Wraps the PlantUML rendering helpers behind a small service interface.

    This service is used by transformation endpoints when they need to render or persist
    the generated UML model as a `.puml` artifact.
    """

    def render(self, uml_model: UmlModel) -> str:
        """Returns the PlantUML text generated from one UML model.

        This method exposes the textual rendering step so callers can inspect the UML
        output before deciding whether to persist it.
        """
        return render(uml_model)

    def write(self, uml_model: UmlModel, output_path: Path) -> Path:
        """Writes the rendered PlantUML artifact to disk and returns its path.

        This method is used by transformation endpoints when they need a persistent UML
        artifact that can be returned or inspected outside the process memory.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        content = self.render(uml_model)
        output_path.write_text(content, encoding="utf-8")
        logger.info(
            "PlantUML artifact written: path=%s, bytes=%s",
            output_path,
            len(content),
        )
        return output_path
