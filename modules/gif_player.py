from PIL import Image, ImageTk, ImageSequence


class GIFPlayer:
    """handles animated GIF playback on a label"""

    _all_gifs = []

    def __init__(self, label, gif_path, width, height):
        self.label = label
        self.gif_path = gif_path
        self.width = width
        self.height = height
        self.frames = []
        self.current_frame = 0
        self.job = None
        self.durations = []

        # Load GIF without processing all frames yet
        self.gif = Image.open(gif_path)
        self.total_frames = self.gif.n_frames if hasattr(self.gif, "n_frames") else 1

        # Extract frame durations
        try:
            for frame_idx in range(self.total_frames):
                self.gif.seek(frame_idx)
                duration = self.gif.info.get("duration", 100)
                self.durations.append(duration)
        except EOFError:
            pass

        GIFPlayer._all_gifs.append(self)

    def _get_frame(self, frame_idx):
        """Get a specific frame and resize it"""
        self.gif.seek(frame_idx)
        frame = self.gif.convert("RGB")
        resized = frame.resize((self.width, self.height), Image.LANCZOS)
        photo = ImageTk.PhotoImage(resized)
        return photo

    def play(self):
        """start playing the GIF"""
        self.stop()
        self.current_frame = 0
        self.animate()

    def animate(self):
        """show next frame"""
        if self.total_frames > 0:
            try:
                # Load frame on demand
                photo = self._get_frame(self.current_frame)
                self.label.config(image=photo)
                self.label.image = photo

                # Get duration for this frame
                duration = (
                    self.durations[self.current_frame]
                    if self.current_frame < len(self.durations)
                    else 100
                )
                duration = max(duration / 5, 20)

                self.current_frame = (self.current_frame + 1) % self.total_frames
                self.job = self.label.after(duration, self.animate)
            except Exception as e:
                pass

    def stop(self):
        """stop the animation"""
        if self.job:
            self.label.after_cancel(self.job)
            self.job = None

    @classmethod
    def stop_all(cls):
        """stop all GIF animations"""
        for gif in cls._all_gifs:
            gif.stop()
