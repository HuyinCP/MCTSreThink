# Dataset của dự án

## Pham vi benchmark da khoa

Dataset goc khong doi: APPS test co 5.000 bai va HumanEval test co 164 bai. De
kiem soat chi phi va giu cung mot tap so sanh cho MCTS, benchmark baseline hien tai
chi chon dung 100 bai ngau nhien moi dataset:

| Dataset | Sample manifest | So bai benchmark | Co dinh cho MCTS |
|---|---|---:|---|
| APPS test | `data/samples/evaluation_v1/apps_test_100.json` | 100 | Co |
| HumanEval test | `data/samples/evaluation_v1/humaneval_test_100.json` | 100 | Co |

`baseline_v1` là sample lịch sử được giữ để truy vết, không phải sample judge hiện tại.
Sample dùng cho judge full-generation được khóa riêng:

| Dataset | Judge manifest | So bai |
|---|---|---:|
| APPS test | `data/samples/evaluation_v1/apps_test_100.json` | 100 |
| HumanEval test | `data/samples/evaluation_v1/humaneval_test_100.json` | 100 |

Seed cua sample v1 la `20260927`. Khong dung `--limit 100` thay cho manifest vi
`--limit` chi lay 100 ID dau, khong phai sample ngau nhien da khoa.

File này ghi quyết định cấp dự án. Cấu trúc file, schema chi tiết và ví dụ đọc dữ
liệu nằm tại [../data/README.md](../data/README.md).

## Phạm vi đã chốt

Dự án sử dụng đúng hai dataset:

| Dataset | Vai trò | Biểu diễn cục bộ | Trạng thái |
|---|---|---|---|
| APPS | Baseline chính theo độ khó | `data/apps/raw` | Đủ 5.000 train + 5.000 test |
| HumanEval | Benchmark hàm Python | `data/humaneval/arrow` | Đủ 164 test |

**Không sử dụng CodeContests** trong phạm vi hiện tại.

## Lý do chọn biểu diễn

- APPS giữ bản raw theo từng bài vì cấu trúc này phù hợp loader của repo
  RethinkMCTS gốc. Không giữ thêm bản Arrow trùng dữ liệu.
- HumanEval giữ bản Arrow vì dữ liệu nhỏ, schema ổn định và có thể load trực tiếp
  bằng Hugging Face `datasets`.

## Nguyên tắc public/private tests

Paper đánh giá search bằng public tests và báo kết quả cuối trên private tests. APPS
không cung cấp sẵn một cột public/private trong biểu diễn raw hiện tại. Cách chia test
cụ thể phải được lấy từ code repo gốc và ghi vào `implementation-audit.md`; không tự
đặt policy trước khi kiểm tra.

HumanEval chứa test chuẩn trong cột `test`. Khi chạy baseline cần kiểm tra repo gốc
dùng toàn bộ test này như thế nào và có tạo public tests riêng hay không.

## Kiểm tra trước mỗi thử nghiệm

- APPS có đúng 5.000 thư mục ở mỗi split.
- Mỗi bài APPS có `question.txt`, `solutions.json`, `input_output.json` và
  `metadata.json`; `starter_code.py` là tùy chọn.
- HumanEval load được 164 dòng và đủ năm cột chuẩn.
- Đường dẫn cấu hình trỏ tới dữ liệu cục bộ, không vô tình tải lại dataset.
- Không log toàn bộ lời giải tham khảo vào prompt hoặc artifact công khai.

## Quy tắc cập nhật

Mọi thay đổi nguồn, split, schema, số lượng, định dạng hoặc đường dẫn phải cập nhật
đồng thời file này, `data/README.md`, `project-status.md` và các script liên quan.

