import streamlit

import streamlit.web.cli as stcli
import os, sys

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(".")

app_path = os.path.join(base_path, "app.py")

if __name__ == "__main__":
    sys.argv = [
        "streamlit",
        "run",
        app_path,
        "--global.developmentMode=false",
    ]
    sys.exit(stcli.main())
