"""
Streamlitによる最適化WEBアプリケーション

```
$ pip install streamlit
```

```
$ streamlit run application_streamlit.py
```
"""

import pandas as pd
import streamlit as st
from optimizer import DmPromotionProblem


def preprocess(customer: str, prob: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    顧客と問題データのファイルパスを受け取り、それぞれをPandasのDataFrameに読み込む。

    Args:
        customer (str): 顧客データファイルのパス。
        prob (str): 問題データファイルのパス。

    Returns:
        tuple[pd.DataFrame, pd.DataFrame]: 顧客データと問題データのDataFrameのタプル。
    """
    customer_df = pd.read_csv(customer)
    prob_df = pd.read_csv(prob)

    return customer_df, prob_df


def convert_to_csv(df: pd.DataFrame) -> bytes:
    """
    DataFrameをCSV形式に変換し、バイト列としてエンコードする。

    Args:
        df (pd.DataFrame): CSVに変換するデータフレーム。

    Returns:
        bytes: エンコードされたCSVデータ。
    """
    return df.to_csv(index=False).encode("utf-8")


# 画面を二分割する（画面の左側をファイルアップロード、右側を最適化結果の表示とする）
# col1: 左側、col2: 右側
col1, col2 = st.columns(2)

# 画面の左側の実装
with col1:
    # ファイルアップロードのフィールド
    customer = st.file_uploader("顧客データ", type="csv")
    prob = st.file_uploader("来店確率データ", type="csv")
    # 全てのデータがアップロードされたら以降のUIを表示（studentsとcarsはファイルアップロードがされていない場合はNoneとなり、以下UIの表示はしない）
    if customer is not None and prob is not None:
        # 最適化ボタンの表示
        if st.button("最適化を実行"):
            # 最適化ボタンが押されたら最適化を実行
            # 前処理（データ読み込み）
            customer_df, prob_df = preprocess(customer, prob)  # noqa
            # 最適化実行
            solution_df, opt_value = DmPromotionProblem(customer_df=customer_df, prob_df=prob_df).solve()
            # 画面の右側にダウンロードボタンと最適化結果を表示する
            with col2:
                st.write("#### 最適化結果")
                st.write("クーポン付きのDM送付による増加UU：", opt_value)
                # ダウンロードボタンの表示
                csv = convert_to_csv(solution_df)
                st.download_button("Press to Download", csv, "solution.csv", "text/csv", key="download-csv")
                # 最適化結果の表示
                st.write(solution_df)
