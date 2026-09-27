# Runbooks

Thu muc nay chua cac huong dan thao tac co the copy/chay truc tiep. Tai lieu ly
thuyet, dataset va kien truc van nam o cac file cap cao hon trong `docs/`.

## Runbook hien tai

- [Full direct baseline](baseline-full.md): sinh va cham toan bo APPS + HumanEval,
  resume artifact da co va tach output theo model.

## Thu tu doc

1. `docs/project-status.md` de biet giai doan va blocker.
2. `docs/llm-provider.md` de kiem tra Ollama/CKEY.
3. `docs/runbooks/baseline-full.md` de chay benchmark.
4. `docs/executors.md` de hieu schema ket qua evaluation.

## Nguyen tac

- Luon chay `--plan` truoc batch lon.
- Khong dung `--no-resume` neu muon bo qua bai da co.
- Generation va evaluation la hai stage rieng.
- Moi output phai nam duoi `run/model/dataset`.
