from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class UmlAttribute:
    name         : str
    type         : str                      = "String"
    default      : Optional[str]            = None
    tagged_values: Dict[str, str]           = field(default_factory=dict)

@dataclass
class UmlMethodParameter:
    name: str
    type: str = "String"

@dataclass
class UmlMethod:
    name         : str
    parameters   : List[UmlMethodParameter]  = field(default_factory=list)
    return_type  : str                       = "void"
    stereotypes  : List[str]                 = field(default_factory=list)
    tagged_values: Dict[str, str]            = field(default_factory=dict)
    comments     : List[str]                 = field(default_factory=list)

@dataclass
class UmlClass:
    name         : str
    stereotypes  : List[str]                 = field(default_factory=list)
    attributes   : List[UmlAttribute]        = field(default_factory=list)
    methods      : List[UmlMethod]           = field(default_factory=list)
    tagged_values: Dict[str, str]            = field(default_factory=dict)
    comments     : List[str]                 = field(default_factory=list)

    def add_attribute(self, attr: UmlAttribute) -> None:
        self.attributes.append(attr)

    def add_method(self, method: UmlMethod) -> None:
        self.methods.append(method)

    def add_comment(self, comment: str) -> None:
        if comment:
            self.comments.append(comment)

    def add_tagged_value(self, key: str, value: str) -> None:
        if key and value:
            self.tagged_values[key] = value

@dataclass
class UmlDependency:
    source    : str          # Nombre de clase origen
    target    : str          # Nombre de clase destino
    stereotype: Optional[str] = None
    label     : Optional[str] = None
    comments  : List[str]     = field(default_factory=list)

@dataclass
class UmlModel:
    name        : str
    classes     : Dict[str, UmlClass]  = field(default_factory=dict)
    dependencies: List[UmlDependency]  = field(default_factory=list)
    comments    : List[str]            = field(default_factory=list)

    def get_or_create_class(self, name: str) -> UmlClass:
        if name not in self.classes:
            self.classes[name] = UmlClass(name=name)
        return self.classes[name]

    def add_dependency(self, dep: UmlDependency) -> None:
        self.dependencies.append(dep)

    def add_comment(self, comment: str) -> None:
        if comment:
            self.comments.append(comment)
