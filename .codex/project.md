# n8n Extended Image project guidance

## Issue and branch

- 作業内容を記した GitHub Issue を着手前に用意し、その Issue に対応するブランチで実装する。
- `prefect-flows` が作成するベースイメージ自動更新 PR は Issue を要せず、固定ブランチ `automation/n8n-stable-update` を使う。

## Documentation

- 利用者に影響するコード変更では関連文書を更新する。新機能の使い方は README に記載する。
- インターフェース変更では該当する文書を更新する。大きな文書は `docs/` に分割し、README からリンクする。

## File operations

- ファイルの移動には `git mv`、削除には `git rm` を使う。
