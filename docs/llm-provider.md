# LLM provider

## Provider benchmark hien tai

Benchmark hien tai uu tien `LLM_PROVIDER=ollama` voi model
`qwen2.5-coder:7b-instruct` tren GPU CKEY. Modal van duoc giu de audit run cu,
nhung khong phai provider cua benchmark v1.

## Quyết định hiện tại

Dự án có adapter cho endpoint OpenAI-compatible trên **Modal.com**, nhưng benchmark
tiếp theo dự kiến chạy trên Ollama tại GPU thuê CKEY. Cấu hình runtime nằm trong file
`.env` ở thư mục gốc; không hard-code endpoint, token hoặc tên model trong source code.

Thông tin instance GPU và checklist vận hành nằm tại [GPU runtime](gpu/README.md).

## Biến môi trường

| Biến | Bắt buộc | Ý nghĩa |
|---|---:|---|
| `MODAL_PROXY_TOKEN_ID` | Có | ID dùng để xác thực Modal proxy |
| `MODAL_PROXY_TOKEN_SECRET` | Có | Secret dùng để xác thực Modal proxy |
| `MODAL_BASE_URL` | Có | Base URL OpenAI-compatible, gồm version path nếu endpoint yêu cầu |
| `KIMI_MODEL` | Modal | Model identifier gửi trong request Modal |
| `LLM_PROVIDER` | Ollama | Provider đang chọn cho benchmark GPU mới |
| `LLM_BASE_URL` | Ollama | Base URL OpenAI-compatible của Ollama |
| `LLM_MODEL` | Ollama | Model identifier, dự kiến `qwen2.5-coder:7b-instruct` |
| `LLM_API_KEY` | Ollama | Giá trị local, thường là `ollama`; không phải secret |

Mẫu không chứa secret được lưu tại `.env.example`. File `.env` thật phải được Git
ignore và không được chép vào log, Markdown, notebook hoặc artifact thử nghiệm.

## Cách khởi tạo client

```python
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url=os.environ["MODAL_BASE_URL"],
    api_key=(
        f"{os.environ['MODAL_PROXY_TOKEN_ID']}."
        f"{os.environ['MODAL_PROXY_TOKEN_SECRET']}"
    ),
)
model = os.environ["KIMI_MODEL"]
```

## Quy tắc thử nghiệm

- Không in token hoặc toàn bộ environment ra terminal/log.
- Không commit `.env`; chỉ commit `.env.example` với giá trị rỗng.
- Smoke test đầu tiên chỉ gửi một request ngắn.
- Khi chạy RethinkMCTS, bắt đầu với 1 bài và rollout thấp.
- Ghi model identifier, tham số sampling, số request và token usage nếu API trả về.
- Không ghi giá trị token vào tài liệu tái lập; chỉ ghi tên biến môi trường.
- Không gọi API chỉ để kiểm tra cấu hình nếu có thể kiểm tra offline.

## Trạng thái xác minh

Đã kiểm tra offline ngày 2026-09-26:

- `.env` tồn tại.
- Bốn biến bắt buộc đều có mặt và không rỗng.
- `MODAL_BASE_URL` có dạng URL HTTP(S).
- `test.py` đọc endpoint và model từ biến môi trường.

Đã gửi request thật qua endpoint Modal và nhận được response/usage. Một lần cấu hình
route sai trả `404 route not found`; sau khi sửa `.env`, plan resolve đúng model và
generation tạo được artifact. Không ghi endpoint hoặc token vào tài liệu/log.
