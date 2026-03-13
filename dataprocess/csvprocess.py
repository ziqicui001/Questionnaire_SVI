import pandas as pd
from pathlib import Path
import random
import string


def make_suffix(length: int = 4) -> str:
    """Generate a short random uppercase alphanumeric suffix."""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=length))


def build_record_id(query_id: str, method: str, idx: int) -> str:
    """
    Build a readable unique record ID.
    Example: Q01_CLIP_0001_A7K2
    """
    method_clean = ''.join(ch for ch in method.upper() if ch.isalnum())
    return f"{query_id}_{method_clean}_{idx:04d}_{make_suffix(4)}"


def main():
    # ====== 修改这里 ======
    input_csv = r"D:\AAG\Human\bench_prompts_pano_ranked_baseline_q99.csv"
    queries_csv = r"D:\AAG\Human\queries.csv"
    output_csv = r"D:\AAG\Human\annotation_items.csv"

    query_id = "Q01"
    method_name = "CLIP"

    # 为了让 display_order 和 record_id 可复现，固定随机种子
    random_seed = 42
    # =====================

    random.seed(random_seed)

    # 读取原始结果表
    df = pd.read_csv(input_csv)

    # 读取 queries.csv，获取 Q01 对应的 query_text
    qdf = pd.read_csv(queries_csv)

    if "query_id" not in qdf.columns or "query_text" not in qdf.columns:
        raise ValueError("queries.csv 必须包含列: query_id, query_text")

    match = qdf.loc[qdf["query_id"] == query_id, "query_text"]
    if match.empty:
        raise ValueError(f"queries.csv 中未找到 query_id={query_id} 对应的 query_text")

    query_text = match.iloc[0]

    # 检查原始列
    required_cols = ["rank", "pano_id", "best_view_path"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"原始 CSV 缺少必要列: {missing}")

    # 新字段
    df["query_id"] = query_id
    df["query_text"] = query_text
    df["method"] = method_name
    df["orig_rank"] = df["rank"]
    df["image_path"] = df["best_view_path"]
    df["image_file_name"] = df["best_view_path"].apply(lambda x: Path(str(x)).name)

    # 可选映射字段
    if "best_view_score" in df.columns:
        df["source_score"] = df["best_view_score"]
    else:
        df["source_score"] = pd.NA

    if "prompt_best" in df.columns:
        df["source_prompt"] = df["prompt_best"]
    else:
        df["source_prompt"] = pd.NA

    # 生成 record_id（按原始 rank 排序后生成，更稳定）
    df = df.sort_values("orig_rank").reset_index(drop=True)
    df["record_id"] = [
        build_record_id(query_id=query_id, method=method_name, idx=i + 1)
        for i in range(len(df))
    ]

    # 生成随机 display_order
    shuffled_indices = list(range(1, len(df) + 1))
    random.shuffle(shuffled_indices)
    df["display_order"] = shuffled_indices

    # 建议输出列顺序
    preferred_cols = [
        "record_id",
        "query_id",
        "query_text",
        "method",
        "orig_rank",
        "display_order",
        "pano_id",
        "image_path",
        "image_file_name",
        "source_score",
        "source_prompt",
        "best_yaw",
        "lng",
        "lat",
        "num_views",
        "num_views_above_thresh",
        # 保留原始字段
        "rank",
        "best_view_path",
        "best_view_score",
        "prompt_best",
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