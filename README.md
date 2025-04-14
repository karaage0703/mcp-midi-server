# MCP MIDI サーバー

このプロジェクトは、MCPフレームワークを使用してMIDI送信機能を提供するサーバーです。

## 機能

- 利用可能なMIDIポートの一覧表示
- MIDIポートの選択と接続
- MIDIノートの送信（チャンネル1）
- MIDI CCメッセージの送信（チャンネル1）

## 必要条件

- Python 3.12以上
- python-rtmidi 1.5.8
- mcp[cli] 1.6.0以上

## インストール

```bash
# 依存関係のインストール
pip install -r requirements.txt
```

## 使用方法

```bash
# サーバーの起動
python midisend.py
```

## 使用例

1. `list_midi_ports()` - 利用可能なMIDIポートの一覧を表示
2. `open_midi_port(port_index)` - 指定したインデックスのMIDIポートを開く
3. `send_midi_note(note_number)` - MIDIノートを送信（0-127）
4. `send_midi_cc(controller, value)` - MIDI CCメッセージを送信（コントローラー: 0-127, 値: 0-127）

## ライセンス

MITライセンス
