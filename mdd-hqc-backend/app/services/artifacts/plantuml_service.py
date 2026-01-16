from pathlib import Path
from typing import List
from app.models.uml import UmlModel


class PlantumlService:
    def render(self, model: UmlModel, output_path: str | Path) -> Path:
        file_path = Path(output_path)

        lines: List[str] = []
        lines.append("@startuml")

        # Clases
        for uml_class in model.classes.values():
            header_parts: List[str] = ["class", uml_class.name]

            if uml_class.stereotypes:
                stereotype_texts: List[str] = []
                for stereotype in uml_class.stereotypes:
                    stereotype_texts.append(f"<<{stereotype}>>")
                header_parts.append(" ".join(stereotype_texts))

            class_header = " ".join(header_parts)
            lines.append(f"{class_header} {{")

            for attribute in uml_class.attributes:
                lines.append(f"  {attribute.name} : {attribute.type}")

            for method in uml_class.methods:
                lines.append(f"  {method.name}() : {method.return_type}")

            lines.append("}")

            for comment in uml_class.comments:
                lines.append(f"note right of {uml_class.name}")
                lines.append(f"  {comment}")
                lines.append("end note")

        # Dependencias
        for dependency in model.dependencies:
            base = f"{dependency.source} --> {dependency.target}"
            if dependency.stereotype:
                base = f"{base} : {dependency.stereotype}"
            lines.append(base)

        lines.append("@enduml")

        content = "\n".join(lines)
        file_path.write_text(content, encoding="utf-8")
        return file_path
