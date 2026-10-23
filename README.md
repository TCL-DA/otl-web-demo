# OTL Roaster — phương án giao diện mới cho otlpro.com

**Xem trực tiếp:** https://tcl-da.github.io/otl-web-demo/

## 6 · Bản nhiều trang kiểu Apple (mới, 23/10/2026)

**Mở:** https://tcl-da.github.io/otl-web-demo/apple/ · Phong cách gốc: [Apple trên Refero](https://styles.refero.design/style/aecac5da-f397-4ddf-b71f-de1efc434cb8)

Làm lại theo góp ý: bỏ kiểu một trang kéo dài, dựng khung nhiều trang như apple.com/ipad và web các hãng máy rang
(Giesen, Loring, Probat). Bản đang phát triển ưu tiên tiếng Việt, gồm 20 trang:

- Trang chủ, trang dòng máy (dải biểu tượng từng model + băng chuyền), trang thiết bị.
- Mỗi model một trang riêng: OTL-1.2, 03, 06, 12, 15, 30, 60, 120. Mỗi trang có thanh phụ dính, số nổi bật,
  tính năng, ảnh và thông số.
- Thiết bị: máy tách đá OD, buồng đốt khói AB, silo OTL và cyclone rời.
- Các trang chung: So sánh 3 model cạnh nhau, Giải pháp, Hỗ trợ, Về OTL, Hỏi giá (điền sẵn model khi bấm từ trang máy).

Có chế độ tối: tự theo cài đặt máy người xem, nút mặt trăng trên menu để đổi tay; trang OTL-30/60/120 luôn nền tối.
Trang chủ có mục “Trò chuyện với OTL”, 5 video Shorts; mọi trang có bảng chat WhatsApp / Zalo / Messenger,
liên kết mạng xã hội và nút sao chép thông tin liên hệ. Trên máy tính, Zalo hiện mã QR của số hotline;
chưa có đường dẫn Zalo OA được xác nhận.

Nội dung lấy từ bản tiếng Việt của otlpro.com và bộ hồ sơ sản phẩm máy chủ. Dải máy 1,2–500 kg và các khu vực
xuất khẩu theo cập nhật của người dùng ngày 23/10/2026. Tám mẫu máy tiêu chuẩn có trang riêng; hệ thống trên
120 kg được giới thiệu theo yêu cầu, chưa gán tên mẫu hay thông số. OTL-60/120 dùng ảnh máy thật theo ngoại lệ
đã được duyệt; sơ đồ tuần hoàn khí nằm trong mục Hệ thống. Máy tách đá OD-30 có trình xem 3D, bấm mới tải.

Trang Về OTL có câu chuyện thương hiệu, mốc 2018/2025, hiện tại và định hướng; ba cơ chế truyền nhiệt,
quy trình sáu bước và liên kết kiến thức rang. Chỉ gán năm cho mốc có nguồn, không thêm tỷ lệ ghi hồ sơ hay
khẳng định toàn bộ máy dùng chung một nền tảng điều khiển.

Thông số cần chốt trước phát hành chính thức: kích thước OTL-06/15/120 đang khác nhau giữa web, brochure
và bản vẽ; nguồn điện OTL-12/15 cần kỹ thuật xác nhận. Số liệu tiết kiệm tới 30% là công bố của OTL cho
OTL-60/120, chưa phải phép đo độc lập của bản demo.

Nguồn dựng: `_src/apple/` (`build.py` dựng trang và xử lý ảnh từ kho `F:\Kho-anh`; `kiem.py` kiểm từng trang:
lỗi, ảnh hỏng, liên kết hỏng, tràn ngang, chữ sát mép, tương tác).

Chạy `python -X utf8 _src/apple/build.py` rồi `python -u -X utf8 _src/apple/kiem.py` tại gốc repository.
Bộ kiểm chạy trên máy tính sáng/tối và điện thoại, kiểm ngôn ngữ, biểu mẫu (gồm email sai định dạng), chat,
sao chép, so sánh và điền sẵn mẫu máy. Lượt kiểm video chặn tải YouTube và chỉ xác nhận tạo iframe đúng mã;
không thay thế kiểm phát video thực tế. Bản tiếng Anh trước khi chuyển được giữ ở `_src/apple/build_en_20261023.py`.

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
