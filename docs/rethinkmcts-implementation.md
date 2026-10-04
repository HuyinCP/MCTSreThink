# RethinkMCTS Native Implementation

## Trạng thái

Đã triển khai bản native và kiểm thử offline. Chưa gọi Ollama/Modal và chưa chạy benchmark
MCTS thật. Repo tác giả được giữ nguyên tại `vendor_rethinkmcts/` ở commit:

```text
3908cacd94feed849f671f6de39f0baec00ed72c
```

Windows không phân biệt hoa thường, nên không thể dùng đồng thời `RethinkMCTS/` và package
`rethinkmcts/`. Vì vậy `vendor_rethinkmcts/` là source audit, còn `rethinkmcts/` là code native.

## Package

```text
rethinkmcts/
├── config.py       # SearchConfig và hyperparameters paper
├── tree.py         # SearchNode, CandidateRecord
├── policies.py     # beta và P-UCB
├── parsing.py      # thought/score/code/feedback parser
├── prompts.py      # expansion, code, self-evaluation, feedback, rethink
├── reward.py       # Dual Evaluation reward
├── workflow.py     # LangGraph StateGraph và Pydantic WorkflowState
├── feedback/
│   ├── trace.py    # AST blocks + sys.settrace runtime values
│   └── verbal.py   # block-level feedback bundle
├── search.py       # Logic miền: expand, evaluate, feedback, backprop, rethink
├── runner.py       # loader, executor adapter, provider adapter, artifact writer
└── cli.py          # entry point một problem
```

## Quy tắc search

Điều phối hiện dùng LangGraph `StateGraph` tuần tự trong `workflow.py`:
`select -> expand -> evaluate -> (rethink -> evaluate)* -> advance -> finalize`.
`WorkflowState` là Pydantic model kiểm tra kiểu node/candidate, rollout và phase;
`ThoughtProposal` cũng được kiểm tra bằng Pydantic. P-UCB, reward, tree và
executor vẫn là code miền độc lập, không được thay bằng agent framework.

- Selection so trực tiếp P-UCB cho mọi child, kể cả child chưa thăm; không có
  ưu tiên cứng cho unvisited. Khi điểm bằng nhau, `--seed` điều khiển tie-break
  cục bộ, không đảm bảo LLM sinh kết quả xác định.
- Expansion mặc định sinh đúng `width=3` thought khác nhau và normalize
  reasonableness về tổng `1`; response thiếu/thừa/trùng bị báo lỗi.
- APPS public tests là nửa đầu `input_output.json`; private tests là phần còn lại.
- HumanEval public tests được lấy từ `given_tests` nếu dataset có, nếu không thì trích ví dụ
  `>>>` trong prompt; final evaluation dùng official harness.
- Self-evaluation chỉ được gọi khi public pass rate bằng `1.0`.
- Rethink thay thought gần nhất in-place, thử tối đa `max_rethink_times` lần sửa
  trong một lượt chọn. Mỗi lần sửa sinh và chấm code mới; dừng ngay khi public
  tests pass. Sau lần sửa cuối vẫn fail, nếu còn rollout thì node được Expansion
  với verbal feedback của candidate cuối (`RETHINK_NEXT`).
- Khi thay thought, visit/Q/prior của chính node được khởi tạo lại để không gán
  thống kê của action cũ cho action mới. Ancestor không đổi state nên giữ lịch
  sử backprop. Candidate cũ và snapshot thought của nó vẫn tồn tại độc lập.
- Search cuối cùng chọn candidate có reward cao nhất, sau đó mới chạy private evaluation.

## Artifact

```text
outputs/rethinkmcts/<run>/<model>/<dataset>/<problem_id>/
├── search_summary.json
├── tree.json
├── events.jsonl
├── final_solution.py
└── candidates/<candidate_id>/
    ├── thoughts.json
    ├── solution.py
    ├── response.txt
    ├── execution.json
    ├── feedback.json
    └── metadata.json
```

`events.jsonl` ghi event search và metadata request đã làm sạch gồm `request_id`,
operation/prompt version, model, finish reason và token usage; không ghi prompt hay
secret. `search_summary.json` lặp lại danh sách `llm_requests` cùng tổng request và
token usage để audit một run độc lập. `candidates/*/response.txt` giữ raw response,
còn `solution.py` là code sau bước bóc fenced response.
`candidates/*/thoughts.json` và trường `thoughts` trong metadata là snapshot
tại thời điểm candidate được chấm, không lấy từ node đã bị Rethink về sau.

Artifact hoàn chỉnh được resume tự động; không tạo request mới nếu đã có
`search_summary.json` và `final_solution.py`.
Graph hiện **không có checkpointer**: LangGraph không tự khôi phục một search
đang dở. Resume giữa chừng, retry provider và chạy nhiều problem song song
vẫn là công việc riêng; graph này không tự gọi LangSmith hay provider trong
offline test.

## Offline check

```powershell
.\venv\Scripts\python.exe -m unittest discover -s tests -v
```

Lệnh plan chỉ load problem/config và không khởi tạo LLM client:

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

## Khác biệt có chủ ý với repo gốc

- Dùng `ChatModels.OllamaClient`/`ModalClient` OpenAI-compatible thay cho `GPTChat` hard-code.
- Dùng `DataProcess` và `Executors` hiện tại thay cho loader/executor cũ.
- Thay phụ thuộc `pyext`/Unix signal bằng executor hiện tại và trace portable dựa trên AST +
  `sys.settrace`.
- Trace portable gán mỗi event vào một AST statement span, có snapshot biến trước/sau
  dựa trên các trace event liên tiếp và giới hạn số event. Đây **chưa phải CFG/basic
  block đầy đủ** như upstream; một số luồng đặc biệt (exception, nhiều statement
  cùng dòng) vẫn có thể thiếu chính xác. Cần audit thêm trước khi khẳng định tương đương
  block-level feedback của paper.
- Giữ public/private policy và công thức reward của paper; không thêm TLE-aware reward hoặc
  root-cause identification trong phiên bản này.
