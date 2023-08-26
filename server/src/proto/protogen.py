import sys
from io import TextIOWrapper
from typing import List

class Namespace:    
    def make_lines(self) -> List[str]:
        pass

    def descriptor(self) -> str:
        pass

class Field:
    type: str
    name: str
    id: int
    is_repeated: bool

    def __init__(self, name: str, type: str, id: int, is_repeated: bool):
        self.name = name
        self.type = Field.parse_type(type)
        self.id = int(id) if id is not None else None
        self.is_repeated = is_repeated

    def make_lines(self) -> List[str]:
        type_hint = self.type
        if type_hint is None:
            return self.make_enum_lines()

        if self.is_repeated:
            type_hint = f"List[{type_hint}]"

        return [
            f"{self.name}: {type_hint}"
        ]

    def make_enum_lines(self) -> List[str]:
        return [
            f"{self.name} = {self.id}"
        ]

    @staticmethod
    def parse_type(s: str) -> str:
        if "string" in s:
            return "str"
        elif "int" in s or "fixed" in s:
            return "int"
        elif "float" in s or "double" in s:
            return "float"
        elif "bool" in s:
            return "bool"
        elif "bytes" in s:
            return "bytes"
        elif "" == s:
            return None
        else:
            return s


class Namespace:
    name: str
    parent: Namespace
    children: List[Namespace]
    fields: List[Field]

    # class Constant
    PREFIX = "\t"

    def __init__(self, name: str, parent: Namespace):
        self.name = name
        self.parent = parent
        self.children = []
        self.fields = []
    
    def add_child(self, space: Namespace) -> None:
        self.children.append(space)

    def add_field(self, name: str, type: str, id: int, is_repeated: bool = False) -> None:
        self.fields.append(Field(name, type, id, is_repeated))
    
    def make_field_lines(self) -> List[str]:
        lines = []
        for field in self.fields:
            lines.extend(field.make_lines())
        return lines

    def make_children_lines(self) -> List[str]:
        lines = []
        for child in self.children:
            lines.extend(child.make_lines())
            lines.append("")
        if len(lines) > 0:
            lines = lines[:-1]
        return lines

    def make_lines(self) -> List[str]:
        pass

    def descriptor(self) -> str:
        return f"{self.parent.descriptor()}.{self.name}"
    
    def set_name(self, name: str) -> None:
        self.name = name


class RootNamespace(Namespace):
    def make_lines(self) -> List[str]:
        lines = []
        lines.extend(self.import_lines())
        lines.append("")
        lines.extend(RootNamespace.proto_lines())
        lines.append("")
        lines.extend(self.make_children_lines())
        lines.extend(self.make_field_lines())
        return lines        

    def descriptor(self) -> str:
        return f"{self.name}_pb2"

    def import_lines(self) -> List[str]:
        return [
            "from enum import Enum",
            "from typing import List",
            "from google import protobuf",
            f"from src.proto import {self.name}_pb2"
        ]
    
    @staticmethod
    def proto_lines() -> List[str]:
        with open("proto.py", "r") as fp:
            return fp.read().split("\n")


class MessageNamespace(Namespace):
    def make_lines(self) -> List[str]:
        lines = []
        lines.extend(self.class_lines())
        lines.extend([ f"{Namespace.PREFIX}{line}" for line in self.make_inner_lines() ])
        return lines    

    def make_inner_lines(self) -> List[str]:
        lines = []
        lines.extend(self.make_children_lines())
        if len(lines) > 0:
            lines.append("")
        lines.extend(self.make_field_lines())
        lines.append("")
        lines.append(f"__proto_descriptor__ = {self.descriptor()}.DESCRIPTOR")
        return lines

    def class_lines(self) -> List[str]:
        return [
            f"class {self.name}(Proto):"
        ]


class EnumNamespace(Namespace):
    def make_lines(self) -> List[str]:
        lines = []
        lines.extend(self.enum_lines())
        lines.extend([ f"{Namespace.PREFIX}{line}" for line in self.make_inner_lines() ])
        return lines    

    def make_inner_lines(self) -> List[str]:
        return self.make_field_lines()
    
    def enum_lines(self) -> List[str]:
        return [
            f"class {self.name}(Enum):"
        ]


class OneofNamespace(Namespace):
    def make_lines(self) -> List[str]:
        lines = []
        lines.extend(self.oneof_lines())
        lines.extend([ f"{Namespace.PREFIX}{line}" for line in self.make_inner_lines() ])
        return lines    

    def make_inner_lines(self) -> List[str]:
        lines = []
        lines.extend(self.make_children_lines())
        if len(lines) > 0:
            lines.append("")
        lines.extend(self.make_field_lines())
        return lines
    
    def oneof_lines(self) -> List[str]:
        return [
            f"class {self.name}:"
        ]

class Generator:
    proto_lines: List[str]
    proto_lines_idx: int
    root: Namespace
    syntax: str
    package: str
    anonymous_counter: int

    # Reserved namespaces
    ROOT = "__ROOT__"
    CHOICE = "Choice"

    # Line types
    LINE_SYNTAX = "syntax"
    LINE_PACKAGE = "package"
    LINE_ENUM = "enum"
    LINE_MESSAGE = "message"
    LINE_ONEOF = "oneof"
    LINE_REPEATED = "repeated"
    LINE_FIELD = "field"
    LINE_CLOSE = "}"

    def __init__(self, proto: str):
        self.proto_lines = Generator.get_proto_lines(proto)
        self.proto_lines_idx = 0
        self.syntax = None
        self.package = None
        self.root = RootNamespace(Generator.ROOT, None)
        self.build_message_tree()

    def build_message_tree(self) -> None:
        self.proto_lines_idx = 0
        self.build(self.root)
    
    def make_file_content(self) -> str:
        lines = self.root.make_lines()
        return "\n".join(lines)

    def build(self, space: Namespace) -> None:
        line = self.next()
        if line is None:
            return  # done
        line_type = self.get_line_type(line)
        if line_type == Generator.LINE_SYNTAX:
            self.build_syntax(space, line)
        elif line_type == Generator.LINE_PACKAGE:
            self.build_package(space, line)
        elif line_type == Generator.LINE_ENUM:
            self.build_enum(space, line)
        elif line_type == Generator.LINE_MESSAGE:
            self.build_message(space, line)
        elif line_type == Generator.LINE_ONEOF:
            self.build_oneof(space, line)
        elif line_type == Generator.LINE_REPEATED:
            self.build_repeated(space, line)
        elif line_type == Generator.LINE_CLOSE:
            return  # done with this sub-type
        else:
            self.build_field(space, line)
        self.build(space)
    
    def build_syntax(self, space: Namespace, line: str) -> None:
        # syntax = "proto3"
        _, _, syntax = line.split()
        self.syntax = syntax.replace("\"", "")
    
    def build_package(self, space: Namespace, line: str) -> None:
        # package carcassonne
        _, self.package = line.split()
        self.root.set_name(self.package)
    
    def build_enum(self, space: Namespace, line: str) -> None:
        # enum SenderType {
        _, name, _ = line.split()
        child = EnumNamespace(name, space)
        self.build(child)
        space.add_child(child)

    def build_message(self, space: Namespace, line: str) -> None:
        # message Sender {
        _, name, _ = line.split()
        child = MessageNamespace(name, space)
        self.build(child)
        space.add_child(child)

    def build_oneof(self, space: Namespace, line: str) -> None:
        # oneof payload {
        _, field_name, _ = line.split()
        child = OneofNamespace(Generator.CHOICE, space)
        self.build(child)
        space.add_child(child)
        space.add_field(field_name, Generator.CHOICE, None)

    def build_repeated(self, space: Namespace, line: str) -> None:
        # repeated string playerNames = 2
        _, field_type, field_name, _, field_id = line.split()
        space.add_field(field_name, field_type, field_id, True)
    
    def build_field(self, space: Namespace, line: str) -> None:
        # string playerNames = 2
        # ANONYMOUS = 0
        pieces = line.split()
        if len(pieces) == 3:
            pieces = ["", *pieces]
        field_type, field_name, _, field_id = pieces
        space.add_field(field_name, field_type, field_id, False)

    def next(self) -> str:
        if self.proto_lines_idx >= len(self.proto_lines):
            return None
        else:
            line = self.proto_lines[self.proto_lines_idx]
            self.proto_lines_idx += 1
            return line

    @staticmethod
    def get_line_type(s: str) -> str:
        # FIXME: do better
        return s.split()[0]

    @staticmethod
    def get_proto_lines(proto: str) -> List[str]:
        implicit_end_chars = [ "{", "}" ]
        END_CHAR = ";"
        for char in implicit_end_chars:
            proto = proto.replace(f"{char}", f"{char}{END_CHAR}")
        def clean(s: str) -> str:
            s = s.strip()
            return ' '.join(s.split())
        lines = [clean(line) for line in proto.split(END_CHAR)]
        lines = filter(lambda line: len(line) > 0, lines)
        return list(lines)


def protogen(infp: TextIOWrapper, outfp: TextIOWrapper) -> None:
    generator = Generator(infp.read())
    outfp.write(generator.make_file_content())

    
def main():
    if len(sys.argv) != 2:
        print("Usage: protogen.py <infile>")
        return 1
    
    infile = sys.argv[1]
    package = infile.split(".")[0]
    outfile = f"{package}_proto.py"

    with open(infile, "r") as infp, open(outfile, "w") as outfp:
        protogen(infp, outfp)


if __name__ == "__main__":
    main()
