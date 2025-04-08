#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def get_platform_specific_script(script_name):
    """根据操作系统返回对应的脚本路径"""
    system = platform.system().lower()
    if system == "windows":
        return f"{script_name}.bat"
    elif system in ("linux", "darwin"):  # darwin = macOS
        return f"./{script_name}.sh"
    else:
        raise OSError(f"Unsupported operating system: {system}")

def run_script(script_path, args=None):
    """执行编译脚本并处理输出"""
    if not os.path.exists(script_path):
        raise FileNotFoundError(f"Script not found: {script_path}")

    cmd = [script_path]
    if args:
        cmd.extend(args)

    try:
        print(f"Executing: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            shell=(platform.system() == "Windows")  # Windows 需要 shell=True
        )
        print(result.stdout)
        print("Script executed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Script failed with code {e.returncode}:")
        print(e.stdout)
        return False

def clone_repository(repo_url, target_dir, branch="main"):
    """从Git仓库克隆代码"""
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    
    print(f"Cloning repository: {repo_url} (branch: {branch})")
    result = subprocess.run(
        ["git", "clone", "--branch", branch, "--depth", "1", repo_url, target_dir],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    if result.returncode != 0:
        print(f"Failed to clone repository:\n{result.stdout}")
        return False
    print("Repository cloned successfully")
    return True

def get_platform_repo_url():
    """根据操作系统返回对应的Git仓库地址"""
    system = platform.system().lower()
    if system == "windows":
        return "https://github.com/HAHAH07/verbose-train.git"
    elif system in ("linux", "darwin"):
        return "https://github.com/your-org/linux-build-repo.git"
    else:
        raise OSError(f"Unsupported operating system: {system}")

def main():
    # Jenkins 环境变量（如果存在）
    workspace = os.getenv("WORKSPACE", os.getcwd())
    script_base_name = os.getenv("BUILD_SCRIPT", "build")  # 默认脚本名为 "build"
    branch = os.getenv("GIT_BRANCH", "main")              # 默认分支为 main

    try:
        # 1. 获取对应系统的Git仓库地址
        repo_url = get_platform_repo_url()
        print(f"Detected OS: {platform.system()}, using repo: {repo_url}")

        # 2. 克隆仓库到工作目录
        if not clone_repository(repo_url, workspace, branch):
            sys.exit(1)

        # 3. 切换到工作目录
        os.chdir(workspace)
        print(f"Working directory: {workspace}")

        # 4. 获取系统对应的脚本
        script_path = get_platform_specific_script(script_base_name)
        print(f"Using build script: {script_path}")

        # 5. 执行脚本（可传递额外参数）
        success = run_script(script_path, args=["--config=release"])

        # 6. 返回状态码
        sys.exit(0 if success else 1)

    except Exception as e:
        print(f"Critical error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
