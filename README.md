# KantanPlay MIDI サーバー

このプロジェクトは、MCP フレームワークを使用して MIDI 送信機能を提供するサーバーです。Python 版のみを提供しています。

## 機能

- 利用可能な MIDI ポートの一覧表示
- MIDI ポートの選択と接続
- MIDI ノートの送信（チャンネル 1）
- MIDI CC メッセージの送信（チャンネル 1）
- MIDI シーケンスの送信（指定した BPM でノート列を再生）

## Python 版

### Python 版の必要条件

- Python 3.12 以上
- python-rtmidi 1.5.8
- mcp[cli] 1.6.0 以上

### Python 版のインストール

```bash
# 依存関係のインストール
pip install -r requirements.txt
```

### Python 版の使用方法

```bash
# サーバーの起動
python kantanplay-midi-server.py
```

## 使用例

1. `list_midi_ports()` - 利用可能な MIDI ポートの一覧を表示
2. `open_midi_port(port_index)` - 指定したインデックスの MIDI ポートを開く
3. `send_midi_note(note_number)` - MIDI ノートを送信（0-127）
4. `send_midi_cc(controller, value)` - MIDI CC メッセージを送信（コントローラー: 0-127, 値: 0-127）
5. `send_midi_sequence(bpm, notes)` - 指定した BPM で MIDI ノートシーケンスを送信

## Claude Desktop での記述例

```
{
  "mcpServers": {
    "かんぷれ": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "mcp[cli]",
        "mcp",
        "run",
        "（ファイルへの絶対パス）/kantanplay-midi-server.py"
      ]
    }
  }
}
```

## ライセンス

MIT ライセンス
