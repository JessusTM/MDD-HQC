"""UML class diagram in-memory model.

This module defines a compact set of models used by the PIM->PSM
transformation to represent classes, methods, attributes, notes, and
dependencies before rendering PlantUML.
"""

from typing import Optional
from pydantic import BaseModel, Field


# ------------ BASE MODEL ------------
class UmlBaseModel(BaseModel):
    """Base class for UML models."""


# ------------ HELPER MODELS ------------
class UmlAttribute(UmlBaseModel):
    """Attribute owned by one UML class."""

    name: str
    type: str = "String"
    default: Optional[str] = None
    notes: list[str] = Field(default_factory=list)


class UmlMethodParameter(UmlBaseModel):
    """Parameter declared by one UML method."""

    name: str
    type: str = "String"


class UmlMethod(UmlBaseModel):
    """Method owned by one UML class."""

    name: str
    parameters: list[UmlMethodParameter] = Field(default_factory=list)
    return_type: str = "void"
    stereotypes: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)

    def add_note(self, note: str):
        text = (note or "").strip()
        if text:
            self.notes.append(text)


class UmlClass(UmlBaseModel):
    """UML class node with members and notes."""

    name: str
    stereotypes: list[str] = Field(default_factory=list)
    attributes: list[UmlAttribute] = Field(default_factory=list)
    methods: list[UmlMethod] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)

    def add_attribute(self, attr: UmlAttribute):
        self.attributes.append(attr)

    def add_method(self, method: UmlMethod):
        self.methods.append(method)

    def add_note(self, note: str):
        text = (note or "").strip()
        if text:
            self.notes.append(text)


class UmlDependency(UmlBaseModel):
    """Dependency relationship between two UML classes."""

    source: str
    target: str
    stereotype: Optional[str] = None
    label: Optional[str] = None
    notes: list[str] = Field(default_factory=list)


# ------------ DIAGRAM MODEL ------------
class UmlModel(UmlBaseModel):
    """UML diagram container.

    Data held in memory:
    - classes: map of class name -> UmlClass
    - dependencies: list of UmlDependency
    - notes: free-form diagram-level notes
    """

    name: str
    classes: dict[str, UmlClass] = Field(default_factory=dict)
    dependencies: list[UmlDependency] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)

    def get_or_create_class(self, label: str) -> UmlClass:
        name = (label or "").strip()
        if not name:
            name = "Class"

        existing = self.classes.get(name)
        if existing is not None:
            return existing

        uml_class = UmlClass(name=name)
        self.classes[name] = uml_class
        return uml_class

    def get_class(self, label: str) -> Optional[UmlClass]:
        name = (label or "").strip()
        if not name:
            return None
        return self.classes.get(name)

    def add_dependency(self, dep: UmlDependency) -> None:
        self.dependencies.append(dep)

    def add_note(self, note: str) -> None:
        text = (note or "").strip()
        if text:
            self.notes.append(text)

    def get_classes(self) -> dict[str, UmlClass]:
        return self.classes

    def get_dependencies(self) -> list[UmlDependency]:
        return self.dependencies

    def add_dependency_by_label(
        self,
        source_label: str,
        target_label: str,
        stereotype: Optional[str] = None,
        label: Optional[str] = None,
        notes: Optional[list[str]] = None,
    ) -> UmlDependency:
        source = self.get_or_create_class(source_label)
        target = self.get_or_create_class(target_label)

        dep = UmlDependency(
            source=source.name,
            target=target.name,
            stereotype=stereotype,
            label=label,
            notes=notes or [],
        )
        self.add_dependency(dep)
        return dep

    def add_attribute_to_class(
        self,
        class_label: str,
        attribute_name: str,
        attribute_type: str = "String",
        default: Optional[str] = None,
    ) -> UmlAttribute:
        uml_class = self.get_or_create_class(class_label)
        attribute = UmlAttribute(
            name=attribute_name, type=attribute_type, default=default
        )
        uml_class.add_attribute(attribute)
        return attribute

    def add_method_to_class(
        self,
        class_name: str,
        method_name: str,
        parameters: Optional[list[UmlMethodParameter]] = None,
        return_type: str = "void",
    ) -> UmlMethod:
        uml_class = self.get_or_create_class(class_name)
        method = UmlMethod(
            name=method_name,
            parameters=parameters or [],
            return_type=return_type,
        )
        uml_class.add_method(method)
        return method

    def get_method_from_class(
        self,
        class_name: str,
        method_name: str,
    ) -> Optional[UmlMethod]:
        uml_class = self.get_class(class_name)
        if uml_class is None:
            return None

        normalized_method_name = (method_name or "").strip()
        if not normalized_method_name:
            return None

        for method in uml_class.methods:
            if method.name == normalized_method_name:
                return method

        return None
