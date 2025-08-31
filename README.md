# MD Converter v1.4

Confluence HTML Pack → Markdown Converter

將 Confluence HTML 匯出包轉換為 Markdown 檔案，並將內嵌圖片複製到專用的 `images` 資料夾。內部連結從 `.html` 重寫為 `.md`，並調整相對路徑。轉換後的整個資料夾可以直接匯入 Notion 等平台。

## 功能特色

- 提取主要內容（嘗試常見的 Confluence 容器；可透過 CSS 選擇器配置）
- 將本機圖片複製到輸出目錄中的 `images` 資料夾，並更新 Markdown 中的路徑。
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

- **圖片會被複製**：所有在 HTML 中參照的本機圖片都會被複製到輸出根目錄下的一個 `images` 資料夾中。Markdown 檔案中的圖片路徑會自動更新為指向這些複製後的圖片的相對路徑。
- 同頁面的 `#錨點` 在同一 HTML 檔案內的連結上會被保留；外部連結保持不變
- 如果你的匯出將頁面嵌套在資料夾下，相同的結構會在輸出目錄下以 `.md` 檔案複製

## 版本

v1.4 - 圖片與 Markdown 共存
- 更新：現在會自動將 HTML 中的圖片複製到輸出目錄的 `images` 資料夾下。
- 更新：調整圖片和連結的相對路徑，確保在 Notion 等平台中可以正確顯示。
- 修正：修復了先前版本中圖片路徑處理的錯誤。

v1.0 - 初始版本
- 基本 HTML 到 Markdown 轉換
- GUI 和 CLI 介面
- 圖片路徑保留
- 內部連結重寫

## 授權

MIT License
