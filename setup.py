
from setuptools import setup

setup(name = "binaryaudit",
        version = "0.0.2",
        description = "ELF binary audit",
        url = "",
        author = "Anatol Belski",
        author_email = "anbelski@linux.microsoft.com",
        license = "MIT",
        packages = ["binaryaudit"],
        install_requires = [
        ],
        scripts = [
            "bin/ba_example",
        ],
        zip_safe = False)

