from pathlib import Path
import runpy


ROOT_DASHBOARD = Path(__file__).resolve().parents[2] / "dashboard.py"
runpy.run_path(str(ROOT_DASHBOARD), run_name="__main__")
