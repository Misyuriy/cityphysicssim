from graphics import Window, InputType


def mainloop():
    window = Window([400, 400], '1')

    running = True

    while running:
        for event in window.get_input():
            if event.type == InputType.QUIT:
                running = False


if __name__ == '__main__':
    mainloop()
