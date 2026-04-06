"""UML class diagram in-memory model.

This module defines a compact set of models used by the PIM->PSM
transformation to represent classes, methods, attributes, notes, and
dependencies before rendering PlantUML.
"""

from typing import Optional
from pydantic import BaseModel, Field


# ------------ BASE MODEL ------------
# Helper models below define the in-memory UML structures used by the transformation pipeline.
class UmlBaseModel(BaseModel):
    """Base class for UML models."""


# ------------ HELPER MODELS ------------
class UmlAttribute(UmlBaseModel):
    """Represents one attribute stored inside a UML class.

    This model keeps attribute data structured so transformations can attach feature
    properties to classes before PlantUML rendering begins.
    """

    name: str
    type: str = "String"
    default: Optional[str] = None
    notes: list[str] = Field(default_factory=list)


class UmlMethodParameter(UmlBaseModel):
    """Represents one parameter declared by a UML method.

    This model preserves method signatures in the in-memory diagram so later renderers
    can output readable operation definitions.
    """

    name: str
    type: str = "String"


class UmlMethod(UmlBaseModel):
    """Represents one method attached to a UML class.

    This model stores operation details and notes so transformations can map feature
    behavior into class-level actions before exporting the UML diagram.
    """

    name: str
    parameters: list[UmlMethodParameter] = Field(default_factory=list)
    return_type: str = "void"
    stereotypes: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)

    def add_note(self, note: str):
        """Appends a non-empty note to the stored UML method.

        This method keeps method-level annotations inside the model so transformations
        can preserve metadata that must later appear in the rendered UML output.

        For example, after adding a note, the model can contain:
            ClassName {
                methodName()
            }
            note for methodName: actor: Analyst
        """
        text = (note or "").strip()
        if text:
            self.notes.append(text)


class UmlClass(UmlBaseModel):
    """Represents one UML class node with its members and annotations.

    This model is the main unit of the generated UML diagram, collecting the state that
    transformations and renderers need to describe one class in memory.
    """

    name: str
    stereotypes: list[str] = Field(default_factory=list)
    attributes: list[UmlAttribute] = Field(default_factory=list)
    methods: list[UmlMethod] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)

    def add_attribute(self, attr: UmlAttribute):
        """Adds one attribute to the UML class.

        This method updates the class state so the in-memory diagram can reflect the
        data members introduced by transformations.

        For example, after adding an attribute, the model can contain:
            QuantumDriver {
                shots: String
            }
        """
        self.attributes.append(attr)

    def add_method(self, method: UmlMethod):
        """Adds one method to the UML class.

        This method updates the class state so the model can represent behavior mapped
        from source features before the final UML artifact is rendered.

        For example, after adding a method, the model can contain:
            SecurityGoal {
                encryptData()
            }
        """
        self.methods.append(method)

    def add_note(self, note: str):
        """Appends a non-empty note to the UML class.

        This method preserves class-level annotations in the model so the generated UML
        diagram can still show metadata gathered during transformation.

        For example, after adding a note, the model can contain:
            note for SecurityGoal: mandatory: EncryptData
        """
        text = (note or "").strip()
        if text:
            self.notes.append(text)


class UmlDependency(UmlBaseModel):
    """Represents one dependency relationship between two UML classes.

    This model keeps cross-class links explicit so transformations can preserve the
    structural constraints that later appear in the UML diagram.
    """

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

    # ====== Public API ======
    # Methods below let services and transformations read or extend the UML model.

    # ------------ Class Management ------------
    # Methods below create or retrieve classes so the diagram stays consistent in memory.
    def get_or_create_class(self, label: str) -> UmlClass:
        """Returns an existing class by label or creates a new one when missing."""
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
        """Returns the UML class that matches the requested label.

        This lookup helps the model reuse an existing class entry instead of duplicating
        nodes when several transformation rules point to the same class.

        For example, it can resolve `SecurityGoal` from:
            class SecurityGoal
        """
        name = (label or "").strip()
        if not name:
            return None
        return self.classes.get(name)

    # ------------ Diagram Annotations and Links ------------
    # Methods below register diagram-level notes and dependencies between stored classes.
    def add_dependency(self, dep: UmlDependency) -> None:
        """Adds one dependency to the UML diagram model.

        This method keeps class relationships in the central diagram state so renderers
        can output the links discovered during transformation.

        For example, the model can store a relation such as:
            SecurityGoal --> EncryptionDriver
        """
        self.dependencies.append(dep)

    def add_note(self, note: str) -> None:
        """Appends a non-empty note to the UML diagram.

        This method keeps diagram-wide annotations available when a transformation needs
        to record information that does not belong to a single class.
        """
        text = (note or "").strip()
        if text:
            self.notes.append(text)

    def get_classes(self) -> dict[str, UmlClass]:
        """Returns the class index stored in the UML model.

        This query gives other backend steps direct access to the generated class set
        when they need to inspect or render the current diagram state.
        """
        return self.classes

    def get_dependencies(self) -> list[UmlDependency]:
        """Returns the dependencies registered in the UML model.

        This query exposes the current cross-class relationships so renderers and
        metrics services can inspect the full diagram connectivity.
        """
        return self.dependencies

    def add_dependency_by_label(
        self,
        source_label: str,
        target_label: str,
        stereotype: Optional[str] = None,
        label: Optional[str] = None,
        notes: Optional[list[str]] = None,
    ) -> UmlDependency:
        """Creates a dependency from class labels and stores it in the UML model.

        This method is useful when a transformation knows only the class names and still
        needs the model to keep both endpoints and their relationship consistent.

        For example, the model can end up containing:
            SecurityGoal ..> EncryptionDriver : requires
        """
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

    # ------------ Class Member Management ------------
    # Methods below add or resolve the attributes and methods stored inside each class.
    def add_attribute_to_class(
        self,
        class_label: str,
        attribute_name: str,
        attribute_type: str = "String",
        default: Optional[str] = None,
    ) -> UmlAttribute:
        """Creates an attribute and attaches it to one UML class.

        This method helps transformations enrich the model with class data members while
        keeping class creation and attribute registration in one place.

        For example, the model can contain:
            QuantumDriver {
                backend: String
            }
        """
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
        """Creates a method and attaches it to one UML class.

        This method lets transformations store behavior in the model without manually
        resolving the class each time they introduce a new operation.

        For example, the model can contain:
            SecurityGoal {
                validateCircuit()
            }
        """
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
        """Returns one stored method from the requested UML class.

        This lookup helps the model reuse existing operations when later rules need to
        add notes or metadata to a method that was already created.

        For example, it can resolve `validateCircuit()` from:
            SecurityGoal {
                validateCircuit()
            }
        """
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
