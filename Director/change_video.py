import os
import subprocess

def find_all_mp4_files(folder_path):
    """递归查找所有子文件夹下的 MP4 文件"""
    mp4_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith('.mp4'):
                full_path = os.path.join(root, file)
                mp4_files.append(full_path)
    return mp4_files
def convert_mp4_file(input_path, output_path):
    """针对 4K/25fps 视频的极限压缩版 ffmpeg 转换"""
    command = [
        "ffmpeg",
        "-i", input_path,
        "-c:v", "libx264",
        
        # --- 核心压缩控制 ---
        "-crf", "28",               # 28 依然是甜点位，如果想更小可以开到 30
        "-preset", "slower",        # 用编码时间换取更小的体积
        "-maxrate", "3000k",        # 【新增】强制限制最高视频码率为 3000kbps (原视频是9870)
        "-bufsize", "6000k",        # 【新增】搭配 maxrate 使用，通常是它的 2 倍
        
        # --- 画面控制 (修复了帧率问题) ---
        # 如果你必须保留 4K 画质，请把下面这行改成： "-vf", "scale=3840:2160",
        "-vf", "scale=1920:1080",   # 默认降为 1080p，注意：去掉了导致体积变大的 fps=30！
        
        # --- 音频与兼容性 ---
        "-c:a", "aac",              
        "-b:a", "128k",             # 压制音频
        "-pix_fmt", "yuv420p",      # 保证所有浏览器都能正常播放色彩
        "-movflags", "+faststart",  # 将视频的 metadata 移到文件头部，网页端实现“边下边播”
        "-y",                       
        output_path
    ]

    print(f"正在深度压缩: {input_path} -> {output_path}")
    try:
        subprocess.run(command, check=True)
        print(f"✅ 成功转换: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"❌ 转换失败: {input_path}")
        print(e)
        
def batch_convert_videos(root_folder, output_root=None):
    """批量转换所有找到的 MP4 文件"""
    if output_root is None:
        output_root = os.path.join(root_folder, "converted_videos")
    
    if not os.path.exists(output_root):
        os.makedirs(output_root)
    
    mp4_files = find_all_mp4_files(root_folder)
    print(f"共找到 {len(mp4_files)} 个 MP4 文件。")

    for input_path in mp4_files:
        # 保持相对路径结构
        relative_path = os.path.relpath(input_path, root_folder)
        output_path = os.path.join(output_root, os.path.splitext(relative_path)[0] + "_converted.mp4")

        # 创建对应的子文件夹
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 转换视频
        convert_mp4_file(input_path, output_path)

    print("🎉 全部转换完成！")

# 示例执行方式
if __name__ == "__main__":
    root_folder = r"/data/new_disk4/guochch/Guochch.github.io/TaoGS/motion"  # 替换为你的视频根目录
    output_folder = "motion_new"  # 输出文件夹，可自定义
    batch_convert_videos(root_folder, output_folder)