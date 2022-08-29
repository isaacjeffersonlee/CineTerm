from setuptools import setup, find_packages

setup(
    name="cineterm",
    description="Stream/download movie torrents from the terminal.",
    version="0.1",
    packages=find_packages(exclude=("tests")),
    scripts=["cineterm/cineterm_run.py"],
    entry_points={
        "console_scripts": [
            "cineterm = cineterm.cineterm_run:main",
        ]
    }
)
