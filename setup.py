from setuptools import find_packages, setup

requirements = ["numpy>=1.16", "toml", "requests", "plum-dispatch"]

setup(
    packages=find_packages(exclude=["docs"]),
    python_requires=">=3.8",
    install_requires=requirements,
    include_package_data=True,
)
