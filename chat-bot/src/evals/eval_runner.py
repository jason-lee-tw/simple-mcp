import os
import sys

from phoenix.client import Client
from phoenix.evals import LLM, LLMEvaluator, evaluate_dataframe

HALLUCINATION_PROMPT = (
    "Given the following question, context, and answer, determine whether the answer "
    "contains hallucinations (information not supported by the context).\n\n"
    "Question: {input}\nContext: {reference}\nAnswer: {output}\n\n"
    "Respond with 'hallucinated' if the answer contains unsupported information, "
    "or 'not hallucinated' otherwise."
)

QA_PROMPT = (
    "Given the following question and answer, determine whether the answer correctly "
    "addresses the question.\n\n"
    "Question: {input}\nAnswer: {output}\n\n"
    "Respond with 'correct' if the answer correctly addresses the question, "
    "or 'incorrect' otherwise."
)


def main():
    phoenix_base_url = os.getenv('PHOENIX_BASE_URL', 'http://localhost:6006')
    api_key = os.environ.get('ANTHROPIC_API_KEY')

    if not api_key:
        print('Error: ANTHROPIC_API_KEY environment variable is required', file=sys.stderr)
        sys.exit(1)

    client = Client(base_url=phoenix_base_url)

    try:
        spans_df = client.spans.get_spans_dataframe(project_name='chat-bot')
    except Exception as e:
        print(f'Error: could not connect to Phoenix at {phoenix_base_url}: {e}', file=sys.stderr)
        sys.exit(1)

    if spans_df is None or spans_df.empty:
        print('No spans found. Send some chat requests first, then re-run.')
        return

    model = LLM(
        provider='anthropic',
        model='claude-sonnet-4-6',
        sync_client_kwargs={'api_key': api_key},
    )

    # LLMEvaluator measures whether the response correctly answers the user's question.
    hallucination_evaluator = LLMEvaluator(
        name='Hallucination',
        llm=model,
        prompt_template=HALLUCINATION_PROMPT,
    )
    qa_evaluator = LLMEvaluator(
        name='QA Correctness',
        llm=model,
        prompt_template=QA_PROMPT,
    )

    hallucination_evals = evaluate_dataframe(
        dataframe=spans_df,
        evaluators=[hallucination_evaluator],
    )
    qa_evals = evaluate_dataframe(
        dataframe=spans_df,
        evaluators=[qa_evaluator],
    )

    client.spans.log_span_annotations_dataframe(dataframe=hallucination_evals, annotation_name='Hallucination', annotator_kind='LLM')
    client.spans.log_span_annotations_dataframe(dataframe=qa_evals, annotation_name='QA Correctness', annotator_kind='LLM')

    print(f'Evaluated {len(spans_df)} spans. Results logged to Phoenix at {phoenix_base_url}')


if __name__ == '__main__':
    main()
