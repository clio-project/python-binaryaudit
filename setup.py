
from setuptools import setup

setup(name="binaryaudit",
      version="0.0.3",
      description="ELF binary audit",
      url="",
      author="Anatol Belski",
      author_email="anbelski@linux.microsoft.com",
      license="MIT",
      packages=["binaryaudit"],
      install_requires=[
        "sqlalchemy",  # XXX Possibly the db wrapper is to be standalone
        "pyodbc",
        "envparse",
        "python-dateutil",
        "rpmfile"
      ],
      scripts=[
        "bin/binaryaudit",
      ],
      zip_safe=False)
