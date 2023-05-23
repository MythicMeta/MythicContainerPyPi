import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="mythic_container",
    version="0.2.9",
    description="Functionality for Mythic Services",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://docs.mythic-c2.net/customizing/payload-type-development",
    author="@its_a_feature_",
    author_email="",
    license="BSD3",
    classifiers=[
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
    ],
    packages=["mythic_container", "mythic_container.grpc", "mythic_container.MythicGoRPC"],
    include_package_data=True,
    install_requires=[
        "aio_pika==9.0.4",
        "dynaconf==3.1.11",
        "ujson==5.7.0",
        "aiohttp==3.8.3",
        "psutil==5.9.4",
        "grpcio",
        "grpcio-tools",
    ],
    entry_points={},
)
