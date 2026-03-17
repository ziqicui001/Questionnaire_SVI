#python D:\AAG\Questionnaire_SVI\dataprocess\csvprocess.py

import pandas as pd
from pathlib import Path
import random
import string


def make_suffix(length: int = 4) -> str:
    """Generate a short random uppercase alphanumeric suffix."""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=length))


def build_record_id(query_id: str, idx: int) -> str:
    """
    Build a readable unique record ID for pooled annotation items.
    Example: Q01_POOL_0001_A7K2
    """
    return f"{query_id}_POOL_{idx:04d}_{make_suffix(4)}"


def main():
    # ====== 修改这里 ======
    input_csv = r"D:\AAG\Questionnaire_SVI\dataprocess\merged_union_by_panoid_yaw.csv"
    queries_csv = r"D:\AAG\Questionnaire_SVI\web\queries.csv"
    output_csv = r"D:\AAG\Questionnaire_SVI\web\annotation_items.csv"

    query_id = "Q01"

    # 为了让 display_order 和 record_id 可复现，固定随机种子
    random_seed = 42
    # =====================

    random.seed(random_seed)

    # 读取 pooled 结果表
    df = pd.read_csv(input_csv)

    # 读取 queries.csv，获取 query_text
    qdf = pd.read_csv(queries_csv)

    if "query_id" not in qdf.columns or "query_text" not in qdf.columns:
        raise ValueError("queries.csv 必须包含列: query_id, query_text")

    match = qdf.loc[qdf["query_id"] == query_id, "query_text"]
    if match.empty:
        raise ValueError(f"queries.csv 中未找到 query_id={query_id} 对应的 query_text")

    query_text = match.iloc[0]

    # 检查必要列
    required_cols = ["pano_id", "best_view_path"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"原始 CSV 缺少必要列: {missing}")

    # 找出所有方法标记列，例如 top_20_M1, top_20_M2...
    method_cols = [c for c in df.columns if c.startswith("top_20_")]
    if len(method_cols) == 0:
        raise ValueError("未找到任何方法标记列，例如 top_20_M1, top_20_M2 ...")

    # 如果你只想保留至少被一个方法命中的图像，可以加这个过滤
    # 例如某一行 top_20_M1~M5 全是空或0，则去掉
    mask = df[method_cols].fillna(0).astype(str).apply(
        lambda row: any(v.strip() not in ["", "0", "0.0"] for v in row),
        axis=1
    )
    df = df[mask].copy().reset_index(drop=True)

    # 新字段
    df["query_id"] = query_id
    df["query_text"] = query_text
    df["image_path"] = df["best_view_path"]
    df["image_file_name"] = df["best_view_path"].apply(lambda x: Path(str(x)).name)

    # 生成 record_id
    df["record_id"] = [
        build_record_id(query_id=query_id, idx=i + 1)
        for i in range(len(df))
    ]

    # 随机生成 display_order
    shuffled_indices = list(range(1, len(df) + 1))
    random.shuffle(shuffled_indices)
    df["display_order"] = shuffled_indices

    # 输出列顺序
    preferred_cols = [
        "record_id",
        "query_id",
        "query_text",
        "display_order",
        "pano_id",
        "best_yaw",
        "image_path",
        "image_file_name",
    ] + method_cols + [
        "best_view_path",
    ]

    final_cols = [c for c in preferred_cols if c in df.columns] + [
        c for c in df.columns if c not in preferred_cols
    ]

    df_out = df[final_cols]

    # 导出
    df_out.to_csv(output_csv, index=False, encoding="utf-8-sig")

    print(f"Saved: {output_csv}")
    print(f"Rows: {len(df_out)}")
    print("Columns:")
    print(df_out.columns.tolist())


if __name__ == "__main__":
    main()