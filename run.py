import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from gesture_face_ai.main import main


if __name__ == "__main__":
    main()
