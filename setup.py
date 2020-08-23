import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tongfang-control",
    version="0.0.1",
    author="Sipho Mateke",
    author_email="siphomateke@gmail.com",
    description="Command line tool for controlling various features of Tongfang-based laptops' such as RGB lighting and fan speed.",
    entry_points={'console_scripts': [
        'tongfang-control = tongfang_control.main:main']},
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/siphomateke/tongfang-control",
    packages=setuptools.find_packages(),
    license="MIT",
    install_requires=["wmi~=1.5.1;platform_system=='Windows'"],
    classifiers=(
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ),
    python_requires='>=3.6',
    project_urls={
        'Bug Reports': 'https://gitlab.com/siphomateke/tongfang-control/issues',
        'Source': 'https://gitlab.com/siphomateke/tongfang-control',
    },
)
