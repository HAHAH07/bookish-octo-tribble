import os
import io
import sys
import subprocess
import platform
import shutil
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

'''
jenkins第一步更新三个py脚本到workspace
调用该脚本
该脚本更新编译目录
编译
将编译脚本和编译完成的文件转移到另一个目录
'''

git_win = "https://github.com/HAHAH07/verbose-train.git"
git_linux = "https://github.com/HAHAH07/linux_source.git"
compileSpace_now = "undefined"
compileSpace_linux = "/home/xiehanqi/Jenkins/workspace"          # 脚本目录
compileSpace_win = "D:/Jenkins/compileSpace"    # 编译目录
script_base_name = os.getenv("BUILD_SCRIPT", "build")  # 默认脚本名build
branch = os.getenv("GIT_BRANCH", "main")              # 默认分支main

# 根据操作系统返回对应的脚本路径
def get_platform_specific_script(script_name):
    # 获取py脚本目录
    script_dir = os.path.dirname(os.path.abspath(__file__))

    system = platform.system().lower()
    if system == "windows":
        source_bat = os.path.join(script_dir, f"{script_name}.bat")
        shutil.copy2(source_bat, compileSpace_win)
        print(f"已复制: {source_bat} -> {os.path.join(compileSpace_win, f"{script_name}.bat")}")
        return f"{script_name}.bat"
    elif system in ("linux", "darwin"):
        source_sh = os.path.join(script_dir, f"{script_name}.sh")
        shutil.copy2(source_sh, compileSpace_linux)
        print(f"已复制: {source_sh} -> {os.path.join(compileSpace_linux, f"{script_name}.sh")}")
        return f"./{script_name}.sh"
    else:
        raise OSError(f"Unsupported operating system: {system}")

# 执行编译脚本并处理输出
def run_script(script_path, args=None):
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
            encoding='utf-8',  # 明确指定编码为 utf-8
            shell=(platform.system() == "Windows")  # Windows 需要 shell=True
        )
        print(result.stdout)
        print("Script executed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Script failed with code {e.returncode}:")
        print(e.stdout)
        return False

def pull_repository(repo_url, target_dir, branch="main"):
    # 从Git仓库克隆代码
    if not os.path.exists(target_dir):
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

    # 从Git仓库更新代码
    else:
        print(f"pulling repository: {repo_url} (branch: {branch})")
        try:
            command = f'git -C {target_dir} pull origin {branch}'
            result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
            print(result.stdout)

        except subprocess.CalledProcessError as e:
            print(f"Failed to pull repository: {e.stderr}")
            return False
        print("Repository update successfully")
        return True
                

# 根据操作系统返回对应的Git仓库地址
def get_platform_repo_url():
    system = platform.system().lower()
    if system == "windows":
        compileSpace_now = compileSpace_win
        return git_win
    elif system in ("linux", "darwin"):
        compileSpace_now = compileSpace_linux
        return git_linux
    else:
        raise OSError(f"Unsupported operating system: {system}")

def main():
    try:
        # 1.获取对应系统的Git仓库地址
        repo_url = get_platform_repo_url()
        print(f"Detected OS: {platform.system()}, using repo: {repo_url}")

        # 2.更新仓库到编译目录
        if not pull_repository(repo_url, compileSpace_now, branch):
            sys.exit(1)

        # 3.获取系统对应的脚本
        script_path = get_platform_specific_script(script_base_name)
        print(f"Using build script: {script_path}")

        # 4.切换到编译目录
        os.chdir(compileSpace_now)
        print(f"Now directory: {compileSpace_now}")

        # 5.执行脚本
        success = run_script(script_path, args=["--config=release"])

        # 6.删除本地仓临时脚本
        os.remove(f"./{script_path}")

        # 6.返回状态码
        sys.exit(0 if success else 1)

    except Exception as e:
        print(f"Critical error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
