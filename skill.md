## OCR 依赖

图片/PDF 文字提取需要 `ppocrv5` skill。如果没有，提醒用户先安装。
调用：`/ppocrv5 <input_path>`（用户提供包含报销图片的文件夹）
输出的ocr.json放在本目录下。

## 任务

把当前目录的 类似`ocr.json`（或 `*_ocr.json`）整理成 `data.js`。

## 要求

- 只看当前目录，不参考别的文件夹
- 输出文件：`data.js`
- 格式固定：`window.REIMBURSEMENT_DB = {...};`
- `schema_version` 固定写 `reimbursement.v3`
- `files` 和 `expenses` 必须是数组

### files[] 必须字段

- `id` `kind` `locator.relative_path` `recognition.summary`
- `kind` 枚举值：invoice_pdf | receipt_image | product_image | order_screenshot | payment_screenshot | chat_screenshot | contract_pdf | other
- `locator` 完整字段：{ relative_path, mime_type?, previous_names? }
- `recognition.summary` 格式："发票：xxx" / "商品图：xxx" / "支付截图：xxx"

### expenses[] 必须字段

- `id` `title` `amount.value` `line_items` `file_ids`
- `amount` 结构：{ value: number, currency?: string }
- `line_items[]` 结构：{ name, quantity?, unit_price?, amount }（amount 必须，用于计算证据金额）

## 关联规则

- 能关联的票据、支付图、订单图、商品图尽量关联；不确定的就保留未关联，不要瞎编
- 商品图的 `recognition.summary` 应包含商品名称，用于匹配 `line_items[].name`
- 直接落盘成 `data.js`，不要只给示例

## 三层关联策略

1. OCR 出来没有关联的，让 AI 再去看图，看看能不能关联上
2. 看完 AI 还不确定的，这时候 AI 去和用户确认

## 最后

生成 `data.js` 后，帮用户本地打开 `viewer.html`