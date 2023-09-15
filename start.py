import os
import sys
import subprocess

process = None

match os.name:
    case "posix":
        if not os.path.isdir("venv"):
            subprocess.run(["./venv.sh"])
    case "nt":
        if not os.path.isdir("venv"):
            subprocess.run(["venv.bat"])

match os.name:
    case "posix":
        pythonPath = "venv/bin/python"
    case "nt":
        pythonPath = "venv/Scripts/python.exe"

twtdlProc = [
    pythonPath,
    "twtdl.py",
]

if sys.argv[1:] is not None:
    twtdlProc.extend(sys.argv[1:])

subprocess.run(twtdlProc)
