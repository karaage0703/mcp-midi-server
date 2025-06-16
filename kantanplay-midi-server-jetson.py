# kantanplay-jetson.py - Jetson専用MIDI MCPサーバー
from mcp.server.fastmcp import FastMCP
import sys
import time
import platform
import os

# Create an MCP server
mcp = FastMCP("kantanplay-jetson")


class JetsonMIDI:
    def __init__(self):
        self.is_jetson = self._detect_jetson()
        self.midi_device = None

    def _detect_jetson(self):
        """Jetson環境かどうかを判定"""
        return platform.machine().startswith("aarch64") and os.path.exists("/dev/snd/midiC0D0")

    def get_output_names(self):
        """利用可能なMIDI出力ポート名を取得"""
        if self.is_jetson:
            if os.path.exists("/dev/snd/midiC0D0"):
                return ["/dev/snd/midiC0D0 (UM-1)"]
            else:
                return []
        else:
            try:
                import mido
                return mido.get_output_names()
            except ImportError:
                return []

    def open_output(self, port_name):
        """MIDI出力ポートを開く"""
        if self.is_jetson:
            self.midi_device = open("/dev/snd/midiC0D0", "wb")
            return self
        else:
            import mido
            self.midi_device = mido.open_output(port_name)
            return self.midi_device

    def send_message(self, msg_type, channel=0, note=None, velocity=None, controller=None, value=None):
        """MIDIメッセージを送信"""
        if self.is_jetson:
            if msg_type == "note_on":
                midi_bytes = bytes([0x90 + channel, note, velocity])
            elif msg_type == "note_off":
                midi_bytes = bytes([0x80 + channel, note, velocity])
            elif msg_type == "control_change":
                midi_bytes = bytes([0xB0 + channel, controller, value])
            else:
                return

            self.midi_device.write(midi_bytes)
            self.midi_device.flush()
        else:
            import mido
            if msg_type == "control_change":
                msg = mido.Message(msg_type, channel=channel, control=controller, value=value)
            else:
                msg = mido.Message(msg_type, channel=channel, note=note, velocity=velocity)
            self.midi_device.send(msg)

    def close(self):
        """ポートを閉じる"""
        if self.midi_device:
            self.midi_device.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# JetsonMIDIインスタンスを作成
jetson_midi = JetsonMIDI()
midi_available = len(jetson_midi.get_output_names()) > 0

if midi_available:
    print(f"MIDI環境: {'Jetson' if jetson_midi.is_jetson else 'Mac/PC'}", file=sys.stderr)
    print("MIDI機能が利用可能です。", file=sys.stderr)
else:
    print("警告: 利用可能なMIDI出力ポートがありません。", file=sys.stderr)
    print("MIDI機能は利用できません。", file=sys.stderr)
    if not jetson_midi.is_jetson:
        print("Mac/PCでは、以下の手順を試してください:", file=sys.stderr)
        print("1. ターミナルで 'pip install mido python-rtmidi' を実行", file=sys.stderr)
        print("2. または 'uv add mido python-rtmidi' を実行", file=sys.stderr)
    else:
        print("Jetsonでは /dev/snd/midiC0D0 デバイスが必要です。", file=sys.stderr)

# MIDI設定
midi_out = None
available_ports = []
selected_port_index = None
midi_port_opened = False

if midi_available:
    available_ports = jetson_midi.get_output_names()

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
        return "MIDI機能がインストールされていないため、利用できません。"

    # 最新のポートリストを取得してグローバル変数を更新
    available_ports = jetson_midi.get_output_names()

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
        midi_out = jetson_midi.open_output(port_name)
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
        return "MIDI機能がインストールされていないため、利用できません。"

    ports = jetson_midi.get_output_names()
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
        return "MIDI機能がインストールされていないため、利用できません。"

    if not midi_port_opened:
        return "MIDIポートが開かれていません。まずopen_midi_port()を使用してポートを選択してください。"

    if not 0 <= note_number <= 127:
        return f"エラー: ノート番号は0から127の間である必要があります。入力値: {note_number}"

    try:
        # Note Onメッセージを送信
        if jetson_midi.is_jetson:
            jetson_midi.send_message("note_on", channel=0, note=note_number, velocity=100)
        else:
            jetson_midi.send_message("note_on", channel=0, note=note_number, velocity=100)

        # 0.5秒後にノートオフメッセージを送信
        time.sleep(0.5)

        # Note Offメッセージ
        if jetson_midi.is_jetson:
            jetson_midi.send_message("note_off", channel=0, note=note_number, velocity=0)
        else:
            jetson_midi.send_message("note_off", channel=0, note=note_number, velocity=0)

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
        return "MIDI機能がインストールされていないため、利用できません。"

    if not midi_port_opened:
        return "MIDIポートが開かれていません。まずopen_midi_port()を使用してポートを選択してください。"

    if not 0 <= controller <= 127:
        return f"エラー: コントローラー番号は0から127の間である必要があります。入力値: {controller}"

    if not 0 <= value <= 127:
        return f"エラー: 値は0から127の間である必要があります。入力値: {value}"

    try:
        # MIDIメッセージを送信
        if jetson_midi.is_jetson:
            jetson_midi.send_message("control_change", channel=0, controller=controller, value=value)
        else:
            jetson_midi.send_message("control_change", channel=0, controller=controller, value=value)
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
        return "MIDI機能がインストールされていないため、利用できません。"

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
            if jetson_midi.is_jetson:
                jetson_midi.send_message("note_on", channel=0, note=note, velocity=100)
            else:
                jetson_midi.send_message("note_on", channel=0, note=note, velocity=100)
            sent_notes.append(note)

            # 1ステップ分待機
            time.sleep(step_time)

            # Note Offメッセージを送信
            if jetson_midi.is_jetson:
                jetson_midi.send_message("note_off", channel=0, note=note, velocity=0)
            else:
                jetson_midi.send_message("note_off", channel=0, note=note, velocity=0)

            # 1ステップ分待機（次のノートまでの間隔）
            time.sleep(step_time)

        return f"BPM {bpm}で以下のMIDIノートシーケンスを送信しました: {sent_notes}"
    except Exception as e:
        return f"MIDI送信エラー: {str(e)}"


if __name__ == "__main__":
    try:
        print("Jetson対応MIDI送信サーバーを起動します...")

        if midi_available:
            print("利用可能なMIDIポート:", jetson_midi.get_output_names())
            print("使用するMIDIポートを選択するには、list_midi_ports()でポート一覧を確認し、")
            print("open_midi_port(port_index)でポートを選択してください。")
        else:
            print("警告: MIDI機能が利用できません。")
            if jetson_midi.is_jetson:
                print("Jetsonでは /dev/snd/midiC0D0 デバイスが必要です。")
            else:
                print("MIDI機能を使用するには、以下のコマンドでmidoをインストールしてください:")
                print("uv add mido python-rtmidi")

        mcp.run()
    finally:
        # プログラム終了時にMIDI接続を閉じる
        if midi_available and midi_out is not None:
            print("MIDI接続を閉じています...")
            midi_out.close()