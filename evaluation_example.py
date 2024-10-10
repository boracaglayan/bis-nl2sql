
import pandas as pd
import sqlglot
from sqlglot import diff, parse_one
from sqlglot.diff import Keep, Move
import sqlite_conn


def calculate_semantic_similarity_s2(q1, q2):
    # this strategy reweighs the diff tree for different types of changes, table change== 0 similarity
    # alias change no penalty
    a1 = parse_one(q1)
    a2 = parse_one(q2)
    total_diff = diff(a1, a2)
    only_diff = [d for d in total_diff if not(isinstance(d, Keep) or isinstance(d, Move))]
    # table diff
    if any(isinstance(d.expression, sqlglot.expressions.Table) for d in only_diff):
        return 0
    # no alias change
    alias_diff = [d for d in only_diff if "alias" in str(d).lower()]
    only_diff = [d for d in  only_diff if "alias" not in str(d).lower()]
    for ad in alias_diff:
        only_diff = [d for d in only_diff if str(ad).lower() not in str(alias_diff).lower()]

    return (len(total_diff) - len(only_diff)) / len(total_diff)


if __name__ == "__main__":
    """
    evaluate a predicted sql for question 1 based on sql result to get a score
    """

    questions_benchmark = pd.read_json("./dataset1/questions_dataset_1.json")

    # load database
    sqldb = sqlite_conn.SqliteDB("./dataset1/dataset_1.sqlite3")

    # this is the predicted sql by our model.
    predicted_sql = '''
        select count(*) as test from pre_ranking_filter_log where task=342111 and filter_key = 'o_rta_filter'
        '''

    # this is the reference sql in the dataset.
    reference_sql = questions_benchmark["query"].iloc[0]
    reference_df = sqldb.read_sql(reference_sql)

    # semantic similarity of queries
    semantic_similarity = calculate_semantic_similarity_s2(predicted_sql, reference_sql)
    print(f"sample result, semantic similarity: {semantic_similarity}")

    # get the evaluation score
    precision, recall, f1 = sqldb.evaluate_sql_result(predicted_sql, reference_df)
    print(f"sample result, Precision: {precision}, Recall: {recall}, F1 score: {f1}")

