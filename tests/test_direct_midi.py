#!/usr/bin/env python3
"""
MCPサーバーを使わずに直接MIDI信号を連続送信するテスト
遅延なしでの動作を確認
"""

import mido
import time
import sys

def test_direct_midi_rapid_fire():
    """遅延なしでMIDI信号を連続送信"""
    try:
        # 利用可能な出力ポートを確認
        output_names = mido.get_output_names()
        print(f"利用可能なMIDI出力ポート: {output_names}")
        
        if not output_names:
            print("MIDI出力ポートが見つかりません")
            return
        
        # 最初のポートを使用
        port_name = output_names[0]
        print(f"使用するポート: {port_name}")
        
        with mido.open_output(port_name) as outport:
            # テストシーケンス: C4, D4, E4, F4, G4
            notes = [60, 62, 64, 65, 67]
            
            print("\n=== 遅延なし連続送信テスト ===")
            for note in notes:
                # Note On
                msg_on = mido.Message('note_on', channel=0, note=note, velocity=64)
                outport.send(msg_on)
                print(f"Note {note} ON送信")
                
                # 極短時間待機（ハードウェアの処理時間）
                time.sleep(0.01)
                
                # Note Off
                msg_off = mido.Message('note_off', channel=0, note=note, velocity=0)
                outport.send(msg_off)
                print(f"Note {note} OFF送信")
                
                # 次のノートまでの最小間隔
                time.sleep(0.05)
            
            print("\n=== 高速BPMシミュレーション (BPM 240) ===")
            # BPM 240 = 250ms/beat
            beat_duration = 60.0 / 240
            note_duration = beat_duration * 0.3  # 75ms
            note_gap = beat_duration * 0.1      # 25ms
            
            print(f"ノート長: {note_duration*1000:.1f}ms, 間隔: {note_gap*1000:.1f}ms")
            
            for note in notes:
                msg_on = mido.Message('note_on', channel=0, note=note, velocity=64)
                outport.send(msg_on)
                print(f"Note {note} ON (高速)")
                
                time.sleep(note_duration)
                
                msg_off = mido.Message('note_off', channel=0, note=note, velocity=0)
                outport.send(msg_off)
                
                time.sleep(note_gap)
            
            print("\n=== 同時和音テスト ===")
            chord = [60, 64, 67]  # Cメジャー
            
            # 和音ON
            for note in chord:
                msg_on = mido.Message('note_on', channel=0, note=note, velocity=64)
                outport.send(msg_on)
                print(f"Chord note {note} ON")
            
            time.sleep(1.0)  # 1秒間和音を鳴らす
            
            # 和音OFF
            for note in chord:
                msg_off = mido.Message('note_off', channel=0, note=note, velocity=0)
                outport.send(msg_off)
                print(f"Chord note {note} OFF")
            
            print("\nテスト完了")
            
    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_direct_midi_rapid_fire()