# OTL Roaster — phương án giao diện mới cho otlpro.com

**Xem trực tiếp:** https://tcl-da.github.io/otl-web-demo/

## 6 · Bản nhiều trang kiểu Apple (mới, 23/10/2026)

**Mở:** https://tcl-da.github.io/otl-web-demo/apple/ · Phong cách gốc: [Apple trên Refero](https://styles.refero.design/style/aecac5da-f397-4ddf-b71f-de1efc434cb8)

Làm lại theo góp ý: bỏ kiểu một trang kéo dài, dựng khung nhiều trang như apple.com/ipad và web các hãng máy rang
(Giesen, Loring, Probat). Gồm 19 trang:

- Trang chủ, trang dòng máy (dải biểu tượng từng model + băng chuyền), trang thiết bị.
- Mỗi model một trang riêng: OTL-1.2, 03, 06, 12, 15, 30, 60, 120. Mỗi trang có thanh phụ dính, số nổi bật,
  tính năng, ảnh và thông số.
- Thiết bị: OD Destoner, AB Afterburner, OTL-Silo.
- Các trang chung: So sánh 3 model cạnh nhau, Giải pháp, Hỗ trợ, Về OTL, Hỏi giá (điền sẵn model khi bấm từ trang máy).

Có chế độ tối: tự theo cài đặt máy người xem, nút mặt trăng trên menu để đổi tay; trang OTL-30/60/120 luôn nền tối.
Trang chủ có mục liên hệ nhanh "Talk to OTL." và mọi trang có nút WhatsApp (giống web cũ, trình bày lại kiểu Apple).

Thông số lấy nguyên từ các trang sản phẩm otlpro.com. OTL-60 và OTL-120 chưa có ảnh máy đúng cấu hình liền khối,
nên tạm dùng sơ đồ tuần hoàn khí vẽ lại (7 điểm đo nhiệt).

Nguồn dựng: `_src/apple/` (`build.py` dựng trang và xử lý ảnh từ kho `F:\Kho-anh`; `kiem.py` kiểm từng trang:
lỗi, ảnh hỏng, liên kết hỏng, tràn ngang, chữ sát mép, tương tác).

## 1–5 · Bản một trang (22–23/10/2026)

Mỗi bản là một trang chủ demo dựng theo một phong cách thiết kế (thư viện [Refero Styles](https://styles.refero.design/)).

| # | Phong cách | Xem demo | Phong cách gốc |
|---|---|---|---|
| 1 | Superlative | [Mở](https://tcl-da.github.io/otl-web-demo/1-superlative.html) | [Refero](https://styles.refero.design/style/10ab6120-3d03-48ff-aebe-0b4910edc046) |
| 2 | Dyson | [Mở](https://tcl-da.github.io/otl-web-demo/2-dyson.html) | [Refero](https://styles.refero.design/style/96845df2-7ddb-420a-814e-c339f95a6554) |
| 3 | BMW.com | [Mở](https://tcl-da.github.io/otl-web-demo/3-bmw.html) | [Refero](https://styles.refero.design/style/b8899cbd-e2ca-4069-83cf-d8f8b0d71100) |
| 4 | Caldera | [Mở](https://tcl-da.github.io/otl-web-demo/4-caldera.html) | [Refero](https://styles.refero.design/style/fe8cdcf9-c850-4d52-be07-5ad269bf9ebf) |
| 5 | Peak Design | [Mở](https://tcl-da.github.io/otl-web-demo/5-peakdesign.html) | [Refero](https://styles.refero.design/style/6f3fb64d-d4c9-4ec1-86a1-7983e5180985) |

Nguồn dựng: `_src/1trang/`. Mỗi file HTML tự chứa ảnh.

Đây là bản demo để chọn hướng thiết kế, không phải web chính thức. Biểu mẫu chỉ kiểm tra ô bắt buộc, không gửi đi đâu.
