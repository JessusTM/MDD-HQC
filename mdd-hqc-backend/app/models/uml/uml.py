from typing import Optional

from pydantic import BaseModel, Field


class UmlBaseModel(BaseModel):
    pass


class UmlAttribute(UmlBaseModel):
    name: str
    type: str = "String"
    default: Optional[str] = None
    tagged_values: dict[str, str] = Field(default_factory=dict)
    comments: list[str] = Field(default_factory=list)


class UmlMethodParameter(UmlBaseModel):
    name: str
    type: str = "String"


class UmlMethod(UmlBaseModel):
    name: str
    parameters: list[UmlMethodParameter] = Field(default_factory=list)
    return_type: str = "void"
    stereotypes: list[str] = Field(default_factory=list)
    tagged_values: dict[str, str] = Field(default_factory=dict)
    comments: list[str] = Field(default_factory=list)


class UmlClass(UmlBaseModel):
    name: str
    stereotypes: list[str] = Field(default_factory=list)
    attributes: list[UmlAttribute] = Field(default_factory=list)
    methods: list[UmlMethod] = Field(default_factory=list)
    tagged_values: dict[str, str] = Field(default_factory=dict)
    comments: list[str] = Field(default_factory=list)

    def add_attribute(self, attr: UmlAttribute):
        self.attributes.append(attr)

    def add_method(self, method: UmlMethod):
        self.methods.append(method)

    def add_comment(self, comment: str):
        text = (comment or "").strip()
        if text:
            self.comments.append(text)

    def add_tagged_value(self, key: str, value: str):
        k = (key or "").strip()
        v = (value or "").strip()
        if k and v:
            self.tagged_values[k] = v


class UmlDependency(UmlBaseModel):
    source: str
    target: str
    stereotype: Optional[str] = None
    label: Optional[str] = None
    comments: list[str] = Field(default_factory=list)


class UmlModel(UmlBaseModel):
    name: str
    classes: dict[str, UmlClass] = Field(default_factory=dict)
    dependencies: list[UmlDependency] = Field(default_factory=list)
    comments: list[str] = Field(default_factory=list)

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

    def add_dependency(self, dep: UmlDependency) -> None:
        self.dependencies.append(dep)

    def add_comment(self, comment: str) -> None:
        text = (comment or "").strip()
        if text:
            self.comments.append(text)


class UML(UmlModel):
    """Facade for building a UML class diagram.

    This class centralizes class creation, relationship wiring, and PlantUML
    rendering. Transformations should depend on this facade instead of
    instantiating low-level helper models directly.
    """

    def add_class(self, label: str) -> UmlClass:
        return self.get_or_create_class(label)

    def add_dependency_by_label(
        self,
        source_label: str,
        target_label: str,
        stereotype: Optional[str] = None,
        label: Optional[str] = None,
        comments: Optional[list[str]] = None,
    ) -> UmlDependency:
        source = self.get_or_create_class(source_label)
        target = self.get_or_create_class(target_label)

        dep = UmlDependency(
            source=source.name,
            target=target.name,
            stereotype=stereotype,
            label=label,
            comments=comments or [],
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
        attr = UmlAttribute(name=attribute_name, type=attribute_type, default=default)
        uml_class.add_attribute(attr)
        return attr

    def add_method_to_class(
        self,
        class_label: str,
        method_name: str,
        parameters: Optional[list[UmlMethodParameter]] = None,
        return_type: str = "void",
    ) -> UmlMethod:
        uml_class = self.get_or_create_class(class_label)
        method = UmlMethod(
            name=method_name,
            parameters=parameters or [],
            return_type=return_type,
        )
        uml_class.add_method(method)
        return method

    def to_plantuml(self) -> str:
        from .plantuml import render

        return render(self)
