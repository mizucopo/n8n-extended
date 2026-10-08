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
N8N_VERSION=x.y.z
N8N_EXTENDED_IMAGE_TAG=x.y.z
N8N_RUNNERS_AUTH_TOKEN=replace-with-a-random-secret
```

`x.y.z` はプレースホルダーです。利用する拡張イメージの元となる実際の n8n バージョンに置き換え、Task Runner のバージョンと揃えてください。

`N8N_EXTENDED_IMAGE_TAG` には利用する拡張イメージのタグを指定します。revision 付きのタグ（例: `x.y.z-r1`）を使用しても、`N8N_VERSION` には revision を付けません。

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

公開は repo-template の [Docker Project Release workflow](.github/workflows/docker-project-release.yml) を使います。PR 全体を [CONTRIBUTING.md](CONTRIBUTING.md) に従って分類し、公開する PR に `release:patch`、`release:minor`、`release:major` のいずれか一つを付けて `main` へ squash merge します。ファイルの変更だけでは公開せず、最新のマージ済み PR にラベルがなければ採番・公開をスキップします。

新しい上流 n8n に更新するときは、`version` に使用する stable n8n バージョンを書き、`revision` を空にします。以下の `x.y.z` は実際の n8n バージョンに置き換えてください。

```bash
printf "x.y.z\n" > version
: > revision
```

`Dockerfile` 先頭の `ARG N8N_VERSION=...` も、`version` と同じ n8n バージョンへ更新します。

採番は [.github/release.json](.github/release.json) の `upstream-revision` scheme に従います。ラベルの分類で上流 n8n version を通常の SemVer patch/minor/major として進めません。同じ上流 version の修正では `version` と `revision` を手動で増やさず、Actions が次の `rN` を採番します。新しい上流の初回タグは `x.y.z`（`-r0` なし）、再公開は `x.y.z-r1` 以降です。既存の Git タグ・GitHub Release・Docker Hub タグと衝突すれば、未使用の revision まで進めます。既存 `2.42.4` は再使用しません。

公式イメージと Task Runner は revision なしの上流 version を使い、Docker イメージ・Git タグ・GitHub Release 名は同じ `<version>[-rN]` になります。採番commitとタグを先に確定してから、n8n固有の [project hook](.github/scripts/docker-image-project.sh) で build・smoke・公開を行います。Docker品質CIはread-onlyで公開secretを使いません。

途中失敗の復旧は**元の workflow run の再実行**を使います。新しい `workflow_dispatch` は過去の公開を復旧しません。同じ採番commitが所有する公開済みimageを確認して不足分だけ再開し、完了後もimage所有権markerを残します。古いrunの再実行で Docker `latest` と GitHub latest Release を巻き戻しません。詳細は [共通公開・復旧手順](docs/release.md) と [project hookの契約](docs/docker-project-pipeline.md) を参照してください。

公開前に `release:patch/minor/major` ラベルと Docker Hub のアクセストークン `DOCKERHUB_TOKEN` を用意します。標準 `GITHUB_TOKEN` に採番commit・タグの直接pushを許す既存設定が必要です。上流更新の自動PRにも、公開する場合はメンテナーが分類ラベルを付けます。

移行時は旧 `Release n8n Extended Image` run が実行中でないことを確認してください。旧workflow・helperは削除し、新しい方式では旧公開runを復旧しません。移行PRはreleaseラベルなしで取り込み、製品公開は別のラベル付きPRで行います。

ローカルの品質確認は次のコマンドです（Docker Buildx、ShellCheck、Python 3.14、jqが必要）。

```bash
IMAGE_REPOSITORY=mizucopo/n8n-extended python3 .github/scripts/docker-image-pipeline.py quality
```

設計判断の詳細は [Extended Image tags](docs/adr/0001-extended-image-tags.md) と [Extended Image release automation](docs/adr/0002-extended-image-release-automation.md) を参照してください。

## ライセンス

[MIT License](LICENSE)
