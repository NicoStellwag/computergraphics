import pygame


def keyboard(event):
    """handle keyboard events

    Args:
        event (pygame event): event

    Returns:
        bool: running
    """
    if event.key == pygame.K_q:
        return False
    return True


def mousebutton(event, camera):
    """handle mouse button events

    Args:
        event (pygame event): event
        camera (Camera): camera struct

    Returns:
        Camera: potentially modified camera struct
    """
    if event.button == 4:  # scroll up zooms in
        camera.distance = max(1, camera.distance - 1)
    elif event.button == 5:  # scroll down zooms out
        camera.distance += 1
    return camera


def mousemotion(camera, window_size, prev_mouse_mvt):
    """handle mouse motion events

    Args:
        camera (Camera): camera struct
        window_size (Tuple[int, int]): window size
        prev_mouse_mvt (pygame mouse get rel): previous mouse movement

    Returns:
        (Camera, mouse_mvt): potentially modified camera struct and mouse movement
    """
    if pygame.mouse.get_pressed()[0]:  # left click drag moves camera center
        if prev_mouse_mvt is not None:
            mouse_mvt = pygame.mouse.get_rel()
            camera.center[0] -= float(mouse_mvt[0]) / window_size[0]
            camera.center[1] += float(mouse_mvt[1]) / window_size[1]
        else:
            mouse_mvt = pygame.mouse.get_rel()
        return camera, mouse_mvt

    elif pygame.mouse.get_pressed()[2]:  # right click drag moves camera angles
        if prev_mouse_mvt is not None:
            mouse_mvt = pygame.mouse.get_rel()
            camera.phi += float(mouse_mvt[0]) / window_size[0]
            camera.psi += float(mouse_mvt[1]) / window_size[1]
        else:
            mouse_mvt = pygame.mouse.get_rel()
    else:
        mouse_mvt = None
    return camera, mouse_mvt


def handle_events(camera, window_size, prev_mouse_mvt):
    """handle pygame events (window close, keyboard, mouse),
    modify camera struct accordingly

    Args:
        camera (Camera): camera struct
        window_size (Tuple[int, int]): window size
        prev_mouse_mvt (pygame mouse get rel): previous mouse movement

    Returns:
        (running, camera, mouse_mvt): running bool, potentially modified camera struct and mouse movement
    """
    running = True
    mouse_mvt = None
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            running = keyboard(event=event)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            camera = mousebutton(event=event, camera=camera)
        elif event.type == pygame.MOUSEMOTION:
            camera, mouse_mvt = mousemotion(
                camera=camera, window_size=window_size, prev_mouse_mvt=prev_mouse_mvt
            )
    return running, camera, mouse_mvt
