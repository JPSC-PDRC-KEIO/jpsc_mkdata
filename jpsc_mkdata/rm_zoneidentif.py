"""
zoneidentifierの拡張子をとる
"""
import os

for curDir, dirs, files in os.walk("./"):
    for file_ in files:
        if file_.endswith(".Identifier"):
            os.remove(os.path.join(curDir, file_))
