import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox
from PIL import Image, ImageDraw, ImageTk


PEACH_BG = "#FFFFFF"
PEACH_PANEL = "#FFD7BA"
PEACH_BUTTON = "#FFFFFF"
PEACH_HOVER = "#000000"
TEXT_COLOR = "#000000"
FONT_MAIN = ("Arial", 10, "bold")

CANVAS_WIDTH = 900
CANVAS_HEIGHT = 550
MAX_UNDO_STEPS = 50


root = tk.Tk()
root.title("Paint Application")
root.geometry("1060x760")
root.minsize(980, 700)
root.configure(bg=PEACH_BG)


image = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), "white")
draw = ImageDraw.Draw(image)
canvas_image = None

canvas_frame = tk.Frame(root, bg=PEACH_BUTTON, padx=4, pady=4)
canvas_frame.pack(padx=18, pady=10)

canvas = tk.Canvas(
    canvas_frame,
    width=CANVAS_WIDTH,
    height=CANVAS_HEIGHT,
    bg="white",
    cursor="cross",
    highlightthickness=0,
)
canvas.pack()


current_color = "black"
brush_size = 5
tool = "brush"
fill_shapes = False

start_x = start_y = None
last_x = last_y = None
preview_shape = None
action_snapshot = None
is_drawing = False


undo_stack = []


def remember_undo_state():
    undo_stack.append(image.copy())
    if len(undo_stack) > MAX_UNDO_STEPS:
        del undo_stack[0]

def undo():
    global image, draw, preview_shape, action_snapshot, is_drawing

    if is_drawing and action_snapshot is not None:
        
        image = action_snapshot.copy()
        action_snapshot = None
        is_drawing = False
        preview_shape = None
        refresh_canvas()
        return

    if not undo_stack:
        messagebox.showinfo("Undo", "There is nothing to undo.")
        return

    image = undo_stack.pop()
    draw = ImageDraw.Draw(image)
    preview_shape = None
    refresh_canvas()



def choose_color():
    global current_color, tool

    selected = colorchooser.askcolor(
        color=current_color,
        title="Choose a drawing color",
    )
    if selected and selected[1]:
        set_color(selected[1])


def set_color(color):
    
    global current_color, tool

    current_color = color
    tool = "brush"
    color_button.config(bg=current_color, activebackground=current_color)
    update_status()


def set_tool(selected_tool):
    global tool

    tool = selected_tool
    update_status()


def change_brush_size(value):
    global brush_size

    brush_size = max(1, min(100, int(float(value))))
    size_value_label.config(text=str(brush_size))


def toggle_fill():
    global fill_shapes

    fill_shapes = fill_var.get()
    update_status()


def update_status():
   
    fill_text = "On" if fill_shapes else "Off"
    status_label.config(
        text=(
            f"Tool: {tool.title()}    "
            f"Color: {current_color}    "
            f"Brush: {brush_size}px    "
            f"Fill: {fill_text}"
        )
    )



def shape_bounds(x1, y1, x2, y2):
    return min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)


def triangle_points(x1, y1, x2, y2):
    left, top, right, bottom = shape_bounds(x1, y1, x2, y2)
    middle_x = (left + right) / 2
    return [(middle_x, top), (right, bottom), (left, bottom)]


def draw_shape_on_image(x1, y1, x2, y2):
    bounds = shape_bounds(x1, y1, x2, y2)
    left, top, right, bottom = bounds
    outline_width = max(1, brush_size)

    if tool == "line":
        draw.line(
            (x1, y1, x2, y2),
            fill=current_color,
            width=outline_width,
        )
    elif tool == "rectangle":
        draw.rectangle(
            bounds,
            outline=current_color,
            fill=current_color if fill_shapes else None,
            width=outline_width,
        )
    elif tool == "oval":
        draw.ellipse(
            bounds,
            outline=current_color,
            fill=current_color if fill_shapes else None,
            width=outline_width,
        )
    elif tool == "triangle":
        points = triangle_points(x1, y1, x2, y2)
        draw.polygon(
            points,
            fill=current_color if fill_shapes else None,
        )
        if not fill_shapes:
            
            closed_points = points + [points[0]]
            draw.line(
                closed_points,
                fill=current_color,
                width=outline_width,
                joint="curve",
            )


def draw_preview(event):
    global preview_shape

    if preview_shape is not None:
        canvas.delete(preview_shape)
        preview_shape = None

    x1, y1 = start_x, start_y
    x2, y2 = event.x, event.y
    outline_width = max(1, brush_size)
    fill_color = current_color if fill_shapes else ""

    if tool == "line":
        preview_shape = canvas.create_line(
            x1, y1, x2, y2,
            fill=current_color,
            width=outline_width,
        )
    elif tool == "rectangle":
        preview_shape = canvas.create_rectangle(
            x1, y1, x2, y2,
            outline=current_color,
            fill=fill_color,
            width=outline_width,
        )
    elif tool == "oval":
        preview_shape = canvas.create_oval(
            x1, y1, x2, y2,
            outline=current_color,
            fill=fill_color,
            width=outline_width,
        )
    elif tool == "triangle":
        points = triangle_points(x1, y1, x2, y2)
        preview_shape = canvas.create_polygon(
            points,
            outline=current_color,
            fill=fill_color,
            width=outline_width,
        )



def start_drawing(event):
    global last_x, last_y, start_x, start_y
    global action_snapshot, is_drawing

    start_x = last_x = event.x
    start_y = last_y = event.y
    action_snapshot = image.copy()
    is_drawing = True

   
    if tool in ("brush", "eraser"):
        color = "white" if tool == "eraser" else current_color
        radius = brush_size / 2
        draw.ellipse(
            (event.x - radius, event.y - radius,
             event.x + radius, event.y + radius),
            fill=color,
        )
        canvas.create_oval(
            event.x - radius, event.y - radius,
            event.x + radius, event.y + radius,
            fill=color,
            outline=color,
        )


def draw_motion(event):
    global last_x, last_y

    if not is_drawing:
        return

    if tool in ("brush", "eraser"):
        color = "white" if tool == "eraser" else current_color
        canvas.create_line(
            last_x, last_y, event.x, event.y,
            fill=color,
            width=brush_size,
            capstyle=tk.ROUND,
            joinstyle=tk.ROUND,
            smooth=True,
        )
        draw.line(
            (last_x, last_y, event.x, event.y),
            fill=color,
            width=brush_size,
        )
        
        radius = brush_size / 2
        draw.ellipse(
            (event.x - radius, event.y - radius,
             event.x + radius, event.y + radius),
            fill=color,
        )
        last_x, last_y = event.x, event.y
    else:
        draw_preview(event)


def finish_drawing(event):
    global preview_shape, action_snapshot, is_drawing

    if not is_drawing:
        return

    if tool in ("line", "rectangle", "oval", "triangle"):
        draw_shape_on_image(start_x, start_y, event.x, event.y)

    if action_snapshot is not None:
        remember_undo_state_from_snapshot(action_snapshot)

    action_snapshot = None
    is_drawing = False
    preview_shape = None
    refresh_canvas()


def remember_undo_state_from_snapshot(snapshot):
    undo_stack.append(snapshot)
    if len(undo_stack) > MAX_UNDO_STEPS:
        del undo_stack[0]



def refresh_canvas():
    global canvas_image

    canvas.delete("all")
    canvas_image = ImageTk.PhotoImage(image)
    canvas.create_image(0, 0, anchor="nw", image=canvas_image)


def clear_canvas():
    global image, draw, preview_shape, action_snapshot, is_drawing

    confirmed = messagebox.askyesno(
        "Clear Canvas",
        "Are you sure you want to clear the entire canvas?",
        icon="warning",
    )
    if not confirmed:
        return

   
    remember_undo_state()
    image = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), "white")
    draw = ImageDraw.Draw(image)
    preview_shape = None
    action_snapshot = None
    is_drawing = False
    refresh_canvas()



def open_image():
    global image, draw

    file_path = filedialog.askopenfilename(
        title="Open an image",
        filetypes=[
            ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"),
            ("All files", "*.*"),
        ],
    )
    if not file_path:
        return

    try:
        with Image.open(file_path) as opened_file:
            opened_image = opened_file.convert("RGB")
            
            opened_image = opened_image.resize(
                (CANVAS_WIDTH, CANVAS_HEIGHT),
                Image.Resampling.LANCZOS,
            )

        remember_undo_state()
        image = opened_image
        draw = ImageDraw.Draw(image)
        refresh_canvas()
    except Exception as error:
        messagebox.showerror(
            "Open Error",
            f"Could not open the selected image:\n{error}",
        )


def save_image():
    file_path = filedialog.asksaveasfilename(
        title="Save your drawing",
        defaultextension=".png",
        filetypes=[
            ("PNG Image", "*.png"),
            ("JPEG Image", "*.jpg"),
            ("Bitmap Image", "*.bmp"),
        ],
    )
    if not file_path:
        return

    try:
        
        image.save(file_path)
        messagebox.showinfo(
            "Saved",
            f"Your drawing has been saved.\n\nSize: {CANVAS_WIDTH} x {CANVAS_HEIGHT}",
        )
    except Exception as error:
        messagebox.showerror(
            "Save Error",
            f"Could not save the drawing:\n{error}",
        )



def make_button(parent, text, command, width=None):
    return tk.Button(
        parent,
        text=text,
        command=command,
        width=width,
        bg=PEACH_BUTTON,
        fg=TEXT_COLOR,
        activebackground=PEACH_HOVER,
        activeforeground=TEXT_COLOR,
        font=FONT_MAIN,
        relief="flat",
        padx=9,
        pady=5,
        cursor="hand2",
    )



main_frame = tk.Frame(root, bg=PEACH_BG)
main_frame.pack(fill="both", expand=True, padx=15, pady=10)


toolbar = tk.Frame(main_frame, bg=PEACH_PANEL, padx=10, pady=10)
toolbar.pack(side="left", fill="y", padx=(0, 15))


tools_row = tk.Frame(toolbar, bg=PEACH_PANEL)
tools_row.pack(fill="x", pady=2)

color_button = make_button(tools_row, "Choose Color", choose_color)
color_button.pack(side="left", padx=3)

make_button(tools_row, "Brush", lambda: set_tool("brush")).pack(side="left", padx=3)
make_button(tools_row, "Eraser", lambda: set_tool("eraser")).pack(side="left", padx=3)
make_button(tools_row, "Line", lambda: set_tool("line")).pack(side="left", padx=3)
make_button(tools_row, "Rectangle", lambda: set_tool("rectangle")).pack(side="left", padx=3)
make_button(tools_row, "Oval", lambda: set_tool("oval")).pack(side="left", padx=3)
make_button(tools_row, "Triangle", lambda: set_tool("triangle")).pack(side="left", padx=3)
make_button(tools_row, "Undo", undo).pack(side="left", padx=3)
make_button(tools_row, "Clear", clear_canvas).pack(side="left", padx=3)
make_button(tools_row, "Open", open_image).pack(side="left", padx=3)
make_button(tools_row, "Save", save_image).pack(side="left", padx=3)


options_row = tk.Frame(toolbar, bg=PEACH_PANEL)
options_row.pack(fill="x", pady=(6, 2))

tk.Label(
    options_row,
    text="Quick Colors:",
    bg=PEACH_PANEL,
    fg=TEXT_COLOR,
    font=FONT_MAIN,
).pack(side="left", padx=(3, 5))

quick_colors = [
    ("Black", "#000000"),
    ("Red", "#FF0000"),
    ("Blue", "#0000FF"),
    ("Green", "#008000"),
    ("Yellow", "#FFFF00"),
    ("Purple", "#800080"),
]

for color_name, color_code in quick_colors:
    swatch = tk.Button(
        options_row,
        text=color_name,
        command=lambda chosen=color_code: set_color(chosen),
        bg=color_code,
        fg="white" if color_name in ("Black", "Blue", "Green", "Purple") else TEXT_COLOR,
        activebackground=color_code,
        font=("Arial", 9, "bold"),
        relief="raised",
        padx=7,
        pady=3,
        cursor="hand2",
    )
    swatch.pack(side="left", padx=2)

tk.Label(
    options_row,
    text="Brush Size:",
    bg=PEACH_PANEL,
    fg=TEXT_COLOR,
    font=FONT_MAIN,
).pack(side="left", padx=(14, 3))

size_slider = tk.Scale(
    options_row,
    from_=1,
    to=100,
    orient="horizontal",
    command=change_brush_size,
    length=180,
    bg=PEACH_PANEL,
    fg=TEXT_COLOR,
    troughcolor=PEACH_BUTTON,
    highlightthickness=0,
    showvalue=False,
)
size_slider.set(5)
size_slider.pack(side="left", padx=2)

size_value_label = tk.Label(
    options_row,
    text="5",
    width=3,
    bg=PEACH_PANEL,
    fg=TEXT_COLOR,
    font=FONT_MAIN,
)
size_value_label.pack(side="left", padx=(0, 8))

fill_var = tk.BooleanVar(value=False)
fill_check = tk.Checkbutton(
    options_row,
    text="Fill Shapes",
    variable=fill_var,
    command=toggle_fill,
    bg=PEACH_PANEL,
    fg=TEXT_COLOR,
    activebackground=PEACH_PANEL,
    selectcolor=PEACH_BUTTON,
    font=FONT_MAIN,
)
fill_check.pack(side="left", padx=8)

status_label = tk.Label(
    root,
    text="",
    bg=PEACH_BG,
    fg=TEXT_COLOR,
    font=("Arial", 9, "bold"),
)
status_label.pack(pady=(3, 8))


canvas.bind("<Button-1>", start_drawing)
canvas.bind("<B1-Motion>", draw_motion)
canvas.bind("<ButtonRelease-1>", finish_drawing)

refresh_canvas()
update_status()
root.mainloop()
