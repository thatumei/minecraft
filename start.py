import os
import subprocess
import threading
from log import write_log


def _run_process(cmd, loader, version, username, retry_count=0):
    """別スレッドで実際にコマンドを実行し、出力をリアルタイムで拾う"""
    write_log(f"プロセス実行開始: {cmd}")
    
    # ANSIカラー出力を維持するための環境変数
    env = os.environ.copy()
    env["FORCE_COLOR"] = "1"
    
    try:
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="ignore",
            env=env,
        )

        full_output = ""
        # 1行ずつリアルタイムに読み込んでログに流す
        while True:
            output = process.stdout.readline()
            if output == "" and process.poll() is not None:
                break
            if output:
                stripped = output.strip()
                write_log(stripped)
                full_output += stripped + "\n"

        return_code = process.poll()

        # 安定版が見つからずに失敗した場合の自動リトライ処理（unstableへ切り替え）
        if return_code != 0 and ("Failed to find" in full_output or "stable loader version" in full_output):
            if retry_count == 0:
                loader_lower = loader.strip().lower() if loader else ""
                
                # リトライ用コマンドの組み立て（不連続なバージョンやstableのフォールバック）
                if loader_lower:
                    new_cmd = f"portablemc start {loader}::{version}:unstable -u {username} --main-dir .minecraft"
                else:
                    new_cmd = f"portablemc start {version}:unstable -u {username} --main-dir .minecraft"

                write_log(f"安定版が見つからないため、不安定版 (unstable) で再挑戦します: {new_cmd}")
                _run_process(new_cmd, loader, version, username, retry_count=1)
                return

        if return_code == 0:
            write_log("マイクラが正常に終了しました。")
        else:
            write_log(f"マイクラが異常終了しました (終了コード: {return_code})")

    except Exception as e:
        write_log(f"例外発生: {e}")


def start(loader, version, username):
    if not username or not username.strip():
        username = "Player"

    # ── コマンドの組み立て ──
    if loader and loader.strip():
        loader_lower = loader.strip().lower()
        # すべてのローダーでローダーバージョン指定に対応するダブルコロン (::) を使用
        cmd = f"portablemc start {loader_lower}::{version} -u {username} --main-dir .minecraft"
    else:
        # バニラの場合
        cmd = f"portablemc start {version} -u {username} --main-dir .minecraft"

    write_log(
        f"起動リクエスト受付 -> ユーザー: {username}, バージョン/ローダーVer: {version},"
        f" ローダー: {loader or 'Vanilla'}"
    )

    # ── フリーズ防止：別スレッドでバックグラウンド実行 ──
    thread = threading.Thread(target=_run_process, args=(cmd, loader, version, username, 0))
    thread.daemon = True  # メインウィンドウ終了時にスレッドも一緒に終了する
    thread.start()