#!/usr/bin/env python3
import json
import mimetypes
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE_DIR = ROOT / "input" / "测试报销图片pdf"
OCR_PATH = SOURCE_DIR / "ocr_output.json"
OUTPUT_PATH = ROOT / "data.js"


def file_id(file_name: str) -> str:
    return f"file_{Path(file_name).stem}"


FILE_META = {
    "f01_0ba9d73eda.pdf": {"kind": "invoice_pdf", "summary": "电子发票：得力计算器，价税合计 19.60 元"},
    "f02_23345069bc.pdf": {"kind": "invoice_pdf", "summary": "电子发票：广告物料制作，价税合计 160.00 元"},
    "f03_f1dbcd2790.pdf": {"kind": "invoice_pdf", "summary": "电子发票：绿联 Type-C 扩展坞，价税合计 49.90 元"},
    "f04_d3330969b5.pdf": {"kind": "invoice_pdf", "summary": "电子发票：永旺日用品采购，价税合计 375.20 元"},
    "f05_e66d9570a4.jpg": {"kind": "payment_screenshot", "summary": "支付截图：抖音支付宏佳商贸 133.60 元"},
    "f06_66b2ba606a.jpg": {"kind": "order_screenshot", "summary": "订单截图：景田饮用水 8 箱，实付款 133.60 元"},
    "f07_461c2636dc.jpg": {"kind": "payment_screenshot", "summary": "支付截图：永旺支付 139.40 元"},
    "f08_b159850a58.png": {"kind": "receipt_image", "summary": "小票图片：永旺采购，实付 139.40 元"},
    "f09_193a000e28.jpg": {"kind": "payment_screenshot", "summary": "支付截图：达利图文广告收款 160.00 元"},
    "f10_b41e4990d6.jpg": {"kind": "payment_screenshot", "summary": "支付截图：抖音支付博宇包装 19.60 元"},
    "f11_c8a9c02d61.jpg": {"kind": "order_screenshot", "summary": "订单截图：得力计算器 2 个，实付款 19.60 元"},
    "f12_9b81facdf9.pdf": {"kind": "invoice_pdf", "summary": "电子发票：景田纯净水 8 箱，价税合计 133.60 元"},
    "f13_4028851811.pdf": {"kind": "invoice_pdf", "summary": "电子发票：永旺水果饮料纸品采购，价税合计 139.40 元"},
    "f14_d227c305f8.jpg": {"kind": "payment_screenshot", "summary": "支付截图：永旺支付 375.20 元"},
    "f15_813e2fe141.jpg": {"kind": "receipt_image", "summary": "小票图片：永旺日用品采购，实付 375.20 元"},
    "f16_d46bb3d2b5.jpg": {"kind": "payment_screenshot", "summary": "支付截图：京东支付绿联 49.90 元"},
    "f17_b9af5aeb77.jpg": {"kind": "order_screenshot", "summary": "订单截图：绿联 Type-C 扩展坞，实付款 49.90 元"},
    "f18_89bb0449ff.jpg": {"kind": "other", "summary": "其他图片：车辆通行证"},
    "f19_ffb62d978c.jpg": {"kind": "product_image", "summary": "商品图：威露士健康抑菌洗手液"},
    "f20_031a0c4e89.jpg": {"kind": "product_image", "summary": "商品图：得力计算器"},
    "f21_db48550947.jpg": {"kind": "product_image", "summary": "商品图：景田纯净水"},
    "f22_86aa73ab2d.jpg": {"kind": "product_image", "summary": "商品图：安速杀虫气雾剂（500ml/600ml）"},
    "f23_61f923c877.jpg": {"kind": "product_image", "summary": "商品图：榄菊电热蚊香液"},
    "f24_cbf6b2d7aa.jpg": {"kind": "product_image", "summary": "商品图：橙色环保袋"},
    "f25_781fd9c48b.jpg": {"kind": "product_image", "summary": "商品图：旺选味道优选砂糖橘"},
    "f26_cf16631d28.jpg": {"kind": "product_image", "summary": "商品图：维达湿巾 10 片 3 包"},
    "f27_6fea59bc89.jpg": {"kind": "product_image", "summary": "商品图：特慧优化妆棉棒"},
    "f28_2796fdfea0.jpg": {"kind": "product_image", "summary": "商品图：徐香猕猴桃 8 粒装"},
    "f29_e0cfebb2ca.jpg": {"kind": "product_image", "summary": "商品图：维他奶原味豆奶饮料"},
    "f30_0570897a4e.jpg": {"kind": "product_image", "summary": "商品图：维达婴儿护肤柔湿巾"},
    "f31_f6968ee7a4.jpg": {"kind": "product_image", "summary": "商品图：维达超韧抽取面巾 24 包"},
    "f32_f203304036.jpg": {"kind": "product_image", "summary": "商品图：维达超韧抽取面巾 24 包"},
    "f33_9a86d6fba8.jpg": {"kind": "product_image", "summary": "商品图：绿联 Type-C 扩展坞"},
    "f34_5f66823a4a.jpg": {"kind": "product_image", "summary": "商品图：旺选味道春见耙耙柑"},
    "f35_29f4fbc33e.jpg": {"kind": "product_image", "summary": "商品图：无纺布购物袋"},
    "f36_40a5b510f8.jpg": {"kind": "product_image", "summary": "商品图：轻迎棉源柔巾 66 片"},
    "f37_d1cf327cef.jpg": {"kind": "product_image", "summary": "商品图：乐比叮防护喷雾剂"},
    "f38_9cbafc19fb.jpg": {"kind": "product_image", "summary": "商品图：超甜蕉"},
}


EXPENSES = [
    {
        "id": "expense_calculator",
        "title": "得力计算器",
        "amount": 19.60,
        "line_items": [
            {"name": "得力计算器", "quantity": 2, "unit_price": 9.80, "amount": 19.60},
        ],
        "file_names": [
            "f01_0ba9d73eda.pdf",
            "f10_b41e4990d6.jpg",
            "f11_c8a9c02d61.jpg",
            "f20_031a0c4e89.jpg",
        ],
    },
    {
        "id": "expense_ad_material",
        "title": "广告物料制作",
        "amount": 160.00,
        "line_items": [
            {"name": "广告物料制作", "quantity": 1, "unit_price": 160.00, "amount": 160.00},
        ],
        "file_names": [
            "f02_23345069bc.pdf",
            "f09_193a000e28.jpg",
        ],
    },
    {
        "id": "expense_ugreen_hub",
        "title": "绿联 Type-C 扩展坞",
        "amount": 49.90,
        "line_items": [
            {"name": "绿联 Type-C 扩展坞转 HDMI 转接头", "quantity": 1, "unit_price": 49.90, "amount": 49.90},
        ],
        "file_names": [
            "f03_f1dbcd2790.pdf",
            "f16_d46bb3d2b5.jpg",
            "f17_b9af5aeb77.jpg",
            "f33_9a86d6fba8.jpg",
        ],
    },
    {
        "id": "expense_water",
        "title": "景田纯净水 360ml*24（8 箱）",
        "amount": 133.60,
        "line_items": [
            {"name": "景田纯净水 360ml*24", "quantity": 8, "unit_price": 16.70, "amount": 133.60},
        ],
        "file_names": [
            "f12_9b81facdf9.pdf",
            "f05_e66d9570a4.jpg",
            "f06_66b2ba606a.jpg",
            "f21_db48550947.jpg",
        ],
    },
    {
        "id": "expense_eon_small",
        "title": "永旺采购（水果 / 饮料 / 纸品）",
        "amount": 139.40,
        "line_items": [
            {"name": "无纺布购物袋", "quantity": 1, "unit_price": 1.20, "amount": 1.20},
            {"name": "旺选味道优选砂糖橘", "quantity": 1, "unit_price": 9.90, "amount": 9.90},
            {"name": "徐香猕猴桃 8 粒装", "quantity": 1, "unit_price": 10.00, "amount": 10.00},
            {"name": "超甜蕉（袋）", "quantity": 1, "unit_price": 10.00, "amount": 10.00},
            {"name": "维达湿巾 10 片 3 包", "quantity": 1, "unit_price": 10.00, "amount": 10.00},
            {"name": "维他奶原味豆奶饮料 250ml*6", "quantity": 2, "unit_price": 17.90, "amount": 35.80},
            {"name": "旺选味道春见耙耙柑", "quantity": 1, "unit_price": 23.60, "amount": 23.60},
            {"name": "维达超韧抽取面巾 24 包", "quantity": 1, "unit_price": 38.90, "amount": 38.90},
        ],
        "file_names": [
            "f13_4028851811.pdf",
            "f07_461c2636dc.jpg",
            "f08_b159850a58.png",
            "f25_781fd9c48b.jpg",
            "f26_cf16631d28.jpg",
            "f28_2796fdfea0.jpg",
            "f29_e0cfebb2ca.jpg",
            "f32_f203304036.jpg",
            "f34_5f66823a4a.jpg",
            "f35_29f4fbc33e.jpg",
            "f38_9cbafc19fb.jpg",
        ],
    },
    {
        "id": "expense_eon_daily",
        "title": "永旺采购（日用品）",
        "amount": 375.20,
        "line_items": [
            {"name": "橙色环保袋", "quantity": 1, "unit_price": 5.00, "amount": 5.00},
            {"name": "特慧优化妆棉棒", "quantity": 2, "unit_price": 6.90, "amount": 13.80},
            {"name": "轻迎棉源柔巾 66 片", "quantity": 4, "unit_price": 11.90, "amount": 47.60},
            {"name": "维达婴儿护肤柔湿巾（80 片）", "quantity": 4, "unit_price": 10.00, "amount": 40.00},
            {"name": "安速杀虫气雾剂（500ml/600ml）", "quantity": None, "unit_price": None, "amount": 49.90},
            {"name": "榄菊电热蚊香液特惠装", "quantity": 4, "unit_price": 20.00, "amount": 80.00},
            {"name": "威露士健康抑菌洗手液", "quantity": 2, "unit_price": 20.00, "amount": 40.00},
            {"name": "维达超韧抽取面巾 24 包", "quantity": 1, "unit_price": 38.90, "amount": 38.90},
            {"name": "乐比叮防护喷雾剂（无香）200ml", "quantity": 2, "unit_price": 30.00, "amount": 60.00},
        ],
        "file_names": [
            "f04_d3330969b5.pdf",
            "f14_d227c305f8.jpg",
            "f15_813e2fe141.jpg",
            "f19_ffb62d978c.jpg",
            "f22_86aa73ab2d.jpg",
            "f23_61f923c877.jpg",
            "f24_cbf6b2d7aa.jpg",
            "f27_6fea59bc89.jpg",
            "f30_0570897a4e.jpg",
            "f31_f6968ee7a4.jpg",
            "f36_40a5b510f8.jpg",
            "f37_d1cf327cef.jpg",
        ],
    },
]


def fallback_summary(ocr_text: str) -> str:
    for line in (ocr_text or "").splitlines():
        line = line.strip()
        if line:
            return line[:60]
    return "未识别摘要"


def build_files():
    source_items = json.loads(OCR_PATH.read_text(encoding="utf-8"))
    files = []
    for item in source_items:
        file_name = item["file_name"]
        meta = FILE_META.get(file_name, {})
        rel_path = f"input/{SOURCE_DIR.name}/{file_name}"
        mime_type = mimetypes.guess_type(file_name)[0] or ""
        files.append(
            {
                "id": file_id(file_name),
                "kind": meta.get("kind", "other"),
                "locator": {
                    "relative_path": rel_path,
                    "previous_names": [file_name],
                    "mime_type": mime_type,
                },
                "recognition": {
                    "summary": meta.get("summary") or fallback_summary(item.get("ocr_text", "")),
                },
            }
        )
    return files


def build_expenses():
    expenses = []
    for expense in EXPENSES:
        expenses.append(
            {
                "id": expense["id"],
                "title": expense["title"],
                "amount": {"value": expense["amount"], "currency": "CNY"},
                "line_items": expense["line_items"],
                "file_ids": [file_id(name) for name in expense["file_names"]],
            }
        )
    return expenses


def main():
    data = {
        "schema_version": "reimbursement.v3",
        "project": {
            "name": SOURCE_DIR.name,
            "source": str(OCR_PATH.relative_to(ROOT)),
        },
        "files": build_files(),
        "expenses": build_expenses(),
    }
    OUTPUT_PATH.write_text(
        "window.REIMBURSEMENT_DB = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n",
        encoding="utf-8",
    )
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
