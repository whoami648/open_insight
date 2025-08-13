import os
import shutil

# def remove_empty_dirs(root_dir):
#     for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
#         # Check if the directory is empty (no files and no subdirectories)
#         if not dirnames and not filenames:
#             try:
#                 os.rmdir(dirpath)
#                 print(f"Removed empty directory: {dirpath}")
#             except Exception as e:
#                 print(f"Failed to remove {dirpath}: {e}")

def remove_dirs_without_nonempty_output(root_dir):
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        # Skip the root directory itself
        if dirpath == root_dir:
            continue
        output_file = os.path.join(dirpath, "output.txt")
        if not (os.path.isfile(output_file) and os.path.getsize(output_file) > 0):
            try:
                shutil.rmtree(dirpath)
                print(f"Removed directory (missing or empty output.txt): {dirpath}")
            except Exception as e:
                print(f"Failed to remove {dirpath}: {e}")
                
        output_file = os.path.join(dirpath, "output_tmp.txt")

        if not (os.path.isfile(output_file) and os.path.getsize(output_file) > 0):
            try:
                shutil.rmtree(dirpath)
                print(f"Removed directory (missing or empty output_tmp.txt): {dirpath}")
            except Exception as e:
                print(f"Failed to remove {dirpath}: {e}")


if __name__ == "__main__":
    target_dir = "/home/zyx/open_insight/Qwen-8b-ans1"
    # remove_empty_dirs(target_dir)Qwen-8b-ans1/Tencent_QTAF/output.txt
    remove_empty_dirs = remove_dirs_without_nonempty_output(target_dir)