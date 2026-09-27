# Audit implementation

Tài liệu này phân biệt rõ mô tả trong paper với hành vi đã quan sát trong code.

## Snapshot workspace hiện tại

| Thành phần | Trạng thái đã kiểm chứng |
|---|---|
| `Executors/APPSExecutor.py` | Chạy từng test `stdin_stdout` và `call_based`, có timeout và báo partial pass |
| `Executors/HumanevalExecutor.py` | Chạy nguyên official harness, báo `1/1` hoặc `0/1` |
| `Executors/common.py` | Report schema và subprocess runner dùng chung; chưa phải security sandbox |
| `Models/` | Rỗng |
| `ChatModels/modal_client.py` | Adapter Modal đã gọi API thật và lưu response/usage |
| `DataProcess/problem_loader.py` | Loader đề APPS/HumanEval, không đọc solution/test |
| `baselines/direct_generation/` | Direct generation package; bước chấm được tách sang `Executors/` |
| `pipelines/direct_baseline.py` | Điều phối generation hoàn tất trước parallel evaluation |
| `evaluation/batch_evaluation.py` | Process pool theo candidate; report JSONL/CSV/summary và resume |
| `requirements.txt` | Đã tổng hợp từ import của code hiện tại và repo gốc; chưa cài/xác minh toàn bộ |
| `RethinkMCTS/` | Chưa tồn tại |
| Dataset | Đã chuẩn bị, xem `docs/datasets.md` |
| `data/scripts/prepare_humaneval.py` | Sau bước kiểm tra dữ liệu cục bộ vẫn gọi `load_dataset()` ở cuối, nên có thể truy cập mạng không cần thiết |
| `data/scripts/prepare_apps.py` | Chỉ kiểm tra thư mục `raw` tồn tại, chưa tự xác minh đủ file/số mẫu trước khi bỏ qua |
| LLM provider | Modal.com, giao diện OpenAI-compatible, cấu hình qua `.env` |
| `test.py` | Đã đọc endpoint/model từ `.env`; chưa chạy request xác minh |
| Python environment | `D:\ReThinkMCTS\venv`, Python 3.14.5 |
| Windows portability | Executor gốc import module Unix `resource`; cần xử lý hoặc chạy trong Linux/WSL |
| `pyext` compatibility | `pyext==0.7` không build trên Python 3.14; cần thay `RuntimeModule.from_string` bằng local shim |

Kết luận: workspace đã có direct-generation baseline và executor offline độc lập,
nhưng chưa phải implementation chạy được của RethinkMCTS.

## Paper mô tả, code cần xác minh

| Chủ đề | Paper | Cần tìm trong code gốc |
|---|---|---|
| Selection | P-UCB với Q là reward lớn nhất | Khởi tạo visit, tie-break, cách lưu Q |
| Expansion | Sinh tối đa `k` thought và reasonableness | Parser, normalize score, retry prompt |
| Evaluation | Sinh code hoàn chỉnh từ current thoughts | Node nào được evaluate sau expansion |
| Dual evaluation | Chỉ cần self-eval để phân biệt code pass public tests | Thứ tự gọi và range score thực tế |
| Verbal feedback | Block-level trace và giá trị biến | Công cụ CFG, giới hạn trace/test/token |
| Backpropagation | Cập nhật node và ancestor bằng scalar reward | Max hay aggregate nội bộ |
| Rethink | Thay thought gần nhất bằng thought mới | Mutation cây, child cũ, số lần rethink |
| Final answer | Code có reward cao nhất trong `program_dict` | Deduplicate và xử lý cùng reward |
| APPS tests | Public để search, private để báo kết quả | Quy tắc chia test cụ thể |

## Checklist sau khi clone repo gốc

- [ ] Ghi URL, branch và commit hash.
- [ ] Lập sơ đồ entry point và module.
- [ ] Đọc loader APPS/HumanEval.
- [ ] Đọc executor và timeout policy.
- [ ] Đọc node/state/action representation.
- [ ] Đọc implementation P-UCB và backpropagation.
- [ ] Đọc prompt expansion, code generation, self-eval và rethink.
- [ ] Xác định nơi tạo verbal feedback/block trace.
- [ ] Ghi mọi khác biệt với `theory-rethinkmcts.md`.
- [ ] Xác định repo gốc dùng SDK/call pattern nào và tạo adapter Modal phù hợp.
- [ ] Kiểm tra response usage, timeout, retry và lỗi rate limit của endpoint Modal.
- [ ] Không sửa code gốc trước khi có một lần chạy baseline được lưu log.

## Mẫu ghi quan sát

```text
Ngày:
Commit:
Lệnh chạy:
Dataset / problem ID:
Model / rollout / seed:
Hành vi quan sát:
Khớp paper:
Khác paper:
Bằng chứng (file:line hoặc log):
Câu hỏi còn mở:
```
# Cap nhat provider/benchmark (2026-09-27)

Phan audit Modal ben duoi la lich su cua run cu. Benchmark hien tai dung Ollama
voi `qwen2.5-coder:7b-instruct` va hai sample manifest co dinh tai
`data/samples/baseline_v1/`; xem `docs/llm-provider.md` va `docs/pipeline-direct.md`.

