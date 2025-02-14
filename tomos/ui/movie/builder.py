from logging import getLogger
from pathlib import Path
import shutil

from moviepy.video.io import ImageSequenceClip

from tomos.ui.movie import configs
from tomos.ui.movie.scene import TomosScene

logger = getLogger(__name__)


if hasattr(configs, "FRAMES_PARENT_PATH"):
    FRAMES_PARENT_PATH = Path(configs.FRAMES_PARENT_PATH)  # type: ignore
else:
    FRAMES_PARENT_PATH = Path.cwd() / "output_tomos"


def build_movie_from_file(source_code_path, movie_path, timeline):
    frames_path = FRAMES_PARENT_PATH / Path(source_code_path).name
    source_code = open(source_code_path, 'r').read()
    build_movie_frames(source_code, timeline, frames_path)
    generate_mp4(frames_path, movie_path)
    return


def build_movie_frames(code, timeline, frames_path):
    frames_path = Path(frames_path)
    clean_folder(frames_path)
    scene = TomosScene(code, timeline=timeline, output_path=frames_path)
    logger.info(f"Rendering movie frames to {frames_path}")
    return scene.render()


def generate_mp4(frames_path, movie_path):
    frames_folder = frames_path / "frames"
    fps = getattr(configs, "FPS", 1)
    image_files = [str(f) for f in sorted(frames_folder.glob("*.jpg"))]
    if not image_files:
        logger.error(f"Unable to find any image in {frames_folder}")
        exit(0)
    clip = ImageSequenceClip.ImageSequenceClip(image_files, fps=fps)
    clip.write_videofile(movie_path, codec="libx264", bitrate="5000k", audio=False)


def clean_folder(folder_path):
    if folder_path.exists():
        if shutil.rmtree.avoids_symlink_attacks:
            shutil.rmtree(folder_path)
        else:
            print(f"Unable to remove folder {folder_path}. Please remove it manually.")
            exit(0)
    folder_path.mkdir(parents=True, exist_ok=True)
