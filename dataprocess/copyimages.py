import shutil
from pathlib import Path
import pandas as pd


def make_unique_path(dst_path: Path) -> Path:
    """
    如果目标文件已存在，则自动加后缀避免覆盖。
    例如:
    img.jpg -> img_1.jpg -> img_2.jpg
    """
    if not dst_path.exists():
        return dst_path

    stem = dst_path.stem
    suffix = dst_path.suffix
    parent = dst_path.parent

    counter = 1
    while True:
        candidate = parent / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def main():
    # ====== 修改这里 ======
    input_csv = r"D:\AAG\Human\web\test.csv"
    output_csv = r"D:\AAG\Human\web\test02.csv"
    images_dir = r"D:\AAG\Human\web\images"
    image_col = "image_path"
    web_col = "web_path"
    # =====================

    input_csv = Path(input_csv)
    output_csv = Path(output_csv)
    images_dir = Path(images_dir)

    images_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(input_csv)

    if image_col not in df.columns:
        raise ValueError(f"CSV 中不存在列: {image_col}")

    web_paths = []
    copy_status = []
    copied_count = 0
    missing_count = 0

    for idx, row in df.iterrows():
        src = Path(str(row[image_col])).expanduser()

        if not src.exists():
            print(f"[Missing] Row {idx}: {src}")
            web_paths.append("")
            copy_status.append("missing")
            missing_count += 1
            continue

        # 目标文件路径
        dst = images_dir / src.name
        dst = make_unique_path(dst)

        try:
            shutil.copy2(src, dst)
            copied_count += 1

            # 记录相对 web 路径，统一用正斜杠更适合网页
            rel_path = Path("images") / dst.name
            web_paths.append(rel_path.as_posix())
            copy_status.append("copied")

            print(f"[Copied] {src} -> {dst}")

        except Exception as e:
            print(f"[Error] Row {idx}: {src} | {e}")
            web_paths.append("")
            copy_status.append(f"error: {e}")

    df[web_col] = web_paths
    df["copy_status"] = copy_status

    df.to_csv(output_csv, index=False, encoding="utf-8-sig")

    print("\nDone.")
    print(f"Output CSV: {output_csv}")
    print(f"Images folder: {images_dir}")
    print(f"Copied: {copied_count}")
    print(f"Missing: {missing_count}")
    print(f"Total rows: {len(df)}")


if __name__ == "__main__":
    main()