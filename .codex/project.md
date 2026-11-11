# n8n Extended Image project guidance

## Branch

- 文書や設定を含むすべての変更は `main` ではなく、作業用ブランチで行う。
- `prefect-flows` が作成するベースイメージ自動更新 PR は固定ブランチ `automation/n8n-stable-update` を使う。

## Documentation

- 利用者に影響するコード変更では関連文書を更新する。新機能の使い方は README に記載する。
- インターフェース変更では該当する文書を更新する。大きな文書は `docs/` に分割し、README からリンクする。

## File operations

- ファイルの移動には `git mv`、削除には `git rm` を使う。

## CI compatibility

- `prefect-flows` の上流更新Flowは `check` と `docker-quality-checks` を待つ。共通分類・Docker品質workflowのjob IDはこの名前を維持する。処理本体はrepo-templateの共通実装を使う。
