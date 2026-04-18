import ffmpeg
import os
import sys
import glob
import tempfile


def create_transparent_gif_from_pngs(image_folder, output_file, fps=30):
    if not os.path.isdir(image_folder):
        raise FileNotFoundError(f"Không tìm thấy thư mục: {image_folder}")

    input_pattern = os.path.join(image_folder, 'frame_*.png')
    frame_paths = sorted(glob.glob(input_pattern))
    if not frame_paths:
        raise FileNotFoundError(
            f"Không tìm thấy ảnh theo mẫu: {input_pattern}\n"
            "Hãy kiểm tra tên file có dạng frame_001.png / frame_0001.png ..."
        )

    # Dùng concat demuxer để tương thích cả build FFmpeg không hỗ trợ pattern_type=glob
    fd, concat_list_path = tempfile.mkstemp(suffix='.txt', prefix='ffmpeg_frames_', dir=image_folder)
    os.close(fd)

    try:
        duration = 1 / max(fps, 1)
        with open(concat_list_path, 'w', encoding='utf-8') as f:
            for p in frame_paths:
                # concat demuxer yêu cầu escape dấu nháy đơn trong path
                safe_path = os.path.abspath(p).replace('\\', '/').replace("'", r"'\\''")
                f.write(f"file '{safe_path}'\n")
                f.write(f"duration {duration:.8f}\n")
            # Lặp lại frame cuối để duration cuối có hiệu lực
            last_safe = os.path.abspath(frame_paths[-1]).replace('\\', '/').replace("'", r"'\\''")
            f.write(f"file '{last_safe}'\n")

        video = (
            ffmpeg
            .input(concat_list_path, format='concat', safe=0)
            .filter('format', 'rgba')
            .filter('fps', fps=fps)
        )

        split = video.filter_multi_output('split')
        video_for_palette = split[0]
        video_for_gif = split[1]

        palette = (
            video_for_palette
            .filter('palettegen', reserve_transparent=1)
        )

        (
            ffmpeg
            .filter([video_for_gif, palette], 'paletteuse', alpha_threshold=1)
            .output(output_file, loop=0)
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        print(f"🎉 Đã tạo GIF thành công: {output_file}")
    except ffmpeg.Error as e:
        stderr = e.stderr.decode(errors='ignore') if e.stderr else str(e)
        if 'No such file or directory' in stderr or 'Could find no file or sequence' in stderr:
            print(
                f"❌ Không tìm thấy ảnh theo mẫu: {input_pattern}\n"
                "   Hãy kiểm tra tên file có dạng frame_001.png / frame_0001.png ..."
            )
        else:
            print(f"❌ Lỗi: {stderr}")
    finally:
        if os.path.exists(concat_list_path):
            try:
                os.remove(concat_list_path)
            except OSError:
                pass

if __name__ == "__main__":
    if len(sys.argv) != 2 and len(sys.argv) != 3:
        print("Usage: python gifmaker.py <image_folder> <output_file>")
        sys.exit(1)

    image_folder = sys.argv[1]
    if len(sys.argv) == 2:
        output_file = os.path.join(image_folder, 'output.gif')
    else:
        output_file = sys.argv[2]
    create_transparent_gif_from_pngs(image_folder, output_file)