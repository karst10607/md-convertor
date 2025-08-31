# MD Converter v1.0

Confluence HTML Pack → Markdown Converter

將 Confluence HTML 匯出包轉換為 Markdown 檔案，同時保留圖片檔案路徑（不複製圖片）。內部連結從 `.html` 重寫為 `.md`，並調整相對路徑。

## 功能特色

- 提取主要內容（嘗試常見的 Confluence 容器；可透過 CSS 選擇器配置）
- 保留圖片 `src` 路徑，重新計算相對於每個輸出 `.md` 檔案的路徑
- 重寫內部 `.html` 連結為 `.md`，保留查詢字串和片段
- 保持外部連結（http/https/mailto/tel/data）不變
- 在輸出中鏡像輸入目錄結構

## 系統需求

- Python 3.10+
- 安裝相依套件：

```bash
# 使用 Conda（推薦）
conda env create -f environment.yml
conda activate mdconv

# 或使用 pip
pip install -r requirements.txt
```

## 使用方式

### GUI 介面（推薦）
```bash
conda activate mdconv
python gui_tk.py
```

### 命令列介面
```bash
python convert_confluence_html.py -i /path/to/html-pack -o /path/to/output-md
```

可選：指定主要內容的 CSS 選擇器：
```bash
python convert_confluence_html.py -i ./export -o ./md --main-selector '#main-content'
```

## 檔案說明

- `convert_confluence_html.py` — 主要轉換器
- `gui_tk.py` — Tkinter GUI 介面
- `requirements.txt` — pip 相依套件
- `environment.yml` — Conda 環境配置
- `README.md` — 使用說明

## 注意事項

- 圖片不會被複製。轉換器會更新 Markdown 以指向原始圖片檔案，使用從輸出 `.md` 位置計算的正確相對路徑
- 同頁面的 `#錨點` 在同一 HTML 檔案內的連結上會被保留；外部連結保持不變
- 如果你的匯出將頁面嵌套在資料夾下，相同的結構會在輸出目錄下以 `.md` 檔案複製

## 版本

v1.0 - 初始版本
- 基本 HTML 到 Markdown 轉換
- GUI 和 CLI 介面
- 圖片路徑保留
- 內部連結重寫

## 授權

MIT License
