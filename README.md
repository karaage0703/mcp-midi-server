# KantanPlay MIDI サーバー

このプロジェクトは、MCP フレームワークを使用して MIDI 送信機能を提供するサーバーです。Python版とTypeScript版の両方を提供しています。

## 機能

- 利用可能な MIDI ポートの一覧表示
- MIDI ポートの選択と接続
- MIDI ノートの送信（チャンネル 1）
- MIDI CC メッセージの送信（チャンネル 1）
- MIDIシーケンスの送信（指定したBPMでノート列を再生）

## Python版

### Python版の必要条件

- Python 3.12 以上
- python-rtmidi 1.5.8
- mcp[cli] 1.6.0 以上

### Python版のインストール

```bash
# 依存関係のインストール
pip install -r requirements.txt
```

### Python版の使用方法

```bash
# サーバーの起動
python kantanplay-midi-server.py
```

## TypeScript版

### TypeScript版の必要条件

- Node.js 18.0.0 以上
- npm 8.0.0 以上

### TypeScript版のインストール

```bash
# 依存関係のインストール
npm install
```

### TypeScript版の使用方法

```bash
# TypeScriptをトランスパイルして実行
npx ts-node src/kantanplay-midi-server.ts
```

## 使用例

1. `list_midi_ports()` - 利用可能な MIDI ポートの一覧を表示
2. `open_midi_port(port_index)` - 指定したインデックスの MIDI ポートを開く
3. `send_midi_note(note_number)` - MIDI ノートを送信（0-127）
4. `send_midi_cc(controller, value)` - MIDI CC メッセージを送信（コントローラー: 0-127, 値: 0-127）
5. `send_midi_sequence(bpm, notes)` - 指定したBPMでMIDIノートシーケンスを送信

## ライセンス

MIT ライセンス
