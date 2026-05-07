from setuptools import setup, find_packages

setup(
    name="rcefuscator",
    version="1.0.0",
    description="RCE Payload Generator & WAF Evasion Toolkit for authorized penetration testing",
    author="ak4hit",
    packages=find_packages(),
    install_requires=["click", "rich", "pyperclip", "pyfiglet"],
    entry_points={
        "console_scripts": [
            "rcefuscator=rcefuscator.cli.main:cli",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Topic :: Security",
    ],
)
