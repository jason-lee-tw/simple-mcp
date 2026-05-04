from unittest.mock import patch
from main import main


def test_main_starts_uvicorn():
    with patch("main.uvicorn.run") as mock_run:
        main()
        mock_run.assert_called_once()
