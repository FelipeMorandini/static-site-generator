import os
import shutil

def copy_static_to_public(src="static", dest="public"):
    """
    Recursively copies all files and directories from src to dest,
    after first deleting all contents in dest (if it exists).
    Logs the path of every copied file.
    """
    if os.path.exists(dest):
        shutil.rmtree(dest)
    os.makedirs(dest, exist_ok=True)

    def recursive_copy(current_src, current_dest):
        for name in os.listdir(current_src):
            src_path = os.path.join(current_src, name)
            dest_path = os.path.join(current_dest, name)
            if os.path.isdir(src_path):
                os.makedirs(dest_path, exist_ok=True)
                recursive_copy(src_path, dest_path)
            else:
                shutil.copy(src_path, dest_path)
                print(f"Copied: {src_path} -> {dest_path}")

    recursive_copy(src, dest)