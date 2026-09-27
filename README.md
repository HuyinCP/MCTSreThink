# ReThinkMCTS Project

## Benchmark baseline hien tai

Benchmark hien tai dung `qwen2.5-coder:7b-instruct` qua Ollama. Generation chay
full APPS/HumanEval; judge evaluation chay 100 bai moi dataset theo manifest
`data/samples/evaluation_v1/`. Huong dan lenh day du nam tai
[baselines/README.md](baselines/README.md).

Runbook thao tac theo tung buoc nam tai
[docs/runbooks/baseline-full.md](docs/runbooks/baseline-full.md).

Đề tài: **Cải thiện khả năng suy luận của LLM trong sinh mã nguồn bằng Monte Carlo
Tree Search với phản hồi từ kiểm thử tự động**.

## Trạng thái hiện tại

Dự án đang ở giai đoạn **direct-generation baseline và đánh giá offline**: gửi một
bài cho LLM qua Ollama trên GPU CKEY, lưu code, rồi chấm bằng executor APPS/HumanEval.
Chưa triển khai MCTS.

Điểm bắt đầu khi mở project:

1. Đọc [docs/README.md](docs/README.md) để biết vai trò từng tài liệu.
2. Đọc [docs/project-status.md](docs/project-status.md) để biết trạng thái đã kiểm chứng.
3. Đọc [docs/plan.md](docs/plan.md) trước khi chọn công việc tiếp theo.

Cấu hình LLM dùng Ollama/Modal được mô tả tại
[docs/llm-provider.md](docs/llm-provider.md). Secret chỉ nằm trong `.env` cục bộ.

Môi trường Python chuẩn là `D:\ReThinkMCTS\venv`; xem
[docs/environment.md](docs/environment.md) trước khi cài dependency.

## Cấu trúc chính

```text
ReThinkMCTS/
├── docs/                # Lý thuyết, kế hoạch, trạng thái và quyết định
├── baselines/           # Các baseline, config và entry point độc lập
├── data/                # APPS, HumanEval và script chuẩn bị dữ liệu
├── RelativeWork/        # Paper tham khảo
├── Executors/           # Chạy test APPS/HumanEval và xuất report JSON
├── Models/              # Chưa có implementation
├── ChatModels/          # Chưa có implementation
└── DataProcess/         # Chưa có implementation
```

Chi tiết dataset và cách đọc dữ liệu nằm tại [data/README.md](data/README.md).
Cách chạy baseline nằm tại [docs/baseline-direct.md](docs/baseline-direct.md).
Cách chấm code nằm tại [docs/executors.md](docs/executors.md).

Lệnh sinh code nhanh theo từng dataset:

```powershell
.\venv\Scripts\python.exe -m baselines.generate_apps --problem-id 0
.\venv\Scripts\python.exe -m baselines.generate_humaneval --problem-id 0
```

Artifact được lưu dưới `outputs/baselines/direct_generation/`; thêm `--evaluate`
để tạo luôn `evaluation.json` cạnh `solution.py`.

Xem trước batch benchmark cố định mà không gọi API:

```powershell
.\venv\Scripts\python.exe -m pipelines --stage generate --dataset apps `
  --run-name qwen25_coder_7b_instruct_baseline_v1 `
  --config baselines/direct_generation/configs/qwen25_coder_7b_instruct.json `
  --sample-file data/samples/baseline_v1/apps_test_100.json --plan
```

Pipeline chính thức sinh toàn bộ code trước rồi mới chấm song song:

```powershell
.\venv\Scripts\python.exe -m pipelines `
  --stage all --dataset all --run-name direct_smoke_v1 --limit 2 --workers 2 --plan
```

Xem hướng dẫn benchmark 100+100 tại [baselines/README.md](baselines/README.md) và
[docs/pipeline-direct.md](docs/pipeline-direct.md).

Sau evaluation, xem nhanh bài sai tại `failures.csv` hoặc `evaluation.log` dưới
`outputs/baselines/evaluations/<run>/<model>/<dataset>/`.
