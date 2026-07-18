# n8n-extended

[n8n 公式 Docker イメージ](https://hub.docker.com/r/n8nio/n8n)に Docker CLI と ffmpeg を追加した拡張イメージです。n8n のワークフローからコンテナ操作や動画・音声処理を実行したい場合に利用できます。

公開イメージ: [mizucopo/n8n-extended](https://hub.docker.com/r/mizucopo/n8n-extended)

## 主な機能

- n8n 公式イメージをベースに使用
- Docker CLI を同梱
- ffmpeg を同梱
- n8n バージョンと任意の revision で識別する不変タグ、および `latest` タグを Docker Hub で公開

このイメージに Docker デーモンは含まれていません。Docker コマンドを実行するには、ホストの Docker ソケットをマウントするか、別の Docker デーモンへの接続を設定してください。

## 対応プラットフォーム

- `linux/amd64`

## クイックスタート

次のコマンドで n8n を起動します。

```bash
docker run --rm -it \
  --name n8n \
  --platform linux/amd64 \
  -p 5678:5678 \
  -e NODES_EXCLUDE='[]' \
  -v n8n_data:/home/node/.n8n \
  -v /var/run/docker.sock:/var/run/docker.sock \
  mizucopo/n8n-extended:latest
```

起動後、<http://localhost:5678> を開いてください。

`NODES_EXCLUDE='[]'` は、n8n 2.0 以降で既定無効となった Execute Command ノードを有効にするための設定です。Docker CLI や ffmpeg は Execute Command ノードから利用できます。

## Python コードを実行する

n8n 2.0 以降で Python の Code ノードを使用する場合は、External Task Runners が必要です。`n8nio/runners` のタグは、n8n と同じバージョンに揃えてください。

`.env` に使用するバージョンと共有トークンを設定します。

```dotenv
N8N_VERSION=2.25.2
N8N_EXTENDED_IMAGE_TAG=2.25.2-r1
N8N_RUNNERS_AUTH_TOKEN=replace-with-a-random-secret
```

`N8N_EXTENDED_IMAGE_TAG` には利用する拡張イメージのタグを指定します。`N8N_VERSION` は公式 n8n と Task Runner のバージョンなので revision を付けません。

同じディレクトリに `compose.yml` を作成します。

```yaml
services:
  n8n:
    image: mizucopo/n8n-extended:${N8N_EXTENDED_IMAGE_TAG}
    platform: linux/amd64
    ports:
      - "5678:5678"
    environment:
      N8N_RUNNERS_ENABLED: "true"
      N8N_RUNNERS_MODE: external
      N8N_RUNNERS_BROKER_LISTEN_ADDRESS: 0.0.0.0
      N8N_RUNNERS_AUTH_TOKEN: ${N8N_RUNNERS_AUTH_TOKEN}
      N8N_NATIVE_PYTHON_RUNNER: "true"
      NODES_EXCLUDE: "[]"
    volumes:
      - n8n_data:/home/node/.n8n
      - /var/run/docker.sock:/var/run/docker.sock

  task-runners:
    image: n8nio/runners:${N8N_VERSION}
    environment:
      N8N_RUNNERS_TASK_BROKER_URI: http://n8n:5679
      N8N_RUNNERS_AUTH_TOKEN: ${N8N_RUNNERS_AUTH_TOKEN}
    depends_on:
      - n8n

volumes:
  n8n_data:
```

次のコマンドで起動します。

```bash
docker compose up -d
```

詳しい設定は [n8n の Task runners ドキュメント](https://docs.n8n.io/hosting/configuration/task-runners/)を参照してください。

## セキュリティ

Docker ソケットをマウントしたコンテナは、ホスト上の Docker デーモンを操作できます。また、Execute Command ノードは任意のコマンドを実行できます。信頼できる利用者だけがアクセスできる環境で使用し、認証、TLS、ネットワーク制限を設けずにインターネットへ直接公開しないでください。

詳細は [Docker Engine security](https://docs.docker.com/engine/security/) と [n8n の Execute Command ドキュメント](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.executecommand/)を参照してください。

## ローカルでビルドする

`version` ファイルに記載された n8n バージョンを使用してビルドします。

```bash
docker build \
  --build-arg N8N_VERSION="$(cat version)" \
  --platform linux/amd64 \
  -t n8n-extended:local \
  .
```

## リリース

通常のリリースでは、`version` に使用する n8n バージョンを書き、`revision` は空にします。

```bash
printf "2.25.2\n" > version
: > revision
```

同じ n8n バージョンに対して拡張イメージだけを修正して再公開する場合は、`revision` に `r1`、`r2` のような Extended Image Revision を書きます。

```bash
printf "r1\n" > revision
```

この場合、公式イメージ `n8nio/n8n:2.25.2` を親にして、Docker イメージ、Git タグ、GitHub Release には `2.25.2-r1` を使用します。

`main` ブランチで `version`、`revision`、`Dockerfile`、タグ解決スクリプト、またはリリースワークフローが更新されると、GitHub Actions が次の処理を行います。

1. Git タグと不変 Docker タグが未使用であることを確認
2. Docker イメージをビルド
3. `mizucopo/n8n-extended:<version>[-<revision>]` と `mizucopo/n8n-extended:latest` を公開
4. 同じ `<version>[-<revision>]` で Git タグと GitHub Release を作成

Pull Request では、リリース対象ファイルが変更された場合だけ Git タグと Docker Hub タグの重複を検査します。既存の不変タグは上書きしません。

リポジトリの GitHub Actions Secret には、Docker Hub のアクセストークンを `DOCKERHUB_TOKEN` として登録してください。

設計判断の詳細は [Extended Image tags](docs/adr/0001-extended-image-tags.md) と [Extended Image release automation](docs/adr/0002-extended-image-release-automation.md) を参照してください。

## ライセンス

[MIT License](LICENSE)
