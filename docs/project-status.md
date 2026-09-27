# Trạng thái dự án

## Quyet dinh benchmark moi nhat (2026-09-27)

- Model baseline: `qwen2.5-coder:7b-instruct` qua Ollama tren GPU CKEY.
- Generation: full 5.000 APPS test + 164 HumanEval test.
- Evaluation judge: 100 APPS + 100 HumanEval trong `data/samples/evaluation_v1/`.
- Sample `baseline_v1` van duoc giu lam tap tham chieu rieng.
- Direct baseline va MCTS ve sau phai dung lai dung sample judge, khong boc lai mau.
- Run moi: `qwen25_coder_7b_instruct_baseline_v1`.
- Output phan tach theo `run/model/dataset`; run cu Modal/Qwen van duoc giu trong
  `direct_full_v1/Qwen_Qwen3.8-2.4T-A95B` va khong duoc tron voi run moi.

## Van hanh hien tai

Direct baseline dang duoc mo rong thanh full run tren cung namespace
`qwen25_coder_7b_instruct_baseline_v1`: APPS 5.000 bai va HumanEval 164 bai.
Resume se bo qua artifact da hoan tat; hai sample manifest 100 bai van duoc giu
nguyen de lam tap doi chi when chay MCTS.

Cập nhật lần cuối: **2026-09-27**.

## Mục tiêu hiện tại

Chạy pipeline direct baseline hai checkpoint: sinh code bằng một LLM provider,
sau đó chấm candidate song song trên APPS/HumanEval. Chưa triển khai MCTS.

## Đã kiểm chứng

- Paper chính có tại `RelativeWork/2409.09584v2.pdf`, gồm 19 trang, arXiv
  `2409.09584v2`.
- Ghi chú kỹ thuật từ paper đã nằm tại `docs/theory-rethinkmcts.md`.
- APPS raw có đủ 5.000 bài train và 5.000 bài test.
- HumanEval Arrow load được đủ 164 bài test.
- APPS chỉ giữ một biểu diễn trên đĩa: `data/apps/raw`.
- `Executors/APPSExecutor.py` đã chấm được cả APPS `stdin_stdout` và `call_based`.
- `Executors/HumanevalExecutor.py` đã chạy được official harness từ Arrow.
- Executor chạy từng test/harness trong subprocess, có timeout, output clipping và
  report JSON gồm số test pass, tổng số test và pass rate.
- HumanEval được báo theo harness (`1/1` hoặc `0/1`), vì dataset không tách từng
  assertion thành test case độc lập.
- 26 unit tests đã pass, gồm baseline, executor và pipeline evaluation/logging.
- Smoke test trên dữ liệu thật: một solution có sẵn của APPS `test/0000` pass `3/3`
  test đầu trong tổng số 565 test; `HumanEval/0` pass official harness với code đúng.
- `Models/` đang rỗng.
- `ChatModels/modal_client.py` đã có adapter Modal OpenAI-compatible.
- `DataProcess/problem_loader.py` đã load đề APPS/HumanEval mà không đọc solution/test.
- `baselines/direct_generation/` đã tách CLI, pipeline và config khỏi root project.
- `baselines/generate_apps.py` và `baselines/generate_humaneval.py` cung cấp lệnh
  riêng, cùng tái sử dụng direct-generation pipeline.
- `baselines/run_apps_benchmark.py` và `run_humaneval_benchmark.py` hỗ trợ chạy
  khoảng/toàn bộ dataset, resume, manifest, delay và chặn full run vô ý.
- Batch generation hỗ trợ `--generation-workers`: nhiều request Modal đồng thời qua
  thread scheduler, còn manifest/log được ghi tuần tự ở process chính.
- `pipelines/direct_baseline.py` điều phối `generate -> evaluate`; generation lỗi thì
  evaluation không bắt đầu.
- `evaluation/batch_evaluation.py` chấm song song theo candidate bằng process pool,
  resume từ `evaluation.json` và tổng hợp JSONL/CSV/summary.
- Logging đã tách `passed.jsonl`, `failures.jsonl/csv`, `evaluation.log`; generation
  và pipeline cũng có log theo stage/problem. Báo cáo lỗi chỉ rõ bài, số test pass,
  index test fail, loại lỗi và artifact chi tiết.
- Smoke evaluation offline đã tạo đủ báo cáo; process pool chấm `HumanEval/0` pass
  `1/1` và APPS `test/0000` pass `3/3` test đầu.
- Baseline hỗ trợ config JSON, `--model` override và output phân cấp theo run/model.
- Config mặc định đặt `max_tokens=null`, nên Modal request không gửi giới hạn output
  thủ công; model/provider vẫn quyết định giới hạn context thực tế.
- Resume chỉ công nhận artifact có `response.txt` và code không rỗng cùng finish reason hoàn chỉnh;
  artifact rỗng hoặc `finish_reason=length` được tự động sinh lại và evaluator bỏ qua.
- Baseline hỗ trợ `--evaluate` để lưu `evaluation.json` cạnh `solution.py`; nếu không
  dùng cờ này, CLI in lệnh chấm lại artifact sau.
- 14 unit tests baseline đã pass; test concurrency xác nhận 2 generation worker
  thực sự chạy đồng thời mà không gọi Modal.
- Môi trường chuẩn tồn tại tại `D:\ReThinkMCTS\venv`, dùng Python 3.14.5 và pip 26.1.1.
- `requirements.txt` đã liệt kê dependency từ code hiện tại và import của repo gốc.
- Pip dry-run đã resolve thành công toàn bộ manifest trên Python 3.14.5; toàn bộ
  nhóm MCTS/PyTorch chưa được cài.
- Repo gốc chưa xuất hiện tại đường dẫn dự kiến `RethinkMCTS/`.
- LLM provider Modal đã được tích hợp và kiểm chứng; benchmark tiếp theo đang chuyển
  sang Ollama trên GPU thuê CKEY, chờ instance hoạt động và adapter provider chung.
- `.env` đã được dùng để gọi Modal thật; route/model hiện tại resolve được và run đã
  tạo artifact. Một cấu hình route sai trước đó trả 404 và đã được sửa.
- `test.py` lấy endpoint và model từ `.env`, không còn hard-code hai giá trị này.
- Các dependency cần cho direct baseline (`openai`, `python-dotenv`, `datasets`) đã
  được cài vào `venv`; nhóm MCTS/PyTorch chưa cài.
- Resume của `direct_full_v1` đã được kiểm chứng sau khi dừng giữa batch; số hoàn
  chỉnh/pending phải xem bằng `--plan` ngay trước mỗi lần chạy vì run đang thay đổi.
- Đã thuê instance CKEY GPU3 với `1x RTX 3090 24 GB`, image Open WebUI + Ollama;
  instance đang ở trạng thái khởi tạo tại thời điểm cập nhật.
- Kế hoạch provider mới là chạy Ollama trên GPU thuê với `qwen2.5-coder:7b-instruct`; chưa thực hiện
  smoke test vì instance chưa chuyển sang trạng thái hoạt động.
- Phạm vi benchmark hiện tại: generation full APPS 5.000 + HumanEval 164; judge
  evaluation sample 100 bài mỗi dataset theo `data/samples/evaluation_v1/`.

## Chưa hoàn thành

- Bổ sung container/VM sandbox trước khi chạy code model không tin cậy ở quy mô lớn.
- Clone và audit RethinkMCTS gốc trước giai đoạn MCTS.

## Blocker hiện tại

Modal generation đã gặp lỗi rate limit/usage limit và không còn là provider ưu tiên
cho benchmark tiếp theo. Cần hoàn tất setup Ollama trên instance CKEY trước khi gọi
LLM lại. Executor hiện chỉ cô lập bằng subprocess/timeout, chưa phải security
sandbox. RethinkMCTS vẫn chưa được triển khai.

## Bước tiếp theo đề xuất

1. Xem pipeline bằng `python -m pipelines --stage all --dataset all --limit 2 --plan`.
2. Chạy smoke pipeline 1-2 bài mỗi dataset qua Modal.
3. Kiểm tra candidate, generation manifest, evaluation và summary.
4. Chốt model/config/run-name rồi mới chạy full generation.
5. Chạy parallel evaluation sau khi generation hoàn tất.

## Cách cập nhật file này

Chỉ ghi vào mục "Đã kiểm chứng" sau khi đã chạy lệnh hoặc đọc nguồn trực tiếp. Mỗi
task làm thay đổi khả năng chạy project phải cập nhật file này trước khi kết thúc.
