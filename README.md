# n8n-extended

n8nにDocker CLIを追加した拡張版Dockerイメージ

## 特徴

- n8n公式イメージ（n8nio/n8n）をベース
- Docker CLIが組み込まれている
- ワークフローからDockerコマンドを実行可能
- ffmpegによる動画・音声処理に対応

## Pythonの実行について

n8n 2.0以降、Pythonコードノードは**External Task Runners**を使用するのが推奨されています。
Pythonの実行が必要な場合は、`n8nio/runners`イメージと組み合わせて使用してください。

### docker-compose.ymlの例

```yaml
services:
  n8n:
    image: mizucopo/n8n-extended:latest
    environment:
      - N8N_RUNNERS_MODE=external
      - N8N_RUNNERS_BROKER_LISTEN_ADDRESS=0.0.0.0
      - N8N_RUNNERS_AUTH_TOKEN=your-secret-token-here
    volumes:
      - n8n_data:/home/node/.n8n
      - /var/run/docker.sock:/var/run/docker.sock

  task-runners:
    image: n8nio/runners:latest
    environment:
      - N8N_RUNNERS_TASK_BROKER_URI=http://n8n:5679
      - N8N_RUNNERS_AUTH_TOKEN=your-secret-token-here
    volumes:
      - n8n_runners:/runners

volumes:
  n8n_data:
  n8n_runners:
```

## 使い方

### ローカルでビルドする場合

```bash
docker build --build-arg N8N_VERSION=$(cat version) --platform linux/amd64 -t mizucopo/n8n-extended:develop .
```

### Docker Hubからプルする場合

```bash
docker pull --platform linux/amd64 mizucopo/n8n-extended:latest
```

## バージョンアップ手順

n8nのバージョンをアップするには、以下の手順で `version` ファイルを更新してください。

1. `version` ファイルに新しいバージョン番号を記載
2. 変更をコミットしてプッシュ
3. GitHub Actionsが自動的にDockerイメージをビルドしてDocker Hubにプッシュ

### バージョンアップ例

```bash
# version ファイルを編集
echo "2.7.0" > version

# 変更をコミット
git add version
git commit -m "chore: バージョンを2.7.0に更新"
git push
```

## GitHub Actionsの設定

このプロジェクトではGitHub Actionsを使用してDockerイメージを自動ビルドしています。以下のSecretを設定してください。

- `DOCKERHUB_TOKEN`: Docker Hubのアクセストークン

## ライセンス

[MIT](LICENSE)
