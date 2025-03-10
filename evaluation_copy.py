import os
import subprocess
import sys

# Config
REMOTE_HOST = "rocket.hpc.ut.ee"
REMOTE_USER = "jannis"
REMOTE_PATH = "~/optimos_v2"
SSH_KEY = "~/.ssh/id_rocket"
REMOTE_LIST_FILE = "remote_file_list.txt"
LOCAL_LIST_FILE = "local_file_list.txt"
LOCAL_OUTPUT_DIR = "evaluations"


def run_command(cmd):
    print(f"Running: {cmd}")

    process = subprocess.Popen(cmd, shell=True, stdout=sys.stdout, stderr=sys.stderr)
    process.wait()  # Wait for the process to finish

    if process.returncode != 0:
        raise subprocess.CalledProcessError(process.returncode, cmd)


def copy_file_to_remote(file_path):
    cmd = f"scp -i {SSH_KEY} {file_path} {REMOTE_USER}@{REMOTE_HOST}:{REMOTE_LIST_FILE}"
    run_command(cmd)


def find_files_on_remote():
    find_command = (
        f"ssh -i {SSH_KEY} {REMOTE_USER}@{REMOTE_HOST} "
        f'"find ~/optimos_v2/stores/*/evaluations/ -type f | grep -F -f {REMOTE_LIST_FILE} > ~/full_paths.txt"'
    )
    run_command(find_command)


def copy_file_back_to_local():
    cmd = f"scp -i {SSH_KEY} {REMOTE_USER}@{REMOTE_HOST}:~/full_paths.txt {LOCAL_LIST_FILE}"
    run_command(cmd)


def run_rsync():
    cmd = (
        f'rsync -e "ssh -i {SSH_KEY}" -avhz --progress '
        f"--files-from={LOCAL_LIST_FILE} --no-relative {REMOTE_USER}@{REMOTE_HOST}:/ {LOCAL_OUTPUT_DIR}/"
    )
    run_command(cmd)


def main():
    os.makedirs(LOCAL_OUTPUT_DIR, exist_ok=True)

    # 1. Copy file with list of filenames to remote
    copy_file_to_remote("/var/folders/dc/mhx8033j757bdr6m2lhpg5h00000gn/T/tmpjpm41p4w")

    # 2. Run find command on remote to get full paths
    find_files_on_remote()

    # 3. Copy full paths file back to local
    copy_file_back_to_local()

    # 4. Run rsync to copy files flat into "evaluations/"
    run_rsync()


if __name__ == "__main__":
    main()
