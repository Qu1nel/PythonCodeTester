import os
from pathlib import Path


class FileProcessor:
    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
        self.processed_files = []
    
    def create_file(self, filename: str, content: str) -> str:
        file_path = self.base_dir / filename
        file_path.write_text(content, encoding="utf-8")
        self.processed_files.append(str(file_path))
        return str(file_path)
    
    def read_file(self, filename: str) -> str:
        file_path = self.base_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"File {filename} not found")
        return file_path.read_text(encoding="utf-8")
    
    def append_to_file(self, filename: str, content: str) -> None:
        file_path = self.base_dir / filename
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(content)
    
    def count_lines(self, filename: str) -> int:
        content = self.read_file(filename)
        return len(content.splitlines())
    
    def count_words(self, filename: str) -> int:
        content = self.read_file(filename)
        return len(content.split())
    
    def cleanup(self) -> None:
        for file_path in self.processed_files:
            try:
                os.remove(file_path)
            except FileNotFoundError:
                pass
        self.processed_files.clear()


def process_text_file(input_file: str, output_file: str) -> dict[str, int]:
    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    lines = len(content.splitlines())
    words = len(content.split())
    chars = len(content)
    
    stats = {
        "lines": lines,
        "words": words,
        "characters": chars
    }
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"File statistics:\n")
        f.write(f"Lines: {lines}\n")
        f.write(f"Words: {words}\n")
        f.write(f"Characters: {chars}\n")
    
    return stats