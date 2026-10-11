import datetime


def write_log(message):
  """メッセージにタイムスタンプを付与してファイルとコンソールに出力する"""
  timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  log_line = f"[{timestamp}] {message}\n"
  print(log_line, end="")

  # 同階層に "minecraft.log" というファイルを作成して追記保存
  try:
    with open("minecraft.log", "a", encoding="utf-8") as f:
      f.write(log_line)
  except Exception as e:
    print(f"ログ書き込みエラー: {e}")