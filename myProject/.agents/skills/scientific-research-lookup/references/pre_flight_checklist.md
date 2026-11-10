# CHECKLIST TỰ KIỂM TRA TRƯỚC KHI TRẢ KẾT QUẢ (PRE-FLIGHT AUDIT CHECKLIST)

Trước khi gửi bất kỳ báo cáo khoa học nào cho người dùng, Agent **BẮT BUỘC** phải tự kiểm tra 10 câu hỏi sau:

---

```
[BẢNG KIỂM 10 ĐIỂM BẮT BUỘC]
[ ] 1. Tính tồn tại thực tế: Mọi bài báo, tác giả, tạp chí được nhắc đến có thực sự tồn tại trên PubMed, Crossref hay cơ sở dữ liệu chính thống không?
[ ] 2. Tính khớp định danh: DOI và PMID có khớp chính xác với tiêu đề bài báo và tác giả không? (Đã chạy verify_citation.py chưa?)
[ ] 3. Nguồn gốc sơ cấp: Nguồn trích dẫn có phải là tài liệu gốc (primary source) hay chỉ là trích dẫn lại từ bài viết khác?
[ ] 4. Mức độ truy cập: Đã phân định rạch ròi giữa việc đọc toản văn [Full Text] hay mới chỉ đọc [Abstract Only]?
[ ] 5. Truy vết khẳng định: Mọi claim quan trọng có citation đi kèm trong Evidence Matrix không? Có claim nào mồ côi (unsupported) mà chưa gắn nhãn không?
[ ] 6. Chống ngụy biện nhân quả: Có vô tình biến mối tương quan (correlation/association) thành quan hệ nhân quả (causation) không?
[ ] 7. Phân biệt lâm sàng: Có lấy kết quả nghiên cứu in-vitro (ống nghiệm) hoặc trên chuột/động vật để kết luận cho người không?
[ ] 8. Công bằng với bằng chứng trái chiều: Đã liệt kê và phân tích các nghiên cứu có kết quả ngược lại chưa? Có che giấu mâu thuẫn để làm đẹp báo cáo không?
[ ] 9. Phân định phản biện: Đã gắn nhãn cảnh báo rõ ràng nếu trích dẫn Preprint (chưa qua peer-review) chưa?
[ ] 10. Loại bỏ kiến thức tự bịa: Báo cáo có hoàn toàn dựa trên dữ liệu trích xuất từ tài liệu đã tra cứu thay vì "trí nhớ tự suy" của mô hình AI không?
```

---

## QUY TẮC XỬ LÝ KHI VI PHẠM CHECKLIST:

* Nếu phát hiện một DOI không kiểm tra được hoặc không tồn tại: **LẬP TỨC XÓA BỎ KHỎI DANH MỤC TRÍCH DẪN**.
* Nếu chỉ đọc được Abstract: Bắt buộc chèn dòng `[ABSTRACT ONLY - Chưa kiểm tra toàn văn]` vào phần phân tích.
* Nếu không tìm thấy đủ tài liệu đạt chuẩn: Bắt buộc ghi nhận `NOT ENOUGH EVIDENCE` thay vì cố gắng đưa ra kết luận chắc chắn.
