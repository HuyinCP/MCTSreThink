# ReThinkMCTS

Đề tài: **Cải thiện khả năng suy luận của LLM trong sinh mã nguồn bằng Monte
Carlo Tree Search với phản hồi từ kiểm thử tự động**.

## Trạng thái hiện tại

Baseline direct-generation đã hoàn thành cho model:

```text
qwen2.5-coder:7b-instruct
provider: Ollama trên GPU CKEY
run: qwen25_coder_7b_instruct_baseline_v1
```

Phạm vi đã chạy:

- Sinh code: toàn bộ APPS test (5.000 bài) và HumanEval test (164 bài).
- Đã đánh giá: sample lịch sử 100 APPS + 100 HumanEval (`evaluation_v1`).
- Benchmark tương lai: đúng 300 APPS + toàn bộ 164 HumanEval (`benchmark_v2`);
  chưa chạy judge/MCTS trên cohort mới.
- Judge: APPS Pass Rate/Pass@1 theo difficulty và HumanEval Pass@1.
- RethinkMCTS native: **đã triển khai và kiểm thử offline**; LangGraph điều
  phối search, Pydantic kiểm tra state; chưa gọi LLM thật.
- Bước kế tiếp: smoke test 1 HumanEval và 1 APPS với Ollama trên GPU CKEY.

Kết quả baseline hiện tại:

| Nhóm | Pass Rate (%) | Pass@1 (%) |
|---|---:|---:|
| APPS Intro. | 39.02 | 23.08 |
| APPS Inter. | 26.14 | 7.46 |
| APPS Comp. | 25.09 | 0.00 |
| APPS Overall | 27.60 | 8.00 |
| HumanEval | N/A | 84.00 |

Kết quả chi tiết nằm trong:
`outputs/baselines/evaluations/qwen25_coder_7b_instruct_baseline_v1/`.

## Bắt đầu đọc

1. [docs/project-status.md](docs/project-status.md): trạng thái đã kiểm chứng và bước tiếp theo.
2. [docs/README.md](docs/README.md): bản đồ tài liệu và source of truth.
3. [docs/runbooks/baseline-full.md](docs/runbooks/baseline-full.md): các lệnh vận hành benchmark.
4. [docs/datasets.md](docs/datasets.md): phạm vi và quyết định về APPS/HumanEval.
5. [docs/theory-rethinkmcts.md](docs/theory-rethinkmcts.md): thuật toán nền tảng từ paper.
6. [rethinkmcts/README.md](rethinkmcts/README.md): thuật toán native từng bước, chi phí mỗi node và điểm khác paper.
7. [docs/rethinkmcts-implementation.md](docs/rethinkmcts-implementation.md): kiến trúc native, artifact và khác biệt với repo tác giả.
8. [docs/runbooks/rethinkmcts-smoke.md](docs/runbooks/rethinkmcts-smoke.md): kiểm thử offline và lệnh smoke test.
9. [docs/runbooks/benchmark-v2.md](docs/runbooks/benchmark-v2.md): danh sách cohort mới và lệnh đánh giá 300+164.
10. [docs/runbooks/remote-evaluation.md](docs/runbooks/remote-evaluation.md): đóng gói và chấm trên máy GPU thuê.
11. [docs/benchmark-results.md](docs/benchmark-results.md): nơi lưu bảng và tham số của từng run.

## Kiến trúc thư mục

```text
D:\ReThinkMCTS\
├── README.md                 # Điểm vào duy nhất của project
├── AGENTS.md                 # Quy ước cộng tác và ràng buộc giai đoạn
├── requirements.txt          # Dependency Python
├── .env.example              # Mẫu cấu hình, không chứa secret
│
├── docs/                     # Kiến thức dự án, lý thuyết, quyết định, runbook
├── RelativeWork/             # Paper tham khảo, gồm 2409.09584v2.pdf
├── data/                     # Dataset cục bộ và sample manifest cố định
│   ├── apps/raw/             # APPS train/test theo thư mục từng bài
│   ├── humaneval/arrow/      # HumanEval test ở định dạng Arrow
│   ├── samples/              # Manifest sample, không bốc lại khi chạy lại
│   └── scripts/              # Script chuẩn bị dữ liệu
│
├── baselines/                # Sinh code direct và config prompt/model
├── pipelines/                # Điều phối generate/evaluate
├── Executors/                # Chạy candidate và tạo ExecutionReport
├── evaluation/               # Batch evaluation và benchmark judge
├── ChatModels/               # Adapter Ollama/Modal OpenAI-compatible
├── DataProcess/              # Loader đề bài, không đọc solution khi generate
├── vendor_rethinkmcts/       # Repo tác giả, pin commit để audit, không sửa
├── rethinkmcts/              # Native implementation của tree/search/reward
├── Models/                   # Reserved cho model/MCTS cũ
├── tests/                    # Unit test offline
├── tools/                    # Smoke/check script không thuộc pipeline chính
│
└── outputs/                  # Artifact sinh tự động, không sửa thủ công
    ├── baselines/
    │   ├── direct_generation/
    │   ├── batch_manifests/
    │   ├── evaluations/
    │   └── pipeline_logs/
    └── rethinkmcts/
        └── <run>/<model>/<dataset>/<problem_id>/
```

Quy ước quan trọng:

- `data/` là input; không sửa trực tiếp file raw hoặc Arrow.
- `data/samples/benchmark_v2/` là cohort chung cho các model và MCTS sau này.
- `data/samples/evaluation_v1/` giữ nguyên để truy vết kết quả baseline 100+100.
- `outputs/` là output; mỗi run được tách theo `run/model/dataset`.
- Không dùng CodeContests trong phạm vi hiện tại.
- Native search không ghi artifact vào `outputs/baselines/`; hai namespace được tách độc lập.

## Môi trường

Luôn dùng virtual environment của project:

```powershell
cd D:\ReThinkMCTS
.\venv\Scripts\python.exe --version
```

Cài dependency nếu cần:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

Provider, endpoint và model được lấy từ `.env`. Không commit `.env` và không ghi
secret vào log. Chi tiết xem [docs/llm-provider.md](docs/llm-provider.md).

## Workflow benchmark

### 1. Kiểm tra kế hoạch, không gọi LLM

```powershell
.\venv\Scripts\python.exe -m pipelines `
  --stage generate `
  --dataset apps `
  --run-name <run_name> `
  --config baselines/direct_generation/configs/qwen25_coder_7b_instruct.json `
  --plan
```

### 2. Sinh code toàn bộ dataset

Generation full không dùng sample judge. Resume mặc định bỏ qua artifact đã hoàn chỉnh:

```powershell
.\venv\Scripts\python.exe -m pipelines `
  --stage generate `
  --dataset all `
  --run-name <run_name> `
  --config baselines/direct_generation/configs/qwen25_coder_7b_instruct.json `
  --generation-workers 1 `
  --delay 1 `
  --confirm-full-run
```

### 3. Đánh giá cohort cố định cho run mới

Dùng run name mới cho cohort 300+164; không chạy lại trên cùng namespace
evaluation 100+100 cũ. Generation vẫn sinh full, còn evaluation chọn theo
hai manifest dưới đây. Số liệu baseline hiện tại ở đầu README **không** phải
kết quả của cohort mới.

APPS:

```powershell
.\venv\Scripts\python.exe -m pipelines `
  --stage evaluate `
  --dataset apps `
  --run-name <run_name> `
  --model <model> `
  --sample-file data/samples/benchmark_v2/apps_test_300.json `
  --workers 8 `
  --test-workers 4 `
  --evaluation-timeout 300 `
  --confirm-full-run
```

HumanEval:

```powershell
.\venv\Scripts\python.exe -m pipelines `
  --stage evaluate `
  --dataset humaneval `
  --run-name <run_name> `
  --model <model> `
  --sample-file data/samples/benchmark_v2/humaneval_test_164.json `
  --workers 8 `
  --evaluation-timeout 300 `
  --confirm-full-run
```

`--workers` chạy nhiều bài đồng thời. `--test-workers` chỉ áp dụng cho APPS và
chạy các test độc lập trong một bài đồng thời. Không chạy hai evaluator cùng lúc
trên một run/model vì chúng ghi chung artifact evaluation.

### 4. Tạo bảng benchmark

Chỉ chạy sau khi cả hai dataset đã có `results.jsonl` và `summary.json`:

```powershell
.\venv\Scripts\python.exe -m evaluation.benchmark_judge `
  --run-name <run_name> `
  --model <model>
```

### 5. Kiểm thử native RethinkMCTS offline

Lệnh dưới đây chỉ chạy fake LLM/executor trong unit test, không gọi provider:

```powershell
.\venv\Scripts\python.exe -m unittest discover -s tests -v
```

Xem kế hoạch search của một bài mà không khởi tạo client:

```powershell
.\venv\Scripts\python.exe -m rethinkmcts `
  --dataset humaneval `
  --problem-id 0 `
  --run-name rethinkmcts_v1 `
  --model qwen2.5-coder:7b-instruct `
  --rollouts 2 `
  --width 3 `
  --plan
```

Smoke provider thật chỉ được chạy sau khi duyệt output offline; xem
[docs/runbooks/rethinkmcts-smoke.md](docs/runbooks/rethinkmcts-smoke.md).

## Đọc kết quả

Kết quả chấm gốc nằm dưới `outputs/baselines/evaluations/<run>/<model>/`.
Với benchmark mới 300 APPS + 164 HumanEval, bảng đã khóa cùng tham số chạy,
cohort, hash dữ liệu/code và chỉ mục candidate nằm tại
`outputs/benchmarks/<run>/<model>/` (`run.json`, `candidates.csv`,
`benchmark_table.md`). Bảng đối chiếu nhiều run nằm trong
`outputs/benchmarks/comparisons/<name>/`; xem
[docs/benchmark-results.md](docs/benchmark-results.md). Cohort 100+100 trước
đây là kết quả lịch sử riêng, không trộn vào benchmark mới.

```text
outputs/baselines/evaluations/<run>/<model>/
├── benchmark_table.md       # Bảng paper-style, dễ đọc
├── benchmark_table.csv      # Bảng để phân tích tiếp
├── benchmark_summary.json   # Metric + manifest + missing candidates
├── apps/
│   ├── results.csv/jsonl
│   ├── failures.csv/jsonl
│   ├── passed.jsonl
│   ├── summary.json
│   └── evaluation.log
└── humaneval/
    ├── results.csv/jsonl
    ├── failures.csv/jsonl
    ├── passed.jsonl
    ├── summary.json
    └── evaluation.log
```

Chi tiết expected/actual, lỗi runtime, timeout và test index nằm trong
`evaluation.json` cạnh artifact candidate:

```text
outputs/baselines/direct_generation/<run>/<model>/<dataset>/<problem_timestamp>/
├── solution.py
├── response.txt
├── metadata.json
├── problem.txt
└── evaluation.json
```

## Kiểm thử codebase

```powershell
.\venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Tài liệu tiếp theo

- [docs/executors.md](docs/executors.md): executor, timeout và schema report.
- [docs/pipeline-direct.md](docs/pipeline-direct.md): generate/evaluate song song.
- [docs/environment.md](docs/environment.md): Python environment.
- [docs/gpu/README.md](docs/gpu/README.md): GPU CKEY và Ollama.
- [docs/decisions.md](docs/decisions.md): các quyết định kiến trúc đã chốt.
- [docs/implementation-audit.md](docs/implementation-audit.md): phần paper/code còn cần đối chiếu.
- [docs/rethinkmcts-implementation.md](docs/rethinkmcts-implementation.md): native search và artifact.
