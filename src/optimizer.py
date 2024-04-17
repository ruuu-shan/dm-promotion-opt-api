import pandas as pd
import pulp
from pandas import DataFrame


class DmPromotionProblem:
    """ダイレクトメールプロモーションの最適化問題を解くクラスです。

    Attributes:
        customer_df (DataFrame): 顧客データを含むDataFrame。
        prob_df (DataFrame): 顧客の訪問確率を含むDataFrame。
        # dm_2_price (int): プロモーションdm2のクーポン金額
        # dm_3_price (int): プロモーションdm3のクーポン金額
        name (str): この問題の名称。
        problem (pulp.LpProblem): 定式化された最適化問題。
    """

    def __init__(
        self,
        customer_df: DataFrame,
        prob_df: DataFrame,
        # プロモーションの金額しては今回はなし
        # dm_2_price: int,
        # dm_3_price: int,
        name: str = "DmPromotionProblem",
    ):
        self.customer_df = customer_df
        self.prob_df = prob_df
        # self.dm_2_price = dm_2_price
        # self.dm_3_price = dm_3_price
        self.name = name
        self.problem = self._formulate()

    def _formulate(self) -> pulp.LpProblem:
        """問題の定式化を行います。

        Returns:
            pulp.LpProblem: 定式化された最適化問題。
        """
        problem = pulp.LpProblem(name=self.name, sense=pulp.LpMaximize)

        # 会員IDのリスト
        I: list[str] = self.customer_df["customer_id"].to_list()

        # ダイレクトメールのパターンのリスト
        M: list[int] = [1, 2, 3]

        # （1）各会員に対してどのパターンのダイレクトメールを送付するかを決定
        xim = {}

        for i in I:
            for m in M:
                xim[i, m] = pulp.LpVariable(name=f"xim({i},{m})", cat="Binary")

        # （2）各会員に対して送付するダイレクトメールはいずれか1パターン
        for i in I:
            problem += pulp.lpSum(xim[i, m] for m in M) == 1

        keys = ["age_cat", "freq_cat"]
        cust_prob_df = pd.merge(self.customer_df, self.prob_df, on=keys)

        cust_prob_ver_df = cust_prob_df.rename(columns={"prob_dm1": 1, "prob_dm2": 2, "prob_dm3": 3}).melt(
            id_vars=["customer_id"], value_vars=[1, 2, 3], var_name="dm", value_name="prob"
        )
        Pim = cust_prob_ver_df.set_index(["customer_id", "dm"])["prob"].to_dict()

        # （3）クーポン付与による来客増加数を最大化
        problem += pulp.lpSum((Pim[i, m] - Pim[i, 1]) * xim[i, m] for i in I for m in [2, 3])

        # セグメントごとのダイレクトメール送付割合を保証
        Cm = {1: 0, 2: 1000, 3: 2000}

        problem += pulp.lpSum(Cm[m] * Pim[i, m] * xim[i, m] for i in I for m in [2, 3]) <= 1000000

        S: list[str] = self.prob_df["segment_id"].to_list()
        Ns: dict[str, int] = cust_prob_df.groupby("segment_id")["customer_id"].count().to_dict()
        Si: dict[str, str] = cust_prob_df.set_index("customer_id")["segment_id"].to_dict()

        for s in S:
            for m in M:
                problem += pulp.lpSum(xim[i, m] for i in I if Si[i] == s) >= 0.1 * Ns[s]

        # クラス変数として格納
        self.variables = xim
        self.indices = {"I": I, "M": M}
        return problem

    def solve(self) -> tuple[DataFrame, float]:
        """最適化問題を解き、結果をDataFrameで返します。

        Returns:
            DataFrame: 各会員に送るダイレクトメールのパターンを示すDataFrame。
        """
        # 最適化問題を解く
        status = self.problem.solve()
        print(f"ステータス: {pulp.LpStatus[status]}")

        xim = self.variables
        I, M = self.indices["I"], self.indices["M"]

        # 解をDataFrameにまとめる
        send_dm_df = pd.DataFrame(
            [[xim[i, m].value() for m in M] for i in I], columns=["send_prob_dm1", "send_prob_dm2", "send_prob_dm3"]
        )
        solution_df = pd.concat([self.customer_df[["customer_id", "age_cat", "freq_cat"]], send_dm_df], axis=1)
        opt_value = pulp.value(self.problem.objective)

        return solution_df, opt_value


if __name__ == "__main__":
    customer_df = pd.read_csv("../data/customers.csv")
    prob_df = pd.read_csv("../data/visit_probability.csv")

    prob = DmPromotionProblem(customer_df=customer_df, prob_df=prob_df)
    solution_df, opt_value = prob.solve()
