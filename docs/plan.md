# Kế hoạch dự án

## Nguyên tắc phạm vi

Baseline phải chạy được và được quan sát trước khi phát triển biến thể. Mọi thử
nghiệm API bắt đầu bằng 1-2 bài và rollout thấp để kiểm soát chi phí.

## Kế hoạch 15 tuần

| Tuần | Trọng tâm | Kết quả cần có |
|---:|---|---|
| 1 | Chốt đề tài và câu hỏi nghiên cứu | Phạm vi, mục tiêu, tiêu chí đánh giá |
| 2 | Đọc RethinkMCTS và RAP | Ghi chú lý thuyết, câu hỏi mở |
| 3 | Chuẩn bị APPS và HumanEval | Dataset load được, schema được mô tả |
| 4 | Lấy và đọc repo RethinkMCTS gốc | Commit hash, sơ đồ module, dependency |
| 5 | Dựng môi trường chạy | Cài đặt tái lập được, loader chạy độc lập |
| 6 | Smoke test baseline | 1-2 bài, rollout thấp, log đầy đủ |
| 7 | Đối chiếu paper với code | Audit các khác biệt và điểm nhập nhằng |
| 8 | Thiết lập baseline đo lường | Protocol, seed, metric, lưu artifact |
| 9 | Thiết kế đóng góp | Đặc tả reward/feedback mới, chưa code vội |
| 10 | Prototype có kiểm thử | Thay đổi nhỏ, test executor và reward |
| 11 | Tích hợp vào search | Chạy end-to-end trên tập nhỏ |
| 12 | Thử nghiệm chính | Baseline và phương pháp đề xuất |
| 13 | Ablation và phân tích lỗi | Bảng kết quả, case study |
| 14 | Viết báo cáo | Phương pháp, thực nghiệm, thảo luận |
| 15 | Hoàn thiện | Rà soát tái lập, slide và phụ lục |

## Giai đoạn hiện tại

Đang ở **pipeline direct generation và đánh giá song song**: generation lưu toàn bộ
candidate trước, sau đó process pool chấm APPS/HumanEval và tổng hợp metric. Chưa
triển khai MCTS. Bước kế tiếp là smoke test Modal 1-2 bài rồi mới chạy full dataset.

### Definition of Done cho direct-generation baseline

- Loader đọc được một bài APPS hoặc HumanEval mà không đọc đáp án/test.
- Prompt yêu cầu model chỉ trả complete Python code.
- Mỗi lệnh gửi tối đa một bài và một request.
- Raw response, code và metadata usage được lưu thành artifact.
- Có dry-run để xem prompt mà không gọi API.
- Bước sinh code không tự thực thi candidate; việc chấm thuộc package `Executors`.

### Definition of Done cho executor baseline

- APPS hỗ trợ cả `stdin_stdout` và `call_based`.
- HumanEval chạy nguyên official harness bằng đúng `entry_point`.
- Báo cáo có số test pass, tổng test, pass rate, lỗi và thời gian chạy.
- Mỗi test/harness có timeout và không làm treo tiến trình benchmark.
- Có unit test offline cho pass, wrong answer và timeout.
- Giới hạn bảo mật của subprocess runner được ghi rõ.

### Definition of Done cho pipeline direct baseline

- Generation và evaluation là hai checkpoint có thể chạy/resume độc lập.
- Stage `all` chỉ bắt đầu evaluation sau khi toàn bộ generation thành công.
- Evaluation song song theo candidate với số worker cấu hình được.
- Mỗi candidate có `evaluation.json`; mỗi dataset có JSONL, CSV và summary.
- Full run cần xác nhận rõ để tránh gọi API hoặc thực thi hàng loạt ngoài ý muốn.
- Pipeline plan và evaluation offline có unit test; smoke Modal thật vẫn cần chạy.

## Definition of Done cho baseline RethinkMCTS sau này

Baseline chỉ được xem là chạy được khi đáp ứng đủ:

- Repo gốc và commit hash được ghi nhận.
- Dependency và lệnh chạy có thể tái lập.
- Loader đọc đúng một mẫu APPS hoặc HumanEval.
- Executor chạy được public tests với timeout.
- Một lượt search tạo được thought, code, reward và kết quả test.
- Có bằng chứng rethink được kích hoạt trên ít nhất một trường hợp lỗi, hoặc ghi rõ
  đã thử nhưng chưa kích hoạt với cấu hình nào.
- Log đủ để đối chiếu với sáu pha trong paper.
- Chi phí API và số request được ghi lại.

## Ngoài phạm vi hiện tại

- Viết MCTS riêng trước khi hiểu code gốc.
- Reward phân biệt TLE/MLE.
- Root-cause identification cho thought.
- CodeContests.
- Chạy toàn bộ benchmark hoặc rollout lớn.
# Cap nhat pham vi hien tai (2026-09-27)

Truoc khi chuyen sang MCTS, direct baseline generation chay full APPS test va
HumanEval test voi model `qwen2.5-coder:7b-instruct` qua Ollama. Judge evaluation
dung sample co dinh 100 bai moi dataset trong `data/samples/evaluation_v1/`; tap nay
se duoc tai lai khi gan MCTS.

