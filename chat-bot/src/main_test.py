from unittest.mock import patch

from main import main


def test_main_starts_uvicorn():
    with patch('main.uvicorn.run') as mock_run, \
         patch('main.register_phoenix_tracer'):
        main()
        mock_run.assert_called_once()


def test_main_registers_phoenix_tracer():
    with patch('main.uvicorn.run'), \
         patch('main.register_phoenix_tracer') as mock_tracer:
        main()
        mock_tracer.assert_called_once()
