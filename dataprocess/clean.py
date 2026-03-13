# python D:\AAG\Human\clean.py

import pandas as pd

# ====== 修改这里 ======
input_csv = r"D:\AAG\Human\annotation_items.csv"
output_csv = r"D:\AAG\Human\annotation_items_clean.csv"
# =====================

# 读取
df = pd.read_csv(input_csv)

# 想保留的核心列顺序
keep_cols = [
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
]

# 只保留当前文件里实际存在的列
final_cols = [c for c in keep_cols if c in df.columns]

# 清理后的表
df_clean = df[final_cols].copy()

# ===== 基本检查 =====
print("原始行数:", len(df))
print("清理后行数:", len(df_clean))
print("清理后列名:")
print(df_clean.columns.tolist())

# 检查 record_id 是否唯一
if "record_id" in df_clean.columns:
    is_unique_record = df_clean["record_id"].is_unique
    print("record_id 是否唯一:", is_unique_record)
    if not is_unique_record:
        dup = df_clean[df_clean["record_id"].duplicated(keep=False)].sort_values("record_id")
        print("\n重复的 record_id 如下：")
        print(dup[["record_id"]].drop_duplicates())

# 检查 display_order 是否唯一
if "display_order" in df_clean.columns:
    is_unique_order = df_clean["display_order"].is_unique
    print("display_order 是否唯一:", is_unique_order)
    if not is_unique_order:
        dup = df_clean[df_clean["display_order"].duplicated(keep=False)].sort_values("display_order")
        print("\n重复的 display_order 如下：")
        print(dup[["display_order"]].drop_duplicates())

# 可选：按 display_order 排序导出，方便后面检查
if "display_order" in df_clean.columns:
    df_clean = df_clean.sort_values("display_order").reset_index(drop=True)

# 导出
df_clean.to_csv(output_csv, index=False, encoding="utf-8-sig")

print(f"\n已保存清理后的文件{output_csv}")