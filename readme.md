## File definitions

Dataset1 is business operation dataset for AD task management.

Dataset2 is smaller operations data and for system operation and infrastructure management.

Files:
1 - *.sqlite3 for sqlite database with sample data
2 - questions_*.json for questions and queries
3 - tables_*.json for schema information.

Check evaluation_example.py to see a sample method for evaluating the sql results.

## Date time information

Date range of the dataset is from 2023-01-02 to 2023-01-17 to test relevant date.

The first day of a week is monday. For example, "last week" means from 2023-01-09 to 2023-01-15

| Monday     | Tuesday    | ... | Sunday     |
|------------|------------|-----|------------|
| 2023-01-02 | ..         |     | 2023-01-08 |
| 2023-01-09 | ..         |     | 2023-01-15 |
| 2023-01-16 | 2023-01-17 |     |            |

Current date or Today should be set on 2023-01-17 to test condition query such as "What is the filter count today?"