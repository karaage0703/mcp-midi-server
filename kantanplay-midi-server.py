# kantanplay.py
from mcp.server.fastmcp import FastMCP
import sys
import time

# Create an MCP server
mcp = FastMCP("kantanplay")

# midoライブラリをインポート
try:
    import mido

    midi_available = True
    print("midoライブラリが正常にインポートされました。", file=sys.stderr)
except ImportError as e:
    midi_available = False
    print(f"警告: midoライブラリのインポートに失敗しました: {str(e)}", file=sys.stderr)
    print("MIDI機能は利用できません。", file=sys.stderr)
    print("Claude Desktopでは、以下の手順を試してください:", file=sys.stderr)
    print("1. ターミナルで 'pip install mido python-rtmidi' を実行", file=sys.stderr)
    print("2. または 'uv add mido python-rtmidi' を実行", file=sys.stderr)
except Exception as e:
    midi_available = False
    print(f"midoライブラリの初期化中にエラーが発生しました: {e}", file=sys.stderr)

# MIDI設定
midi_out = None
available_ports = []
selected_port_index = None
midi_port_opened = False

if midi_available:
    available_ports = mido.get_output_names()

    # 利用可能なポートの確認
    if not available_ports:
        print("利用可能なMIDIポートが見つかりませんでした。", file=sys.stderr)
    else:
        print(f"利用可能なMIDIポート: {len(available_ports)}個", file=sys.stderr)
        for i, port in enumerate(available_ports):
            print(f"{i}: {port}")


@mcp.tool()
def open_midi_port(port_index: int) -> str:
    """
    指定されたインデックスのMIDIポートを開きます

    Args:
        port_index: 開きたいMIDIポートのインデックス

    Returns:
        操作結果のメッセージ
    """
    global selected_port_index, midi_port_opened, available_ports, midi_out

    if not midi_available:
        return "midoライブラリがインストールされていないため、MIDI機能は利用できません。"

    # 最新のポートリストを取得してグローバル変数を更新
    available_ports = mido.get_output_names()

    if not available_ports:
        return "利用可能なMIDIポートがありません。"

    if not 0 <= port_index < len(available_ports):
        return f"エラー: 有効なポートインデックスを指定してください (0-{len(available_ports) - 1})"

    try:
        # 既に開いているポートがあれば閉じる
        if midi_out is not None:
            midi_out.close()

        # 指定されたポートを開く
        port_name = available_ports[port_index]
        midi_out = mido.open_output(port_name)
        selected_port_index = port_index
        midi_port_opened = True

        return f"MIDIポートを開きました: {available_ports[port_index]}"
    except Exception as e:
        # エラーが発生した場合は状態をリセット
        midi_port_opened = False
        selected_port_index = None
        return f"MIDIポートを開く際にエラーが発生しました: {str(e)}"


@mcp.tool()
def list_midi_ports() -> str:
    """利用可能なMIDIポートの一覧を返します"""
    if not midi_available:
        return "midoライブラリがインストールされていないため、MIDI機能は利用できません。"

    ports = mido.get_output_names()
    if not ports:
        return "利用可能なMIDIポートはありません"

    port_list = "\n".join([f"{i}: {port}" for i, port in enumerate(ports)])

    if selected_port_index is not None and midi_port_opened:
        current_port = f"\n\n現在選択中のポート: {selected_port_index}: {ports[selected_port_index]}"
    else:
        current_port = "\n\n現在ポートは選択されていません。open_midi_port()を使用してポートを選択してください。"

    return f"利用可能なMIDIポート:\n{port_list}{current_port}"


@mcp.tool()
def send_midi_note(note_number: int) -> str:
    """
    指定されたノート番号のMIDIノートをチャンネル1で送信します

    Args:
        note_number: MIDIノート番号 (0-127)

    Returns:
        送信結果のメッセージ
    """
    if not midi_available:
        return "midoライブラリがインストールされていないため、MIDI機能は利用できません。"

    if not midi_port_opened:
        return "MIDIポートが開かれていません。まずopen_midi_port()を使用してポートを選択してください。"

    if not 0 <= note_number <= 127:
        return f"エラー: ノート番号は0から127の間である必要があります。入力値: {note_number}"

    try:
        # Note Onメッセージを送信
        msg_on = mido.Message("note_on", channel=0, note=note_number, velocity=100)
        midi_out.send(msg_on)

        # 0.5秒後にノートオフメッセージを送信
        time.sleep(0.5)

        # Note Offメッセージ
        msg_off = mido.Message("note_off", channel=0, note=note_number, velocity=0)
        midi_out.send(msg_off)

        return f"MIDI Note {note_number} をチャンネル1で送信しました"
    except Exception as e:
        return f"MIDI送信エラー: {str(e)}"


@mcp.tool()
def send_midi_cc(controller: int, value: int) -> str:
    """
    指定されたコントローラー番号とバリューでMIDI CCメッセージをチャンネル1で送信します

    Args:
        controller: コントローラー番号 (0-127)
        value: コントロール値 (0-127)

    Returns:
        送信結果のメッセージ
    """
    if not midi_available:
        return "midoライブラリがインストールされていないため、MIDI機能は利用できません。"

    if not midi_port_opened:
        return "MIDIポートが開かれていません。まずopen_midi_port()を使用してポートを選択してください。"

    if not 0 <= controller <= 127:
        return f"エラー: コントローラー番号は0から127の間である必要があります。入力値: {controller}"

    if not 0 <= value <= 127:
        return f"エラー: 値は0から127の間である必要があります。入力値: {value}"

    # MIDIメッセージを作成 (CC, チャンネル1)
    # チャンネル1のCCは0xB0
    midi_message = [0xB0, controller, value]

    try:
        # MIDIメッセージを送信
        midi_out.send_message(midi_message)
        return f"MIDI CC {controller}={value} をチャンネル1で送信しました"
    except Exception as e:
        return f"MIDI送信エラー: {str(e)}"


@mcp.tool()
def send_midi_sequence(bpm: int, notes: list) -> str:
    """
    指定されたBPMで複数のMIDIノートを順番に送信します

    Args:
        bpm: テンポ（1分間あたりの拍数）
        notes: 送信するMIDIノート番号のリスト (各ノートは0-127の範囲)

    Returns:
        送信結果のメッセージ
    """
    if not midi_available:
        return "rtmidiライブラリがインストールされていないため、MIDI機能は利用できません。"

    if not midi_port_opened:
        return "MIDIポートが開かれていません。まずopen_midi_port()を使用してポートを選択してください。"

    # BPMの妥当性チェック
    if bpm <= 0:
        return f"エラー: BPMは正の値である必要があります。入力値: {bpm}"

    # 1ステップの時間を計算（秒）
    # 1分（60秒）をBPMで割り、それをさらに2で割る（オンとオフで等分）
    step_time = 60.0 / bpm / 2

    try:
        sent_notes = []
        print(f"DEBUG: BPM {bpm}でのシーケンス開始 (ステップ時間:{step_time:.3f}s)", file=sys.stderr)

        for note in notes:
            if not 0 <= note <= 127:
                return f"エラー: ノート番号は0から127の間である必要があります。入力値: {note}"

            print(f"DEBUG: ノート{note}開始", file=sys.stderr)

            # Note Onメッセージを送信（チャンネル1、ベロシティ100）
            msg_on = mido.Message("note_on", channel=0, note=note, velocity=100)
            midi_out.send(msg_on)
            sent_notes.append(note)

            # 1ステップ分待機
            time.sleep(step_time)

            # Note Offメッセージを送信
            msg_off = mido.Message("note_off", channel=0, note=note, velocity=0)
            midi_out.send(msg_off)

            # 1ステップ分待機（次のノートまでの間隔）
            time.sleep(step_time)

        return f"BPM {bpm}で以下のMIDIノートシーケンスを送信しました: {sent_notes}"
    except Exception as e:
        return f"MIDI送信エラー: {str(e)}"


if __name__ == "__main__":
    try:
        print("MIDI送信サーバーを起動します...")

        if midi_available:
            print("利用可能なMIDIポート:", mido.get_output_names())
            print("使用するMIDIポートを選択するには、list_midi_ports()でポート一覧を確認し、")
            print("open_midi_port(port_index)でポートを選択してください。")
        else:
            print("警告: midoライブラリがインストールされていないため、MIDI機能は利用できません。")
            print("MIDI機能を使用するには、以下のコマンドでmidoをインストールしてください:")
            print("uv add mido python-rtmidi")

        mcp.run()
    finally:
        # プログラム終了時にMIDI接続を閉じる
        if midi_available and midi_out is not None:
            print("MIDI接続を閉じています...")
            midi_out.close()
