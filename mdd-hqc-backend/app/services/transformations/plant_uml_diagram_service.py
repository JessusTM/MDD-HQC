import zlib
from typing import List


class PlantUMLDiagramService:
    """Proporciona operaciones de codificación compatibles con el servidor público de PlantUML."""

    PLANTUML_SERVER = "https://www.plantuml.com/plantuml"

    def encode_diagram_to_plantuml_server_format(self, diagram: str) -> str:
        """Comprime y codifica un diagrama PlantUML usando el algoritmo propio de la herramienta."""

        compressor = zlib.compressobj(level=9, method=zlib.DEFLATED, wbits=-15)
        compressed_bytes = compressor.compress(diagram.encode("utf-8"))
        compressed_bytes += compressor.flush()
        encoded_diagram = self.convert_bytes_to_custom_base64(compressed_bytes)
        return encoded_diagram

    def build_plantuml_server_url(self, diagram: str, output_format: str = "svg") -> str:
        """Genera la URL que renderiza el diagrama proporcionado a través de PlantUML."""

        encoded_diagram = self.encode_diagram_to_plantuml_server_format(diagram)
        plantuml_url = f"{self.PLANTUML_SERVER}/{output_format}/{encoded_diagram}"
        return plantuml_url

    def convert_bytes_to_custom_base64(self, data: bytes) -> str:
        """Codifica bytes siguiendo la variante de base64 personalizada de PlantUML."""

        encoded_parts: List[str] = []
        current_index = 0
        while current_index < len(data):
            chunk = data[current_index : current_index + 3]
            first_byte = chunk[0]
            second_byte = chunk[1] if len(chunk) > 1 else 0
            third_byte = chunk[2] if len(chunk) > 2 else 0
            encoded_chunk = self.encode_three_byte_chunk(first_byte, second_byte, third_byte)
            encoded_parts.append(encoded_chunk)
            current_index += 3
        encoded_string = "".join(encoded_parts)
        return encoded_string

    def encode_three_byte_chunk(self, first_byte: int, second_byte: int, third_byte: int) -> str:
        """Convierte tres bytes en cuatro caracteres compatibles con PlantUML."""

        first_value = first_byte >> 2
        second_value = ((first_byte & 0x3) << 4) | (second_byte >> 4)
        third_value = ((second_byte & 0xF) << 2) | (third_byte >> 6)
        fourth_value = third_byte & 0x3F
        encoded_values = [first_value, second_value, third_value, fourth_value]
        encoded_characters: List[str] = []
        for value in encoded_values:
            encoded_character = self.encode_six_bit_value(value & 0x3F)
            encoded_characters.append(encoded_character)
        encoded_text = "".join(encoded_characters)
        return encoded_text

    def encode_six_bit_value(self, value: int) -> str:
        """Mapea un entero de seis bits al alfabeto utilizado por PlantUML."""

        if value < 10:
            return chr(48 + value)
        adjusted_value = value - 10
        if adjusted_value < 26:
            return chr(65 + adjusted_value)
        adjusted_value -= 26
        if adjusted_value < 26:
            return chr(97 + adjusted_value)
        adjusted_value -= 26
        if adjusted_value == 0:
            return "-"
        return "_"
