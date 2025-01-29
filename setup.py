from setuptools import setup, find_packages

# Read the contents of README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="google-pronouncer",
    version="0.2.1",
    author="Hachiro",
    author_email="farhad@farhad.my",
    description="A library for downloading pronunciation MP3 files from Google's dictionary service",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/HachiroSan/google-pronouncer",
    project_urls={
        "Homepage": "https://github.com/HachiroSan/google-pronouncer",
        "Bug Tracker": "https://github.com/HachiroSan/google-pronouncer/issues",
        "Documentation": "https://github.com/HachiroSan/google-pronouncer#readme",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Education",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="pronunciation, audio, google, dictionary, text-to-speech, education, language",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.31.0,<3.0.0",
        "tqdm>=4.65.0",
    ],
    entry_points={
        "console_scripts": [
            "google-pronouncer=google_pronouncer.cli:main",
        ],
    },
) 