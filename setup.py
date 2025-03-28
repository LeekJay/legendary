from setuptools import setup, find_packages
from Cython.Build import cythonize

setup(
    name="legendary-flask-api",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    ext_modules=cythonize(
        [
            "./src/client/auto_game.py",
            "./src/client/admin_panel.py",
            "./src/client/firebase_api.py",
            "./src/client/register_window.py",
        ],
        language_level=3,
    ),
    install_requires=[
        line.strip()
        for line in open("requirements.txt")
        if line.strip() and not line.startswith("#")
    ],
    python_requires=">=3.9",
    include_package_data=True,
)
