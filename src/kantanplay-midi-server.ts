import { FastMCP } from '@modelcontextprotocol/sdk';
import { Output } from 'midi';
import { z } from 'zod';

// MCPサーバーの作成
const mcp = new FastMCP('kantanplay');

// MIDI設定
let midiOut: Output | null = null;
let availablePorts: string[] = [];
let selectedPortIndex: number | null = null;
let midiPortOpened = false;

// MIDIの初期化
try {
  console.log('MIDIを初期化しています...');
  midiOut = new Output();
  
  // 利用可能なポートの取得
  const portCount = midiOut.getPortCount();
  for (let i = 0; i < portCount; i++) {
    availablePorts.push(midiOut.getPortName(i));
  }
  
  // 利用可能なポートの確認
  if (availablePorts.length === 0) {
    // 利用可能なポートがない場合は仮想ポートを作成
    midiOut.openVirtualPort('Virtual MIDI Port');
    console.log('利用可能なMIDIポートがありません。仮想MIDIポートを作成しました。');
    midiPortOpened = true;
  } else {
    console.log(`利用可能なMIDIポート: ${availablePorts.length}個`);
    availablePorts.forEach((port, index) => {
      console.log(`${index}: ${port}`);
    });
  }
} catch (error) {
  console.error(`警告: MIDIの初期化に失敗しました: ${error}`);
  console.error('MIDI機能は利用できません。');
  console.error('以下の手順を試してください:');
  console.error('1. ターミナルで \'npm install midi\' を実行');
}

// MIDIポートを開く
mcp.tool({
  name: 'open_midi_port',
  description: '指定されたインデックスのMIDIポートを開きます',
  parameters: z.object({
    port_index: z.number().int().describe('開きたいMIDIポートのインデックス')
  }),
  handler: async ({ port_index }: { port_index: number }) => {
    if (!midiOut) {
      return 'MIDIライブラリが初期化されていないため、MIDI機能は利用できません。';
    }
    
    if (availablePorts.length === 0) {
      return '利用可能なMIDIポートがありません。';
    }
    
    if (port_index < 0 || port_index >= availablePorts.length) {
      return `エラー: 有効なポートインデックスを指定してください (0-${availablePorts.length - 1})`;
    }
    
    try {
      // 既に開いているポートがあれば閉じる
      if (midiPortOpened) {
        midiOut.closePort();
      }
      
      // 指定されたポートを開く
      midiOut.openPort(port_index);
      selectedPortIndex = port_index;
      midiPortOpened = true;
      
      return `MIDIポートを開きました: ${availablePorts[port_index]}`;
    } catch (error) {
      return `MIDIポートを開く際にエラーが発生しました: ${error}`;
    }
  }
});

// 利用可能なMIDIポートの一覧を取得
mcp.tool({
  name: 'list_midi_ports',
  description: '利用可能なMIDIポートの一覧を返します',
  parameters: z.object({}),
  handler: async () => {
    if (!midiOut) {
      return 'MIDIライブラリが初期化されていないため、MIDI機能は利用できません。';
    }
    
    if (availablePorts.length === 0) {
      return '利用可能なMIDIポートはありません';
    }
    
    const portList = availablePorts.map((port, index) => `${index}: ${port}`).join('\n');
    
    let currentPort = '';
    if (selectedPortIndex !== null && midiPortOpened) {
      currentPort = `\n\n現在選択中のポート: ${selectedPortIndex}: ${availablePorts[selectedPortIndex]}`;
    } else {
      currentPort = '\n\n現在ポートは選択されていません。open_midi_port()を使用してポートを選択してください。';
    }
    
    return `利用可能なMIDIポート:\n${portList}${currentPort}`;
  }
});

// MIDIノートを送信
mcp.tool({
  name: 'send_midi_note',
  description: '指定されたノート番号のMIDIノートをチャンネル1で送信します',
  parameters: z.object({
    note_number: z.number().int().min(0).max(127).describe('MIDIノート番号 (0-127)')
  }),
  handler: async ({ note_number }: { note_number: number }) => {
    if (!midiOut) {
      return 'MIDIライブラリが初期化されていないため、MIDI機能は利用できません。';
    }
    
    if (!midiPortOpened) {
      return 'MIDIポートが開かれていません。まずopen_midi_port()を使用してポートを選択してください。';
    }
    
    try {
      // MIDIメッセージを作成 (Note On, チャンネル1, ベロシティ100)
      // チャンネル1のNote Onは0x90
      midiOut.sendMessage([0x90, note_number, 100]);
      
      // 0.5秒後にノートオフメッセージを送信
      setTimeout(() => {
        if (midiOut) {
          // Note Offメッセージ (ベロシティ0のNote Onと同じ)
          midiOut.sendMessage([0x90, note_number, 0]);
        }
      }, 500);
      
      return `MIDI Note ${note_number} をチャンネル1で送信しました`;
    } catch (error) {
      return `MIDI送信エラー: ${error}`;
    }
  }
});

// MIDI CCメッセージを送信
mcp.tool({
  name: 'send_midi_cc',
  description: '指定されたコントローラー番号とバリューでMIDI CCメッセージをチャンネル1で送信します',
  parameters: z.object({
    controller: z.number().int().min(0).max(127).describe('コントローラー番号 (0-127)'),
    value: z.number().int().min(0).max(127).describe('コントロール値 (0-127)')
  }),
  handler: async ({ controller, value }: { controller: number, value: number }) => {
    if (!midiOut) {
      return 'MIDIライブラリが初期化されていないため、MIDI機能は利用できません。';
    }
    
    if (!midiPortOpened) {
      return 'MIDIポートが開かれていません。まずopen_midi_port()を使用してポートを選択してください。';
    }
    
    try {
      // MIDIメッセージを作成 (CC, チャンネル1)
      // チャンネル1のCCは0xB0
      midiOut.sendMessage([0xB0, controller, value]);
      return `MIDI CC ${controller}=${value} をチャンネル1で送信しました`;
    } catch (error) {
      return `MIDI送信エラー: ${error}`;
    }
  }
});

// MIDIシーケンスを送信
mcp.tool({
  name: 'send_midi_sequence',
  description: '指定されたBPMで複数のMIDIノートを順番に送信します',
  parameters: z.object({
    bpm: z.number().positive().describe('テンポ（1分間あたりの拍数）'),
    notes: z.array(z.number().int().min(0).max(127)).describe('送信するMIDIノート番号のリスト (各ノートは0-127の範囲)')
  }),
  handler: async ({ bpm, notes }: { bpm: number, notes: number[] }) => {
    if (!midiOut) {
      return 'MIDIライブラリが初期化されていないため、MIDI機能は利用できません。';
    }
    
    if (!midiPortOpened) {
      return 'MIDIポートが開かれていません。まずopen_midi_port()を使用してポートを選択してください。';
    }
    
    // 1ステップの時間を計算（ミリ秒）
    // 1分（60000ミリ秒）をBPMで割り、それをさらに2で割る（オンとオフで等分）
    const stepTime = 60000 / bpm / 2;
    
    try {
      const sentNotes: number[] = [];
      
      // 各ノートを順番に送信する関数
      const sendNote = (index: number) => {
        if (index >= notes.length || !midiOut) return;
        
        const note = notes[index];
        
        // Note Onメッセージを送信（チャンネル1、ベロシティ100）
        midiOut.sendMessage([0x90, note, 100]);
        sentNotes.push(note);
        
        // 1ステップ分待機後にNote Offを送信
        setTimeout(() => {
          if (midiOut) {
            // Note Offメッセージを送信
            midiOut.sendMessage([0x90, note, 0]);
            
            // 1ステップ分待機後に次のノートを送信
            setTimeout(() => {
              sendNote(index + 1);
            }, stepTime);
          }
        }, stepTime);
      };
      
      // 最初のノートから送信開始
      sendNote(0);
      
      return `BPM ${bpm}で以下のMIDIノートシーケンスを送信しました: ${notes.join(', ')}`;
    } catch (error) {
      return `MIDI送信エラー: ${error}`;
    }
  }
});

// サーバー起動
try {
  console.log('MIDI送信サーバーを起動します...');
  
  if (midiOut) {
    console.log('利用可能なMIDIポート:', availablePorts);
    console.log('使用するMIDIポートを選択するには、list_midi_ports()でポート一覧を確認し、');
    console.log('open_midi_port(port_index)でポートを選択してください。');
  } else {
    console.log('警告: MIDIライブラリが初期化されていないため、MIDI機能は利用できません。');
    console.log('MIDI機能を使用するには、以下のコマンドでmidiをインストールしてください:');
    console.log('npm install midi');
  }
  
  // MCPサーバーの起動
  mcp.run();
  
  // プログラム終了時の処理
  process.on('SIGINT', () => {
    if (midiOut && midiPortOpened) {
      console.log('MIDI接続を閉じています...');
      midiOut.closePort();
    }
    process.exit(0);
  });
} catch (error) {
  console.error(`サーバー起動エラー: ${error}`);
}
