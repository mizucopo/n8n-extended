# n8n-extended

n8nにDocker CLIを追加した拡張版Dockerイメージ

## 特徴

- n8n公式イメージ（n8nio/n8n:2.2.1）をベース
- Docker CLIが組み込まれている
- ワークフローからDockerコマンドを実行可能

## 使い方

### ローカルでビルドする場合

```bash
docker build -t mizucopo/n8n-extended:develop .
```

### Docker Hubからプルする場合

```bash
docker pull mizucopo/n8n-extended:latest
```

## GitHub Actionsの設定

このプロジェクトではGitHub Actionsを使用してDockerイメージを自動ビルドしています。以下のSecretを設定してください。

- `DOCKERHUB_TOKEN`: Docker Hubのアクセストークン

## ライセンス

MIT
