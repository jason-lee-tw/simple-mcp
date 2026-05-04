import sys
from unittest.mock import MagicMock, patch

import pytest

from evals.eval_runner import main


def test_main_exits_when_api_key_missing():
    with patch.dict('os.environ', {}, clear=True), \
         pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 1


def test_main_exits_when_phoenix_unreachable():
    mock_client = MagicMock()
    mock_client.spans.get_spans_dataframe.side_effect = Exception('connection refused')
    with patch('evals.eval_runner.Client', return_value=mock_client), \
         patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}), \
         pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 1


def test_main_prints_message_when_no_spans(capsys):
    mock_client = MagicMock()
    mock_client.spans.get_spans_dataframe.return_value = None
    with patch('evals.eval_runner.Client', return_value=mock_client), \
         patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
        main()
    captured = capsys.readouterr()
    assert 'No spans found' in captured.out


def test_main_runs_evals_and_logs_results():
    import pandas as pd
    mock_spans_df = pd.DataFrame({'col': [1, 2, 3]})
    mock_client = MagicMock()
    mock_client.spans.get_spans_dataframe.return_value = mock_spans_df
    mock_evals_result = pd.DataFrame()
    with patch('evals.eval_runner.Client', return_value=mock_client), \
         patch('evals.eval_runner.LLM'), \
         patch('evals.eval_runner.LLMEvaluator'), \
         patch('evals.eval_runner.evaluate_dataframe', return_value=mock_evals_result), \
         patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
        main()
    assert mock_client.spans.log_span_annotations_dataframe.call_count == 2
