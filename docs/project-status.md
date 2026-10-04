# Trạng thái dự án

Cập nhật lần cuối: **2026-10-04**.

## Giai đoạn hiện tại

Dự án đã hoàn thành checkpoint **DIRECT-GENERATION + OFFLINE EVALUATION** và đã có
bản native **RethinkMCTS implementation-ready-for-smoke-test**. Chưa gọi LLM và
chưa chạy benchmark MCTS thật.

## Baseline đã hoàn thành

| Thuộc tính | Giá trị |
|---|---|
| Model | `qwen2.5-coder:7b-instruct` |
| Provider | Ollama trên GPU CKEY |
| Run | `qwen25_coder_7b_instruct_baseline_v1` |
| Generation | APPS test 5.000 + HumanEval test 164 |
| Judge sample | APPS 100 + HumanEval 100 |
| Sample manifest | `data/samples/evaluation_v1/` |

Kết quả judge đã kiểm chứng:

| Nhóm | Pass Rate (%) | Pass@1 (%) |
|---|---:|---:|
| APPS Intro. | 39.02 | 23.08 |
| APPS Inter. | 26.14 | 7.46 |
| APPS Comp. | 25.09 | 0.00 |
| APPS Overall | 27.60 | 8.00 |
| HumanEval | N/A | 84.00 |

Artifact tổng hợp:

```text
outputs/baselines/evaluations/
└── qwen25_coder_7b_instruct_baseline_v1/
    └── qwen2.5-coder_7b-instruct/
        ├── benchmark_table.md
        ├── benchmark_table.csv
        ├── benchmark_summary.json
        ├── apps/
        └── humaneval/
```

## Đã kiểm chứng

- Dataset cục bộ có APPS train/test, mỗi split 5.000 bài.
- HumanEval Arrow có 164 bài test.
- Sample judge có đúng 100 ID duy nhất cho mỗi dataset và được khóa bằng seed.
- Generation lưu `solution.py`, `response.txt`, `metadata.json` và `problem.txt`
  theo `run/model/dataset/problem_timestamp`.
- APPS executor hỗ trợ `stdin_stdout` và `call_based`.
- HumanEval executor dùng official harness.
- Evaluation chạy song song theo candidate; APPS còn hỗ trợ song song test bằng
  `--test-workers`.
- Judge tạo macro Pass Rate, micro Pass Rate và Pass@1 cho APPS; HumanEval chỉ
  báo Pass@1 theo quy ước đã chốt.
- Unit test hiện tại pass `45/45`, gồm direct baseline, executor, judge, pipeline
  và native RethinkMCTS.
- Code generated của baseline không bị thay đổi trong quá trình cleanup tài liệu.
- Run cũ Modal/Qwen được giữ riêng trong namespace `direct_full_v1`.
- Repo tác giả được pin tại `vendor_rethinkmcts/` ở commit
  `3908cacd94feed849f671f6de39f0baec00ed72c`.
- Native package nằm tại `rethinkmcts/`, artifact tách dưới `outputs/rethinkmcts/`.
- Native selection, vòng Rethink, candidate thought snapshot và APPS call-based
  trace đã được chỉnh theo audit; xem `docs/implementation-audit.md`.

## Quyết định phạm vi

- Không dùng CodeContests.
- Generation full và evaluation sample là hai phạm vi độc lập.
- Mọi model/MCTS sau này phải dùng lại `data/samples/evaluation_v1/` khi cần
  so sánh công bằng.
- Candidate bị manual stop được ghi rõ trong `evaluation.json`, không sửa
  `solution.py`.

## Chưa hoàn thành

- Chạy smoke thật một bài HumanEval và một bài APPS với Ollama trên GPU CKEY.
- Đối chiếu output native với log/reward của repo gốc sau khi có smoke run.
- Thay trace AST hiện tại bằng CFG/basic-block đầy đủ nếu cần đối chiếu feedback
  chính xác với repo gốc.
- Tách executor vào sandbox/container có giới hạn mạng, CPU và RAM thật sự.
- Thiết kế experiment runner cho 100 bài sample và nhiều model/rollout.

## Cách cập nhật

Chỉ ghi một điều vào mục đã kiểm chứng sau khi đọc trực tiếp file, chạy lệnh hoặc
đối chiếu nguồn. Khi thay đổi dataset, sample, output schema hoặc workflow, cập
nhật thêm `data/README.md`, `docs/decisions.md` và runbook liên quan.
