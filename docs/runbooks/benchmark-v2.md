# Benchmark v2: APPS 300 + HumanEval 164

## Pham vi

- APPS: dung dung 300 ID cua [cohort nhom doi chieu](https://github.com/Viendeptrai1/rethink-mcts-slm/blob/main/data/cohorts/apps_benchmark_300.json), 100 bai moi muc kho.
- HumanEval: dung toan bo 164 bai `HumanEval/0..163`.
- Hai manifest co dinh nam tai `data/samples/benchmark_v2/`. Khong boc lai ID
  khi doi model hoac phuong phap. Dataset raw/Arrow va candidate cu khong bi sua.
- `evaluation_v1` la run lich su 100+100; bang ket qua do khong thuoc cohort nay.
- **Chua chay benchmark v2.** Cac lenh duoi day la huong dan cho run moi.

## Truoc khi chay

Doc `docs/llm-provider.md` va `docs/executors.md`; kiem tra model, provider,
worker, timeout va chi phi. Dung `--run-name` **moi** de tranh ghi de evaluation
100+100 cu. Neu can sinh code, generation full khong truyen `--sample-file`;
xem `docs/runbooks/baseline-full.md` cho stage generate.

## Danh gia

APPS:

```powershell
.\venv\Scripts\python.exe -m pipelines `
  --stage evaluate `
  --dataset apps `
  --run-name <run_moi> `
  --model <model> `
  --sample-file data/samples/benchmark_v2/apps_test_300.json `
  --workers 4 `
  --confirm-full-run
```

HumanEval:

```powershell
.\venv\Scripts\python.exe -m pipelines `
  --stage evaluate `
  --dataset humaneval `
  --run-name <run_moi> `
  --model <model> `
  --sample-file data/samples/benchmark_v2/humaneval_test_164.json `
  --workers 4 `
  --confirm-full-run
```

Chi sau khi **ca hai** evaluation hoan tat, tao bang tong hop. Judge dung
`benchmark_v2` theo mac dinh; chi doc ket qua, khong goi LLM hay chay code:

```powershell
.\venv\Scripts\python.exe -m evaluation.benchmark_judge `
  --run-name <run_moi> `
  --model <model>
```

Ket qua o `outputs/baselines/evaluations/<run_moi>/<model>/`. Judge tinh
`missing_candidate` vao denominator; khong coi bang v2 la hoan thanh neu con
candidate thieu. Run lich su can truyen ro `--apps-sample-file` va
`--humaneval-sample-file` cua `evaluation_v1` khi tong hop lai.

Khi chạy theo [workflow remote](remote-evaluation.md), runner còn tạo hồ sơ
`outputs/benchmarks/<run_moi>/<model>/` với cấu hình/hashes và bảng kết quả
bất biến; xem [schema](../benchmark-results.md). Chạy `benchmark_judge`
riêng lẻ không tự tạo hồ sơ này nếu không có `bundle.json` và kết quả đầy đủ.

## Luu y khi so voi nhom doi chieu

Trung ID chua du de so sanh metric. [Adapter APPS cua ho](https://github.com/Viendeptrai1/rethink-mcts-slm/blob/main/src/rethink_mcts/adapters/datasets/apps.py)
dung hai test dau lam public va phan con lai lam hidden (loai duplicate public).
Pipeline hien tai cua chung ta co policy public/private rieng. Can chot cung
test split, timeout va denominator truoc khi so sanh con so giua hai project.
