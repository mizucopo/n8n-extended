# n8n-extended

n8nにDocker CLIを追加した拡張版Dockerイメージ

## 特徴

- n8n公式イメージ（n8nio/n8n:2.2.1）をベース
- Docker CLIが組み込まれている
- ワークフローからDockerコマンドを実行可能

## 使い方

```bash
docker pull [USERNAME]/n8n-extended:latest
```

## GitHub Actionsの設定

このプロジェクトではGitHub Actionsを使用してDockerイメージを自動ビルドしています。以下のSecretsを設定してください。

- `DOCKERHUB_USERNAME`: Docker Hubのユーザー名
- `DOCKERHUB_TOKEN`: Docker Hubのアクセストークン

## ライセンス

MIT
