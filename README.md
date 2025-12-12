# Youjo Run

遊べるURLはこちら
https://suzunayui.com/youjo-run/

mp4 からスプライトシートを作って、`index.html` で動かす簡単なデモです。

## スプライトシートの作り方

`make_sprite_sheets.py` を使うには、`bin` フォルダに `ffmpeg.exe` を置いてください。  
（別の場所にある場合は `--ffmpeg` でパス指定できます）

1. 依存インストール
   ```sh
   python -m pip install pillow
   ```
2. mp4 があるディレクトリで実行
   ```sh
   python make_sprite_sheets.py
   ```

### オプション例

列数や出力先を変える場合:
```sh
python make_sprite_sheets.py --columns 8 --output-dir spritesheets
```

## 実行

`index.html` をブラウザで開くと動きます。
