# Tools

Các script trong thư mục này chỉ phục vụ kiểm tra thủ công hoặc chẩn đoán,
không phải entry point của benchmark.

## `smoke_modal.py`

Gọi thử một request Modal theo biến môi trường cũ. Benchmark hiện tại dùng Ollama
trên GPU CKEY và chạy qua `pipelines`, vì vậy script này chỉ giữ cho việc kiểm tra
provider Modal lịch sử.

Không ghi secret vào file hoặc commit `.env`.
