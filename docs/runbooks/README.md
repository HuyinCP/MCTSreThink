# Runbook scope (2026-09-27)

Direct baseline đã hoàn tất với model `qwen2.5-coder:7b-instruct` qua Ollama.
Native RethinkMCTS đã sẵn sàng ở mức offline; runbook smoke ở bước tiếp theo sẽ
dùng cùng dataset/sample policy nhưng artifact riêng dưới `outputs/rethinkmcts/`.

# Runbooks

Runbook là các lệnh thao tác có thể copy/chạy trực tiếp. Root
[README.md](../../README.md) là điểm vào chính; file này chỉ lập bản đồ thao tác.

## Runbook hiện tại

- [Full direct baseline](baseline-full.md): generation full, evaluation sample cố
  định và benchmark judge.
- [RethinkMCTS smoke](rethinkmcts-smoke.md): test native offline và smoke một bài
  HumanEval/APPS sau khi duyệt output.

## Thứ tự vận hành

1. Đọc `docs/project-status.md` và kiểm tra `.env`/provider trong
   [llm-provider.md](../llm-provider.md).
2. Với direct baseline, chạy `--plan` trước batch lớn.
3. Với native RethinkMCTS, chạy unit test offline và `--plan` trước provider smoke.
4. Generation full không truyền `--sample-file`.
5. Evaluation dùng đúng manifest trong `data/samples/evaluation_v1/`.
6. Judge chỉ chạy sau khi cả APPS và HumanEval có `results.jsonl`.

## Quy tắc resume

- Generation mặc định skip artifact hoàn chỉnh.
- Evaluation mặc định skip candidate đã có `evaluation.json`.
- Không dùng `--no-resume` nếu chỉ muốn chạy tiếp.
- Không chạy hai evaluator cùng lúc trên cùng run/model.
- `outputs/` là artifact tự động; không sửa `solution.py` để làm thay đổi metric.
