import matplotlib.pyplot as plt
import matplotlib.animation as animation
from IPython.display import HTML
import matplotlib
import matplotlib as mpl
import random
import cv2

mpl.rcParams["savefig.pad_inches"] = 0
matplotlib.rcParams["animation.embed_limit"] = 2**128

plt.ioff()
# Function to update each frame
def update(frame):
    plt.clf()  # Clear the previous plot
    plt.imshow(frame, cmap="viridis")  # Show the new frame
    plt.axis("off")
    plt.tight_layout()
    plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
    plt.gca().set_axis_off()

def create_video(frames):
    ratio = frames[0].shape[0] / frames[0].shape[1]
    constant = 8
    # Create animation
    fig = plt.figure(figsize=(constant, constant * ratio))
    ani = animation.FuncAnimation(fig, update, frames=frames, interval=60)
    # Display animation as HTML
    return HTML(ani.to_jshtml())



def save_video(frames, frame_number, car_set_object, box_index):
    FPS = 30
    out = cv2.VideoWriter(
        f"videos/{frame_number}_{car_set_object}_{box_index}.mp4",
        cv2.VideoWriter_fourcc(*"mp4v"),
        FPS,
        (frames[0].shape[1], frames[0].shape[0]),
    )
    for frame in frames:
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        out.write(frame)
    out.release()
