# Bản đồ tài liệu

Thư mục này là bộ nhớ chung giữa người thực hiện và trợ lý. Mục tiêu là giữ rõ ba
loại thông tin: điều đã kiểm chứng, điều đang dự định và điều còn chưa chắc chắn.

## Thứ tự đọc

1. [project-status.md](project-status.md): trạng thái thực tế mới nhất và bước kế tiếp.
2. [plan.md](plan.md): roadmap, phạm vi từng giai đoạn và điều kiện hoàn thành.
3. [theory-rethinkmcts.md](theory-rethinkmcts.md): thuật toán từ paper nền tảng.
4. [datasets.md](datasets.md): quyết định sử dụng APPS và HumanEval.
5. [baseline-direct.md](baseline-direct.md): baseline đưa đề bài cho LLM và nhận code.
6. [executors.md](executors.md): chạy code và tính số test pass cho từng dataset.
7. [pipeline-direct.md](pipeline-direct.md): generation trước, evaluation song song sau.
8. [environment.md](environment.md): virtual environment và dependency.
9. [implementation-audit.md](implementation-audit.md): khoảng cách giữa paper và code.
10. [llm-provider.md](llm-provider.md): cấu hình Ollama/Modal và quy tắc sử dụng API.
11. [decisions.md](decisions.md): các quyết định đã chốt và lý do.
12. [theory-rap.md](theory-rap.md): đối chiếu khái niệm với RAP, không phải baseline chính.
13. [gpu/README.md](gpu/README.md): thông tin instance CKEY, Ollama và kế hoạch chạy GPU thuê.
14. [runbooks/README.md](runbooks/README.md): hướng dẫn thao tác generation/evaluation theo từng bước.

## Source of truth

| Nội dung | File chịu trách nhiệm |
|---|---|
| Trạng thái hiện tại, blocker, bước tiếp theo | `docs/project-status.md` |
| Roadmap và phạm vi từng giai đoạn | `docs/plan.md` |
| Công thức/thuật toán RethinkMCTS | `docs/theory-rethinkmcts.md` |
| Dataset nào được dùng và vì sao | `docs/datasets.md` |
| Cấu trúc file, schema và cách load dữ liệu | `data/README.md` |
| Hành vi và cách chạy direct-generation baseline | `docs/baseline-direct.md` |
| Giao diện, cách chấm và giới hạn an toàn của executor | `docs/executors.md` |
| Pipeline generation/evaluation và artifact tổng hợp | `docs/pipeline-direct.md` |
| Python environment và dependency | `docs/environment.md` |
| Trạng thái implementation và điểm chưa rõ | `docs/implementation-audit.md` |
| Provider, biến môi trường và quy tắc gọi LLM | `docs/llm-provider.md` |
| Quyết định kiến trúc/phạm vi đã chốt | `docs/decisions.md` |
| Lệnh vận hành benchmark theo từng bước | `docs/runbooks/baseline-full.md` |
| Metric Pass Rate/Pass@1 và bảng judge | `evaluation/benchmark_judge.py` |

Không sao chép toàn bộ cùng một nội dung sang nhiều file. File khác chỉ nên tóm tắt
và liên kết tới source of truth tương ứng.

## Quy ước trạng thái

Các tài liệu dùng ba nhãn sau:

- **Đã kiểm chứng**: đã đọc trực tiếp từ file, chạy lệnh hoặc đối chiếu nguồn gốc.
- **Giả thuyết**: suy luận hợp lý nhưng chưa xác nhận bằng code/chạy thử.
- **Cần xác minh**: câu hỏi mở phải kiểm tra trước khi triển khai.

Khi trạng thái thay đổi, cập nhật `project-status.md` trong cùng task. Khi một quyết
định thay đổi phạm vi hoặc kiến trúc, cập nhật thêm `decisions.md` và các tài liệu
chịu ảnh hưởng.

## Quy tắc tránh tài liệu lỗi thời

- Mỗi dữ kiện chỉ có một file chịu trách nhiệm chính.
- Đường dẫn, số lượng mẫu và trạng thái code phải được kiểm tra trực tiếp.
- Không đánh dấu hoàn thành chỉ vì file/thư mục tồn tại.
- Không âm thầm sửa khác biệt giữa paper và code; ghi vào audit trước.
- Sau khi đổi tên/di chuyển file, tìm tên cũ trên toàn workspace.
