import os
import sqlite3
import numpy as np
import pandas as pd
import re


mock_now = '2023-01-17 20:20:15'


class SqliteDB:
    def __init__(self, database_path=":memory:"):
        # create a sqlite connection
        self.cnx = sqlite3.connect(database_path)

    def mock_date_sql(self, sql: str):
        """
        convert sql date('now') to return date of the '2023-01-17 20:20:15'
        """
        sql = re.sub("(?i)\\bdate\\b\(\s*'now'", f"date('{mock_now}'", sql)
        return sql

    def read_sql(self, sql: str) -> pd.DataFrame:
        """
        pandas real_sql function wrap for mock date
        """
        sql = self.mock_date_sql(sql)
        return pd.read_sql(sql, self.cnx)

    @staticmethod
    def compare_df(out_df, ref_df):
        """
        compare two sql dataframe result and give a score
        find common columns based on column value rather than column name
        """
        common_col = []

        ref_column_indexes = list(range(len(ref_df.columns)))
        out_column_indexes = list(range(len(out_df.columns)))
        for ref_col_index in ref_column_indexes:
            # print(ref_col_index)
            ref_v = ref_df.iloc[:, ref_col_index]
            for out_col_index in out_column_indexes:

                # in case referenced data has no rows, we only compare the column headers
                if ref_df.shape[0] == 0:
                    if ref_df.columns[ref_col_index] == out_df.columns[out_col_index]:
                        common_col = common_col + [[ref_df.columns[ref_col_index], out_df.columns[out_col_index]]]
                        out_column_indexes.remove(out_col_index)
                        break
                else:
                    out_v = out_df.iloc[:, out_col_index]
                    try:
                        is_close = np.allclose(out_v.to_numpy(dtype=float, na_value=0), ref_v.to_numpy(dtype=float, na_value=0))
                    except:
                        is_close = False
                    if out_v.equals(ref_v) or is_close:
                        common_col = common_col + [[ref_df.columns[ref_col_index], out_df.columns[out_col_index]]]
                        out_column_indexes.remove(out_col_index)
                        break

        return common_col

    def evaluate_sql_result(self, sql, ref_df: pd.DataFrame, out_df: pd.DataFrame=None):
        """
        evaluate predicted sql with reference sql result (dataframe)
        """
        try:
            if out_df is None:
                out_df = self.read_sql(sql)

            # a special case, where both reference and predicted result are empty
            if ref_df.shape[1] == 0 and out_df.shape[1] == 0:
                precision, recall, f1 = 1, 1, 1
            elif ref_df.shape[1] == 0 and out_df.shape[1] > 0:
                precision, recall, f1 = 0, 0, 0
            elif ref_df.shape[1] > 0 and out_df.shape[1] == 0:
                precision, recall, f1 = 0, 0, 0
            elif ref_df.shape[0] != out_df.shape[0]:
                precision, recall, f1 = 0, 0, 0

            common_col = self.compare_df(out_df, ref_df)
            precision = len(common_col) / len(out_df.columns)
            recall = len(common_col) / len(ref_df.columns)
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) != 0 else 0
        except:
            # handle case where sql cannot be executed.
            precision, recall, f1 = 0, 0, 0

        return precision, recall, f1
