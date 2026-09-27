# Runbooks

Runbook là các lệnh thao tác có thể copy/chạy trực tiếp. Root
[README.md](../../README.md) là điểm vào chính; file này chỉ lập bản đồ thao tác.

## Runbook hiện tại

- [Full direct baseline](baseline-full.md): generation full, evaluation sample cố
  định và benchmark judge.

## Thứ tự vận hành

1. Kiểm tra `.env` và provider trong [llm-provider.md](../llm-provider.md).
2. Chạy `--plan` trước batch lớn.
3. Generation full không truyền `--sample-file`.
4. Evaluation dùng đúng manifest trong `data/samples/evaluation_v1/`.
5. Judge chỉ chạy sau khi cả APPS và HumanEval có `results.jsonl`.

## Quy tắc resume

- Generation mặc định skip artifact hoàn chỉnh.
- Evaluation mặc định skip candidate đã có `evaluation.json`.
- Không dùng `--no-resume` nếu chỉ muốn chạy tiếp.
- Không chạy hai evaluator cùng lúc trên cùng run/model.
- `outputs/` là artifact tự động; không sửa `solution.py` để làm thay đổi metric.
