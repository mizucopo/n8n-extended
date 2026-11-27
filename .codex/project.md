# n8n Extended Image project guidance

## Branch

- 文書や設定を含むすべての変更は `main` ではなく、作業用ブランチで行う。
- ベースイメージの自動更新 PR には、固定ブランチ `automation/n8n-stable-update` を使う。

## Documentation

- 利用者に影響するコード変更では関連文書を更新する。新機能の使い方は README に記載する。
- インターフェース変更では該当する文書を更新する。大きな文書は `docs/` に分割し、README からリンクする。

## File operations

- ファイルの移動には `git mv`、削除には `git rm` を使う。

## CI compatibility

- ベースイメージの自動更新 PR の必須チェックとして、リリース分類のジョブ ID `check` と Docker 品質チェックのジョブ ID `docker-quality-checks` を維持する。両チェックのワークフローには `repo-template` の共通実装を使う。
