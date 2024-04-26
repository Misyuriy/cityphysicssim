# City editor/simulator

## Class architecture:
See class architecture scheme on Figma:
https://www.figma.com/file/BHkfvJoLa1lQHx5yA7jFKt/class_architecture?type=design&node-id=0%3A1&mode=design&t=6fWoQtrckCo5ET9w-1

Or see `architecture.png`

## Controls

While work on the UI is in progress, there are temporary controls for the editor and simulator modes

### General
`WASD` - Camera movement

`SHIFT` + `X` - Switch camera between real view and map view

`Mouse wheel` - Zoom in/out. ZOOM ONLY WORKS IN MAP VIEW

### Editor-only
`LMB` - select **buildings** and **road joints**

`SHIFT` + `LMB` - select a road when clicked on a road joint **if another joint is selected**

`RMB` - move **buildings** and **road joints**

`Mouse wheel` - rotate **buildings** if any is selected

`1`, `2` - spawn 2 types of buildings **if nothing is selected**

`2`, `4`, `6`, `8` - set the amount of lanes on a road **if a road is selected**

`DELETE` - delete a road **if a road is selected**

`SHIFT` + `Z` - spawn new road joint **if a road joint is selected**
