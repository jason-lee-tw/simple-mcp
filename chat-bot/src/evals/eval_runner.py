import os
import sys

from dotenv import load_dotenv
from phoenix.client import Client

load_dotenv()
from phoenix.evals import LLM, ClassificationEvaluator, evaluate_dataframe
from phoenix.evals.utils import to_annotation_dataframe

HALLUCINATION_PROMPT = (
    "Given the following question and answer, determine whether the answer "
    "contains hallucinations (fabricated information presented as fact).\n\n"
    "Question: {input}\nAnswer: {output}\n\n"
    "Respond with 'hallucinated' if the answer contains fabricated information, "
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

    hallucination_evaluator = ClassificationEvaluator(
        name='Hallucination',
        llm=model,
        prompt_template=HALLUCINATION_PROMPT,
        choices={'hallucinated': 0.0, 'not hallucinated': 1.0},
    )
    qa_evaluator = ClassificationEvaluator(
        name='QA Correctness',
        llm=model,
        prompt_template=QA_PROMPT,
        choices={'correct': 1.0, 'incorrect': 0.0},
    )

    eval_df = spans_df.rename(columns={
        'attributes.input.value': 'input',
        'attributes.output.value': 'output',
    })

    hallucination_evals = evaluate_dataframe(
        dataframe=eval_df,
        evaluators=[hallucination_evaluator],
    )
    qa_evals = evaluate_dataframe(
        dataframe=eval_df,
        evaluators=[qa_evaluator],
    )

    for evals_df, name in [(hallucination_evals, 'Hallucination'), (qa_evals, 'QA Correctness')]:
        try:
            client.spans.log_span_annotations_dataframe(dataframe=to_annotation_dataframe(evals_df, score_names=[name]))
        except Exception as e:
            print(f'Warning: could not log {name} annotations to Phoenix: {e}')

    print(f'Evaluated {len(spans_df)} spans. Results logged to Phoenix at {phoenix_base_url}')


if __name__ == '__main__':
    main()
