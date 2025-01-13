""" common.py
"""

import numpy as np
import matplotlib.pyplot as plt
import numpy.ma as ma
import rasterio as rio
import matplotlib.pyplot as plt
import numpy as np
import re
import os
from skimage import exposure
from pyproj import Transformer


def rgb_plot(rgb_data, title=None):
    plt.figure(figsize=(10, 8))
    plt.imshow(rgb_data, cmap='RdYlGn')
    plt.title(title, fontsize=15)
    plt.axis("off")
    plt.show()

# 緯度軽度をピクセル座標に変換する関数
def latlon_to_pixel(lat, lon, raster):
    transformer = Transformer.from_crs('EPSG:4326', raster.crs, always_xy=True)
    x, y = transformer.transform(lon, lat)
    row, col = raster.index(x, y)
    return row, col

# ピクセル(row, col)の周辺を抽出する関数
def extract_window_from_img(raster, row, col, window_size):
    row_start = max(0, row - window_size)
    row_end = min(raster.height, row + window_size)
    col_start = max(0, col - window_size)
    col_end = min(raster.width, col + window_size)
    return raster.read([1, 2, 3])[:, row_start:row_end, col_start:col_end].transpose(1, 2, 0).astype('float')

# ピクセル(row, col)の周辺を抽出する関数
def extract_window_from_band(raster, row, col, window_size):
    row_start = max(0, row - window_size)
    row_end = min(raster.height, row + window_size)
    col_start = max(0, col - window_size)
    col_end = min(raster.width, col + window_size)
    return raster.read(1)[row_start:row_end, col_start:col_end].astype('float')

# 正規化してヒストグラム均等化を行う関数
def normalize_and_histeq(data):
    data_norm = (data - np.nanmin(data)) / (np.nanmax(data) - np.nanmin(data))
    # nanがる場合は0で埋める
    if np.isnan(data_norm).any():
        data_norm = ma.masked_invalid(data).filled(0)
    return exposure.equalize_hist(data_norm)

def list_buckets(s3_client):
    try:
        response = s3_client.list_buckets()
        print("S3 Buckets:")
        for bucket in response['Buckets']:
            print(f"  - {bucket['Name']}")
    except Exception as e:
        print(f"Error listing buckets: {e}")

def get_filelist(s3_client, s3_bucket, prefix):
    response = s3_client.list_objects_v2(Bucket=s3_bucket, Prefix=prefix)
    # ファイル一覧を表示
    file_list = []
    if 'Contents' in response:
        for obj in response['Contents']:
            file_list.append(obj['Key'])
    return file_list

def extract_date(file_path):
    # ファイル名を取得
    file_name = file_path.split("/")[-1]

    # 正規表現で日付を抽出 (YYYYMMDD の形式を検索)
    match = re.search(r"_(\d{8})T", file_name)
    if match:
        date_str = match.group(1)  # YYYYMMDD の部分を取得
        return date_str
    else:
        return None

def s3_upload(s3_client, s3_bucket, output_path, data, meta):
    local_file_path = "./tmp/" + os.path.basename(output_path)
    with rio.open(local_file_path, "w", **meta) as dst:
        dst.write(data.astype(rio.float32), 1)
    s3_client.upload_file(local_file_path, s3_bucket, output_path)
    os.remove(local_file_path)

def get_mask(s3_client, s3_bucket, prefix):
    # ファイル一覧を入手
    file_list = get_filelist(s3_client, s3_bucket, prefix)

    # 条件に一致するファイルを抽出
    files = [path for path in file_list if "_B03" in path]

    mask = rio.open('s3://' + s3_bucket + '/' + files[1])
    meta = mask.meta.copy()
    meta.update({
        "count": 1,  # 出力バンド数
        "dtype": "float32",
    })

    mask = mask.read(1).astype(np.float16)

    return mask
