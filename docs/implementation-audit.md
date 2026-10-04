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
| `requirements.txt` | Đã tổng hợp từ import của code hiện tại và repo gốc; native offline tests đã chạy |
| `vendor_rethinkmcts/` | Repo tác giả, pin commit `3908cacd94feed849f671f6de39f0baec00ed72c`, giữ nguyên để audit |
| `rethinkmcts/` | Native tree/P-UCB/reward/feedback/search loop và CLI plan đã triển khai |
| Dataset | Đã chuẩn bị, xem `docs/datasets.md` |
| `data/scripts/prepare_humaneval.py` | Sau bước kiểm tra dữ liệu cục bộ vẫn gọi `load_dataset()` ở cuối, nên có thể truy cập mạng không cần thiết |
| `data/scripts/prepare_apps.py` | Chỉ kiểm tra thư mục `raw` tồn tại, chưa tự xác minh đủ file/số mẫu trước khi bỏ qua |
| LLM provider | Ollama hiện tại; Modal.com được giữ để audit run cũ; cấu hình qua `.env` |
| `tools/smoke_modal.py` | Smoke script lịch sử cho Modal, không phải benchmark entry point |
| Python environment | `D:\ReThinkMCTS\venv`, Python 3.14.5 |
| Windows portability | Executor gốc import module Unix `resource`; cần xử lý hoặc chạy trong Linux/WSL |
| `pyext` compatibility | `pyext==0.7` không build trên Python 3.14; cần thay `RuntimeModule.from_string` bằng local shim |

Kết luận: workspace có direct-generation baseline, executor offline độc lập và native
implementation có thể đọc/test offline; smoke provider thật vẫn chưa chạy.

## Sửa sai lệch native (2026-10-04)

Sau các sửa thuật toán bên dưới, phần điều phối đã chuyển sang LangGraph.
Chuyển đổi này chỉ thay luồng control, không thay P-UCB/reward/public-private
policy. Pydantic chặn state sai kiểu, thought rỗng, score không hữu hạn và
response Expansion thiếu/thừa; kết quả offline cần được xác nhận thêm bằng
smoke provider thật. LangGraph hiện chưa có checkpoint/resume giữa chừng.

- Selection trước đây ưu tiên cứng unvisited; nay chọn theo P-UCB cho toàn bộ child.
  Điểm hòa được tie-break bằng RNG cục bộ theo seed.
- Expansion nay yêu cầu đúng `width` thought khác nhau; trước đây parser âm thầm
  nhận ít hơn cấu hình và làm cây có độ rộng không mong muốn.
- Vòng Rethink trước đây chỉ sửa một lần dù cấu hình lớn hơn; nay sửa lặp có giới hạn,
  dừng khi public tests pass và dùng feedback cuối để Expansion khi còn rollout.
- Node bị thay thought nay reset visit/Q/prior, tránh gán thống kê action cũ cho action
  mới; ancestor giữ lịch sử vì state của ancestor không đổi. Candidate cũ vẫn giữ.
- Candidate artifact nay ghi snapshot thought tại thời điểm Evaluation; trước đây
  `thoughts.json` có thể phản ánh thought sau Rethink.
- Trace cho APPS call-based nay luôn được trả về. Trace AST giảm gán lặp event và
  ghi trạng thái biến trước/sau, nhưng **chưa tạo CFG thực** như repo tác giả.
- Chưa kiểm chứng bằng smoke Ollama hoặc so output với upstream trên cùng problem;
  không gọi đây là tương đương hoàn toàn với paper.

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

## Checklist audit repo gốc

- [x] Ghi URL, branch và commit hash tại `vendor_rethinkmcts/`.
- [x] Lập sơ đồ entry point và module.
- [x] Đọc loader APPS/HumanEval.
- [x] Đọc executor và timeout policy.
- [x] Đọc node/state/action representation.
- [x] Đọc implementation P-UCB và backpropagation.
- [x] Đọc prompt expansion, code generation, self-eval và rethink.
- [x] Xác định nơi tạo verbal feedback/block trace.
- [x] Ghi các khác biệt chính trong `docs/rethinkmcts-implementation.md`.
- [x] Tạo adapter OpenAI-compatible dùng client hiện tại; chưa gọi provider trong task này.
- [ ] Kiểm tra response usage, timeout, retry và lỗi rate limit của provider trong smoke thật.
- [x] Không sửa code upstream.

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
voi `qwen2.5-coder:7b-instruct` va hai sample manifest lich su tai
`data/samples/evaluation_v1/`. Cohort moi la `data/samples/benchmark_v2/`;
xem `docs/llm-provider.md` và `docs/pipeline-direct.md`.

