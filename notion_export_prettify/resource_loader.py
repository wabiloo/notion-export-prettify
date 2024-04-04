from os import path


class ResourceLoader:
    def __init__(self) -> None:
        self.dir = None

    def set_folder(self, dir):
        self.dir = dir

    def get_resource_path(self, filename):
        if self.dir:
            file_path = path.join(self.dir, filename)
            if path.exists(file_path):
                return file_path

    def get_resource_content(self, filename):
        file_path = self.get_resource_path(filename)
        if file_path:
            with open(file_path, "r") as f:
                return f.read()
