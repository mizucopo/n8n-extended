# n8n Extended Image project guidance

## Issue and branch

- 作業内容を記した GitHub Issue を着手前に用意する。
- 文書や設定を含むすべての変更は `main` ではなく、その Issue に対応するブランチで行う。
- `prefect-flows` が作成するベースイメージ自動更新 PR は Issue を要せず、固定ブランチ `automation/n8n-stable-update` を使う。

## Documentation

- 利用者に影響するコード変更では関連文書を更新する。新機能の使い方は README に記載する。
- インターフェース変更では該当する文書を更新する。大きな文書は `docs/` に分割し、README からリンクする。

## File operations

- ファイルの移動には `git mv`、削除には `git rm` を使う。

## CI compatibility

- `prefect-flows` の上流更新Flowは `check` と `docker-quality-checks` を待つ。共通分類・Docker品質workflowのjob IDはこの名前を維持する。処理本体はrepo-templateの共通実装を使う。

## Temporary template exceptions

- Docker project helperはpush後の確認直前にHub tokenを再取得する（[repo-template#172](https://github.com/mizucopo/repo-template/issues/172)）。n8nサンプルは削除した旧タグ検査testを呼ばない（[repo-template#173](https://github.com/mizucopo/repo-template/issues/173)）。共通修正が供給されたらCopier適用・検証で例外を解消する。
