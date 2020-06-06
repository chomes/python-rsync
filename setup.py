import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="python-rsync-chomes", # Replace with your own username
    version="1.4",
    author="James Joseph",
    author_email="jaayjay@gmail.com",
    description="Python version of rsync client",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/chomes/python-rsync",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
