# Dataset của dự án

## Benchmark cohort cho cac lan chay moi

Dataset goc khong doi: APPS test 5.000 bai, HumanEval test 164 bai. Cohort
`benchmark_v2` duoc khoa cho model/MCTS va judge tu nay ve sau:

| Dataset | Manifest | Quy mo | Cach chon |
|---|---|---:|---|
| APPS test | `data/samples/benchmark_v2/apps_test_300.json` | 300 | Dung 100 ID moi muc kho tu cohort cua nhom doi chieu |
| HumanEval test | `data/samples/benchmark_v2/humaneval_test_164.json` | 164 | Toan bo `HumanEval/0` den `HumanEval/163` |

APPS duoc lay tu [manifest goc](https://github.com/Viendeptrai1/rethink-mcts-slm/blob/main/data/cohorts/apps_benchmark_300.json)
va [script chon mau](https://github.com/Viendeptrai1/rethink-mcts-slm/blob/main/scripts/sample_apps_300_stratified.py):
loc `len(inputs) >= 3` va `len(inputs) == len(outputs)`, sau do lay mau ngau
nhien phan tang khong hoan lai, seed `2027`, 100 bai moi muc introductory,
interview, competition. Nguon HumanEval la [processed.jsonl](https://github.com/Viendeptrai1/rethink-mcts-slm/blob/main/data/humaneval/processed.jsonl)
du 164 `Python/0..163`; ID so duoc doi chieu voi `HumanEval/0..163` cuc bo.

`evaluation_v1` (100 APPS + 100 HumanEval) la benchmark **da chay truoc day**;
giu nguyen manifest va ket qua de truy vet, khong so truc tiep voi cohort moi.
`baseline_v1` con cu hon va cung duoc giu de truy vet. Generation full khong
truyen `--sample-file`. Khong dung `--limit` thay cho manifest vi no chi lay
nhung ID dau, khong giu dung cohort.

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

