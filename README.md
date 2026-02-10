# n8n-extended

n8nにDocker CLIを追加した拡張版Dockerイメージ

## 特徴

- n8n公式イメージ（n8nio/n8n）をベース
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

MIT
