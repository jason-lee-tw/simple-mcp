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
         patch('evals.eval_runner.ClassificationEvaluator'), \
         patch('evals.eval_runner.evaluate_dataframe', return_value=mock_evals_result), \
         patch('evals.eval_runner.to_annotation_dataframe', return_value=pd.DataFrame()), \
         patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
        main()
    assert mock_client.spans.log_span_annotations_dataframe.call_count == 2


def test_evaluate_dataframe_receives_columns_renamed_from_phoenix_attributes():
    import pandas as pd
    mock_spans_df = pd.DataFrame({
        'attributes.input.value': ['question 1', 'question 2'],
        'attributes.output.value': ['answer 1', 'answer 2'],
    })
    mock_client = MagicMock()
    mock_client.spans.get_spans_dataframe.return_value = mock_spans_df

    captured_dfs = []

    def capture_evaluate(dataframe, evaluators):
        captured_dfs.append(dataframe.copy())
        return pd.DataFrame()

    with patch('evals.eval_runner.Client', return_value=mock_client), \
         patch('evals.eval_runner.LLM'), \
         patch('evals.eval_runner.ClassificationEvaluator'), \
         patch('evals.eval_runner.evaluate_dataframe', side_effect=capture_evaluate), \
         patch('evals.eval_runner.to_annotation_dataframe', return_value=pd.DataFrame()), \
         patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
        main()

    assert len(captured_dfs) == 2
    for df in captured_dfs:
        assert 'input' in df.columns, "evaluate_dataframe must receive 'input' column"
        assert 'output' in df.columns, "evaluate_dataframe must receive 'output' column"
        assert 'attributes.input.value' not in df.columns
        assert 'attributes.output.value' not in df.columns


def test_hallucination_prompt_does_not_use_reference_placeholder():
    from evals.eval_runner import HALLUCINATION_PROMPT
    assert '{reference}' not in HALLUCINATION_PROMPT, (
        "HALLUCINATION_PROMPT must not use {reference} — no retrieval context exists in these spans"
    )


def test_log_span_annotations_receives_dataframe_with_label_score_explanation():
    import pandas as pd
    mock_spans_df = pd.DataFrame({
        'attributes.input.value': ['q1'],
        'attributes.output.value': ['a1'],
    })
    mock_client = MagicMock()
    mock_client.spans.get_spans_dataframe.return_value = mock_spans_df

    mock_evals_result = pd.DataFrame({
        'context.span_id': ['span-abc'],
        'Hallucination_score': [{'name': 'Hallucination', 'score': 1.0, 'label': 'not hallucinated', 'explanation': 'looks fine', 'kind': 'llm'}],
        'QA Correctness_score': [{'name': 'QA Correctness', 'score': 1.0, 'label': 'correct', 'explanation': 'correct', 'kind': 'llm'}],
    }).set_index('context.span_id')

    logged_dfs = []

    def capture_log(dataframe, **kwargs):
        logged_dfs.append(dataframe.copy())

    mock_client.spans.log_span_annotations_dataframe.side_effect = capture_log

    with patch('evals.eval_runner.Client', return_value=mock_client), \
         patch('evals.eval_runner.LLM'), \
         patch('evals.eval_runner.ClassificationEvaluator'), \
         patch('evals.eval_runner.evaluate_dataframe', return_value=mock_evals_result), \
         patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
        main()

    assert len(logged_dfs) == 2
    for df in logged_dfs:
        assert 'label' in df.columns or 'score' in df.columns or 'explanation' in df.columns, (
            "log_span_annotations_dataframe must receive a dataframe with label, score, or explanation columns"
        )


def test_main_prints_warning_and_continues_when_logging_to_phoenix_times_out(capsys):
    import pandas as pd
    mock_spans_df = pd.DataFrame({
        'attributes.input.value': ['q1'],
        'attributes.output.value': ['a1'],
    })
    mock_client = MagicMock()
    mock_client.spans.get_spans_dataframe.return_value = mock_spans_df
    mock_client.spans.log_span_annotations_dataframe.side_effect = Exception('timed out')

    with patch('evals.eval_runner.Client', return_value=mock_client), \
         patch('evals.eval_runner.LLM'), \
         patch('evals.eval_runner.ClassificationEvaluator'), \
         patch('evals.eval_runner.evaluate_dataframe', return_value=pd.DataFrame()), \
         patch('evals.eval_runner.to_annotation_dataframe', return_value=pd.DataFrame()), \
         patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
        main()

    captured = capsys.readouterr()
    assert 'Warning' in captured.out or 'warning' in captured.out.lower() or 'timed out' in captured.out, (
        "When logging to Phoenix times out, main should print a warning instead of crashing"
    )


def test_evaluators_passed_to_evaluate_dataframe_are_classification_evaluators():
    import pandas as pd
    from phoenix.evals import ClassificationEvaluator
    mock_spans_df = pd.DataFrame({
        'attributes.input.value': ['q1'],
        'attributes.output.value': ['a1'],
    })
    mock_client = MagicMock()
    mock_client.spans.get_spans_dataframe.return_value = mock_spans_df

    captured_evaluators = []

    def capture_evaluate(dataframe, evaluators):
        captured_evaluators.extend(evaluators)
        return pd.DataFrame()

    with patch('evals.eval_runner.Client', return_value=mock_client), \
         patch('evals.eval_runner.LLM'), \
         patch('evals.eval_runner.evaluate_dataframe', side_effect=capture_evaluate), \
         patch('evals.eval_runner.to_annotation_dataframe', return_value=pd.DataFrame()), \
         patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
        main()

    assert len(captured_evaluators) == 2
    for evaluator in captured_evaluators:
        assert isinstance(evaluator, ClassificationEvaluator), (
            f"Expected ClassificationEvaluator, got {type(evaluator).__name__}. "
            "LLMEvaluator is abstract and raises NotImplementedError on _evaluate."
        )
