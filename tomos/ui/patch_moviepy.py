from moviepy.video.io.ffplay_previewer import FFPLAY_VideoPreviewer


class FixedPreviewer(FFPLAY_VideoPreviewer):
    # When preview window is closed by the user, moviepy is handling it wrongly
    # and dumping an ugly traceback.

    def show_frame(self, img_array):
        """Writes one frame in the file."""
        try:
            self.proc.stdin.write(img_array.tobytes())
        except BrokenPipeError:  # these 3 lines are the fix
            import sys  # these 3 lines are the fix

            sys.exit(1)  # these 3 lines are the fix
        except IOError as err:
            _, ffplay_error = self.proc.communicate()
            if ffplay_error is not None:
                ffplay_error = ffplay_error.decode()

            error = (
                f"{err}\n\nMoviePy error: FFPLAY encountered the following error while "
                f"previewing clip :\n\n {ffplay_error}"
            )

            raise IOError(error)
