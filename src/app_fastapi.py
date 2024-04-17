"""
最適化問題を解き、最適化結果を返すAPI

```
# Install uvicorn
$ pip install "uvicorn[standard]"
```

```
# Run FastAPI server
$ uvicorn app_fastapi:app --workers 4
```

```
$ curl -X POST \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d @resource/request_fastapi.json \
    http://127.0.0.1:8000/api
```
"""

import pandas as pd
import uvicorn
from fastapi import FastAPI
from optimizer import DmPromotionProblem
from pydantic import BaseModel

app = FastAPI()


class Customer(BaseModel):
    customer_id: int
    age_cat: str
    freq_cat: str


class Prob(BaseModel):
    age_cat: str
    freq_cat: str
    segment_id: int
    prob_dm1: float
    prob_dm2: float
    prob_dm3: float


class Solution(BaseModel):
    customer_id: int
    age_cat: str
    freq_cat: str
    prob_dm1: float
    prob_dm2: float
    prob_dm3: float


def preprocess(customer_data: list[dict], prob_data: list[dict]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    顧客データと問題データのリストをPandasのDataFrameに変換します。

    引数:
        customer_data (list[dict]): 顧客情報を含む辞書のリスト。
        prob_data (list[dict]): 問題パラメータを含む辞書のリスト。

    戻り値:
        Tuple[pd.DataFrame, pd.DataFrame]: 顧客データと問題データのDataFrameを含むタプル。
    """
    customer_df = pd.DataFrame(customer_data)
    prob_df = pd.DataFrame(prob_data)
    return customer_df, prob_df


def postprocess(solution_df: pd.DataFrame) -> list[dict]:
    """
    解のDataFrameをJSONレスポンスに適した辞書のリストに変換します。

    引数:
        solution_df (pd.DataFrame): 解を含むDataFrame。

    戻り値:
        list[dict]: 解を含む辞書のリスト。
    """
    return solution_df.to_dict(orient="records")


@app.post("/api")
def solve(students: list[Customer], cars: list[Prob]) -> list[Solution]:
    """
    与えられた顧客と問題データを元に最適化問題を解きます。

    引数:
        students (list[Customer]): 顧客情報を持つCustomerオブジェクトのリスト。
        cars (list[Prob]): 問題情報を持つProbオブジェクトのリスト。

    戻り値:
        list[Solution]: 解の情報を持つSolutionオブジェクトのリスト。
    """
    customers = [s.dict() for s in students]
    probs = [c.dict() for c in cars]
    customers_df, probs_df = preprocess(customers, probs)
    solution_df = DmPromotionProblem(customers_df, probs_df).solve()
    solution_dicts = postprocess(solution_df)
    return [Solution(**sol) for sol in solution_dicts]
    return postprocess(solution_df)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
