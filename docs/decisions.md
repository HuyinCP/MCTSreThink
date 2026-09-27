# Nhật ký quyết định

Các quyết định ở đây được xem là đang có hiệu lực cho tới khi có entry mới thay thế.

## D-018: Full generation, sampled evaluation judge

- Ngày: 2026-09-27
- Trạng thái: Chấp nhận
- Quyết định: Generation chay full APPS test + HumanEval test. Evaluation chi
  chay 100 bai moi dataset theo manifest `data/samples/evaluation_v1/`.
- Metric APPS: macro Pass Rate la metric chinh, micro Pass Rate la metric phu,
  va Pass@1 la ty le bai pass toan bo test. HumanEval chi bao Pass@1.
- Lý do: Giữ toàn bộ candidate để tái sử dụng, nhưng giới hạn chi phí thực thi và
  giữ một tập judge cố định để so sánh model/MCTS.
- Ràng buộc: Không sample lại khi chấm; không dùng sample judge làm giới hạn
  generation; missing candidate vẫn nằm trong denominator của Pass Rate/Pass@1.

## D-017: Khoa sample benchmark va tach model output

- Ngày: 2026-09-27
- Trạng thái: Chấp nhận
- Quyết định: Baseline hiện tại dùng `qwen2.5-coder:7b-instruct` qua Ollama và
  judge 100 bài APPS test + 100 bài HumanEval test trong hai manifest cố định tại
  `data/samples/evaluation_v1/`. `baseline_v1` chỉ giữ để truy vết lịch sử.
- Lý do: Giam chi phi, tranh sample drift va tao tap so sanh co dinh cho MCTS sau nay.
- Ràng buộc: Moi lan chay generation/evaluation phai dung cung sample file; output
  phai nam duoi `outputs/baselines/<stage>/<run>/<model>/<dataset>/`. Run cu cua
  model Modal/Qwen duoc giu rieng, khong tron voi run moi.

## D-001: Baseline trước, đóng góp sau

- Ngày: 2026-09-26
- Trạng thái: Chấp nhận
- Quyết định: Phải hiểu và chạy được RethinkMCTS gốc trước khi viết MCTS riêng hoặc
  thêm reward/root-cause mới.
- Lý do: Cần baseline quan sát được để tránh triển khai dựa trên giả định sai.

## D-002: Chỉ dùng APPS và HumanEval

- Ngày: 2026-09-26
- Trạng thái: Chấp nhận
- Quyết định: Không dùng CodeContests trong phạm vi dự án.
- Lý do: Tập trung tái lập setup của paper và giới hạn khối lượng chuẩn bị dữ liệu.

## D-003: APPS chỉ giữ bản raw

- Ngày: 2026-09-26
- Trạng thái: Chấp nhận
- Quyết định: Chỉ giữ `data/apps/raw`; không giữ bản Arrow trùng lặp.
- Lý do: Repo gốc cần cấu trúc raw và bản Arrow chiếm thêm khoảng 1,33 GB.

## D-004: HumanEval giữ bản Arrow

- Ngày: 2026-09-26
- Trạng thái: Chấp nhận
- Quyết định: Giữ HumanEval tại `data/humaneval/arrow`.
- Lý do: Dataset nhỏ, load trực tiếp được và chưa có yêu cầu từ repo gốc buộc đổi dạng.

## D-005: Tài liệu có source of truth

- Ngày: 2026-09-26
- Trạng thái: Chấp nhận
- Quyết định: Mỗi loại thông tin có một file chịu trách nhiệm theo `docs/README.md`.
- Lý do: Tránh đường dẫn, trạng thái và số liệu mâu thuẫn giữa nhiều file Markdown.

## D-006: Sử dụng LLM qua Modal.com

- Ngày: 2026-09-26
- Trạng thái: Chấp nhận
- Quyết định: Dùng endpoint OpenAI-compatible trên Modal.com; cấu hình endpoint,
  token và model qua `.env`.
- Lý do: Tách provider/runtime khỏi code và cho phép thay đổi deployment mà không sửa
  thuật toán.
- Ràng buộc: Không commit secret, không hard-code endpoint/model, và mọi smoke test
  phải giới hạn request để kiểm soát chi phí.

## D-007: Virtual environment chuẩn

- Ngày: 2026-09-26
- Trạng thái: Chấp nhận
- Quyết định: Toàn bộ Python/pip của dự án dùng `D:\ReThinkMCTS\venv`.
- Lý do: Tránh dependency global và giữ một môi trường chung có thể kiểm tra.
- Ràng buộc: Mọi thay đổi Python version hoặc dependency phải cập nhật
  `requirements.txt`, `docs/environment.md` và `project-status.md`.

## D-008: Direct generation trước evaluation và MCTS

- Ngày: 2026-09-26
- Trạng thái: Chấp nhận
- Quyết định: Baseline đầu tiên chỉ gửi một bài cho LLM và lưu code trả về.
- Chưa bao gồm: chạy code, test pass/fail, reward, tree search hoặc rethink.
- Lý do: Xác minh riêng data-to-prompt-to-code pipeline trước khi thêm execution và
  search, giúp lỗi ở mỗi tầng dễ quan sát hơn.

## D-009: Mỗi baseline có package và namespace artifact riêng

- Ngày: 2026-09-26
- Trạng thái: Chấp nhận
- Quyết định: Baseline nằm dưới `baselines/<name>/`, có config versioned và output
  dưới `outputs/baselines/<name>/<run>/<model>/`.
- Lý do: Cho phép benchmark nhiều model, prompt và sampling parameters mà không trộn
  code hoặc artifact giữa các phương pháp.
- Ràng buộc: Secret/endpoint vẫn nằm trong `.env`; config benchmark chỉ chứa model
  identifier và tham số không nhạy cảm.

## D-010: Tách sinh code và chấm code thành hai tầng

- Ngày: 2026-09-26
- Trạng thái: Chấp nhận
- Quyết định: Core direct generation chỉ sinh artifact; `Executors/` nhận source
  code và trả `ExecutionReport` thống nhất cho APPS/HumanEval. CLI có thể điều phối
  hai tầng khi người dùng chọn rõ `--evaluate`, nhưng không trộn logic executor vào
  pipeline sinh code.
- Lý do: Cho phép tái chấm cùng candidate, thay executor hoặc benchmark nhiều model
  mà không phải gọi lại LLM.
- Quy ước: APPS tính theo từng test trong `input_output.json`; HumanEval tính theo
  toàn bộ official harness (`1/1` hoặc `0/1`), không tự tách các câu assert.
- Ràng buộc: Subprocess và timeout không phải security sandbox. Chạy quy mô lớn cần
  thêm container/VM, tắt mạng và giới hạn tài nguyên ở tầng hệ điều hành.

## D-011: Entry point riêng theo dataset, implementation dùng chung

- Ngày: 2026-09-26
- Trạng thái: Chấp nhận
- Quyết định: Người dùng chạy `baselines.generate_apps` hoặc
  `baselines.generate_humaneval`; hai wrapper cố định dataset và gọi chung
  `baselines.direct_generation.cli`.
- Lý do: Lệnh ngắn, khó chọn nhầm dataset nhưng không nhân đôi logic gọi Modal,
  prompt, config hoặc lưu artifact.
- Quy ước: Output mặc định luôn nằm dưới
  `outputs/baselines/direct_generation/<run>/<model>/<dataset>/` của project.

## D-012: Full benchmark phải resumable và có xác nhận

- Ngày: 2026-09-26
- Trạng thái: Chấp nhận
- Quyết định: APPS và HumanEval có batch entry point riêng nhưng dùng chung bộ điều
  phối tuần tự. Resume bật mặc định và mỗi kết quả được ghi vào JSONL manifest.
- Lý do: Full APPS test + HumanEval cần 5.164 request; batch phải tiếp tục được sau
  lỗi hoặc gián đoạn mà không mặc định gọi lại các bài đã hoàn thành.
- Ràng buộc: Chọn hơn 20 bài cần `--confirm-full-run`; retry mặc định bằng 0 và phải
  có `--plan` để xem model, số bài, output và manifest trước khi chạy.

## D-013: Generation hoàn tất trước parallel evaluation

- Ngày: 2026-09-26
- Trạng thái: Chấp nhận
- Quyết định: Pipeline chính có hai checkpoint. Toàn bộ generation của các dataset
  đã chọn phải thành công trước khi evaluation bắt đầu. Evaluation song song theo
  candidate bằng process pool; test trong một candidate không dùng pool lồng nhau.
- Lý do: Tách chi phí/gọi LLM khỏi thực thi code, cho phép chấm lại không gọi model,
  và giữ mức song song có thể kiểm soát trên Windows.
- Artifact: Mỗi candidate có `evaluation.json`; mỗi run/model/dataset có
  `results.jsonl`, `results.csv` và `summary.json`.
- Ràng buộc: Mặc định tối đa 4 worker. Process isolation hiện tại không thay thế
  container/VM sandbox cho code không tin cậy.

## D-014: Log phải truy ngược được tới problem và test fail

- Ngày: 2026-09-26
- Trạng thái: Chấp nhận
- Quyết định: Generation, pipeline stage và evaluation đều có text log; evaluation
  còn tách `passed.jsonl`, `failures.jsonl/csv` và báo cáo tổng hợp.
- Mỗi failure phải có: dataset, problem ID, artifact, loại lỗi, số test pass/tổng
  test, index test fail và lỗi đầu tiên. Expected/actual đầy đủ nằm trong
  `evaluation.json` của candidate.
- Lý do: Có thể đọc nhanh bài nào sai và tỷ lệ pass, đồng thời vẫn giữ đủ bằng chứng
  để phân tích lỗi hoặc dùng làm feedback cho MCTS sau này.

## D-015: Không resume generation rỗng hoặc bị cắt

- Ngày: 2026-09-26
- Trạng thái: Chấp nhận
- Quyết định: Config mặc định không gửi `max_tokens`. Artifact chỉ hoàn chỉnh khi
  source không rỗng và finish reason là `stop` hoặc không được provider cung cấp.
- Lý do: Giới hạn 2.048 token đã tạo nhiều response `length` và solution chỉ chứa
  xuống dòng; xem chúng là hoàn thành làm mất candidate trong benchmark.
- Ràng buộc: Không gửi `max_tokens` không có nghĩa vô hạn; context/model/provider
  vẫn có giới hạn. Artifact lỗi vẫn giữ để audit nhưng resume và evaluation bỏ qua.

## D-016: Generation song song có giới hạn

- Ngày: 2026-09-26
- Trạng thái: Chấp nhận
- Quyết định: Batch generation hỗ trợ `--generation-workers N` bằng thread scheduler;
  mỗi worker chạy một problem trong subprocess, manifest/log do scheduler chính ghi.
- Mặc định: 1 worker để tương thích và kiểm soát chi phí; full run bắt đầu với 2.
- Lý do: Request LLM chủ yếu chờ mạng/model nên chạy đồng thời giảm wall-clock time
  mà không cần thay đổi artifact hoặc resume semantics.
- Ràng buộc: Không tăng quá khả năng concurrency/rate limit của Modal. Parallelism
  không giảm tổng request, token hay chi phí; completion có thể về khác thứ tự ID.
