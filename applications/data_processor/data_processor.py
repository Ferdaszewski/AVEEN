import os
from datetime import datetime

import ffmpeg


def create_video(image_dir, video_filename):
    if image_dir is None:
        return None
    if video_filename is None:
        video_filename = "%s-earth.mp4" % datetime.utcnow().strftime("%Y%m%d-%H.%M.%S")
    output = os.path.join(os.path.dirname(__file__), video_filename)

    (ffmpeg
     .input(image_dir, pattern_type='glob', framerate=2)
     .filter('scale', size='hd1080', force_original_aspect_ratio='decrease')
     .filter('minterpolate', fps='60', scd='none', mi_mode='mci', mc_mode='obmc', search_param=128, me='epzs', vsbmc=1)
     .output(output, movflags='faststart', pix_fmt='yuv420p', r=60)
     .run())


if __name__ == "__main__":
    # connection = setup_db_connection()
    # Get image data from DB
    image_dir = os.path.normpath(
        os.path.join(os.path.dirname(__file__), os.pardir, 'data_fetcher', 'test_images', '*.png'))
    print(image_dir)
    create_video(image_dir, '2024-06-11-earth.mp4')
