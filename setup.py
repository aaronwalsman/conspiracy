import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="conspiracy",
    version="0.0.1",
    license='MIT',
    install_requires = ['numpy', 'colorama'],
    author="Aaron Walsman",
    author_email="aaronwalsman@gmail.com",
    description='Terminal Plotter',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aaronwalsman/conspiracy",
    packages=setuptools.find_packages(),
)
