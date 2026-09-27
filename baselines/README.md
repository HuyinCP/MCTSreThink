# Baselines

## Benchmark tham chieu: 100 bai moi dataset

Baseline benchmark chinh hien tai dung model Ollama `qwen2.5-coder:7b-instruct`.
Judge khong boc sample moi moi lan chay. Hai sample manifest tham chieu
co dinh la:

- `data/samples/baseline_v1/apps_test_100.json`: 100 bai APPS test.
- `data/samples/baseline_v1/humaneval_test_100.json`: 100 bai HumanEval test.

Manifest ghi ro seed, population size va danh sach `problem_ids`. Khi gan MCTS,
phai tai lai dung file nay de so sanh cong bang voi direct baseline.

Run name full hien tai: `qwen25_coder_7b_instruct_baseline_v1`. Run nay mo rong tu
tap 100 bai sang full APPS test + HumanEval test; artifact da co trong cung
run/model se duoc skip.

Sau khi full generation hoan tat, evaluation chi chay sample judge moi:
`data/samples/evaluation_v1/apps_test_100.json` va
`data/samples/evaluation_v1/humaneval_test_100.json`. Sau hai evaluation, chay:

```powershell
.\venv\Scripts\python.exe -m evaluation.benchmark_judge `
  --run-name qwen25_coder_7b_instruct_baseline_v1 `
  --model qwen2.5-coder:7b-instruct
```
Ten folder model duoc sanitize boi pipeline thanh `qwen2.5-coder_7b-instruct`
(dau `:` khong nam trong ten folder Windows).

Tat ca artifact moi deu duoc tach theo model. Huong dan van hanh day du nam tai
[`docs/runbooks/baseline-full.md`](../docs/runbooks/baseline-full.md).

```text
outputs/baselines/direct_generation/<run>/<model>/<dataset>/
outputs/baselines/batch_manifests/<run>/<model>/
outputs/baselines/evaluations/<run>/<model>/<dataset>/
```

Lenh xem truoc, khong goi LLM:

```powershell
.\venv\Scripts\python.exe -m pipelines `
  --stage generate `
  --dataset apps `
  --run-name qwen25_coder_7b_instruct_baseline_v1 `
  --config baselines/direct_generation/configs/qwen25_coder_7b_instruct.json `
  --sample-file data/samples/baseline_v1/apps_test_100.json `
  --generation-workers 1 `
  --plan

.\venv\Scripts\python.exe -m pipelines `
  --stage generate `
  --dataset humaneval `
  --run-name qwen25_coder_7b_instruct_baseline_v1 `
  --config baselines/direct_generation/configs/qwen25_coder_7b_instruct.json `
  --sample-file data/samples/baseline_v1/humaneval_test_100.json `
  --generation-workers 1 `
  --plan
```

Sau khi generation hoan tat, chay evaluation voi cung sample file. Resume se bo
qua artifact da co cua dung model/run/problem.

Lenh chay that tren GPU CKEY (can dat `LLM_PROVIDER=ollama` trong `.env`):

```powershell
$run = "qwen25_coder_7b_instruct_baseline_v1"
$config = "baselines/direct_generation/configs/qwen25_coder_7b_instruct.json"

# 1. Generate APPS: 100 bai
.\venv\Scripts\python.exe -m pipelines `
  --stage generate --dataset apps --run-name $run --config $config `
  --sample-file data/samples/baseline_v1/apps_test_100.json `
  --generation-workers 1 --delay 1 --confirm-full-run

# 2. Generate HumanEval: 100 bai
.\venv\Scripts\python.exe -m pipelines `
  --stage generate --dataset humaneval --run-name $run --config $config `
  --sample-file data/samples/baseline_v1/humaneval_test_100.json `
  --generation-workers 1 --delay 1 --confirm-full-run

# 3. Evaluate APPS
.\venv\Scripts\python.exe -m pipelines `
  --stage evaluate --dataset apps --run-name $run `
  --model qwen2.5-coder:7b-instruct `
  --sample-file data/samples/baseline_v1/apps_test_100.json `
  --workers 4 --confirm-full-run

# 4. Evaluate HumanEval
.\venv\Scripts\python.exe -m pipelines `
  --stage evaluate --dataset humaneval --run-name $run `
  --model qwen2.5-coder:7b-instruct `
  --sample-file data/samples/baseline_v1/humaneval_test_100.json `
  --workers 4 --confirm-full-run
```

Code sinh ra nam tai
`outputs/baselines/direct_generation/qwen25_coder_7b_instruct_baseline_v1/qwen2.5-coder_7b-instruct/`.
Bao cao cham nam tai `outputs/baselines/evaluations/` voi cung run/model/dataset.

Mỗi baseline nằm trong một package riêng và tự quản lý:

- CLI/entry point.
- Prompt version.
- Config tham số generation.
- Cấu trúc artifact.
- Unit test liên quan.

```text
baselines/
├── README.md
├── generate_apps.py
├── generate_humaneval.py
├── run_apps_benchmark.py
├── run_humaneval_benchmark.py
├── batch_generation.py
└── direct_generation/
    ├── __init__.py
    ├── __main__.py
    ├── cli.py
    ├── pipeline.py
    └── configs/
        └── default.json
```

Artifact của từng baseline được tách namespace dưới `outputs/baselines/`. Khi thêm
baseline mới, không ghi output vào namespace của baseline khác.

Hai entry point theo dataset chỉ cố định `--dataset`; toàn bộ logic gọi LLM, prompt,
config và lưu artifact vẫn dùng chung trong `direct_generation/`:

```powershell
.\venv\Scripts\python.exe -m baselines.generate_apps --problem-id 0 --dry-run
.\venv\Scripts\python.exe -m baselines.generate_humaneval --problem-id 0 --dry-run
```

Hai batch entry point chạy một khoảng hoặc toàn bộ dataset, có plan/resume/manifest:

```powershell
.\venv\Scripts\python.exe -m baselines.run_apps_benchmark --plan
.\venv\Scripts\python.exe -m baselines.run_humaneval_benchmark --plan
```

Model identifier không phải secret và có thể override bằng CLI để benchmark. Endpoint
và token vẫn chỉ lấy từ `.env`.

## Quick start: full direct baseline

Các lệnh dưới đây dùng PowerShell và chạy từ root project:

```powershell
Set-Location D:\ReThinkMCTS
```

Pipeline chính thức có hai checkpoint:

```text
generate toàn bộ code -> evaluate song song toàn bộ candidate
```

### 1. Kiểm tra kế hoạch

Không gọi Modal và không chạy candidate:

```powershell
.\venv\Scripts\python.exe -m pipelines `
  --stage generate `
  --dataset all `
  --run-name direct_full_v1 `
  --plan
```

Kết quả dự kiến là 5.000 bài APPS test và 164 bài HumanEval, tương ứng 5.164
request LLM trước retry.

### 2. Chạy thử trước khi full

Sinh hai bài mỗi dataset, sau đó chấm bằng hai worker:

```powershell
.\venv\Scripts\python.exe -m pipelines `
  --stage all `
  --dataset all `
  --run-name direct_smoke_v1 `
  --limit 2 `
  --workers 2
```

### 3. Sinh toàn bộ code

Lệnh này chỉ gọi LLM và lưu candidate, chưa thực thi code sinh ra:

```powershell
.\venv\Scripts\python.exe -m pipelines `
  --stage generate `
  --dataset all `
  --run-name direct_full_v1 `
  --generation-workers 2 `
  --delay 1 `
  --confirm-full-run
```

Lệnh trên giữ tối đa 2 request Modal đang xử lý đồng thời, mỗi request tương ứng
với một bài toán. `--delay 1` giãn thời điểm cấp request mới để giảm nguy cơ rate
limit. Nếu muốn kiểm tra trước mà không gọi LLM, thêm
`--generation-workers 2 --plan` vào lệnh kiểm tra kế hoạch ở bước 1.

Candidate được lưu tại:

```text
outputs/baselines/direct_generation/direct_full_v1/<model>/
├── apps/
└── humaneval/
```

Liệt kê generation log:

```powershell
Get-ChildItem outputs\baselines\batch_manifests\direct_full_v1 `
  -Filter *.log -Recurse |
  Select-Object FullName
```

Theo dõi APPS log trong một PowerShell khác mà không cần nhập tên model:

```powershell
$appsLog = Get-ChildItem outputs\baselines\batch_manifests\direct_full_v1 `
  -Filter apps.log -Recurse |
  Select-Object -First 1

Get-Content $appsLog.FullName -Wait
```

Theo dõi HumanEval log:

```powershell
$humanEvalLog = Get-ChildItem outputs\baselines\batch_manifests\direct_full_v1 `
  -Filter humaneval.log -Recurse |
  Select-Object -First 1

Get-Content $humanEvalLog.FullName -Wait
```

Resume bật mặc định. Nếu tiến trình bị ngắt, chạy lại nguyên lệnh generation; các
bài có `response.txt` và `solution.py` không rỗng cùng finish reason hoàn chỉnh sẽ
được bỏ qua. Bài rỗng hoặc bị `finish_reason=length` sẽ tự động được sinh lại.

Config mặc định không gửi `max_tokens` tới Modal. Model/provider vẫn áp dụng giới
hạn context của nó; dùng `--max-tokens N` khi muốn đặt giới hạn thủ công.

### 4. Chấm song song

Chỉ chạy sau khi full generation đã hoàn tất:

```powershell
.\venv\Scripts\python.exe -m pipelines `
  --stage evaluate `
  --dataset all `
  --run-name direct_full_v1 `
  --workers 4 `
  --confirm-full-run
```

Bắt đầu với 4 worker. Chỉ tăng lên 8 sau khi đã kiểm tra CPU và RAM. Evaluation
resume từ `evaluation.json`, nên có thể chạy lại cùng lệnh sau khi bị gián đoạn.

### 5. Xem kết quả

Liệt kê summary của cả hai dataset mà không cần nhập tên model:

```powershell
Get-ChildItem outputs\baselines\evaluations\direct_full_v1 `
  -Filter summary.json -Recurse |
  ForEach-Object {
    Write-Host "`n=== $($_.Directory.Name) ==="
    Get-Content $_.FullName
  }
```

Liệt kê tất cả bài sai:

```powershell
Get-ChildItem outputs\baselines\evaluations\direct_full_v1 `
  -Filter failures.csv -Recurse |
  ForEach-Object { Import-Csv $_.FullName } |
  Select-Object dataset, problem_id, failure_type, passed_tests, total_tests, pass_rate
```

Các file kết quả của mỗi dataset:

```text
outputs/baselines/evaluations/direct_full_v1/<model>/<dataset>/
├── summary.json
├── results.csv
├── results.jsonl
├── failures.csv
├── failures.jsonl
├── passed.jsonl
└── evaluation.log
```

Chi tiết expected, actual và traceback của một bài nằm trong `evaluation.json` cạnh
`solution.py` của bài đó.

## Tùy chọn thường dùng

| Tham số | Ý nghĩa |
|---|---|
| `--stage generate` | Chỉ sinh code |
| `--stage evaluate` | Chỉ chấm artifact đã sinh |
| `--stage all` | Sinh xong toàn bộ rồi mới chấm |
| `--dataset all` | Chạy cả APPS test và HumanEval |
| `--limit N` | Chỉ chạy N bài đầu mỗi dataset |
| `--workers N` | Số candidate được chấm song song |
| `--generation-workers N` | Số request Modal sinh code đồng thời; lệnh full baseline dùng 2 |
| `--delay N` | Nghỉ N giây giữa hai request Modal |
| `--retries N` | Số lần gọi lại khi request lỗi; mặc định 0 |
| `--no-resume` | Chủ ý bỏ qua resume và chạy lại |
| `--confirm-full-run` | Bắt buộc khi chọn hơn 20 bài |
| `--plan` | Chỉ in kế hoạch, không gọi LLM/chạy candidate |

Full generation tạo 5.164 request trước retry. Full evaluation thực thi code do model
sinh; subprocess/timeout hiện chưa phải security sandbox, vì vậy nên dùng container
hoặc VM khi cần cô lập code không tin cậy.

Generation song song chỉ giảm wall-clock time khi Modal deployment xử lý được nhiều
request đồng thời; nó không giảm tổng token hoặc chi phí. Nếu gặp 429/rate limit,
giảm `--generation-workers` về 1 hoặc 2.

Chi tiết pipeline và schema log nằm tại
[`docs/pipeline-direct.md`](../docs/pipeline-direct.md).
