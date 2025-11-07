from pathlib import Path

class UVL:
    FILE_NAME = Path("app/data/model.uvl")

    def create_file(self):
        self.FILE_NAME.parent.mkdir(parents=True, exist_ok=True)
        self.FILE_NAME.touch(exist_ok=True)

    def write(self, text):
        with self.FILE_NAME.open("a") as file:
            file.write(text)
