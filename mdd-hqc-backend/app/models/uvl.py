from pathlib import Path

class UVL:
    FILE_NAME = Path("app/data/model.uvl")

    def create_file(self):
        self.FILE_NAME.parent.mkdir(parents=True, exist_ok=True)
        self.FILE_NAME.touch(exist_ok=True)

    def write(self, text):
        with self.FILE_NAME.open("a") as file:
            file.write(text)

    def set_metadata(self, elements):
        for element in elements:
            if not element : continue
            self.write("// " + element + "\n")

    def set_section(self, text, elements, optional_elements=None):
        self.write("\n" + text + "{")

        for element in elements:
            self.write("\n      " + element)

        if optional_elements:
            for element in optional_elements:
                self.write("\n      " + element)
        self.write("\n}" + "\n")
