from pathlib import Path
from typing import Dict, List, Optional
from app.models.feature import Feature


class UVL:
    FILE_NAME = Path("app/data/model.uvl")

    def __init__(self):
        self.namespace          : str                   = "HQC_SPL"
        self.features           : List[Feature]         = []
        self.constraints        : List[str]             = [] 
        self.contributions      : List[str]             = []
        self.or_groups          : Dict[str, List[str]]  = {}
        self.allowed_categories : List[str]             = [
            "@Functionality",
            "@Algorithm",
            "@Programming",
            "@Integration_model",
            "@Quantum_HW_constraint",
        ]

    def clear(self):
        self.features       = []
        self.constraints    = []
        self.contributions  = []
        self.or_groups      = {}

    def add_feature(
        self,
        name        : str,
        category    : str,
        kind        : Optional[str]             = None,
        attributes  : Optional[Dict[str, str]]  = None,
        comments    : Optional[List[str]]       = None,
    ) -> Feature:
        if category not in self.allowed_categories : category = "@Functionality"

        feature = Feature(
            name        = name,
            category    = category,
            kind        = kind,
            attributes  = attributes or {},
            comments    = comments or [],
        )
        self.features.append(feature)
        return feature

    def add_comment_to_feature(self, feature_name: str, category: str, comment: str):
        for feat in self.features:
            if feat.name == feature_name and feat.category == category:
                feat.comments.append(comment)
                return

    def add_attribute_to_feature(
        self,
        feature_name    : str,
        category        : str,
        attr_name       : str,
        attr_value      : str,
    ):
        for feat in self.features:
            if feat.name == feature_name and feat.category == category:
                feat.attributes[attr_name] = attr_value
                return

    def add_constraint(self, expr: str) -> None:
        expr = expr.strip()
        if expr:
            parts = expr.split(" -> ")
            if len(parts) == 2:
                left    = parts[0].strip()
                right   = parts[1].strip()
                if left.lower() == right.lower() : return
            self.constraints.append(expr)
    
    def add_contribution(self, comment: str) -> None:
        if comment:
            self.contributions.append(comment)
    
    def add_or_group(self, parent_name: str, child_name: str) -> None:
        if parent_name not in self.or_groups:
            self.or_groups[parent_name] = []
        if child_name not in self.or_groups[parent_name]:
            self.or_groups[parent_name].append(child_name)

    def create_file(self) -> None:
        self.FILE_NAME.parent.mkdir(parents=True, exist_ok=True)
        with self.FILE_NAME.open("w", encoding="utf-8") as file:
            self._write_namespace_header(file)
            self._write_categories(file)
            self._write_constraints(file)

    def _write_namespace_header(self, file) -> None:
        file.write(f"{self.namespace}\n\n")

    def _write_categories(self, file) -> None:
        file.write("features:\n\n")
        
        # Recopilar todos los recursos de features de Functionality
        all_resources = set()
        for feat in self.features:
            if feat.category == "@Functionality":
                for comment in feat.comments:
                    if comment.startswith("resource:") and ":" in comment:
                        resource_name = comment.split(":", 1)[1].strip()
                        if resource_name:
                            all_resources.add(resource_name)
        
        # Escribir cada categoría
        for category in self.allowed_categories:
            # Obtener features de esta categoría
            category_features = []
            for feat in self.features:
                if feat.category == category:
                    category_features.append(feat)
            
            # Si no hay features en esta categoría, saltarla
            if not category_features:
                continue

            file.write(f"  {category}:\n")
            
            # Escribir recursos si es Functionality
            if category == "@Functionality" and all_resources:
                file.write("    # Recursos no generan variabilidad\n")
                for resource in sorted(all_resources):
                    file.write(f"    # {resource}\n")
            
            # Escribir features según el tipo de categoría
            if category == "@Algorithm":
                self._write_algorithm_category(file, category_features)
            else:
                self._write_regular_category(file, category_features)
            
            file.write("\n")
    
    def _write_algorithm_category(self, file, features: List[Feature]) -> None:
        # Separar features en Classical, Quantum y otros
        classical_features = []
        quantum_features = []
        other_features = []
        
        for feat in features:
            name_lower = feat.name.lower()
            if "quantum" in name_lower or "annealing" in name_lower:
                quantum_features.append(feat)
            elif "grafos" in name_lower or "clasico" in name_lower or "classical" in name_lower:
                classical_features.append(feat)
            else:
                other_features.append(feat)
        
        # Escribir features Classical
        if classical_features:
            file.write("    @Classical:\n")
            for i, feat in enumerate(classical_features):
                self._write_feature(file, feat, indent="      ")
                if i < len(classical_features) - 1:
                    file.write("\n")
        
        # Escribir features Quantum
        if quantum_features:
            file.write("    @Quantum:\n")
            for i, feat in enumerate(quantum_features):
                self._write_feature(file, feat, indent="      ")
                if i < len(quantum_features) - 1:
                    file.write("\n")
        
        # Escribir otros features
        if other_features:
            for i, feat in enumerate(other_features):
                self._write_feature(file, feat, indent="    ")
                if i < len(other_features) - 1:
                    file.write("\n")
    
    def _write_regular_category(self, file, category_features: List[Feature]) -> None:
        # Separar features: las que son padres de grupos OR, las que son hijos, y las regulares
        features_with_or_groups = []
        features_without_or_groups = []
        
        # Obtener todos los nombres de hijos en grupos OR
        all_or_children = set()
        for children_list in self.or_groups.values():
            for child_name in children_list:
                all_or_children.add(child_name)
        
        # Clasificar cada feature
        for feat in category_features:
            if feat.name in self.or_groups:
                # Es un padre de grupo OR
                features_with_or_groups.append(feat)
            elif feat.name not in all_or_children:
                # No es padre ni hijo, es una feature regular
                features_without_or_groups.append(feat)
        
        # Escribir primero las features regulares, luego las que tienen grupos OR
        all_features_to_write = features_without_or_groups + features_with_or_groups
        
        for i, feat in enumerate(all_features_to_write):
            self._write_feature(file, feat)
            
            # Si esta feature tiene hijos en un grupo OR, escribirlos
            if feat.name in self.or_groups:
                file.write("    or\n")
                for child_name in self.or_groups[feat.name]:
                    # Buscar el feature hijo en la categoría
                    child_feat = None
                    for f in category_features:
                        if f.name == child_name:
                            child_feat = f
                            break
                    
                    # Escribir el hijo
                    if child_feat:
                        file.write(f"      {child_feat.name}")
                        if child_feat.kind:
                            file.write(f" {{kind \"{child_feat.kind}\"}}")
                        if child_feat.attributes:
                            file.write(" {\n")
                            attr_items = list(child_feat.attributes.items())
                            for j, (attr_name, attr_value) in enumerate(attr_items):
                                if attr_value.lower() in ["true", "false"]:
                                    value = attr_value.lower()
                                else:
                                    value = attr_value
                                comma = "," if j < len(attr_items) - 1 else ""
                                file.write(f"        {attr_name.capitalize()} {value}{comma}\n")
                            file.write("      }\n")
                        else:
                            file.write("\n")
                    else:
                        file.write(f"      {child_name}\n")
            
            # Agregar línea en blanco entre features (excepto la última)
            if i < len(all_features_to_write) - 1:
                file.write("\n")

    def _write_feature(self, file, feat: Feature, indent: str = "    ", simple: bool = False) -> None:
        # Escribir comentarios (solo si no es modo simple)
        if not simple:
            seen_actors = set()
            for comment in feat.comments:
                # Escribir comentarios de actores
                if comment.startswith("actor:") or comment.startswith("agent:") or comment.startswith("role:"):
                    if ":" in comment:
                        actor_name = comment.split(":", 1)[1].strip()
                        if actor_name and actor_name not in seen_actors:
                            seen_actors.add(actor_name)
                            file.write(f"{indent}# Actor: {actor_name}\n")
                # Escribir otros comentarios (excepto resource y contribution)
                elif not comment.startswith("resource:") and not comment.startswith("contribution"):
                    file.write(f"{indent}# {comment}\n")

        # Si no tiene kind ni attributes, escribir solo el nombre
        if not feat.kind and not feat.attributes:
            file.write(f"{indent}{feat.name}\n")
            return

        # Escribir nombre de la feature
        file.write(f"{indent}{feat.name}")
        
        # Escribir kind si existe
        if feat.kind:
            file.write(f" {{kind \"{feat.kind}\"}}")
        
        # Escribir attributes si existen
        if feat.attributes:
            file.write(" {\n")
            attr_items = list(feat.attributes.items())
            for i, (attr_name, attr_value) in enumerate(attr_items):
                # Convertir true/false a minúsculas, otros valores se dejan como están
                if attr_value.lower() in ["true", "false"]:
                    value = attr_value.lower()
                else:
                    value = attr_value
                
                # Agregar coma si no es el último atributo
                if i < len(attr_items) - 1:
                    file.write(f"{indent}      {attr_name.capitalize()} {value},\n")
                else:
                    file.write(f"{indent}      {attr_name.capitalize()} {value}\n")
            file.write(f"{indent}    }}\n")
        else:
            file.write("\n")

    def _write_constraints(self, file) -> None:
        valid_constraints = []
        feature_names = {feat.name.lower() for feat in self.features}
        
        for c in self.constraints:
            constraint  = c.replace(" => ", " -> ")
            parts       = constraint.split(" -> ")
            if len(parts) == 2:
                left    = parts[0].strip()
                right   = parts[1].strip()
                if left.lower() == right.lower():
                    continue
                if left.lower() in feature_names and right.lower() in feature_names:
                    valid_constraints.append(constraint)
        
        if valid_constraints:
            file.write("\nconstraints:\n")
            for constraint in valid_constraints:
                file.write(f"  {constraint}\n")
        
        if self.contributions:
            file.write("\n# helps / makes / hurts / breaks\n")
            for contribution in self.contributions:
                file.write(f"# {contribution}\n")