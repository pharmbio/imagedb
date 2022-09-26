from typing_extensions import Protocol

class Fileparser(Protocol):
    def parse_path_and_file(self, path: str) -> dict:
        return {}