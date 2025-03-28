import os
import subprocess
import sys
import json
from typing import Tuple
from dotenv import load_dotenv
import PyInstaller.__main__
from PyInstaller.utils.hooks import collect_submodules, collect_all
from PyInstaller.utils.win32.versioninfo import (
    VSVersionInfo,
    FixedFileInfo,
    StringFileInfo,
    StringTable,
    StringStruct,
    VarFileInfo,
    VarStruct,
)

load_dotenv()


def parse_version(version: str) -> Tuple[int, int, int]:
    """將版本號字符串解析為元組 (major, minor, patch)"""
    parts = version.split(".")
    if len(parts) != 3:
        raise ValueError(f"無效的版本號格式: {version}")
    return tuple(map(int, parts))


def update_version_json(version: str):
    """更新version.json文件中的版本號"""
    with open("version.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    data["version"] = version

    # 更新exe_url中的檔案名
    base_url = data["exe_url"].rsplit("/", 1)[0]
    data["exe_url"] = f"{base_url}/Legendary_{version}.exe"

    with open("version.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def sync_version():
    try:
        version = os.getenv("VERSION", "1.0.0")
        print(f"檢測到版本號: {version}")

        update_version_json(version)
        print("✅ 已更新 version.json")

        print("🎉 所有檔案版本同步完成！")
    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")
        exit(1)


def run_command(command):
    """运行命令并实时输出结果"""
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        shell=True,
    )

    for line in process.stdout:
        print(line, end="")

    process.wait()
    return process.returncode


def create_version_info(version: str) -> VSVersionInfo:
    """創建版本資訊對象"""
    version_tuple = parse_version(version)

    return VSVersionInfo(
        ffi=FixedFileInfo(
            filevers=(version_tuple[0], version_tuple[1], version_tuple[2], 0),
            prodvers=(version_tuple[0], version_tuple[1], version_tuple[2], 0),
            mask=0x3F,
            flags=0x0,
            OS=0x40004,
            fileType=0x1,
            subtype=0x0,
            date=(0, 0),
        ),
        kids=[
            StringFileInfo(
                [
                    StringTable(
                        "040904B0",
                        [
                            StringStruct("CompanyName", "Legendary"),
                            StringStruct("FileDescription", "Legendary Auto Clicker"),
                            StringStruct("FileVersion", version),
                            StringStruct("InternalName", "Legendary"),
                            StringStruct("LegalCopyright", "Copyright (c) 2025"),
                            StringStruct("OriginalFilename", "Legendary.exe"),
                            StringStruct("ProductName", "Legendary"),
                            StringStruct("ProductVersion", version),
                        ],
                    )
                ]
            ),
            VarFileInfo([VarStruct("Translation", [1033, 1200])]),
        ],
    )


def build_application(version: str):
    """使用 PyInstaller 構建應用程式"""
    # 收集所需的依賴
    datas = []
    binaries = []
    hiddenimports = ["ttkbootstrap", "keyboard", "win32gui", "win32con", "win32api"]
    hiddenimports += collect_submodules("pyperclip")

    # 收集 pywin32 相關的所有依賴
    tmp_ret = collect_all("pywin32")
    datas += tmp_ret[0]
    binaries += tmp_ret[1]
    hiddenimports += tmp_ret[2]

    # 構建參數
    args = [
        "src/client/Legendary.py",  # 入口腳本
        "--name",
        f"Legendary_{version}",  # 輸出檔案名
        "--noconfirm",  # 不詢問確認
        "--onefile",  # 生成單個可執行檔案
        "--windowed",  # 使用 GUI 模式
        "--icon",
        "src/assets/icon/legendary.ico",  # 圖標
        "--distpath",
        "./release",  # 輸出目錄
        "--clean",  # 清理臨時檔案
    ]

    # 添加隱藏導入
    for imp in hiddenimports:
        args.extend(["--hidden-import", imp])

    # 添加數據檔案
    for data in datas:
        args.extend(["--add-data", f"{data[0]};{data[1]}"])

    # 添加二進制檔案
    for binary in binaries:
        args.extend(["--add-binary", f"{binary[0]};{binary[1]}"])

    # 設置版本資訊
    version_info = create_version_info(version)
    version_info_path = "version_info.txt"
    with open(version_info_path, "w") as f:
        f.write(str(version_info))
    args.extend(["--version-file", version_info_path])

    try:
        PyInstaller.__main__.run(args)
    finally:
        # 清理臨時檔案
        if os.path.exists(version_info_path):
            os.remove(version_info_path)


def main():
    print("🔄 正在同步版本資訊...")
    try:
        version = os.getenv("VERSION", "1.0.0")
        sync_version()
    except Exception as e:
        print(f"❌ 版本同步失敗: {str(e)}")
        sys.exit(1)

    print("\n🚀 開始構建應用程式...")
    try:
        # 清理舊的構建目錄
        import shutil

        for dir_path in ["build", "release"]:
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)
                print(f"🧹 已清理 {dir_path} 目錄")

        build_application(version)
        print("\n✅ 構建成功！")

        # 清理 .spec 檔案
        spec_file = f"Legendary_{version}.spec"
        if os.path.exists(spec_file):
            os.remove(spec_file)
            print("🧹 已清理 .spec 檔案")

    except Exception as e:
        print(f"\n❌ 構建失敗：{str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
