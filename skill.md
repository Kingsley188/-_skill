把当前目录里的 `ocr.json`（或 `*_ocr.json`）整理成 `viewer.html` 可直接读取的 `data.js`。

要求：
- 只看当前目录，不参考别的文件夹
- 先读 `viewer.html`，按它实际用到的字段生成
- 输出文件：`data.js`
- 格式固定：`window.REIMBURSEMENT_DB = {...};`
- `schema_version` 固定写 `reimbursement.v3`
- `files` 和 `expenses` 必须是数组
- `files[]` 至少包含：`id` `kind` `locator.relative_path` `recognition.summary`
- `expenses[]` 至少包含：`id` `title` `amount.value` `line_items` `file_ids`
- 能关联的票据、支付图、订单图、商品图尽量关联；不确定的就保留未关联，不要瞎编
- 直接落盘成 `data.js`，不要只给示例

1.OCR出来没有关联的报销单呢的让AI再去看图，看看能不能关联上。看完AI还不确认的，这时候AI去和用户来确认。