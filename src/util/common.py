import rasterio as rio
from pyproj import Transformer
from skimage import exposure
import numpy as np
import matplotlib.pyplot as plt
import numpy.ma as ma

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